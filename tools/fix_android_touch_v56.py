from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / 'NEW_DARK_RPG' / 'index.html', ROOT / 'android' / 'app' / 'src' / 'main' / 'assets' / 'index.html']
JAVA = ROOT / 'android' / 'app' / 'src' / 'main' / 'java' / 'com' / 'chronicles' / 'abyss' / 'MainActivity.java'

OLD_MARKERS = [
    'ANDROID-TOUCH-STABLE-V56', 'ANDROID-TOUCH-STABLE-V55',
    'ANDROID-TOUCH-FIX-V42', 'ANDROID-TOUCH-FIX-V54',
    'ANDROID-CLASS-SELECT-FIX-V43', 'TOUCH-BUTTON-FIX-V39',
]

# ВАЖНО: никаких pointerup/touchend -> click. Такой отложенный fallback
# ошибочно превращает окончание прокрутки страницы в нажатие кнопки.
NEW_JS = r'''/* ANDROID-TOUCH-STABLE-V56 — только защита от повторных действий; штатный WebView tap не перехватывается. */
(function(){
  if(window.__androidTouchStableV56)return;
  window.__androidTouchStableV56=true;
  const lastClick=new WeakMap();
  document.addEventListener('click',function(e){
    const b=e.target&&e.target.closest?e.target.closest('button'):null;
    if(b) lastClick.set(b,Date.now());
  },true);
  // Никаких обработчиков pointerup/touchend и никакого программного b.click().
  // Прокрутка должна оставаться полностью нативной для WebView.
  if(typeof selectAbyssDepth==='function' && !window.selectAbyssDepth){
    window.selectAbyssDepth=function(){return selectAbyssDepth.apply(this,arguments);};
  }
  if(typeof openAbyssKeyCache==='function' && !window.openAbyssKeyCache){
    window.openAbyssKeyCache=function(){return openAbyssKeyCache.apply(this,arguments);};
  }
})();
'''

def remove_iife(s, marker):
    # Удаляем IIFE, начинающийся с комментария marker.
    start = s.find(marker)
    while start >= 0:
        comment = s.rfind('/*', 0, start)
        end = s.find('})();', start)
        if comment < 0 or end < 0:
            raise SystemExit(f'Cannot remove block: {marker}')
        s = s[:comment] + s[end + len('})();'):]
        start = s.find(marker)
    return s

def remove_old_touch_blocks(s):
    for marker in OLD_MARKERS:
        s = remove_iife(s, marker)
    return s

def patch_html(path):
    s = path.read_text(encoding='utf-8')
    s = remove_old_touch_blocks(s)
    pos = s.rfind('</script>')
    if pos < 0:
        raise SystemExit(f'{path}: no script terminator')
    s = s[:pos] + '\n' + NEW_JS + s[pos:]
    if s.count('ANDROID-TOUCH-STABLE-V56') != 1:
        raise SystemExit(f'{path}: V56 insertion failed')
    for bad in OLD_MARKERS[1:]:
        if bad in s:
            raise SystemExit(f'{path}: obsolete marker remains: {bad}')
    path.write_text(s, encoding='utf-8')

for p in FILES:
    patch_html(p)

# На случай, если предыдущие патчи успели добавить native fallback, удаляем его.
s = JAVA.read_text(encoding='utf-8')
s = s.replace('import android.view.MotionEvent;\n', '')
for token in ['\n        // Не перехватываем штатное касание WebView.', '\n        // Не блокируем штатное касание WebView.']:
    start = s.find(token)
    if start >= 0:
        end = s.find('\n        root.addView(web,', start)
        if end < 0: raise SystemExit('MainActivity root.addView marker not found')
        s = s[:start] + s[end:]
        break
start = s.find('\n    /**\n     * Резерв для Android WebView:')
if start >= 0:
    end = s.find('\n    @Override\n    public void onBackPressed()', start)
    if end < 0: raise SystemExit('MainActivity onBackPressed marker not found')
    s = s[:start] + s[end:]
JAVA.write_text(s, encoding='utf-8')

print('ANDROID TOUCH V56 SCROLL-SAFE: PASS')
