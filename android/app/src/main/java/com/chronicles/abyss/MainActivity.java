package com.chronicles.abyss;

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

    /* ANDROID-NATIVE-TOUCH-FALLBACK-V62 — резервный DOM tap подключён к реальному JS bridge. */
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
                String js = "(function(){if(typeof window.__nativeTapFallbackAt==='function'){" +
                        "window.__nativeTapFallbackAt(" + cssX + "," + cssY + ");}})()";
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
                    if (Math.abs(event.getX() - downX) > touchSlop ||
                            Math.abs(event.getY() - downY) > touchSlop) {
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

    private void installNativeTapBridge() {
        String js =
                "(function(){" +
                "if(window.__nativeTapBridgeV61)return;" +
                "window.__nativeTapBridgeV61=1;" +
                "window.__nativeTapLastClick=0;" +
                "document.addEventListener('click',function(e){" +
                "var r=e.target&&e.target.getBoundingClientRect?e.target.getBoundingClientRect():null;" +
                "window.__nativeTapLastClick={t:Date.now(),x:e.clientX,y:e.clientY,r:r};" +
                "},true);" +
                "window.__nativeTapFallbackAt=function(x,y){" +
                "try{" +
                "var now=Date.now(),last=window.__nativeTapLastClick;" +
                "if(last&&now-last.t<350&&Math.abs(last.x-x)<28&&Math.abs(last.y-y)<28)return;" +
                "var el=document.elementFromPoint(x,y);" +
                "if(!el)return;" +
                "var startup=el.closest?el.closest('#continueHit,.start-hit'):null;" +
                "if(startup&&typeof window.__nativeStartupTap==='function'){" +
                "var isContinue=startup.id==='continueHit',isStart=startup.classList&&startup.classList.contains('start-hit');" +
                "if(isContinue||isStart){window.__nativeStartupTap(isContinue?'continue':'start');return;}}" +
                "var target=el.closest?el.closest('button,a,input,select,textarea,[role=button],[onclick]'):el;" +
                "if(!target)return;" +
                "target.focus&&target.focus();" +
                "target.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true,clientX:x,clientY:y,view:window}));" +
                "target.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,cancelable:true,clientX:x,clientY:y,view:window}));" +
                "target.click&&target.click();" +
                "}catch(e){}};" +
                "})();";
        web.evaluateJavascript(js, null);
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
                installNativeTapBridge();
                super.onPageCommitVisible(view, url);
            }
            @Override public void onPageFinished(WebView view, String url) {
                webViewReady = true;
                installNativeTapBridge();
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
