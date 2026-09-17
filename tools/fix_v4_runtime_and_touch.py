from pathlib import Path
import re

# V4 runtime: исправляем подключение внешнего скрипта и не меняем игровую логику.
FILES = [Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s = p.read_text(encoding='utf-8')
    s = s.replace('<script src="art-atlas-v4.js">', '<script src="art-atlas-v4.js"></script>')
    p.write_text(s, encoding='utf-8')

# В Android WebView V56 уже даёт JS-fallback. Старый native fallback в
# MainActivity срабатывал параллельно со штатным click() и давал двойные taps.
p = Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java')
s = p.read_text(encoding='utf-8')
s = s.replace('import android.view.MotionEvent;\n', '')
# Удаляем любой установленный native touch listener между его началом и root.addView.
s = re.sub(r'(?s)\n\s*// Не (?:перехватываем|блокируем) штатное касание WebView\..*?\n\s*root\.addView\(web,', '\n\n        root.addView(web,', s, count=1)
s = re.sub(r'(?s)\n\s*web\.setOnTouchListener\(\(v, event\) -> \{.*?\n\s*\}\);\n\n\s*root\.addView\(web,', '\n\n        root.addView(web,', s, count=1)
# Удаляем старый Java fallback, если он есть. Повторный запуск скрипта безопасен.
s = re.sub(r'(?s)\n\s*/\*\*\n\s*\* Резерв для Android WebView:.*?\n\s*private void dispatchTouchFallback\(.*?\n\s*\}\n\n(?=\s*@Override\n\s*public void onBackPressed)', '\n\n', s, count=1)
p.write_text(s, encoding='utf-8')

# В V4 background-position выбирает конкретную ячейку атласа. background-size=cover
# показывал весь атлас/не ту область вместо выбранной картинки.
for p in [Path('NEW_DARK_RPG/art-atlas-v4.js'), Path('android/app/src/main/assets/art-atlas-v4.js')]:
    s = p.read_text(encoding='utf-8')
    s = s.replace("s.style.backgroundSize='cover';s.style.backgroundPosition='center';", "s.style.backgroundSize='400% 600%';")
    s = s.replace("e.style.backgroundSize='cover';e.style.backgroundPosition='center';", "e.style.backgroundSize='400% 600%';")
    p.write_text(s, encoding='utf-8')

ma = Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java').read_text(encoding='utf-8')
if any(x in ma for x in ['dispatchTouchFallback', 'setOnTouchListener', 'MotionEvent']):
    raise SystemExit('MainActivity native duplicate touch fallback still present')
print('V4 runtime + touch duplicate fix: PASS')
