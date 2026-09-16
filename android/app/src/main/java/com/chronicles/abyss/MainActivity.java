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
                super.onPageCommitVisible(view, url);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                webViewReady = true;
                super.onPageFinished(view, url);
            }
        });

        // ANDROID-TOUCH-NATIVE-FALLBACK-V45:
        // Резервный обработчик выполняет hit-test напрямую из Android.
        // Для карточек класса он не зависит от pointer/touch/click-событий HTML.
        web.setOnTouchListener((v, event) -> {
            if (event.getActionMasked() == MotionEvent.ACTION_DOWN) {
                downX = event.getX();
                downY = event.getY();
                downAt = System.currentTimeMillis();
            } else if (event.getActionMasked() == MotionEvent.ACTION_UP) {
                final float x = event.getX();
                final float y = event.getY();
                final long duration = System.currentTimeMillis() - downAt;
                if (Math.hypot(x - downX, y - downY) < 45f && duration < 1500L) {
                    touchHandler.postDelayed(() -> {
                        if (web == null) return;

                        // Сначала пробуем точно определить карточку класса по её DOM-геометрии.
                        String js = "(function(px,py){"
                                + "var vw=document.documentElement.clientWidth||window.innerWidth||1;"
                                + "var vh=document.documentElement.clientHeight||window.innerHeight||1;"
                                + "var sx=vw/Math.max(1," + web.getWidth() + ");"
                                + "var sy=vh/Math.max(1," + web.getHeight() + ");"
                                + "var x=px*sx,y=py*sy;"
                                + "var cards=document.querySelectorAll('.class-card');"
                                + "for(var i=0;i<cards.length;i++){var r=cards[i].getBoundingClientRect();"
                                + "if(x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom){"
                                + "var o=cards[i].getAttribute('onclick')||'';"
                                + "var m=o.match(/start\\(['\"]([^'\"]+)['\"]\\)/);"
                                + "if(m&&typeof window.start==='function'){window.start(m[1]);return 'class';}" 
                                + "}}"
                                + "var e=document.elementFromPoint(x,y);"
                                + "var b=e&&e.closest?e.closest('button'):null;"
                                + "if(b&&!b.disabled){b.click();return 'button';}"
                                + "return 'none';"
                                + "})(" + x + "," + y + ")";
                        web.evaluateJavascript(js, null);
                    }, 40L);
                }
            }
            // Не блокируем штатную обработку WebView.
            return false;
        });

        web.loadUrl("file:///android_asset/index.html");
        setContentView(web);
        new Handler(Looper.getMainLooper()).postDelayed(() -> webViewReady = true, 5000);
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
