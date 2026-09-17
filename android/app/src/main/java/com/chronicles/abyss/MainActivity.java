package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
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
                installAndroidClassTouchFix(view);
                super.onPageFinished(view, url);
            }
        });

        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        web.loadUrl("file:///android_asset/index.html");
        setContentView(root);
    }

    /**
     * Android WebView: выбор класса обрабатывается напрямую из touch-события.
     * Остальные кнопки остаются полностью под управлением существующей игры.
     */
    private void installAndroidClassTouchFix(WebView view) {
        view.evaluateJavascript(
                "(function(){" +
                "if(window.__androidClassTouchFixV53)return;" +
                "window.__androidClassTouchFixV53=true;" +
                "var lock=false;" +
                "function activate(e){" +
                "var t=e.target;var card=t&&t.closest?t.closest('#classes .class-card'):null;" +
                "if(!card||lock)return;" +
                "var o=card.getAttribute('onclick')||'';" +
                "var m=o.match(/start\\((['\\\"])(.*?)\\1\\)/);" +
                "if(!m||typeof window.start!=='function')return;" +
                "lock=true;" +
                "if(e.cancelable)e.preventDefault();" +
                "if(e.stopImmediatePropagation)e.stopImmediatePropagation();" +
                "if(e.stopPropagation)e.stopPropagation();" +
                "window.start(m[2]);" +
                "setTimeout(function(){lock=false;},700);" +
                "}" +
                "document.addEventListener('touchend',activate,{capture:true,passive:false});" +
                "document.addEventListener('pointerup',activate,{capture:true,passive:false});" +
                "})()", null);
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
