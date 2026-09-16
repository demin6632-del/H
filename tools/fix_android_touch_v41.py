from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
OLD='if(synthetic){synthetic=false;e.stopPropagation();}'
NEW='if(synthetic){synthetic=false;}'
MARK='ANDROID-TOUCH-FIX-V4-FINAL'
for p in FILES:
    s=p.read_text(encoding='utf-8')
    if OLD in s:
        s=s.replace(OLD,NEW)
    elif 'if(synthetic){synthetic=false;}' not in s:
        raise SystemExit(f'{p}: V39 synthetic click blocker not found')
    if MARK not in s:
        s += f'\n<!-- {MARK}: synthetic click now reaches the original button handler. -->\n'
    p.write_text(s,encoding='utf-8')
print(MARK)
