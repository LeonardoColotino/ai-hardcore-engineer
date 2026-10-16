"""SQLite transactions; each operation owns its connection (thread safe)."""
import json, os, sqlite3, uuid
from contextlib import contextmanager
from pathlib import Path
from fastapi import HTTPException

class Store:
    def __init__(self):
        self.path = Path(os.getenv("STATE_DB", "app/data/state.sqlite3"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, owner TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, session TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, metadata TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS tickets(id TEXT PRIMARY KEY, session TEXT NOT NULL, owner TEXT NOT NULL, reason TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'OPEN', operator TEXT, reply TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP, updated TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS conversation_state(session TEXT PRIMARY KEY, state TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS requests(owner TEXT NOT NULL, key TEXT NOT NULL, fingerprint TEXT NOT NULL, response TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(owner,key));
            CREATE TABLE IF NOT EXISTS traces(id TEXT PRIMARY KEY, session TEXT NOT NULL, owner TEXT NOT NULL, data TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS feedback(request_id TEXT NOT NULL, owner TEXT NOT NULL, rating INTEGER NOT NULL, PRIMARY KEY(request_id,owner));
            PRAGMA user_version=2;
            CREATE INDEX IF NOT EXISTS messages_session ON messages(session,id);
            """)
    @contextmanager
    def db(self):
        c=sqlite3.connect(self.path, timeout=10)
        c.row_factory=sqlite3.Row
        try:
            with c: yield c
        finally: c.close()
    def session(self, owner):
        sid=uuid.uuid4().hex
        with self.db() as c: c.execute("INSERT INTO sessions(id,owner) VALUES (?,?)",(sid,owner))
        return {"session_id":sid}
    def check(self,sid,owner):
        with self.db() as c: row=c.execute("SELECT * FROM sessions WHERE id=? AND owner=?",(sid,owner)).fetchone()
        if not row: raise HTTPException(404,"Conversa não encontrada")
    def sessions(self,owner):
        with self.db() as c: return [dict(r) for r in c.execute("SELECT s.id AS session_id,s.created,COALESCE((SELECT m.content FROM messages m WHERE m.session=s.id AND m.role='user' ORDER BY m.id LIMIT 1),'Nova conversa') AS title FROM sessions s WHERE s.owner=? ORDER BY s.rowid DESC",(owner,))]
    def messages(self,sid,owner):
        self.check(sid,owner)
        with self.db() as c: return [{**dict(r),"metadata":json.loads(r['metadata'])} for r in c.execute("SELECT * FROM messages WHERE session=? ORDER BY id",(sid,))]
    def add(self,sid,role,content,metadata=None):
        with self.db() as c: c.execute("INSERT INTO messages(session,role,content,metadata) VALUES (?,?,?,?)",(sid,role,content,json.dumps(metadata or {})))
    def ticket(self,sid,owner,reason):
        tid='T-'+uuid.uuid4().hex[:16]
        with self.db() as c:
            c.execute("BEGIN IMMEDIATE")
            existing=c.execute("SELECT id FROM tickets WHERE session=? AND owner=? AND status IN ('OPEN','IN_PROGRESS') ORDER BY rowid DESC LIMIT 1",(sid,owner)).fetchone()
            if existing: return existing['id']
            c.execute("INSERT INTO tickets(id,session,owner,reason) VALUES (?,?,?,?)",(tid,sid,owner,reason[:500]))
        return tid
    def tickets(self,identity):
        with self.db() as c:
            rows=c.execute("SELECT * FROM tickets ORDER BY created DESC") if identity['role'] in ('operator','admin') else c.execute("SELECT * FROM tickets WHERE owner=? ORDER BY created DESC",(identity['sub'],))
            return [dict(r) for r in rows]
    def get_ticket(self,tid,identity):
        row=next((r for r in self.tickets(identity) if r['id']==tid),None)
        if row is None: raise HTTPException(404,"Ticket não encontrado")
        return row
    def transition(self,tid,identity,status,reply):
        if identity['role'] not in ('operator','admin'): raise HTTPException(403,"Somente operador")
        with self.db() as c:
            c.execute("BEGIN IMMEDIATE")
            r=c.execute("SELECT * FROM tickets WHERE id=?",(tid,)).fetchone()
            if not r: raise HTTPException(404,"Ticket não encontrado")
            allowed={'OPEN':['IN_PROGRESS'],'IN_PROGRESS':['RESOLVED'],'RESOLVED':['CLOSED'],'CLOSED':[]}
            if status not in allowed[r['status']]: raise HTTPException(409,"Transição inválida")
            if r['operator'] and r['operator']!=identity['sub'] and identity['role']!='admin': raise HTTPException(403,"Ticket assumido por outro operador")
            if status=='RESOLVED' and not reply.strip(): raise HTTPException(422,"Resposta obrigatória")
            c.execute("UPDATE tickets SET status=?,operator=?,reply=?,updated=CURRENT_TIMESTAMP WHERE id=?",(status,identity['sub'],reply or r['reply'],tid))
            if status=='RESOLVED': c.execute("INSERT INTO messages(session,role,content,metadata) VALUES (?,?,?,?)",(r['session'],'human',reply,json.dumps({'ticket_id':tid})))
        return self.get_ticket(tid,identity)

    def state(self, sid, owner):
        self.check(sid, owner)
        with self.db() as c:
            row = c.execute("SELECT state FROM conversation_state WHERE session=?", (sid,)).fetchone()
            return json.loads(row['state']) if row else {}
    def save_state(self, sid, owner, state):
        self.check(sid, owner)
        with self.db() as c:
            c.execute("INSERT INTO conversation_state(session,state) VALUES (?,?) ON CONFLICT(session) DO UPDATE SET state=excluded.state", (sid, json.dumps(state, ensure_ascii=False)))

    def active_ticket(self, sid, owner):
        self.check(sid, owner)
        with self.db() as c:
            row=c.execute("SELECT * FROM tickets WHERE session=? AND owner=? AND status IN ('OPEN','IN_PROGRESS') ORDER BY rowid DESC LIMIT 1",(sid,owner)).fetchone()
            return dict(row) if row else None

    def reserve_request(self, owner, key, fingerprint):
        with self.db() as c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT * FROM requests WHERE owner=? AND key=?",(owner,key)).fetchone()
            if row:
                if row['fingerprint'] != fingerprint: raise HTTPException(409,'Chave já usada para outra mensagem')
                if row['response'] is None: raise HTTPException(409,'Solicitação em andamento ou interrompida. Consulte o histórico antes de reenviar.')
                return json.loads(row['response'])
            c.execute("INSERT INTO requests(owner,key,fingerprint) VALUES (?,?,?)",(owner,key,fingerprint))
        return None

    def finish_request(self, owner, key, response):
        with self.db() as c:
            c.execute("UPDATE requests SET response=? WHERE owner=? AND key=?",(json.dumps(response,ensure_ascii=False),owner,key))

    def save_trace(self, request_id, sid, owner, metadata):
        # Allowlist only operational metadata. Never persist plan queries/answers/history here.
        allowed=('agents','stages','duration_ms','outcome','generation_kind','fallback','coverage','planner_origin','prompt_version','provider_usage','plan','task_outcomes')
        safe={k:metadata[k] for k in allowed if k in metadata}
        # Stage records can contain arbitrary provider text: project again.
        safe['stages']=[{k:v for k,v in stage.items() if k in ('agent','tool','duration_ms','status','task_id','decision','review','error_type')} for stage in metadata.get('stages',[])]
        with self.db() as c:
            c.execute("INSERT OR REPLACE INTO traces(id,session,owner,data) VALUES (?,?,?,?)",(request_id,sid,owner,json.dumps(safe)))

    def trace(self, request_id, identity):
        with self.db() as c:
            row=c.execute("SELECT * FROM traces WHERE id=? AND owner=?",(request_id,identity['sub'])).fetchone()
            if not row and identity['role'] in ('operator','admin'):
                row=c.execute("SELECT * FROM traces WHERE id=?",(request_id,)).fetchone()
        if not row: raise HTTPException(404,'Trace não encontrado')
        return {'request_id':row['id'],'session_id':row['session'],'created':row['created'],**json.loads(row['data'])}

    def record_feedback(self, request_id, owner, rating):
        self.trace(request_id, {'sub':owner,'role':'customer'})
        with self.db() as c:
            c.execute("INSERT INTO feedback(request_id,owner,rating) VALUES (?,?,?) ON CONFLICT(request_id,owner) DO UPDATE SET rating=excluded.rating",(request_id,owner,rating))
        return {'saved':True}
