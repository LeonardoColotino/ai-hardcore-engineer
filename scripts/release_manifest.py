"""Hash release inputs without secrets or runtime databases; no approval inferred."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def manifest():
    files = {}
    for path in sorted(ROOT.rglob('*')):
        rel = path.relative_to(ROOT)
        if any(part in {'.git', '.venv', '__pycache__', '.pytest_cache', 'evidence', 'node_modules'} for part in rel.parts):
            continue
        if not path.is_file() or path.name == '.env' or path.suffix in {'.sqlite3', '.db', '.pyc'} or path.name == 'demo_users.json':
            continue
        if rel.parts[0] == 'evaluation' and ('responses' in path.name or path.name == 'report.json'):
            continue
        files[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    versions = {}
    for name in ('fastapi', 'starlette', 'pydantic', 'requests', 'numpy', 'pytest', 'uvicorn'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {'captured_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
            'platform': platform.platform(), 'dependencies': versions, 'files': files,
            'release_sha256': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(),
            'scope': 'source/config/tests/public corpus; excludes evidence, secrets and runtime state; not a quality approval'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'evidence/current/release-manifest.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest(), indent=2), encoding='utf-8')
    print(args.output)
