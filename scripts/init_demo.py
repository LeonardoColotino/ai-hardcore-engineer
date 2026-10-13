"""Explicit local demo provisioning; no public default password."""
import json, os, secrets, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.security import password_hash
from dotenv import load_dotenv
load_dotenv()
password=os.getenv('DEMO_PASSWORD')
if not password or len(password)<10: raise SystemExit('Defina DEMO_PASSWORD (mínimo 10 caracteres)')
path=Path(os.getenv('DEMO_USERS_FILE','app/data/demo_users.json'))
path.parent.mkdir(parents=True,exist_ok=True)
result={}
for name,role in [('cliente1988','customer'),('cliente2026','customer'),('operador','operator')]:
 salt=secrets.token_hex(16); result[name]={'role':role,'salt':salt,'hash':password_hash(password,salt)}
path.write_text(json.dumps(result),encoding='utf-8')
print('Identidades de demonstração provisionadas; senha obtida do ambiente.')
