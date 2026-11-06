package local.codex.depthhome;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Toast;
import org.json.JSONArray;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Offline, minute-driven TV home. One landscape bitmap is held at a time. */
public final class MainActivity extends Activity {
    private static final String[] IMAGES = {"morning.jpg", "day.jpg", "sunset.jpg", "night.jpg"};
    private static final String[] LABELS = {"Sagora", "YouTube", "Play Store"};
    private static final String[] PACKAGES = {"cloud.walter.sagora", "io.gh.reisxd.tizentube.cobalt", "com.android.vending"};
    private final TimeZone zone = TimeZone.getTimeZone("Asia/Bangkok");
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final ExecutorService decoder = Executors.newSingleThreadExecutor();
    private HomeView home;
    private SharedPreferences preferences;
    private boolean resumed;
    private int preview = -1;
    private int requestedPhase = -1;
    private int loadedPhase = -1;
    private long generation;
    private Bitmap landscape;
    private float[][][] ridges = new float[4][0][0];
    private final Drawable[] banners = new Drawable[3];
    private final Runnable tick = new Runnable() {
        @Override public void run() {
            if (!resumed) return;
            refresh();
            handler.postDelayed(this, 60000L - System.currentTimeMillis() % 60000L + 40);
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().setNavigationBarColor(Color.BLACK);
        preferences = getSharedPreferences("landscape_home", MODE_PRIVATE);
        preview = preferences.getInt("preview", -1);
        readPreviewIntent(getIntent());
        try (InputStream in = getAssets().open("ridge.json")) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buffer = new byte[4096]; int count;
            while ((count = in.read(buffer)) != -1) out.write(buffer, 0, count);
            JSONArray phases = new JSONArray(out.toString("UTF-8"));
            for (int phase = 0; phase < 4; phase++) {
                JSONArray points = phases.getJSONArray(phase);
                ridges[phase] = new float[points.length()][2];
                for (int i = 0; i < points.length(); i++) {
                    ridges[phase][i][0] = (float) points.getJSONArray(i).getDouble(0);
                    ridges[phase][i][1] = (float) points.getJSONArray(i).getDouble(1);
                }
            }
        } catch (Exception error) {
            Toast.makeText(this, "Le relief n’a pas pu être chargé", Toast.LENGTH_LONG).show();
        }
        loadBanners();
        home = new HomeView();
        setContentView(home);
        immersive();
    }

