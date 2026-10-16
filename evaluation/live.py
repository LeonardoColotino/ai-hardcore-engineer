"""Real HTTP capture only. No automatic semantic quality approval."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import requests

ROOT = Path(__file__).resolve().parents[1]

def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / 'app').rglob('*')):
        if path.is_file() and path.suffix in ('.py', '.html', '.js', '.css'):
            digest.update(str(path.relative_to(root)).encode('utf-8'))
            digest.update(path.read_bytes())
    return digest.hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='http://127.0.0.1:8000')
    p.add_argument('--dataset', choices=['historical','development','validation'], default='development')
    p.add_argument('--repetitions', type=int, default=3)
    p.add_argument('--timeout', type=float, default=180)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    if not 1 <= args.repetitions <= 10 or args.timeout <= 0:
        p.error('repetitions deve estar entre 1 e 10 e timeout > 0')
    base = args.url.rstrip('/')
    dataset_name = 'live_dataset.json' if args.dataset == 'historical' else args.dataset+'_dataset.json'
    dataset_path = Path(__file__).with_name(dataset_name)
    cases = json.loads(dataset_path.read_text(encoding='utf-8'))
    output = args.output or Path(__file__).with_name('live_'+args.dataset+'_responses.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    startup = {'category':'real_http_capture_attempt','quality_status':'pending_factual_review',
               'started_at':datetime.now(timezone.utc).isoformat(), 'code_sha256':digest_tree(ROOT),
               'dataset_sha256':hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
               'dataset':args.dataset, 'repetitions':args.repetitions, 'rows':[],
               'status':'starting', 'client_python':platform.python_version()}
    output.write_text(json.dumps(startup, ensure_ascii=False, indent=2), encoding='utf-8')
    try:
        return capture(args, base, cases, output, startup)
    except KeyboardInterrupt:
        current=json.loads(output.read_text(encoding='utf-8'))
        current.update(status='interrupted', finished_at=datetime.now(timezone.utc).isoformat())
        output.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding='utf-8')
        raise
    except (requests.RequestException, ValueError, KeyError, RuntimeError) as exc:
        current=json.loads(output.read_text(encoding='utf-8'))
        current.update(status='failed', error_type=type(exc).__name__,
                       error='Capture failed; inspect local endpoint/configuration. No credentials recorded.',
                       finished_at=datetime.now(timezone.utc).isoformat())
        output.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding='utf-8')
        raise SystemExit('Captura falhou; detalhes seguros e resultados parciais em '+str(output)) from None

def capture(args, base, cases, output, startup):
    health = requests.get(base+'/health', timeout=10)
    health.raise_for_status()
    if health.json().get('llm_provider') not in ('ollama', 'llama_cpp', 'openai_compatible', 'openai-compatible'):
        raise RuntimeError('Configure um provedor real; configuração não comprova inferência.')
    password = os.getenv('DEMO_PASSWORD') or getpass.getpass('Senha demo: ')
    login = requests.post(base+'/auth/login',json={'username':'cliente1988','password':password},timeout=10)
    login.raise_for_status()
    headers = {'Authorization':'Bearer '+login.json()['access_token']}
    manifest = {**startup, 'status':'running', 'health':health.json(), 'inference_note':'Provider configuration is not execution proof. Review response generation_kind, model and corpus against server manifest.'}
    # Checkpoint each scenario; interruption retains completed/error rows. No credentials stored.
    def save():
        output.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    save()
    for repeat in range(1,args.repetitions+1):
        for case in cases:
            sid = None
            row = {**case,'repeat':repeat,'results':[],'reviewer_type':None,'reviewer':None,'review_scores':None}
            manifest['rows'].append(row)
            save()
            print(f"Executando {case['id']} repetição {repeat}...",flush=True)
            for text in case['turns']:
                started = time.perf_counter()
                try:
                    response = requests.post(base+'/chat',json={'message':text,'session_id':sid},headers=headers,timeout=args.timeout)
                    response.raise_for_status()
                    result = response.json()
                    sid = result['session_id']
                    row['results'].append({'input':text,'http_status':response.status_code,'elapsed_ms':round((time.perf_counter()-started)*1000,2),'response':result})
                except (requests.RequestException, ValueError, KeyError) as exc:
                    row['results'].append({'input':text,'elapsed_ms':round((time.perf_counter()-started)*1000,2),'error_type':type(exc).__name__,'error':'HTTP/provider capture failed; inspect server safe logs','session_continuity':'unknown_after_error'})
                    save()
                    # Remaining turns are counted explicitly but not sent into an unknown session.
                    remaining = case['turns'][len(row['results']):]
                    row['results'].extend({'input':item,'error_type':'blocked_by_previous_turn','error':'Not executed after failed continuity'} for item in remaining)
                    break
                save()
            save()
    turns = [turn for row in manifest['rows'] for turn in row['results']]
    responses = [turn['response'] for turn in turns if 'response' in turn]
    manifest['capture_summary']={'scenario_attempts':len(manifest['rows']),'turns_total':len(turns),'http_responses':len(responses),'capture_errors':sum('error' in t for t in turns),'llm_generated':sum(r.get('metadata',{}).get('generation_kind')=='llm' for r in responses),'extractive_fallback':sum(r.get('metadata',{}).get('generation_kind')=='extractive_fallback' for r in responses),'abstention':sum(bool(r.get('metadata',{}).get('abstained')) for r in responses),'escalated':sum(bool(r.get('escalated')) for r in responses),'semantic_quality':'not_scored'}
    manifest['status']='completed_with_errors' if manifest['capture_summary']['capture_errors'] else 'completed'
    manifest['finished_at']=datetime.now(timezone.utc).isoformat()
    save()
    print(f'Captura salva: {output}. Rever fontes completas; não há aprovação automática de qualidade.')

if __name__ == '__main__':
    main()
