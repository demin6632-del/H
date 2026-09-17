from pathlib import Path
import base64

# ART-ATLAS-V4: визуальный слой в стиле утверждённого пользователем референса.
ATLAS_JS_B64 = '''BASE64_PLACEHOLDER'''

ROOT = Path('.')
js = base64.b64decode(ATLAS_JS_B64.encode('ascii')).decode('utf-8')
for rel in ['NEW_DARK_RPG/art-atlas-v4.js', 'android/app/src/main/assets/art-atlas-v4.js']:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(js, encoding='utf-8')

for rel in ['NEW_DARK_RPG/index.html', 'android/app/src/main/assets/index.html']:
    p = ROOT / rel
    s = p.read_text(encoding='utf-8')
    tag = '<script src="art-atlas-v4.js"></script>'
    if tag not in s:
        marker = '<script src="art-atlas-v3.js"></script>'
        if marker in s:
            s = s.replace(marker, marker+'\n'+tag, 1)
        elif '</body>' in s:
            s = s.replace('</body>', tag+'\n</body>', 1)
        else:
            s += '\n'+tag+'\n'
        p.write_text(s, encoding='utf-8')
print('ART-ATLAS-V4 installed')
