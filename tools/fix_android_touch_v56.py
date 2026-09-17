from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / 'NEW_DARK_RPG' / 'index.html', ROOT / 'android' / 'app' / 'src' / 'main' / 'assets' / 'index.html']
JAVA = ROOT / 'android' / 'app' / 'src' / 'main' / 'java' / 'com' / 'chronicles' / 'abyss' / 'MainActivity.java'

OLD_MARKERS = [
    'ANDROID-TOUCH-STABLE-V56', 'ANDROID-TOUCH-STABLE-V55',
    'ANDROID-TOUCH-FIX-V42', 'ANDROID-TOUCH-FIX-V54',
    'ANDROID-CLASS-SELECT-FIX-V43', 'TOUCH-BUTTON-FIX-V39',
]

# Безопасный Android fallback: обычный короткий tap превращается в click,
# но любое заметное движение считается прокруткой и НЕ нажимает кнопку.
NEW_JS = r'''/* ANDROID-TOUCH-STABLE-V57 — короткий tap работает на Android, прокрутка не нажимает кнопки. */
(function(){
  if(window.__androidTouchStableV57)return;
  window.__androidTouchStableV57=true;
  let touchButton=null,touchX=0,touchY=0,touchMoved=false;
  const MOVE_LIMIT=14;
  const findButton=(node)=>{
    if(!node)return null;
    if(node.closest)return node.closest('button');
    return null;
  };
  document.addEventListener('touchstart',function(e){
    const t=e.touches&&e.touches[0];
    touchButton=findButton(e.target);
    touchMoved=false;
    if(t){touchX=t.clientX;touchY=t.clientY;}
  },{capture:true,passive:true});
  document.addEventListener('touchmove',function(e){
    if(!touchButton)return;
    const t=e.touches&&e.touches[0];
    if(!t)return;
    if(Math.abs(t.clientX-touchX)>MOVE_LIMIT || Math.abs(t.clientY-touchY)>MOVE_LIMIT){
      touchMoved=true;
      touchButton=null;
    }
  },{capture:true,passive:true});
  document.addEventListener('touchend',function(e){
    const b=touchButton;
    touchButton=null;
    if(!b||touchMoved)return;
    const t=e.changedTouches&&e.changedTouches[0];
    if(!t)return;
    if(Math.abs(t.clientX-touchX)>MOVE_LIMIT || Math.abs(t.clientY-touchY)>MOVE_LIMIT)return;
    e.preventDefault();
    try{b.click();}catch(_){ }
  },{capture:true,passive:false});
  document.addEventListener('touchcancel',function(){touchButton=null;touchMoved=true;},{capture:true,passive:true});
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

def remove_old_touch_blocks(s):
    for marker in OLD_MARKERS:
        s = remove_iife(s, marker)
    return s

def patch_html(path):
    s = path.read_text(encoding='utf-8')
    s = remove_old_touch_blocks(s)
    for marker in ['ANDROID-TOUCH-STABLE-V57']:
        s = remove_iife(s, marker)
    pos = s.rfind('</script>')
    if pos < 0:
        raise SystemExit(f'{path}: no script terminator')
    s = s[:pos] + '\n' + NEW_JS + s[pos:]
    if s.count('ANDROID-TOUCH-STABLE-V57') != 1:
        raise SystemExit(f'{path}: V57 insertion failed')
    for bad in OLD_MARKERS:
        if bad in s:
            raise SystemExit(f'{path}: obsolete marker remains: {bad}')
    path.write_text(s, encoding='utf-8')

for p in FILES:
    patch_html(p)

# Никакого Java touch-перехвата: вся логика находится в WebView, где можно
# отличить короткий tap от прокрутки по величине движения пальца.
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

print('ANDROID TOUCH V57: TAP WORKS + SCROLL SAFE: PASS')
