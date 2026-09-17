from pathlib import Path

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
start = s.find('\n        // Не перехватываем штатное касание WebView.')
if start < 0:
    start = s.find('\n        // Не блокируем штатное касание WebView.')
if start >= 0:
    end = s.find('\n        root.addView(web,', start)
    if end < 0:
        raise SystemExit('MainActivity root.addView marker not found')
    s = s[:start] + s[end:]
else:
    # Безопасный повторный запуск: если комментария уже нет, удаляем listener по сигнатуре.
    start = s.find('\n        web.setOnTouchListener(')
    if start >= 0:
        end = s.find('\n        root.addView(web,', start)
        if end < 0:
            raise SystemExit('MainActivity root.addView marker not found')
        s = s[:start] + s[end:]
method_start = s.find('\n    /**\n     * Резерв для Android WebView:')
if method_start >= 0:
    method_end = s.find('\n    @Override\n    public void onBackPressed()', method_start)
    if method_end < 0:
        raise SystemExit('MainActivity onBackPressed marker not found')
    s = s[:method_start] + s[method_end:]
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
