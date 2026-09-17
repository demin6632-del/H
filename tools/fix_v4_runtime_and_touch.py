from pathlib import Path

# V4 runtime: исправляем подключение внешнего скрипта и не меняем игровую логику.
FILES = [Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s = p.read_text(encoding='utf-8')
    s = s.replace('<script src="art-atlas-v4.js">', '<script src="art-atlas-v4.js"></script>')
    p.write_text(s, encoding='utf-8')

# В Android WebView уже есть JS-fallback V56. Дополнительный native fallback
# одновременно с обычным WebView tap создавал повторные click(). Убираем
# только этот дублирующий слой, остальное поведение Activity сохраняем.
p = Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java')
s = p.read_text(encoding='utf-8')
s = s.replace('import android.view.MotionEvent;\n', '')
start = s.find('        // Не перехватываем штатное касание WebView.')
if start >= 0:
    end = s.find('        root.addView(web,', start)
    if end < 0:
        raise SystemExit('MainActivity touch block end not found')
    s = s[:start] + s[end:]
method_start = s.find('    /**\n     * Резерв для Android WebView:')
if method_start >= 0:
    method_end = s.find('    @Override\n    public void onBackPressed()', method_start)
    if method_end < 0:
        raise SystemExit('MainActivity fallback method end not found')
    s = s[:method_start] + s[method_end:]
p.write_text(s, encoding='utf-8')

# В V4 background-position задаёт нужную ячейку атласа. Нельзя заменять
# background-size на cover, иначе показывается весь атлас вместо одной картинки.
for p in [Path('NEW_DARK_RPG/art-atlas-v4.js'), Path('android/app/src/main/assets/art-atlas-v4.js')]:
    s = p.read_text(encoding='utf-8')
    s = s.replace("s.style.backgroundSize='cover';s.style.backgroundPosition='center';", "s.style.backgroundSize='400% 600%';")
    s = s.replace("e.style.backgroundSize='cover';e.style.backgroundPosition='center';", "e.style.backgroundSize='400% 600%';")
    p.write_text(s, encoding='utf-8')

print('V4 runtime + touch duplicate fix: PASS')
