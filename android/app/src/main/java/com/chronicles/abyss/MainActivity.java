package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.view.KeyEvent;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.core.splashscreen.SplashScreen;

public class MainActivity extends Activity {
    private volatile boolean webViewReady = false;
    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Важно: SplashScreen подключается до super.onCreate().
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);

        // Не закрываем загрузочный экран, пока WebView не подготовил игру.
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
                // Первый видимый кадр игры уже готов — можно плавно убрать splash.
                webViewReady = true;
                super.onPageCommitVisible(view, url);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                // Резервный вариант для устройств, где onPageCommitVisible не вызывается.
                webViewReady = true;
                super.onPageFinished(view, url);
            }
        });

        web.loadUrl("file:///android_asset/index.html");
        setContentView(web);

        // Защита от вечного splash при ошибке загрузки WebView.
        new Handler(Looper.getMainLooper()).postDelayed(() -> webViewReady = true, 5000);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // Системная кнопка/жест Назад сначала возвращает на предыдущий экран игры.
        // Если истории игры уже нет, Android выполняет стандартное действие выхода.
        if (keyCode == KeyEvent.KEYCODE_BACK && web != null && web.canGoBack()) {
            web.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
