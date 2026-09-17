package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
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
    private final Handler uiHandler = new Handler(Looper.getMainLooper());
    private boolean classScreenVisible = false;
    private boolean classTouchHandled = false;
    private long classTouchLockUntil = 0L;

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

        // V49: нативный перехватчик работает непосредственно на WebView.
        // Прозрачные View поверх HTML больше не используются, поэтому они не могут перекрыть неверную область экрана.
        web.setOnTouchListener((v, event) -> {
            if (!webViewReady) return false;
            if (event.getAction() == MotionEvent.ACTION_DOWN) {
                classTouchHandled = false;
                if (classScreenVisible && System.currentTimeMillis() >= classTouchLockUntil) {
                    classTouchHandled = true;
                    dispatchNativeClassTouch(event.getX(), event.getY());
                    return true;
                }
            }
            if (classTouchHandled && (event.getAction() == MotionEvent.ACTION_MOVE
                    || event.getAction() == MotionEvent.ACTION_UP
                    || event.getAction() == MotionEvent.ACTION_CANCEL)) {
                if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
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
     * V49: нормализует реальные координаты MotionEvent относительно WebView.
     * Затем DOM сам определяет, какая карточка класса находится под пальцем.
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
                + "var x=" + nx + "*window.innerWidth,y=" + ny + "*window.innerHeight;"
                + "var e=document.elementFromPoint(x,y);"
                + "var b=e&&e.closest?e.closest('.class-card'):null;"
                + "if(!b)return 'NONE';"
                + "var o=b.getAttribute('onclick')||'';"
                + "var m=o.match(/start\\(['\"]([^'\"]+)['\"]\\)/);"
                + "if(!m||typeof window.start!=='function')return 'BAD';"
                + "window.__nativeClassTouchV49=true;"
                + "window.start(m[1]);return 'OK:'+m[1];"
                + "})()";
        web.evaluateJavascript(js, value -> {
            if (value != null && value.contains("OK:")) {
                classTouchLockUntil = System.currentTimeMillis() + 900L;
            }
        });
    }

    /** V49: обновляет только признак экрана выбора класса. */
    private void installNativeTouchBridge() {
        if (web == null) return;
        web.evaluateJavascript(
                "(function(){if(window.__nativeTouchBridgeV49)return 'READY';"
                        + "window.__nativeTouchBridgeV49=true;"
                        + "setInterval(function(){var s=document.getElementById('classes');"
                        + "window.__classesVisibleV49=!!(s&&!s.classList.contains('hidden'));},150);"
                        + "return 'READY';})()",
                value -> pollClassVisibility());
    }

    private void pollClassVisibility() {
        if (web == null || !webViewReady) return;
        web.evaluateJavascript("!!window.__classesVisibleV49", value -> {
            classScreenVisible = "true".equals(value);
            uiHandler.postDelayed(this::pollClassVisibility, 150L);
        });
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
        uiHandler.removeCallbacksAndMessages(null);
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
