package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.core.splashscreen.SplashScreen;

public class MainActivity extends Activity {
    private volatile boolean webViewReady = false;
    private WebView web;
    private final Handler touchHandler = new Handler(Looper.getMainLooper());
    private float downX;
    private float downY;
    private long downAt;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Важно: SplashScreen подключается до super.onCreate().
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);
        splashScreen.setKeepOnScreenCondition(() -> !webViewReady);
        super.onCreate(savedInstanceState);

        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(8, 8, 8));

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageCommitVisible(WebView view, String url) {
                webViewReady = true;
                installClickAudit(view);
                super.onPageCommitVisible(view, url);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                webViewReady = true;
                installClickAudit(view);
                super.onPageFinished(view, url);
            }
        });

        // ANDROID-TOUCH-NATIVE-FALLBACK-V42:
        // штатное событие WebView остаётся основным; если оно не дошло до JS,
        // после короткой задержки выполняем точечный fallback по координатам касания.
        web.setOnTouchListener((v, event) -> {
            if (event.getActionMasked() == MotionEvent.ACTION_DOWN) {
                downX = event.getX();
                downY = event.getY();
                downAt = System.currentTimeMillis();
            } else if (event.getActionMasked() == MotionEvent.ACTION_UP) {
                final float x = event.getX();
                final float y = event.getY();
                final long duration = System.currentTimeMillis() - downAt;
                if (Math.hypot(x - downX, y - downY) < 35f && duration < 1200L) {
                    final float density = getResources().getDisplayMetrics().density;
                    touchHandler.postDelayed(() -> {
                        if (web == null) return;
                        final float cssX = x / Math.max(1f, density);
                        final float cssY = y / Math.max(1f, density);
                        String js = "(function(x,y){if(Date.now()-(window.__lastNativeAuditClick||0)<600)return;var e=document.elementFromPoint(x,y);var b=e&&e.closest?e.closest('button'):null;if(b&&!b.disabled)b.click();})(" + cssX + "," + cssY + ")";
                        web.evaluateJavascript(js, null);
                    }, 300L);
                }
            }
            return false;
        });

        web.loadUrl("file:///android_asset/index.html");
        setContentView(web);
        new Handler(Looper.getMainLooper()).postDelayed(() -> webViewReady = true, 5000);
    }

    private void installClickAudit(WebView view) {
        view.evaluateJavascript("(function(){if(window.__nativeTouchAudit)return;window.__nativeTouchAudit=true;document.addEventListener('click',function(){window.__lastNativeAuditClick=Date.now()},true)})()", null);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // Системная кнопка/жест Назад сначала возвращает на предыдущий экран игры.
        if (keyCode == KeyEvent.KEYCODE_BACK && web != null && web.canGoBack()) {
            web.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
