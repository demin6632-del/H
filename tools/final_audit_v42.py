from pathlib import Path
import re
import subprocess

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
REQUIRED=['stats','skills','depthSelect','exploreBtn','abyssKeyBtn','inventoryList','shopList']
KNOWN={'if','for','while','switch','catch','setTimeout','clearTimeout','Math','Number','String','Boolean'}

for path in FILES:
    s=path.read_text(encoding='utf-8')
    scripts='\n'.join(m.group(1) for m in re.finditer(r'<script[^>]*>(.*?)</script>',s,re.S))
    Path('/tmp/final_game.js').write_text(scripts,encoding='utf-8')
    subprocess.run(['node','--check','/tmp/final_game.js'],check=True)
    ids=re.findall(r'\bid=["\']([^"\']+)',s,re.I)
    dup=sorted({x for x in ids if ids.count(x)>1})
    if dup: raise SystemExit(f'{path}: duplicate ids: {dup}')
    for ident in REQUIRED:
        if f'id="{ident}"' not in s and f"id='{ident}'" not in s:
            raise SystemExit(f'{path}: missing id={ident}')
    funcs=set(re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(',scripts))
    funcs|=set(re.findall(r'window\.([A-Za-z_$][\w$]*)\s*=\s*function',scripts))
    missing=[]
    for m in re.finditer(r'onclick\s*=\s*["\']([^"\']+)',s,re.I):
        for fn in re.findall(r'\b([A-Za-z_$][\w$]*)\s*\(',m.group(1)):
            if fn not in funcs and fn not in KNOWN: missing.append(fn)
    if missing: raise SystemExit(f'{path}: missing onclick handlers: {sorted(set(missing))}')
    if 'TOUCH-BUTTON-FIX-V39' in s: raise SystemExit(f'{path}: obsolete V39 touch interceptor remains')
    if 'ANDROID-TOUCH-FIX-V42' not in s: raise SystemExit(f'{path}: V42 touch marker missing')
    print(f'FINAL AUDIT OK: {path}; buttons={len(re.findall(r"<button\\b",s,re.I))}; functions={len(funcs)}')

java=Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java').read_text(encoding='utf-8')
for token in ['setOnTouchListener','elementFromPoint','ACTION_UP','ANDROID-TOUCH-NATIVE-FALLBACK-V42']:
    if token not in java: raise SystemExit(f'MainActivity.java: missing {token}')
print('FINAL ANDROID TOUCH AUDIT OK')