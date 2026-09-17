from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT/'NEW_DARK_RPG/index.html', ROOT/'android/app/src/main/assets/index.html']
JAVA = ROOT/'android/app/src/main/java/com/chronicles/abyss/MainActivity.java'

OLD_MARKERS = [
    'ANDROID-TOUCH-STABLE-V59', 'ANDROID-TOUCH-STABLE-V58', 'ANDROID-TOUCH-STABLE-V57',
    'ANDROID-TOUCH-STABLE-V56', 'ANDROID-TOUCH-STABLE-V55', 'ANDROID-TOUCH-FIX-V54',
    'ANDROID-TOUCH-FIX-V42', 'ANDROID-CLASS-SELECT-FIX-V43', 'TOUCH-BUTTON-FIX-V39'
]

NEW_JS = r'''/* ANDROID-TOUCH-STABLE-V60 — pointer tap + native fallback, scroll safe. */
(function(){
  if(window.__androidTouchStableV60)return;
  window.__androidTouchStableV60=true;
  let activeButton=null,downX=0,downY=0,moved=false,suppressNativeClick=false;
  const MOVE_LIMIT=14;
  const findButton=node=>{
    try{
      const b=node&&node.closest?node.closest('button'):null;
      return b&&!b.disabled?b:null;
    }catch(_){return null;}
  };
  const findButtonAt=(x,y)=>{
    try{
      const nodes=document.elementsFromPoint?document.elementsFromPoint(x,y):[document.elementFromPoint(x,y)];
      for(const n of nodes){const b=findButton(n);if(b)return b;}
    }catch(_){ }
    return null;
  };
  const fire=b=>{
    if(!b||b.disabled)return false;
    try{
      window.__nativeTapConsumed=true;
      suppressNativeClick=true;
      b.click();
      setTimeout(()=>{suppressNativeClick=false;},350);
      return true;
    }catch(_){return false;}
  };
  window.__nativeTapConsumed=false;
  window.__nativeTapFallbackAt=function(x,y){
    if(window.__nativeTapConsumed)return false;
    const b=findButtonAt(Number(x),Number(y));
    return fire(b);
  };
  document.addEventListener('click',function(e){
    if(suppressNativeClick){
      e.preventDefault();
      e.stopImmediatePropagation();
      suppressNativeClick=false;
      return;
    }
    const b=findButton(e.target);
    if(b)window.__nativeTapConsumed=true;
  },{capture:true});
  document.addEventListener('pointerdown',function(e){
    if(e.pointerType==='mouse'&&e.button!==0)return;
    activeButton=findButton(e.target)||findButtonAt(e.clientX,e.clientY);
    downX=e.clientX;downY=e.clientY;moved=false;
    window.__nativeTapConsumed=false;
  },{capture:true,passive:true});
  document.addEventListener('pointermove',function(e){
    if(!activeButton)return;
    if(Math.abs(e.clientX-downX)>MOVE_LIMIT||Math.abs(e.clientY-downY)>MOVE_LIMIT){
      moved=true;activeButton=null;
    }
  },{capture:true,passive:true});
  document.addEventListener('pointerup',function(e){
    if(e.pointerType==='mouse'&&e.button!==0)return;
    const b=activeButton;activeButton=null;
    if(moved)return;
    if(Math.abs(e.clientX-downX)>MOVE_LIMIT||Math.abs(e.clientY-downY)>MOVE_LIMIT)return;
    fire(b||findButtonAt(e.clientX,e.clientY));
  },{capture:true,passive:true});
  document.addEventListener('pointercancel',function(){activeButton=null;moved=true;},{capture:true,passive:true});
  document.addEventListener('touchcancel',function(){activeButton=null;moved=true;},{capture:true,passive:true});
})();
'''

def remove_iife(s, marker):
    while True:
        pos=s.find(marker)
        if pos<0:return s
        start=s.rfind('/*',0,pos)
        end=s.find('})();',pos)
        if start<0 or end<0:raise SystemExit(f'Cannot remove block: {marker}')
        s=s[:start]+s[end+5:]

for p in HTML_FILES:
    s=p.read_text(encoding='utf-8')
    for marker in OLD_MARKERS:
        s=remove_iife(s,marker)
    pos=s.rfind('</script>')
    if pos<0:raise SystemExit(f'{p}: no script terminator')
    s=s[:pos]+'\n'+NEW_JS+s[pos:]
    if s.count('ANDROID-TOUCH-STABLE-V60')!=1:raise SystemExit(f'{p}: V60 insertion failed')
    p.write_text(s,encoding='utf-8')

