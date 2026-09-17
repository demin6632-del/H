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
            uiHandler.postDelayed(this, 250L);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Важно: SplashScreen подключается до super.onCreate().
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

        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        // Нативный прозрачный слой находится поверх WebView только для четырёх карточек классов.
        // Он не изменяет внешний вид игры и не вмешивается в остальные кнопки.
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
            hit.setOnClickListener(v -> {
                if (web == null || !webViewReady) return;
                // Вызывается существующая игровая функция выбора класса.
                String cls = classNames[index].replace("'", "\\'");
                web.evaluateJavascript("(function(){if(typeof window.start==='function'){window.start('" + cls + "');}})()", null);
                classHitLayer.setVisibility(View.GONE);
            });
            classHitBoxes[i] = hit;
            classHitLayer.addView(hit, new FrameLayout.LayoutParams(1, 1));
        }

        web.loadUrl("file:///android_asset/index.html");
        setContentView(root);
        uiHandler.post(classHitboxUpdater);
        uiHandler.postDelayed(() -> webViewReady = true, 5000L);
    }

    /**
     * ANDROID-NATIVE-CLASS-HITBOX-V47:
     * Нативные прозрачные области поверх карточек классов.
     * Это полностью обходит проблемную HTML-цепочку touch/pointer/click.
     * Игровая логика не дублируется: Android вызывает существующий window.start().
     */
    private void updateNativeClassHitboxes() {
        if (web == null || classHitLayer == null || !webViewReady) return;

        String js = "(function(){"
                + "var s=document.getElementById('classes');"
                + "if(!s||s.classList.contains('hidden'))return 'H';"
                + "var a=s.querySelectorAll('.class-card');"
                + "if(a.length<4)return 'H';"
                + "var vw=document.documentElement.clientWidth||window.innerWidth||1;"
                + "var vh=document.documentElement.clientHeight||window.innerHeight||1;"
                + "var out=vw+','+vh;"
                + "for(var i=0;i<4;i++){var r=a[i].getBoundingClientRect();"
                + "out+='|'+r.left+','+r.top+','+r.width+','+r.height;}"
                + "return out;"
                + "})()";

        web.evaluateJavascript(js, value -> {
            if (value == null) return;
            String data = value;
            if (data.length() >= 2 && data.charAt(0) == '"' && data.charAt(data.length() - 1) == '"') {
                data = data.substring(1, data.length() - 1).replace("\\\"", "\"");
            }
            if ("H".equals(data)) {
                classHitLayer.setVisibility(View.GONE);
                return;
            }

            try {
                String[] parts = data.split("\\|");
                if (parts.length < 5) return;
                String[] viewport = parts[0].split(",");
                float cssW = Float.parseFloat(viewport[0]);
                float cssH = Float.parseFloat(viewport[1]);
                float scaleX = web.getWidth() / Math.max(1f, cssW);
                float scaleY = web.getHeight() / Math.max(1f, cssH);

                for (int i = 0; i < 4; i++) {
                    String[] r = parts[i + 1].split(",");
                    if (r.length < 4) continue;
                    float left = Float.parseFloat(r[0]) * scaleX;
                    float top = Float.parseFloat(r[1]) * scaleY;
                    float width = Float.parseFloat(r[2]) * scaleX;
                    float height = Float.parseFloat(r[3]) * scaleY;

                    FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                            Math.max(1, Math.round(width)),
                            Math.max(1, Math.round(height)));
                    lp.leftMargin = Math.round(left);
                    lp.topMargin = Math.round(top);
                    classHitBoxes[i].setLayoutParams(lp);
                }
                classHitLayer.setVisibility(View.VISIBLE);
                classHitLayer.bringToFront();
            } catch (Exception ignored) {
                // При временно некорректных координатах слой просто не активируется.
            }
        });
    }

    @Override
    public void onBackPressed() {
        // Сначала возвращаемся внутри игры через её собственную кнопку/историю.
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
    private void superOnBackPressed() {
        super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        uiHandler.removeCallbacks(classHitboxUpdater);
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