    private void readPreviewIntent(Intent intent) {
        if (intent != null && intent.hasExtra("preview_phase")) {
            int value = intent.getIntExtra("preview_phase", -1);
            preview = value >= 0 && value < 4 ? value : -1;
        }
    }

    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        readPreviewIntent(intent);
        refresh();
    }

    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override public void onWindowFocusChanged(boolean focused) {
        super.onWindowFocusChanged(focused);
        if (focused) immersive();
    }

    @Override protected void onResume() {
        super.onResume();
        resumed = true;
        handler.removeCallbacks(tick);
        handler.post(tick);
    }

    @Override protected void onPause() {
        resumed = false;
        handler.removeCallbacks(tick);
        super.onPause();
    }

    @Override protected void onDestroy() {
        generation++;
        decoder.shutdown();
        handler.removeCallbacksAndMessages(null);
        landscape = null;
        super.onDestroy();
    }

    private int phaseNow() {
        if (preview >= 0) return preview;
        Calendar now = Calendar.getInstance(zone);
        int hour = now.get(Calendar.HOUR_OF_DAY);
        if (hour < 6 || hour >= 20) return 3;
        if (hour < 11) return 0;
        if (hour < 17) return 1;
        return 2;
    }

    private void refresh() {
        int phase = phaseNow();
        home.invalidate();
        if (phase == requestedPhase && landscape != null) return;
        requestedPhase = phase;
        final long task = ++generation;
        decoder.execute(() -> {
            Bitmap decoded = null;
            try (InputStream in = getAssets().open(IMAGES[phase])) {
                BitmapFactory.Options options = new BitmapFactory.Options();
                options.inPreferredConfig = Bitmap.Config.ARGB_8888;
                decoded = BitmapFactory.decodeStream(in, null, options);
            } catch (Exception ignored) { }
            final Bitmap next = decoded;
            handler.post(() -> {
                if (task != generation || isFinishing() || isDestroyed()) return;
                if (next != null) {
                    landscape = next;
                    loadedPhase = phase;
                    home.invalidate();
                } else {
                    requestedPhase = -1;
                    Toast.makeText(this, "Paysage indisponible", Toast.LENGTH_SHORT).show();
                }
            });
        });
    }

    private void loadBanners() {
        PackageManager pm = getPackageManager();
        String[] artPackages = {PACKAGES[0], "com.google.android.youtube.tv", PACKAGES[2]};
        for (int i = 0; i < artPackages.length; i++) {
            try {
                ApplicationInfo info = pm.getApplicationInfo(artPackages[i], PackageManager.MATCH_DISABLED_COMPONENTS);
                banners[i] = pm.getApplicationBanner(info);
                if (banners[i] == null) {
                    Intent launch = pm.getLeanbackLaunchIntentForPackage(artPackages[i]);
                    if (launch != null && pm.resolveActivity(launch, 0) != null)
                        banners[i] = pm.resolveActivity(launch, 0).activityInfo.loadBanner(pm);
                }
                if (banners[i] == null) banners[i] = pm.getApplicationIcon(info);
            } catch (Exception ignored) { }
        }
        // Sagora : sa propre vignette plutôt que l'icône de l'appli AIOStreams qu'elle ouvre.
        try (java.io.InputStream in = getAssets().open("sagora_banner.png")) {
            Bitmap sagora = BitmapFactory.decodeStream(in);
            if (sagora != null) banners[0] = new android.graphics.drawable.BitmapDrawable(getResources(), sagora);
        } catch (Exception ignored) { }
    }

    private void launch(int index) {
        if (index == 3) {
            startActivity(new Intent(Settings.ACTION_WIFI_SETTINGS));
            return;
        }
        if (index == 4) { menu(); return; }
        try {
            Intent launch = getPackageManager().getLeanbackLaunchIntentForPackage(PACKAGES[index]);
            if (launch == null) launch = getPackageManager().getLaunchIntentForPackage(PACKAGES[index]);
            if (launch == null) throw new IllegalStateException();
            launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(launch);
        } catch (Exception error) {
            Toast.makeText(this, LABELS[index] + " n’est pas disponible", Toast.LENGTH_SHORT).show();
        }
    }

    private void menu() {
        String[] items = {"Ambiance automatique — Bangkok", "Aperçu : matin", "Aperçu : journée",
                "Aperçu : coucher de soleil", "Aperçu : nuit", "Paramètres du téléviseur", "Ouvrir l’accueil classique"};
        new AlertDialog.Builder(this).setTitle("Paysages")
            .setItems(items, (dialog, which) -> {
                if (which <= 4) {
                    preview = which - 1;
                    preferences.edit().putInt("preview", preview).apply();
                    refresh();
                } else if (which == 5) {
                    startActivity(new Intent(Settings.ACTION_SETTINGS));
                } else {
                    try {
                        startActivity(new Intent().setClassName("com.gathin.tvhome", "com.gathin.tvhome.MainActivity"));
                    } catch (Exception error) {
                        Toast.makeText(this, "Accueil classique indisponible", Toast.LENGTH_SHORT).show();
                    }
                }
            }).setNegativeButton("Fermer", null).show();
    }

    @Override public void onBackPressed() {
        if (home.selected >= 3) { home.selected = 0; home.invalidate(); }
    }

    private final class HomeView extends View {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
        private final Typeface thin = Typeface.create("sans-serif-thin", Typeface.NORMAL);
        private final Typeface medium = Typeface.create("sans-serif-medium", Typeface.NORMAL);
        private final RectF[] hit = new RectF[5];
        private final SimpleDateFormat clock = new SimpleDateFormat("HH:mm", Locale.FRANCE);
        private final SimpleDateFormat date = new SimpleDateFormat("EEEE, MMMM d", Locale.ENGLISH);
        private int selected = 0;

        HomeView() {
            super(MainActivity.this);
            setFocusable(true); setFocusableInTouchMode(true); requestFocus();
            clock.setTimeZone(zone); date.setTimeZone(zone);
            setContentDescription("Accueil Paysages. Gauche et droite pour les applications, haut pour les réglages.");
            for (int i = 0; i < hit.length; i++) hit[i] = new RectF();
        }

        @Override protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            float sx = getWidth() / 1920f, sy = getHeight() / 1080f;
            canvas.save(); canvas.scale(sx, sy);
            final RectF screen = new RectF(0, 0, 1920, 1080);
            paint.setShader(null); paint.setColor(Color.rgb(10, 22, 40));
            canvas.drawRect(screen, paint);
            Bitmap image = landscape;
            // Original square Apple photos: a 16:9 crop retains the sky and coastline.
            Rect crop = image == null ? null : new Rect(0, Math.round(image.getHeight() * .04f),
                    image.getWidth(), Math.round(image.getHeight() * .04f) + Math.round(image.getWidth() * 9f / 16f));
            float[][] ridge = loadedPhase >= 0 ? ridges[loadedPhase] : new float[0][0];
            if (image != null) canvas.drawBitmap(image, crop, screen, paint);

            // Date and enormous live clock are below the foreground relief layer.
            Date now = new Date();
            paint.setTextAlign(Paint.Align.CENTER);
            paint.setTypeface(medium); paint.setTextSize(23);
            paint.setColor(Color.argb(235, 255, 255, 255));
            paint.setShadowLayer(8, 0, 2, Color.argb(55, 0, 0, 0));
            canvas.drawText(date.format(now).toUpperCase(Locale.ENGLISH), 960, 126, paint);
            paint.setTypeface(thin); paint.setTextSize(345);
            paint.setColor(Color.argb(244, 255, 255, 255));
            canvas.drawText(clock.format(now), 960, 530, paint);
            paint.clearShadowLayer();

            // The same bitmap is redrawn through its measured ridge path. No video,
            // segmentation model, second decoded bitmap or frame loop is needed.
            if (image != null && ridge.length > 0) {
                paint.setColor(Color.WHITE);
                Path foreground = new Path();
                foreground.moveTo(ridge[0][0] * 1920, ridge[0][1] * 1080);
                for (int i = 1; i < ridge.length; i++) foreground.lineTo(ridge[i][0] * 1920, ridge[i][1] * 1080);
                foreground.lineTo(1920, 1080); foreground.lineTo(0, 1080); foreground.close();
                canvas.save(); canvas.clipPath(foreground);
                canvas.drawBitmap(image, crop, screen, paint); canvas.restore();
            }

            paint.setShader(new LinearGradient(0, 690, 0, 1080,
                    new int[]{Color.TRANSPARENT, Color.argb(130, 0, 0, 0)}, null, Shader.TileMode.CLAMP));
            canvas.drawRect(0, 690, 1920, 1080, paint); paint.setShader(null);
            paint.setColor(Color.argb(140, 15, 19, 28));
            canvas.drawRoundRect(new RectF(363, 818, 1557, 1030), 34, 34, paint);
            paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(1);
            paint.setColor(Color.argb(58, 255, 255, 255));
            canvas.drawRoundRect(new RectF(363, 818, 1557, 1030), 34, 34, paint);
            paint.setStyle(Paint.Style.FILL);
            for (int i = 0; i < 3; i++) {
                float left = 389 + i * 388;
                RectF rect = hit[i]; rect.set(left, 839, left + 366, 1005);
                boolean focused = selected == i;
                if (focused) {
                    paint.setColor(Color.argb(238, 255, 255, 255));
                    canvas.drawRoundRect(new RectF(left - 6, 833, left + 372, 1011), 23, 23, paint);
                }
                Drawable art = banners[i];
                int tileColor = Color.rgb(24, 28, 36);
                if (art instanceof android.graphics.drawable.BitmapDrawable) {
                    Bitmap artBitmap = ((android.graphics.drawable.BitmapDrawable) art).getBitmap();
                    int corner = artBitmap.getPixel(0, 0);
                    if (Color.alpha(corner) == 255) tileColor = corner;
                }
                paint.setColor(tileColor);
                canvas.drawRoundRect(rect, 18, 18, paint);
                if (art != null) {
                    Path round = new Path(); round.addRoundRect(rect, 18, 18, Path.Direction.CW);
                    canvas.save(); canvas.clipPath(round);
                    int artWidth = Math.max(1, art.getIntrinsicWidth());
                    int artHeight = Math.max(1, art.getIntrinsicHeight());
                    float scale = i == 0 ? Math.max(rect.width() / artWidth, rect.height() / artHeight)
                            : Math.min(rect.width() / artWidth, rect.height() / artHeight);
                    float width = artWidth * scale, height = artHeight * scale;
                    int x = Math.round(rect.centerX() - width / 2), y = Math.round(rect.centerY() - height / 2);
                    art.setBounds(x, y, Math.round(x + width), Math.round(y + height));
                    art.draw(canvas); canvas.restore();
                } else {
                    paint.setColor(Color.WHITE); paint.setTypeface(medium); paint.setTextSize(28);
                    canvas.drawText(LABELS[i], left + 183, 930, paint);
                }
            }
            button(canvas, 3, 1458, 48, 170, "Wi-Fi");
            button(canvas, 4, 1644, 48, 218, "Réglages");
            canvas.restore();
        }

        private void button(Canvas canvas, int id, float left, float top, float width, String label) {
            RectF rect = hit[id]; rect.set(left, top, left + width, top + 62);
            paint.setColor(selected == id ? Color.argb(235, 255, 255, 255) : Color.argb(90, 10, 17, 28));
            canvas.drawRoundRect(rect, 31, 31, paint);
            paint.setTypeface(medium); paint.setTextAlign(Paint.Align.CENTER); paint.setTextSize(22);
            paint.setColor(selected == id ? Color.rgb(20, 25, 35) : Color.WHITE);
            canvas.drawText(label, rect.centerX(), top + 39, paint);
        }

        @Override public boolean onKeyDown(int key, KeyEvent event) {
            if (event.getRepeatCount() > 0 && (key == KeyEvent.KEYCODE_DPAD_CENTER || key == KeyEvent.KEYCODE_ENTER)) return true;
            switch (key) {
                case KeyEvent.KEYCODE_DPAD_LEFT:
                    selected = selected < 3 ? Math.max(0, selected - 1) : 3; invalidate(); return true;
                case KeyEvent.KEYCODE_DPAD_RIGHT:
                    selected = selected < 3 ? Math.min(2, selected + 1) : 4; invalidate(); return true;
                case KeyEvent.KEYCODE_DPAD_UP: selected = 3; invalidate(); return true;
                case KeyEvent.KEYCODE_DPAD_DOWN: selected = 0; invalidate(); return true;
                case KeyEvent.KEYCODE_DPAD_CENTER:
                case KeyEvent.KEYCODE_ENTER: launch(selected); return true;
                case KeyEvent.KEYCODE_MENU: menu(); return true;
                default: return super.onKeyDown(key, event);
            }
        }

        @Override public boolean onTouchEvent(MotionEvent event) {
            if (event.getAction() == MotionEvent.ACTION_DOWN) return true;
            if (event.getAction() == MotionEvent.ACTION_UP) {
                float x = event.getX() * 1920 / getWidth(), y = event.getY() * 1080 / getHeight();
                for (int i = 0; i < hit.length; i++) if (hit[i].contains(x, y)) {
                    selected = i; invalidate(); performClick(); launch(i); return true;
                }
                return true;
            }
            return true;
        }

        @Override public boolean performClick() { super.performClick(); return true; }
    }
}
