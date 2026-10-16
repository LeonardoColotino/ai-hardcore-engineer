"""Real HTTP process, optional browser, synthetic support with inference disabled."""
import json, os, secrets, socket, subprocess, sys, tempfile, time
from pathlib import Path
import urllib.request
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
def main():
    report={'category':'real_http_synthetic_support_no_llm','semantic_quality':'not_evaluated','checks':{}}
    with tempfile.TemporaryDirectory(prefix='getnet-http-') as temp:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
        env={**os.environ,'AUTH_SECRET':secrets.token_urlsafe(48),'DEMO_PASSWORD':secrets.token_urlsafe(20),'STATE_DB':temp+'/state.sqlite3','DEMO_USERS_FILE':temp+'/users.json','INDEX_DIR':temp+'/index','LLM_PROVIDER':'disabled','WEB_SEARCH_ENABLED':'false'}
        subprocess.run([sys.executable,'scripts/init_demo.py'],cwd=ROOT,env=env,check=True,capture_output=True)
        def request(path,payload=None,token=None):
            headers={'Content-Type':'application/json'}
            if token: headers['Authorization']='Bearer '+token
            req=urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=json.dumps(payload).encode() if payload is not None else None,headers=headers)
            with urllib.request.urlopen(req,timeout=20) as response: return json.load(response)
        def start():
            proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            for _ in range(50):
                try: request('/health'); return proc
                except OSError: time.sleep(.1)
            proc.terminate();proc.wait(timeout=10);raise RuntimeError('HTTP startup failed')
        proc=start()
        try:
            report['health']=request('/health')
            tokens={n:request('/auth/login',{'username':n,'password':env['DEMO_PASSWORD']})['access_token'] for n in ('cliente1988','cliente2026','operador')}
            token=tokens['cliente1988'];op=tokens['operador']
            result=request('/chat',{'message':'Quando recebo minhas vendas?','idempotency_key':'smoke-payment'},token)
            assert request('/chat',{'message':'Quando recebo minhas vendas?','idempotency_key':'smoke-payment'},token)==result
            report['checks']['idempotent_chat']=True;sid=result['session_id']
            try: request('/sessions/'+sid+'/messages',token=tokens['cliente2026']);raise AssertionError('Ownership leaked')
            except HTTPError as exc: assert exc.code in (403,404)
            report['checks']['ownership']=True
            request('/chat',{'message':'Quero atendimento humano','session_id':sid},token)
            ticket=request('/tickets',token=token)[0]['id']
            request('/tickets/'+ticket+'/reply',{'status':'IN_PROGRESS'},op)
            request('/tickets/'+ticket+'/reply',{'status':'RESOLVED','reply':'Resposta humana de teste.'},op)
            request('/tickets/'+ticket+'/reply',{'status':'CLOSED'},op)
            messages=request('/sessions/'+sid+'/messages',token=token)
            assert sum(m['role']=='human' for m in messages)==1
            report['checks']['operator_lifecycle']=True
            proc.terminate();proc.wait(timeout=10);proc=start()
            assert request('/sessions/'+sid+'/messages',token=token)==messages
            assert request('/tickets/'+ticket,token=token)['status']=='CLOSED'
            report['checks']['restart_persistence']=True
            if '--browser' in sys.argv:
                env['BROWSER_TEST_URL']=f'http://127.0.0.1:{port}'
                completed=subprocess.run(['node','scripts/browser_smoke.cjs'],cwd=ROOT,env=env,text=True,capture_output=True)
                report['browser']={'exit_code':completed.returncode,'output':completed.stdout[-1000:],'errors':completed.stderr[-1500:]}
                report['checks']['browser']=completed.returncode==0
            report['status']='passed' if all(report['checks'].values()) else 'failed'
        finally: proc.terminate();proc.wait(timeout=10)
    output=ROOT/'evidence/current/http-smoke.json';output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2),encoding='utf-8');print(output)
    if report['status']!='passed': raise SystemExit(1)
if __name__=='__main__': main()
