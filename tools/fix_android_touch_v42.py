from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
OLD='if(synthetic){synthetic=false;e.stopPropagation();}'
NEW='if(synthetic){synthetic=false;}'
MARK='ANDROID-TOUCH-FIX-V4-ROOT-CAUSE'
for p in FILES:
    s=p.read_text(encoding='utf-8')
    if OLD in s:
        s=s.replace(OLD,NEW)
    elif 'TOUCH-BUTTON-FIX-V39' not in s:
        raise SystemExit(f'{p}: V39 touch handler not found')
    if MARK not in s:
        s += f'\n<!-- {MARK}: V39 synthetic click no longer stops propagation. -->\n'
    p.write_text(s,encoding='utf-8')
print(MARK)
