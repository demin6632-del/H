from pathlib import Path
import base64

# ART-ATLAS-V4: новый визуальный слой по референсу пользователя.
# В репозиторий сохраняется текстовый установщик, чтобы CI одинаково
# применял изображения к Web и Android-версии.
ATLAS_B64 = '''__ATLAS_B64__'''

ROOT = Path('.')
JS = base64.b64decode(ATLAS_B64.encode('ascii')).decode('utf-8')

for rel in ['NEW_DARK_RPG/art-atlas-v4.js', 'android/app/src/main/assets/art-atlas-v4.js']:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(JS, encoding='utf-8')

for rel in ['NEW_DARK_RPG/index.html', 'android/app/src/main/assets/index.html']:
    p = ROOT / rel
    s = p.read_text(encoding='utf-8')
    tag = '<script src="art-atlas-v4.js"></script>'
    if tag not in s:
        if '<script src="art-atlas-v3.js"></script>' in s:
            s = s.replace('<script src="art-atlas-v3.js"></script>', '<script src="art-atlas-v3.js"></script>\n'+tag, 1)
        elif '</body>' in s:
            s = s.replace('</body>', tag+'\n</body>', 1)
        else:
            s += '\n'+tag+'\n'
        p.write_text(s, encoding='utf-8')

print('ART-ATLAS-V4 installed')
