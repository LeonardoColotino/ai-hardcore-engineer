"""Real Docker build, non-root volume/persistence and HTTP lifecycle gate.
No provider calls; a successful run validates container engineering only.
"""
import json
from pathlib import Path
import secrets
import subprocess
import time
import urllib.request

root = Path(__file__).resolve().parents[1]
name = 'getnet-smoke-' + secrets.token_hex(4)
volume = name + '-state'
image = 'getnet-candidate:smoke'
password = secrets.token_urlsafe(20)

def run(*args):
    return subprocess.run(['docker', *args], cwd=root, check=True, text=True, capture_output=True).stdout.strip()

try:
    run('build', '-t', image, '.')
    run('volume', 'create', volume)
    run('run', '--rm', '-v', volume+':/state', image, 'python', '-c',
        "import os; from pathlib import Path; assert os.getuid()!=0; Path('/state/persistence-probe').write_text('persisted')")
    run('run', '-d', '--name', name, '-p', '127.0.0.1::8000', '-v', volume+':/state',
        '-e', 'AUTH_SECRET='+secrets.token_urlsafe(48), '-e', 'DEMO_PASSWORD='+password,
        '-e', 'STATE_DB=/state/state.sqlite3', '-e', 'DEMO_USERS_FILE=/state/demo_users.json',
        '-e', 'LLM_PROVIDER=disabled', '-e', 'WEB_SEARCH_ENABLED=false', image)
    port = json.loads(run('inspect', name))[0]['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']
    def health():
        for attempt in range(30):
            try:
                with urllib.request.urlopen('http://127.0.0.1:'+port+'/health', timeout=2) as response:
                    assert response.status == 200
                    return
            except (OSError, AssertionError):
                time.sleep(1)
        raise RuntimeError('Container health never became ready')
    health()
    run('exec', name, 'python', 'scripts/init_demo.py')
    def request(path, payload=None, token=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer '+token
        req = urllib.request.Request('http://127.0.0.1:'+port+path,
              data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    token = request('/auth/login', {'username': 'cliente1988', 'password': password})['access_token']
    sid = request('/sessions', {}, token)['session_id']
    result = request('/chat', {'message': 'Quando recebo minhas vendas?', 'session_id': sid}, token)
    assert result['session_id'] == sid
    before = request('/sessions/'+sid+'/messages', token=token)
    assert before
    run('restart', name)
    health()
    assert request('/sessions/'+sid+'/messages', token=token) == before
    run('exec', name, 'python', '-c', "from pathlib import Path; assert Path('/state/persistence-probe').read_text()=='persisted'")
    print('PASS: real image build, non-root writable volume, HTTP login/chat/history, restart persistence. LLM and semantic gates NOT executed.')
finally:
    subprocess.run(['docker', 'rm', '-f', name], capture_output=True)
    subprocess.run(['docker', 'volume', 'rm', volume], capture_output=True)
