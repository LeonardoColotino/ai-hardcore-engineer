import json
from pathlib import Path

def test_eval_datasets_utf8_versioned_and_multiturn(tmp_path):
    root = Path(__file__).resolve().parents[2] / 'evaluation'
    dev = json.loads((root/'development_dataset.json').read_text(encoding='utf-8'))
    val = json.loads((root/'validation_dataset.json').read_text(encoding='utf-8'))
    assert len(dev) == 20 and len(val) == 10
    assert len({row['id'] for row in dev+val}) == 30
    assert sum(len(row['turns'])>1 for row in dev+val) >= 10
    assert all(row['expected'] and row['prohibited'] for row in dev+val)
    path = tmp_path/'acentos.json'
    text = 'soluções contratação não ç'
    path.write_text(json.dumps({'text':text},ensure_ascii=False),encoding='utf-8')
    assert json.loads(path.read_text(encoding='utf-8'))['text'] == text
