"""Download pinned GGUF weights separately; preserve/verify existing files."""

import hashlib
from pathlib import Path
import requests

URL = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
SHA256 = "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"
p = Path("models/qwen2.5-3b.gguf")
p.parent.mkdir(exist_ok=True)
if not p.exists():
    temporary = p.with_suffix(".partial")
    with requests.get(URL, stream=True, timeout=60) as response:
        response.raise_for_status()
        with temporary.open("wb") as output:
            for block in response.iter_content(1024 * 1024):
                output.write(block)
    temporary.replace(p)
with p.open("rb") as source:
    actual = hashlib.file_digest(source, "sha256").hexdigest()
if actual != SHA256:
    raise SystemExit("Model hash differs. Do not use changed weights without review.")
print("Modelo verificado em " + str(p.resolve()))
