package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.core.splashscreen.SplashScreen;

public class MainActivity extends Activity {
    private volatile boolean webViewReady = false;
    private WebView web;
    private final Handler touchHandler = new Handler(Looper.getMainLooper());
    private float downRawX;
    private float downRawY;
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
                super.onPageCommitVisible(view, url);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                webViewReady = true;
                super.onPageFinished(view, url);
            }
        });

        web.loadUrl("file:///android_asset/index.html");
        setContentView(web);
        new Handler(Looper.getMainLooper()).postDelayed(() -> webViewReady = true, 5000);
    }

    /**
     * ANDROID-TOUCH-DISPATCH-V46:
     * Перехватываем касание на уровне Activity, до WebView.
     * Это исключает проблему, когда WebView/HTML не доставляет touch/click-событие.
     * Игровая логика не изменяется: Android только вызывает существующий window.start().
     */
    @Override
    public boolean dispatchTouchEvent(MotionEvent event) {
        if (event != null) {
            final int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN) {
                downRawX = event.getRawX();
                downRawY = event.getRawY();
                downAt = System.currentTimeMillis();
            } else if (action == MotionEvent.ACTION_UP) {
                final float rawX = event.getRawX();
                final float rawY = event.getRawY();
                final long duration = System.currentTimeMillis() - downAt;
                final float distance = (float)Math.hypot(rawX - downRawX, rawY - downRawY);

                if (web != null && distance < 60f && duration < 1500L) {
                    final int[] loc = new int[2];
                    web.getLocationOnScreen(loc);
                    final float localX = rawX - loc[0];
                    final float localY = rawY - loc[1];

                    touchHandler.postDelayed(() -> {
                        if (web == null || !webViewReady) return;

                        // Координаты переводятся из физических пикселей WebView в CSS-пиксели.
                        final float webWidth = Math.max(1f, web.getWidth());
                        final float webHeight = Math.max(1f, web.getHeight());
                        String js = "(function(px,py,pw,ph){"
                                + "var vw=document.documentElement.clientWidth||window.innerWidth||1;"
                                + "var vh=document.documentElement.clientHeight||window.innerHeight||1;"
                                + "var x=px*(vw/pw),y=py*(vh/ph);"
                                + "var cards=document.querySelectorAll('.class-card');"
                                + "for(var i=0;i<cards.length;i++){"
                                + "var r=cards[i].getBoundingClientRect();"
                                + "if(x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom){"
                                + "var o=cards[i].getAttribute('onclick')||'';"
                                + "var m=o.match(/start\\(['\"]([^'\"]+)['\"]\\)/);"
                                + "if(m&&typeof window.start==='function'){window.start(m[1]);return 'class';}"
                                + "}}"
                                + "var e=document.elementFromPoint(x,y);"
                                + "var b=e&&e.closest?e.closest('button'):null;"
                                + "if(b&&!b.disabled){b.click();return 'button';}"
                                + "return 'none';"
                                + "})(" + localX + "," + localY + "," + webWidth + "," + webHeight + ")";
                        web.evaluateJavascript(js, null);
                    }, 25L);
                }
            }
        }

        // Обязательно передаём событие дальше обычному WebView.
        return super.dispatchTouchEvent(event);
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
