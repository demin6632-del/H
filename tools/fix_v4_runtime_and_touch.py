from pathlib import Path

# Финальный runtime-патч V4 и Android touch.
FILES = [Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]

# Исправляем закрытие внешнего V4 script, если предыдущие патчи оставили его открытым.
for p in FILES:
    s = p.read_text(encoding='utf-8')
    s = s.replace('<script src="art-atlas-v4.js">', '<script src="art-atlas-v4.js"></script><script>')
    p.write_text(s, encoding='utf-8')

# Удаляем native touch fallback из Android. Штатный WebView должен получать
# одно обычное касание; программный click после ACTION_UP ломает прокрутку.
p = Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java')
s = p.read_text(encoding='utf-8')
s = s.replace('import android.view.MotionEvent;\n', '')
for token in ['\n        // Не перехватываем штатное касание WebView.', '\n        // Не блокируем штатное касание WebView.']:
    start = s.find(token)
    if start >= 0:
        end = s.find('\n        root.addView(web,', start)
        if end < 0:
            raise SystemExit('MainActivity root.addView marker not found')
        s = s[:start] + s[end:]
        break
method_start = s.find('\n    /**\n     * Резерв для Android WebView:')
if method_start >= 0:
    method_end = s.find('\n    @Override\n    public void onBackPressed()', method_start)
    if method_end < 0:
        raise SystemExit('MainActivity onBackPressed marker not found')
    s = s[:method_start] + s[method_end:]
p.write_text(s, encoding='utf-8')

# V4 tile fix: исходный CSS содержит .scene{background-size:cover!important;
# background-position:center!important}, поэтому обычный inline style проигрывал
# !important и показывал весь атлас/не ту картинку. Используем setProperty(...,important)
# и отключаем старые чёрные псевдо-слои поверх новой иллюстрации.
for p in [Path('NEW_DARK_RPG/art-atlas-v4.js'), Path('android/app/src/main/assets/art-atlas-v4.js')]:
    s = p.read_text(encoding='utf-8')
    old = "function setScene(id,key){const s=document.querySelector('#'+id+' .scene');if(!s)return;s.style.cssText+=v4Tile(key);s.style.backgroundSize='400% 600%';}"
    new = """function setScene(id,key){
const s=document.querySelector('#'+id+' .scene');if(!s)return;
const i=idx[key];if(i==null)return;
s.classList.add('art-v4-scene');
s.style.setProperty('background-image','url(\\\"'+SHEET+'\\\")','important');
s.style.setProperty('background-size','400% 600%','important');
s.style.setProperty('background-position',((i%4)*100/3)+'% '+(Math.floor(i/4)*100/5)+'%','important');
s.style.setProperty('background-repeat','no-repeat','important');
}"""
    if old in s:
        s = s.replace(old, new)
    elif 'function setScene(id,key)' not in s:
        raise SystemExit(f'{p}: setScene missing')

    # CSS for old pseudo overlays is inserted exactly once.
    if 'art-v4-scene:before' not in s:
        marker = "const names=['shadow'"
        style = "const V4_STYLE=document.createElement('style');V4_STYLE.textContent='.scene.art-v4-scene:before,.scene.art-v4-scene:after{display:none!important}.scene.art-v4-scene{background-repeat:no-repeat!important;}';document.head.appendChild(V4_STYLE);"
        if marker not in s:
            raise SystemExit(f'{p}: atlas name table missing')
        s = s.replace(marker, style + marker, 1)

    # Battle creature tiles use the same exact 4x6 crop.
    s = s.replace("e.style.backgroundSize='400% 600%';", "e.style.setProperty('background-size','400% 600%','important');e.style.setProperty('background-position',((idx[k]%4)*100/3)+'% '+(Math.floor(idx[k]/4)*100/5)+'%','important');")
    p.write_text(s, encoding='utf-8')

# Final static guarantees.
ma = Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java').read_text(encoding='utf-8')
if any(x in ma for x in ['dispatchTouchFallback', 'setOnTouchListener', 'MotionEvent']):
    raise SystemExit('MainActivity native duplicate touch fallback still present')
for p in [Path('NEW_DARK_RPG/art-atlas-v4.js'), Path('android/app/src/main/assets/art-atlas-v4.js')]:
    s = p.read_text(encoding='utf-8')
    if 'setProperty(\'background-size\',\'400% 600%\',\'important\')' not in s:
        raise SystemExit(f'{p}: V4 important tile sizing missing')
    if 'art-v4-scene:before' not in s:
        raise SystemExit(f'{p}: V4 legacy overlay suppression missing')

print('V4 EXACT TILE + SCROLL-SAFE TOUCH: PASS')
