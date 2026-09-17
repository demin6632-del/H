package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.view.MotionEvent;
import android.view.ViewGroup;
import android.webkit.JavascriptInterface;
import android.widget.FrameLayout;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.core.splashscreen.SplashScreen;

public class MainActivity extends Activity {
    private volatile boolean webViewReady = false;
    private WebView web;
    private FrameLayout root;
    private boolean classTouchHandled = false;
    private volatile boolean classScreenVisible = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);
        splashScreen.setKeepOnScreenCondition(() -> !webViewReady);
        super.onCreate(savedInstanceState);

        root = new FrameLayout(this);
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(8, 8, 8));

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);

        // V52: реально подключаем мост, который V51 ожидал в JavaScript.
        web.addJavascriptInterface(new AndroidTouchBridge(), "AndroidTouchBridge");

        web.setWebViewClient(new WebViewClient() {
            @Override public void onPageCommitVisible(WebView view, String url) {
                webViewReady = true;
                super.onPageCommitVisible(view, url);
            }
            @Override public void onPageFinished(WebView view, String url) {
                webViewReady = true;
                installNativeTouchBridge();
                super.onPageFinished(view, url);
            }
        });

        // V51/V52: экран выбора класса — SPA-экран и не меняет URL.
        web.setOnTouchListener((v, event) -> {
            if (!webViewReady) return false;

            if (event.getAction() == MotionEvent.ACTION_DOWN) {
                classTouchHandled = false;
                if (classScreenVisible) {
                    classTouchHandled = true;
                    return true;
                }
                return false;
            }

            if (classScreenVisible && classTouchHandled) {
                if (event.getAction() == MotionEvent.ACTION_UP) {
                    dispatchNativeClassTouch(event.getX(), event.getY());
                    classTouchHandled = false;
                } else if (event.getAction() == MotionEvent.ACTION_CANCEL) {
                    classTouchHandled = false;
                }
                return true;
            }
            return false;
        });

        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        web.loadUrl("file:///android_asset/index.html");
        setContentView(root);
    }

    /**
     * V51/V52: узнаём фактическое состояние DOM-экрана #classes.
     * URL для setScreen('classes') не меняется.
     */
    private void installNativeTouchBridge() {
        if (web == null) return;
        web.evaluateJavascript(
                "(function(){if(window.__nativeTouchBridgeV52)return 'EXISTS';" +
                "window.__nativeTouchBridgeV52=true;" +
                "window.__nativeTouchBridgeTimerV52=setInterval(function(){" +
                "var s=document.getElementById('classes');" +
                "var visible=!!s&&!s.classList.contains('hidden')&&getComputedStyle(s).display!=='none';" +
                "if(window.AndroidTouchBridge&&window.AndroidTouchBridge.setClassScreenVisible)" +
                "window.AndroidTouchBridge.setClassScreenVisible(visible);" +
                "},100);return 'READY';})()", value -> { });
    }

    /**
     * Координаты MotionEvent переводятся в CSS-координаты WebView через долю фактического размера.
     * Затем DOM сам проверяет реальные границы карточек классов.
     */
    private void dispatchNativeClassTouch(float px, float py) {
        if (web == null) return;
        final float vw = Math.max(1f, web.getWidth());
        final float vh = Math.max(1f, web.getHeight());
        final float nx = Math.max(0f, Math.min(1f, px / vw));
        final float ny = Math.max(0f, Math.min(1f, py / vh));

        final String js = "(function(){"
                + "var s=document.getElementById('classes');"
                + "if(!s||s.classList.contains('hidden'))return 'HIDE';"
                + "var x=" + nx + ",y=" + ny + ";"
                + "var a=document.querySelectorAll('#classes .class-card');"
                + "var cx=x*window.innerWidth,cy=y*window.innerHeight;"
                + "for(var i=0;i<a.length;i++){var r=a[i].getBoundingClientRect();"
                + "if(cx>=r.left&&cx<=r.right&&cy>=r.top&&cy<=r.bottom){"
                + "var o=a[i].getAttribute('onclick')||'';"
                + "var m=o.match(/start\\(['\"]([^'\"]+)['\"]\\)/);"
                + "if(!m||typeof window.start!=='function')return 'BAD';"
                + "if(window.__nativeClassSelectionLockV52)return 'LOCK';"
                + "window.__nativeClassSelectionLockV52=true;"
                + "window.start(m[1]);"
                + "setTimeout(function(){window.__nativeClassSelectionLockV52=false;},1000);"
                + "return 'OK:'+m[1];}}"
                + "return 'NONE';})()";
        web.evaluateJavascript(js, value -> { });
    }

    private final class AndroidTouchBridge {
        @JavascriptInterface
        public void setClassScreenVisible(boolean visible) {
            classScreenVisible = visible;
        }
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
