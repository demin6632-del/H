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

        // Не перехватываем штатное касание WebView. На ACTION_UP лишь ставим
        // отложенный JS-fallback, чтобы дать WebView закончить собственный tap/click.
        web.setOnTouchListener((v, event) -> {
            if (webViewReady && event.getAction() == MotionEvent.ACTION_UP) {
                final float px = event.getX();
                final float py = event.getY();
                web.postDelayed(() -> dispatchTouchFallback(px, py), 90);
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
     * Резерв для Android WebView: самостоятельно определяет HTML-кнопку
     * под фактическим пальцем и запускает её click().
     * Здесь нет зависимости от отдельной JS-функции в игре: весь fallback
     * находится в Android-обёртке, поэтому работает даже на старой версии HTML.
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
                + "if(!b||b.disabled)return false;"
                + "if(window.__lastDomButtonClick && now-window.__lastDomButtonClick<350)return true;"
                + "window.__lastNativeButtonAt=now;"
                + "try{b.click();return true;}catch(err){console.error('ANDROID_TOUCH_FALLBACK',err);return false;}"
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
