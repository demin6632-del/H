package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.view.MotionEvent;
import android.view.ViewGroup;
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

        // V50: никаких прозрачных Android View поверх HTML.
        // Касание перехватывается непосредственно WebView только на экране выбора класса.
        web.setOnTouchListener((v, event) -> {
            if (!webViewReady) return false;
            String url = web.getUrl();
            boolean classScreen = url != null && url.contains("#classes");
            if (!classScreen) {
                classTouchHandled = false;
                return false;
            }

            // На экране выбора класса WebView не получает обычный touch/click.
            // Нативный обработчик проверяет точку пальца через реальные DOM-границы карточек.
            if (event.getAction() == MotionEvent.ACTION_DOWN
                    || event.getAction() == MotionEvent.ACTION_UP) {
                classTouchHandled = true;
                dispatchNativeClassTouch(event.getX(), event.getY());
                return true;
            }
            if (classTouchHandled) {
                if (event.getAction() == MotionEvent.ACTION_CANCEL) classTouchHandled = false;
                return true;
            }
            return true;
        });

        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        web.loadUrl("file:///android_asset/index.html");
        setContentView(root);
    }

    /**
     * V50: координаты MotionEvent нормализуются относительно фактического размера WebView.
     * JS сравнивает точку с getBoundingClientRect() всех карточек и вызывает существующий start().
     * Это не зависит от плотности экрана, status bar или фиксированных процентов Activity.
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
                + "for(var i=0;i<a.length;i++){var r=a[i].getBoundingClientRect();"
                + "if(x*window.innerWidth>=r.left&&x*window.innerWidth<=r.right&&y*window.innerHeight>=r.top&&y*window.innerHeight<=r.bottom){"
                + "var o=a[i].getAttribute('onclick')||'';"
                + "var m=o.match(/start\\(['\"]([^'\"]+)['\"]\\)/);"
                + "if(!m||typeof window.start!=='function')return 'BAD';"
                + "if(window.__nativeClassSelectionLockV50)return 'LOCK';"
                + "window.__nativeClassSelectionLockV50=true;"
                + "window.start(m[1]);"
                + "setTimeout(function(){window.__nativeClassSelectionLockV50=false;},1000);"
                + "return 'OK:'+m[1];}}"
                + "return 'NONE';})()";
        web.evaluateJavascript(js, value -> { });
    }

    /** V50: диагностический маркер без polling и без блокировки других экранов. */
    private void installNativeTouchBridge() {
        if (web == null) return;
        web.evaluateJavascript("window.__nativeTouchBridgeV50=true; 'READY'", value -> { });
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
