from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'NEW_DARK_RPG' / 'index.html'
ANDROID = ROOT / 'android' / 'app' / 'src' / 'main' / 'assets' / 'index.html'
JAVA = ROOT / 'android' / 'app' / 'src' / 'main' / 'java' / 'com' / 'chronicles' / 'abyss' / 'MainActivity.java'

OLD_MARKERS = [
    'ANDROID-TOUCH-STABLE-V56',
    'ANDROID-TOUCH-STABLE-V55',
    'ANDROID-TOUCH-FIX-V42',
    'ANDROID-TOUCH-FIX-V54',
    'ANDROID-CLASS-SELECT-FIX-V43',
    'TOUCH-BUTTON-FIX-V39',
]

NEW_JS = r'''/* ANDROID-TOUCH-STABLE-V56 — прямой и не блокирующий fallback касания Android/WebView. */
(function(){
  if(window.__androidTouchStableV56)return;
  window.__androidTouchStableV56=true;
  const lastNative=new WeakMap();
  const pending=new WeakMap();
  const WINDOW_MS=500;
  const DELAY=90;
  const getButton=t=>t&&t.closest?t.closest('button'):null;
  const cancel=b=>{const id=pending.get(b);if(id){clearTimeout(id);pending.delete(b)}};
  document.addEventListener('click',e=>{
    const b=getButton(e.target);if(!b)return;
    cancel(b);lastNative.set(b,Date.now());
  },true);
  function fallback(b){
    if(!b||b.disabled||!document.documentElement.contains(b))return;
    if(Date.now()-(lastNative.get(b)||0)<WINDOW_MS)return;
    b.click();
  }
  function arm(e){
    const b=getButton(e.target);if(!b||b.disabled)return;
    cancel(b);
    pending.set(b,setTimeout(()=>{pending.delete(b);fallback(b)},DELAY));
  }
  function cancelTarget(e){const b=getButton(e.target);if(b)cancel(b)}
  document.addEventListener('pointerup',arm,{passive:true,capture:false});
  document.addEventListener('touchend',arm,{passive:true,capture:false});
  document.addEventListener('pointercancel',cancelTarget,{passive:true,capture:false});
  document.addEventListener('touchcancel',cancelTarget,{passive:true,capture:false});
  window.__nativeButtonAt=function(x,y){
    const e=document.elementFromPoint(Number(x)||0,Number(y)||0);
    const b=getButton(e);
    if(!b||b.disabled)return false;
    cancel(b);b.click();lastNative.set(b,Date.now());return true;
  };
})();
'''


def remove_touch_blocks(s: str) -> str:
    for marker in OLD_MARKERS:
        while marker in s:
            marker_pos = s.find(marker)
            start = s.rfind('/*', 0, marker_pos)
            if start < 0: start = marker_pos
            end_marker = s.find('})();', marker_pos)
            if end_marker < 0:
                raise SystemExit(f'Cannot remove block {marker}: terminator not found')
            s = s[:start] + s[end_marker + len('})();'):]
    return s


def patch_html(path: Path):
    s = path.read_text(encoding='utf-8')
    s = remove_touch_blocks(s)
    marker = '</script>'
    pos = s.rfind(marker)
    if pos < 0: raise SystemExit(f'{path}: no script terminator')
    s = s[:pos] + '\n' + NEW_JS + s[pos:]
    if s.count('ANDROID-TOUCH-STABLE-V56') != 1:
        raise SystemExit(f'{path}: V56 insertion failed')
    path.write_text(s, encoding='utf-8')


def patch_java():
    s = JAVA.read_text(encoding='utf-8')
    start = -1
    for token in [
        '        // Не перехватываем штатное касание WebView.',
        '        // Не блокируем штатное касание WebView.',
    ]:
        start = s.find(token)
        if start >= 0: break
    end = s.find('        root.addView(web, new FrameLayout.LayoutParams(', start)
    if start < 0 or end < 0:
        raise SystemExit('MainActivity touch section not found')
    replacement = '''        // Не перехватываем штатное касание WebView. На ACTION_UP лишь ставим\n        // отложенный JS-fallback, чтобы дать WebView закончить собственный tap/click.\n        web.setOnTouchListener((v, event) -> {\n            if (webViewReady && event.getAction() == MotionEvent.ACTION_UP) {\n                final float px = event.getX();\n                final float py = event.getY();\n                web.postDelayed(() -> dispatchTouchFallback(px, py), 90);\n            }\n            return false;\n        });\n\n'''
    s = s[:start] + replacement + s[end:]

    mstart = s.find('    /**\n     * Резерв для Android WebView:')
    mend = s.find('\n    @Override\n    public void onBackPressed()', mstart)
    if mstart < 0 or mend < 0:
        raise SystemExit('MainActivity fallback method not found')
    method = '''    /**\n     * Резерв для Android WebView: вызывает DOM-кнопку под фактическим пальцем.\n     * Координаты переводятся из координат WebView в CSS-пиксели.\n     */\n    private void dispatchTouchFallback(float px, float py) {\n        if (web == null || web.getWidth() <= 0 || web.getHeight() <= 0) return;\n        final float scale = Math.max(0.0001f, web.getScale());\n        final float cssX = Math.max(0f, px / scale);\n        final float cssY = Math.max(0f, py / scale);\n        final String js = "(function(){"\n                + "if(typeof window.__nativeButtonAt!=='function')return false;"\n                + "return window.__nativeButtonAt(" + cssX + "," + cssY + ");"\n                + "})()";\n        web.evaluateJavascript(js, value -> { });\n    }\n'''
    s = s[:mstart] + method + s[mend:]
    JAVA.write_text(s, encoding='utf-8')

for p in (WEB, ANDROID):
    patch_html(p)
patch_java()
print('ANDROID TOUCH V56 PATCH: PASS')
