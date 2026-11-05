from pathlib import Path
import json
import re
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
data = json.loads((root / '.work/projects.json').read_text('utf-8'))
selected = [p for p in data if not p.get('archived', False)]
manifest = json.loads((root / 'output/pdf/manifest.json').read_text('utf-8'))
assert len(selected) == len(manifest) == 11, 'PDF catalog must match the eleven selected projects'
normalize = lambda s: re.sub(r'\s+', '', s)
total = 0
for p in selected:
    file = root / 'output/pdf' / f'{p["id"]}-portfolio.pdf'
    reader = PdfReader(file)
    text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    assert len(reader.pages) >= 4, (p['id'], 'rich detail PDF must not remain the old short brochure')
    assert len(normalize(reader.pages[-1].extract_text() or '')) > 300, (p['id'], 'orphaned closing page')
    assert '\ufffd' not in text, p['id']
    assert p['github'] in text, p['id']
    for decision in p['detail']['engineering']:
        assert normalize(decision['choice']) in normalize(text), (p['id'], 'missing engineering explanation')
    for paragraph in p['detail']['contribution']:
        assert normalize(paragraph) in normalize(text), (p['id'], 'missing contribution text')
    uris = []
    for page in reader.pages:
        assert page.extract_text().strip(), (p['id'], 'empty page')
        for ref in page.get('/Annots', []):
            uri = ref.get_object().get('/A', {}).get('/URI')
            if uri:
                uris.append(str(uri))
    assert p['github'] in uris, p['id']
    for source in p['detail']['sources']:
        assert source['url'] in uris, (p['id'], 'source URL not clickable')
    assert manifest[p['id']]['bytes'] == file.stat().st_size, p['id']
    assert manifest[p['id']]['pages'] == len(reader.pages), p['id']
    total += len(reader.pages)
print(json.dumps({'ok': True, 'pdfs': len(selected), 'pages': total, 'completeEngineeringText': True, 'clickableSources': True}))
