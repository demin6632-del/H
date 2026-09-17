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
    const xx=Number(x)||0,yy=Number(y)||0;
    const e=document.elementFromPoint(xx,yy);
    let b=getButton(e);
    if(!b){
      const cs=document.querySelectorAll('#classes .class-card');
      for(let i=0;i<cs.length;i++){
        const r=cs[i].getBoundingClientRect();
        if(xx>=r.left&&xx<=r.right&&yy>=r.top&&yy<=r.bottom){b=cs[i];break;}
      }
    }
    if(!b){
      const bs=document.querySelectorAll('button');
      for(let i=0;i<bs.length;i++){
        const r=bs[i].getBoundingClientRect();
        if(xx>=r.left&&xx<=r.right&&yy>=r.top&&yy<=r.bottom){b=bs[i];break;}
      }
    }
    if(!b||b.disabled)return false;
    cancel(b);b.click();lastNative.set(b,Date.now());return true;
  };
  // Явно экспортируем обработчики, которые вызываются inline-атрибутами.
  if(typeof selectAbyssDepth==='function'){
    window.selectAbyssDepth=function(){return selectAbyssDepth.apply(this,arguments);};
  }
  if(typeof openAbyssKeyCache==='function'){
    window.openAbyssKeyCache=function(){return openAbyssKeyCache.apply(this,arguments);};
  }
})();
'''


def remove_old_touch_blocks(s: str) -> str:
    # Удаляем именно целые IIFE-блоки старых touch-патчей. Это намеренно
    # делается до вставки V56, чтобы в APK не оставалось конкурирующих fallback.
    for marker in OLD_MARKERS[1:]:
        pattern = re.compile(r'(?s)/\*[^*]*' + re.escape(marker) + r'.*?\*/\s*\(function\(\)\{.*?\}\)\(\);')
        s, n = pattern.subn('', s)
        if n == 0 and marker in s:
            raise SystemExit(f'Cannot remove old touch block: {marker}')
    return s


def patch_html(path: Path):
    s = path.read_text(encoding='utf-8')
    # Сначала удаляем любой уже установленный V56/V55 и все старые touch-IIFE.
    s = remove_old_touch_blocks(s)
    marker_comment = '/* ANDROID-TOUCH-STABLE-V56'
    while marker_comment in s:
        start = s.rfind('/*', 0, s.find(marker_comment))
        end = s.find('})();', s.find(marker_comment))
        if start < 0 or end < 0:
            raise SystemExit('Cannot remove previous V56 block')
        s = s[:start] + s[end + len('})();'):]
    pos = s.rfind('</script>')
    if pos < 0:
        raise SystemExit(f'{path}: no script terminator')
    s = s[:pos] + '\n' + NEW_JS + s[pos:]
    leftovers = [m for m in OLD_MARKERS[1:] if m in s]
    if leftovers:
        raise SystemExit(f'{path}: obsolete touch markers remain: {leftovers}')
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
    replacement = '''        // Не перехватываем штатное касание WebView. На ACTION_UP лишь ставим
        // отложенный JS-fallback, чтобы дать WebView закончить собственный tap/click.
        web.setOnTouchListener((v, event) -> {
            if (webViewReady && event.getAction() == MotionEvent.ACTION_UP) {
                final float px = event.getX();
                final float py = event.getY();
                web.postDelayed(() -> dispatchTouchFallback(px, py), 90);
            }
            return false;
        });

'''
    s = s[:start] + replacement + s[end:]

    mstart = s.find('    /**\n     * Резерв для Android WebView:')
    mend = s.find('\n    @Override\n    public void onBackPressed()', mstart)
    if mstart < 0 or mend < 0:
        raise SystemExit('MainActivity fallback method not found')
    method = '''    /**
     * Резерв для Android WebView: самостоятельно определяет HTML-кнопку
     * под фактическим пальцем и запускает её click().
     * Сначала используется hit-test WebView, затем проверка геометрии DOM.
     * Это закрывает случай, когда WebView возвращает не тот элемент из-за
     * масштабирования или вложенного текста внутри карточки класса.
     */
    private void dispatchTouchFallback(float px, float py) {
        if (web == null || web.getWidth() <= 0 || web.getHeight() <= 0) return;
        final float scale = Math.max(0.0001f, web.getScale());
        final float cssX = Math.max(0f, px / scale);
        final float cssY = Math.max(0f, py / scale);
        final String js = "(function(){"
                + "var now=Date.now();"
                + "if(window.__lastNativeButtonAt && now-window.__lastNativeButtonAt<350)return true;"
                + "var e=document.elementFromPoint(" + cssX + "," + cssY + ");"
                + "var b=e&&e.closest?e.closest('button'):null;"
                + "if(!b){"
                + "var cs=document.querySelectorAll('#classes .class-card');"
                + "for(var i=0;i<cs.length;i++){var r=cs[i].getBoundingClientRect();if(" + cssX + ">=r.left&&" + cssX + "<=r.right&&" + cssY + ">=r.top&&" + cssY + "<=r.bottom){b=cs[i];break;}}"
                + "}"
                + "if(!b){"
                + "var bs=document.querySelectorAll('button');"
                + "for(var j=0;j<bs.length;j++){var q=bs[j].getBoundingClientRect();if(" + cssX + ">=q.left&&" + cssX + "<=q.right&&" + cssY + ">=q.top&&" + cssY + "<=q.bottom){b=bs[j];break;}}"
                + "}"
                + "if(!b||b.disabled)return false;"
                + "window.__lastNativeButtonAt=now;"
                + "try{b.click();return true;}catch(err){console.error('ANDROID_TOUCH_FALLBACK',err);return false;}"
                + "})()";
        web.evaluateJavascript(js, value -> { });
    }
'''
    s = s[:mstart] + method + s[mend:]
    JAVA.write_text(s, encoding='utf-8')

for p in (WEB, ANDROID):
    patch_html(p)
patch_java()
print('ANDROID TOUCH V56 PATCH: PASS')
