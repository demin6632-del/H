package com.chronicles.abyss;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.view.KeyEvent;
import android.view.View;
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
    private FrameLayout classHitLayer;
    private final Handler uiHandler = new Handler(Looper.getMainLooper());
    private final View[] classHitBoxes = new View[4];
    private final String[] classNames = {"Воин", "Разбойник", "Маг", "Охотник"};
    private final Runnable classHitboxUpdater = new Runnable() {
        @Override public void run() {
            updateNativeClassHitboxes();
            uiHandler.postDelayed(this, 300L);
        }
    };

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

        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        // V48: отдельный нативный слой только для выбора класса.
        // Позиции рассчитываются от фактического размера Activity, а не от CSS/WebView-координат.
        classHitLayer = new FrameLayout(this);
        classHitLayer.setBackgroundColor(Color.TRANSPARENT);
        classHitLayer.setVisibility(View.GONE);
        root.addView(classHitLayer, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        for (int i = 0; i < classHitBoxes.length; i++) {
            final int index = i;
            View hit = new View(this);
            hit.setBackgroundColor(Color.TRANSPARENT);
            hit.setClickable(true);
            hit.setFocusable(false);
            hit.setOnTouchListener((v, event) -> {
                if (event.getAction() == android.view.MotionEvent.ACTION_UP) {
                    selectNativeClass(index);
                }
                return true;
            });
            classHitBoxes[i] = hit;
            classHitLayer.addView(hit, new FrameLayout.LayoutParams(1, 1));
        }

        web.loadUrl("file:///android_asset/index.html");
        setContentView(root);
        root.post(classHitboxUpdater);
    }

    /**
     * ANDROID-NATIVE-CLASS-HITBOX-V48
     * Фикс не использует DOM rect, density или координаты WebView.
     * Четыре реальные Android View получают касание напрямую.
     */
    private void updateNativeClassHitboxes() {
        if (root == null || classHitLayer == null || web == null || !webViewReady) return;

        web.evaluateJavascript("(function(){var s=document.getElementById('classes');return s&&!s.classList.contains('hidden')?'SHOW':'HIDE';})()", value -> {
            boolean show = value != null && value.contains("SHOW");
            if (!show) {
                classHitLayer.setVisibility(View.GONE);
                return;
            }
            layoutNativeClassHitboxes();
        });
    }

    private void layoutNativeClassHitboxes() {
        int w = root.getWidth();
        int h = root.getHeight();
        if (w <= 0 || h <= 0) return;

        // Пропорции соответствуют сетке четырёх карточек на экране выбора класса.
        // Небольшой запас по краям делает касание надёжным, не затрагивая кнопку "Назад".
        float leftX = w * 0.055f;
        float rightX = w * 0.505f;
        float cardW = w * 0.440f;
        float topY = h * 0.155f;
        float secondY = h * 0.385f;
        float cardH = h * 0.215f;

        setHitBox(classHitBoxes[0], leftX, topY, cardW, cardH);
        setHitBox(classHitBoxes[1], rightX, topY, cardW, cardH);
        setHitBox(classHitBoxes[2], leftX, secondY, cardW, cardH);
        setHitBox(classHitBoxes[3], rightX, secondY, cardW, cardH);

        classHitLayer.setVisibility(View.VISIBLE);
        classHitLayer.bringToFront();
    }

    private void setHitBox(View v, float x, float y, float width, float height) {
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                Math.max(1, Math.round(width)), Math.max(1, Math.round(height)));
        lp.leftMargin = Math.round(x);
        lp.topMargin = Math.round(y);
        v.setLayoutParams(lp);
    }

    private void selectNativeClass(int index) {
        if (index < 0 || index >= classNames.length || web == null || !webViewReady) return;
        String cls = classNames[index].replace("'", "\\'");
        // Используется существующая игровая функция. Игровые характеристики и логика не дублируются.
        web.evaluateJavascript("(function(){if(typeof window.start==='function'){window.start('" + cls + "');return 'OK';}return 'NO_START';})()", value -> {
            classHitLayer.setVisibility(View.GONE);
            updateNativeClassHitboxes();
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
        superOnBackPressed();
    }

    @SuppressWarnings("deprecation")
    private void superOnBackPressed() { super.onBackPressed(); }

    @Override
    protected void onDestroy() {
        uiHandler.removeCallbacks(classHitboxUpdater);
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
