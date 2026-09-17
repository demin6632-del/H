package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.view.MotionEvent;
import android.view.ViewGroup;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.core.splashscreen.SplashScreen;

public class MainActivity extends Activity {
    private boolean webViewReady = false;
    private WebView web;
    private FrameLayout root;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);
        splashScreen.setKeepOnScreenCondition(() -> !webViewReady);
        super.onCreate(savedInstanceState);

        root = new FrameLayout(this);
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(8, 8, 8));
        web.setClickable(true);
        web.setFocusable(true);
        web.setFocusableInTouchMode(true);

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);
        settings.setTextZoom(100);

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

        // Не блокируем штатное касание WebView. Если WebView не создаст click,
        // на ACTION_UP выполняется безопасный JS-fallback по фактической координате.
        web.setOnTouchListener((v, event) -> {
            if (webViewReady && event.getAction() == MotionEvent.ACTION_UP) {
                dispatchTouchFallback(event.getX(), event.getY());
            }
            return false;
        });

        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        web.loadUrl("file:///android_asset/index.html");
        setContentView(root);
        web.requestFocus();
    }

    /**
     * Резерв для Android WebView: определяет кнопку под пальцем и запускает её
     * штатный DOM click. Само касание при этом не перехватывается.
     */
    private void dispatchTouchFallback(float px, float py) {
        if (web == null || web.getWidth() <= 0 || web.getHeight() <= 0) return;
        final float nx = Math.max(0f, Math.min(1f, px / web.getWidth()));
        final float ny = Math.max(0f, Math.min(1f, py / web.getHeight()));
        final String js = "(function(){"
                + "var x=" + nx + ",y=" + ny + ";"
                + "var cx=x*window.innerWidth,cy=y*window.innerHeight;"
                + "var e=document.elementFromPoint(cx,cy);"
                + "var b=e&&e.closest?e.closest('button'):null;"
                + "if(!b||b.disabled)return 'NONE';"
                + "b.click();return 'OK';"
                + "})()";
        web.evaluateJavascript(js, value -> { });
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
