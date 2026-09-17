from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / 'NEW_DARK_RPG' / 'index.html', ROOT / 'android' / 'app' / 'src' / 'main' / 'assets' / 'index.html']
JAVA = ROOT / 'android' / 'app' / 'src' / 'main' / 'java' / 'com' / 'chronicles' / 'abyss' / 'MainActivity.java'

OLD_MARKERS = [
    'ANDROID-TOUCH-STABLE-V56', 'ANDROID-TOUCH-STABLE-V57', 'ANDROID-TOUCH-STABLE-V58', 'ANDROID-TOUCH-STABLE-V59',
    'ANDROID-TOUCH-STABLE-V55', 'ANDROID-TOUCH-FIX-V42', 'ANDROID-TOUCH-FIX-V54',
    'ANDROID-CLASS-SELECT-FIX-V43', 'TOUCH-BUTTON-FIX-V39',
]

# V59: Android tap is accepted from touchstart/touchend, while movement cancels it.
# This avoids relying only on WebView's synthesized click timing.
NEW_JS = r'''/* ANDROID-TOUCH-STABLE-V59 — надёжный tap без кликов при прокрутке. */
(function(){
  if(window.__androidTouchStableV59)return;
  window.__androidTouchStableV59=true;
  let touchButton=null,touchX=0,touchY=0,touchMoved=false,touchTimer=null;
  let syntheticClick=false,suppressNativeClick=false;
  const MOVE_LIMIT=14;
  const clearPending=()=>{if(touchTimer){clearTimeout(touchTimer);touchTimer=null;}};
  const findButton=(node)=>{
    if(!node)return null;
    if(node.closest){const b=node.closest('button');if(b&&!b.disabled)return b;}
    return null;
  };
  const findButtonAt=(x,y)=>{
    try{
      const list=document.elementsFromPoint?document.elementsFromPoint(x,y):[document.elementFromPoint(x,y)];
      for(const node of list){const b=findButton(node);if(b)return b;}
    }catch(_){ }
    return null;
  };
  const fire=(b)=>{
    if(!b||b.disabled)return;
    try{
      syntheticClick=true;
      b.click();
      syntheticClick=false;
      suppressNativeClick=true;
      setTimeout(function(){suppressNativeClick=false;},350);
    }catch(_){syntheticClick=false;}
  };
  document.addEventListener('click',function(e){
    if(syntheticClick)return;
    if(suppressNativeClick){
      suppressNativeClick=false;
      e.preventDefault();
      e.stopImmediatePropagation();
    }
  },{capture:true});
  document.addEventListener('touchstart',function(e){
    clearPending();
    const t=e.touches&&e.touches[0];
    touchButton=findButton(e.target)|| (t?findButtonAt(t.clientX,t.clientY):null);
    touchMoved=false;
    if(t){touchX=t.clientX;touchY=t.clientY;}
    if(touchButton){
      touchTimer=setTimeout(function(){
        touchTimer=null;
        if(!touchMoved){const b=touchButton;touchButton=null;fire(b);}
      },160);
    }
  },{capture:true,passive:true});
  document.addEventListener('touchmove',function(e){
    const t=e.touches&&e.touches[0];
    if(!t)return;
    if(Math.abs(t.clientX-touchX)>MOVE_LIMIT || Math.abs(t.clientY-touchY)>MOVE_LIMIT){
      touchMoved=true;
      touchButton=null;
      clearPending();
    }
  },{capture:true,passive:true});
  document.addEventListener('touchend',function(e){
    clearPending();
    let b=touchButton;
    touchButton=null;
    const t=e.changedTouches&&e.changedTouches[0];
    if(!t||touchMoved)return;
    if(Math.abs(t.clientX-touchX)>MOVE_LIMIT || Math.abs(t.clientY-touchY)>MOVE_LIMIT)return;
    if(!b)b=findButtonAt(t.clientX,t.clientY);
    fire(b);
  },{capture:true,passive:true});
  document.addEventListener('touchcancel',function(){touchButton=null;touchMoved=true;clearPending();},{capture:true,passive:true});
  if(typeof selectAbyssDepth==='function' && !window.selectAbyssDepth){
    window.selectAbyssDepth=function(){return selectAbyssDepth.apply(this,arguments);};
  }
  if(typeof openAbyssKeyCache==='function' && !window.openAbyssKeyCache){
    window.openAbyssKeyCache=function(){return openAbyssKeyCache.apply(this,arguments);};
  }
})();
'''

def remove_iife(s, marker):
    start = s.find(marker)
    while start >= 0:
        comment = s.rfind('/*', 0, start)
        end = s.find('})();', start)
        if comment < 0 or end < 0:
            raise SystemExit(f'Cannot remove block: {marker}')
        s = s[:comment] + s[end + len('})();'):]
        start = s.find(marker)
    return s

def patch_html(path):
    s = path.read_text(encoding='utf-8')
    for marker in OLD_MARKERS:
        s = remove_iife(s, marker)
    pos = s.rfind('</script>')
    if pos < 0:
        raise SystemExit(f'{path}: no script terminator')
    s = s[:pos] + '\n' + NEW_JS + s[pos:]
    if s.count('ANDROID-TOUCH-STABLE-V59') != 1:
        raise SystemExit(f'{path}: V59 insertion failed')
    for bad in OLD_MARKERS:
        if bad in s:
            raise SystemExit(f'{path}: obsolete marker remains: {bad}')
    path.write_text(s, encoding='utf-8')

for p in FILES:
    patch_html(p)

# Java не перехватывает touch-события: WebView получает штатную обработку.
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

print('ANDROID TOUCH V59: TOUCHSTART + TOUCHEND TAP, SCROLL SAFE: PASS')