JAVA_TEXT='''package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.view.MotionEvent;
import android.view.ViewConfiguration;
import android.view.ViewGroup;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.core.splashscreen.SplashScreen;

public class MainActivity extends Activity {
    private boolean webViewReady = false;
    private TouchWebView web;
    private FrameLayout root;

    /* ANDROID-NATIVE-TOUCH-FALLBACK-V60 — штатный WebView + резервный DOM tap. */
    private static final class TouchWebView extends WebView {
        private final Handler handler = new Handler(Looper.getMainLooper());
        private float downX, downY;
        private boolean moved;
        private long downTime;
        private final int touchSlop;
        private Runnable fallback;

        TouchWebView(Activity context) {
            super(context);
            touchSlop = Math.max(24, ViewConfiguration.get(context).getScaledTouchSlop() * 2);
            setClickable(true);
            setFocusable(true);
            setFocusableInTouchMode(true);
        }

        private void cancelFallback() {
            if (fallback != null) {
                handler.removeCallbacks(fallback);
                fallback = null;
            }
        }

        private void scheduleFallback(final float x, final float y) {
            cancelFallback();
            final float density = getResources().getDisplayMetrics().density;
            final float cssX = x / Math.max(1f, density);
            final float cssY = y / Math.max(1f, density);
            fallback = () -> {
                fallback = null;
                String js = "(function(){if(typeof window.__nativeTapFallbackAt==='function'){window.__nativeTapFallbackAt(" + cssX + "," + cssY + ");}})()";
                evaluateJavascript(js, null);
            };
            handler.postDelayed(fallback, 180);
        }

        @Override
        public boolean onTouchEvent(MotionEvent event) {
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    cancelFallback();
                    downX = event.getX();
                    downY = event.getY();
                    downTime = System.currentTimeMillis();
                    moved = false;
                    break;
                case MotionEvent.ACTION_MOVE:
                    if (Math.abs(event.getX() - downX) > touchSlop || Math.abs(event.getY() - downY) > touchSlop) {
                        moved = true;
                        cancelFallback();
                    }
                    break;
                case MotionEvent.ACTION_UP:
                    boolean tap = !moved &&
                            Math.abs(event.getX() - downX) <= touchSlop &&
                            Math.abs(event.getY() - downY) <= touchSlop &&
                            (System.currentTimeMillis() - downTime) <= 1500;
                    boolean result = super.onTouchEvent(event);
                    if (tap) scheduleFallback(event.getX(), event.getY());
                    return result;
                case MotionEvent.ACTION_CANCEL:
                    moved = true;
                    cancelFallback();
                    break;
            }
            return super.onTouchEvent(event);
        }

        @Override
        protected void onDetachedFromWindow() {
            cancelFallback();
            super.onDetachedFromWindow();
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);
        splashScreen.setKeepOnScreenCondition(() -> !webViewReady);
        super.onCreate(savedInstanceState);

        root = new FrameLayout(this);
        web = new TouchWebView(this);
        web.setBackgroundColor(Color.rgb(8, 8, 8));

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);
        settings.setTextZoom(100);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(false);

        web.setWebViewClient(new WebViewClient() {
            @Override public void onPageCommitVisible(WebView view, String url) {
                webViewReady = true;
                super.onPageCommitVisible(view, url);
            }
            @Override public void onPageFinished(WebView view, String url) {
                webViewReady = true;
                super.onPageFinished(view, url);
            }
        });

        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        web.loadUrl("file:///android_asset/index.html");
        setContentView(root);
        web.requestFocus();
    }

    @Override
    public void onBackPressed() {
        if (web != null) {
            web.evaluateJavascript("(function(){if(typeof goBack==='function'){goBack();return 'game';}return 'none';})()", value -> {
                if (value == null || value.contains("none")) {
                    if (web.canGoBack()) web.goBack();
                    else superOnBackPressed();
                }
            });
            return;
        }
        super.onBackPressed();
    }

    @SuppressWarnings("deprecation")
    private void superOnBackPressed() { super.onBackPressed(); }

    @Override
    protected void onDestroy() {
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
'''
JAVA.write_text(JAVA_TEXT,encoding='utf-8')
print('ANDROID TOUCH V60: pointer tap + native fallback, scroll safe')
