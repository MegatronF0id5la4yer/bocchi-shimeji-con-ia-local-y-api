package com.bocchi.pinkchan.shimeji;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.graphics.PixelFormat;
import android.graphics.Point;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Vibrator;
import android.util.DisplayMetrics;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class ShimejiService extends Service {

    public static final String ACTION_START = "com.bocchi.pinkchan.shimeji.START";
    public static final String ACTION_STOP = "com.bocchi.pinkchan.shimeji.STOP";
    public static final String ACTION_SET_SKIN = "com.bocchi.pinkchan.shimeji.SET_SKIN";
    public static final String ACTION_SET_SIZE = "com.bocchi.pinkchan.shimeji.SET_SIZE";
    public static final String ACTION_SET_GRAVITY = "com.bocchi.pinkchan.shimeji.SET_GRAVITY";
    public static final String ACTION_CENTER = "com.bocchi.pinkchan.shimeji.CENTER";
    public static final String ACTION_TRIGGER = "com.bocchi.pinkchan.shimeji.TRIGGER";

    public static final String EXTRA_SKIN = "extra_skin";
    public static final String EXTRA_SIZE_DP = "extra_size_dp";
    public static final String EXTRA_ZERO_GRAVITY = "extra_zero_gravity";
    public static final String EXTRA_TRIGGER_ACTION = "extra_trigger_action";

    private static final String CHANNEL_ID = "shimeji_overlay_channel";
    private static final int NOTIFICATION_ID = 1001;

    public static boolean isRunning = false;

    private WindowManager windowManager;
    private View overlayView;
    private ImageView ivSprite;
    private TextView tvSpeechBubble;
    private WindowManager.LayoutParams params;

    private SkinData currentSkin;
    private int sizePx;
    private boolean zeroGravity = false;

    // Física y Estados
    private float posX, posY;
    private float velX, velY;
    private int facing = 1; // 1: derecha, -1: izquierda
    private String state = "STAND"; // STAND, WALK, FALL, SIT, CLIMB_LEFT, CLIMB_RIGHT, GUITAR, BOX
    private int stateTimer = 90;
    private int tickCount = 0;
    private final Random random = new Random();

    // Cache de Bitmaps cargados
    private final Map<String, Bitmap> bitmapCache = new HashMap<>();

    // Pantalla
    private int screenWidth;
    private int screenHeight;

    // Drag & Drop
    private boolean isDragging = false;
    private float touchStartX, touchStartY;
    private float initialPosX, initialPosY;
    private long touchStartTime;
    private float lastMoveX, lastMoveY;
    private long lastMoveTime;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private Runnable loopRunnable;
    private Runnable hideBubbleRunnable;

    private Vibrator vibrator;

    @Override
    public void onCreate() {
        super.onCreate();
        isRunning = true;
        vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);

        currentSkin = SkinData.get("Konata");
        sizePx = dpToPx(128);

        updateScreenDimensions();
        createNotificationChannel();
        startForeground(NOTIFICATION_ID, buildNotification());

        setupOverlayView();
        startPhysicsLoop();
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "PinkChan Shimeji Overlay",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Control de Shimeji flotante en pantalla");
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }

    private Notification buildNotification() {
        Intent openIntent = new Intent(this, MainActivity.class);
        PendingIntent pOpen = PendingIntent.getActivity(
            this, 0, openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0)
        );

        Intent stopIntent = new Intent(this, ShimejiService.class);
        stopIntent.setAction(ACTION_STOP);
        PendingIntent pStop = PendingIntent.getService(
            this, 1, stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0)
        );

        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(this, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }

        builder.setContentTitle("PinkChan Shimeji activo")
            .setContentText("Personaje: " + currentSkin.name)
            .setSmallIcon(R.drawable.ic_launcher)
            .setContentIntent(pOpen)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Detener", pStop)
            .setOngoing(true);

        return builder.build();
    }

    private void updateScreenDimensions() {
        DisplayMetrics dm = getResources().getDisplayMetrics();
        screenWidth = dm.widthPixels;
        screenHeight = dm.heightPixels;
    }

    private void setupOverlayView() {
        LayoutInflater inflater = LayoutInflater.from(this);
        overlayView = inflater.inflate(R.layout.view_shimeji_overlay, null);

        ivSprite = overlayView.findViewById(R.id.shimeji_image_view);
        tvSpeechBubble = overlayView.findViewById(R.id.shimeji_speech_bubble);

        int layoutType;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutType = WindowManager.LayoutParams.TYPE_PHONE;
        }

        params = new WindowManager.LayoutParams(
            sizePx,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        );

        params.gravity = Gravity.TOP | Gravity.START;
        posX = screenWidth / 2f - (sizePx / 2f);
        posY = getFloorY();
        params.x = (int) posX;
        params.y = (int) posY;

        setupTouchEvents();

        windowManager.addView(overlayView, params);
        showRandomSpeech();
    }

    private int getFloorY() {
        // Altura del suelo considerando la barra de navegación
        return screenHeight - sizePx - dpToPx(35);
    }

    private void setupTouchEvents() {
        overlayView.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        isDragging = true;
                        touchStartTime = System.currentTimeMillis();
                        touchStartX = event.getRawX();
                        touchStartY = event.getRawY();
                        initialPosX = posX;
                        initialPosY = posY;

                        lastMoveX = touchStartX;
                        lastMoveY = touchStartY;
                        lastMoveTime = touchStartTime;

                        state = "FALL";
                        velX = 0;
                        velY = 0;
                        triggerHaptic(25);
                        updateSprite();
                        return true;

                    case MotionEvent.ACTION_MOVE:
                        if (!isDragging) return false;
                        float curX = event.getRawX();
                        float curY = event.getRawY();

                        posX = initialPosX + (curX - touchStartX);
                        posY = initialPosY + (curY - touchStartY);

                        params.x = (int) posX;
                        params.y = (int) posY;
                        windowManager.updateViewLayout(overlayView, params);

                        lastMoveX = curX;
                        lastMoveY = curY;
                        lastMoveTime = System.currentTimeMillis();
                        return true;

                    case MotionEvent.ACTION_UP:
                        if (!isDragging) return false;
                        isDragging = false;

                        float totalDist = (float) Math.hypot(event.getRawX() - touchStartX, event.getRawY() - touchStartY);
                        long duration = System.currentTimeMillis() - touchStartTime;

                        // Si fue un toque rápido y corto -> POKE / TAP
                        if (totalDist < dpToPx(12) && duration < 350) {
                            onPoke();
                        } else {
                            // Calcular velocidad de lanzamiento
                            long dt = System.currentTimeMillis() - lastMoveTime;
                            if (dt > 0 && dt < 150) {
                                velX = (event.getRawX() - lastMoveX) * 0.8f;
                                velY = (event.getRawY() - lastMoveY) * 0.8f;
                            } else {
                                velX = 0;
                                velY = 1f;
                            }
                            velX = Math.max(-25f, Math.min(25f, velX));
                            velY = Math.max(-30f, Math.min(30f, velY));
                            triggerHaptic(15);
                        }
                        return true;
                }
                return false;
            }
        });
    }

    private void onPoke() {
        triggerHaptic(40);
        state = "STAND";
        stateTimer = 50;

        String[] poked = currentSkin.poked;
        if (poked.length > 0) {
            String text = poked[random.nextInt(poked.length)];
            say(text, 2800);
        }
    }

    public void say(String text, int durationMs) {
        if (tvSpeechBubble == null) return;
        tvSpeechBubble.setText(text);
        tvSpeechBubble.setVisibility(View.VISIBLE);

        if (hideBubbleRunnable != null) {
            handler.removeCallbacks(hideBubbleRunnable);
        }
        hideBubbleRunnable = new Runnable() {
            @Override
            public void run() {
                if (tvSpeechBubble != null) {
                    tvSpeechBubble.setVisibility(View.GONE);
                }
            }
        };
        handler.postDelayed(hideBubbleRunnable, durationMs);
    }

    private void showRandomSpeech() {
        String[] dl = currentSkin.dialogues;
        if (dl.length > 0) {
            say(dl[random.nextInt(dl.length)], 3200);
        }
    }

    private void triggerHaptic(long ms) {
        if (vibrator != null && vibrator.hasVibrator()) {
            try {
                vibrator.vibrate(ms);
            } catch (Exception ignored) {}
        }
    }

    private void startPhysicsLoop() {
        loopRunnable = new Runnable() {
            @Override
            public void run() {
                updatePhysics();
                handler.postDelayed(this, 33); // ~30 FPS
            }
        };
        handler.post(loopRunnable);
    }

    private void updatePhysics() {
        if (isDragging || overlayView == null) return;

        updateScreenDimensions();
        int floor = getFloorY();
        int ceiling = dpToPx(20);
        int leftWall = -dpToPx(15);
        int rightWall = screenWidth - sizePx + dpToPx(15);

        tickCount++;

        // 1. Estado de Caída libre o Gravedad Cero
        if ("FALL".equals(state)) {
            float gravity = zeroGravity ? 0.15f : 1.8f;
            velY += gravity;
            posX += velX;
            posY += velY;

            // Rebotar en paredes laterales
            if (posX < leftWall) {
                posX = leftWall;
                velX = -velX * 0.5f;
                if (!zeroGravity && random.nextFloat() < 0.4f) {
                    state = "CLIMB_LEFT";
                    velY = -dpToPx(2);
                }
            } else if (posX > rightWall) {
                posX = rightWall;
                velX = -velX * 0.5f;
                if (!zeroGravity && random.nextFloat() < 0.4f) {
                    state = "CLIMB_RIGHT";
                    velY = -dpToPx(2);
                }
            }

            // Aterrizaje en el suelo
            if (posY >= floor) {
                posY = floor;
                velY = 0;
                velX *= 0.5f;
                state = "STAND";
                stateTimer = 40 + random.nextInt(60);
                triggerHaptic(10);
            }
        }
        // 2. Caminar por el suelo
        else if ("WALK".equals(state)) {
            posX += velX;
            posY = floor;

            if (posX <= leftWall) {
                posX = leftWall;
                if (random.nextFloat() < 0.35f) {
                    state = "CLIMB_LEFT";
                    velY = -dpToPx(2);
                } else {
                    facing = 1;
                    velX = Math.abs(velX);
                }
            } else if (posX >= rightWall) {
                posX = rightWall;
                if (random.nextFloat() < 0.35f) {
                    state = "CLIMB_RIGHT";
                    velY = -dpToPx(2);
                } else {
                    facing = -1;
                    velX = -Math.abs(velX);
                }
            }

            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }
        // 3. Escalar pared izquierda
        else if ("CLIMB_LEFT".equals(state)) {
            posX = leftWall;
            posY += (velY != 0 ? velY : -dpToPx(2));
            facing = 1;

            if (posY <= ceiling) {
                posY = ceiling;
                state = "FALL";
                velY = 1;
            }
        }
        // 4. Escalar pared derecha
        else if ("CLIMB_RIGHT".equals(state)) {
            posX = rightWall;
            posY += (velY != 0 ? velY : -dpToPx(2));
            facing = -1;

            if (posY <= ceiling) {
                posY = ceiling;
                state = "FALL";
                velY = 1;
            }
        }
        // 5. Estados estáticos (STAND, SIT, GUITAR, BOX)
        else {
            posY = floor;
            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }

        // Diálogos aleatorios espontáneos (1 cada ~25 segundos)
        if (random.nextInt(800) == 42 && tvSpeechBubble.getVisibility() != View.VISIBLE) {
            showRandomSpeech();
        }

        params.x = (int) posX;
        params.y = (int) posY;
        windowManager.updateViewLayout(overlayView, params);

        updateSprite();
    }

    private void pickRandomState() {
        float r = random.nextFloat();
        if (r < 0.40f) {
            state = "WALK";
            facing = random.nextBoolean() ? 1 : -1;
            velX = facing * (dpToPx(1.5f) + random.nextFloat() * dpToPx(1.5f));
            stateTimer = 90 + random.nextInt(120);
        } else if (r < 0.70f) {
            state = "STAND";
            velX = 0;
            stateTimer = 60 + random.nextInt(100);
        } else if (r < 0.85f) {
            state = "SIT";
            velX = 0;
            stateTimer = 80 + random.nextInt(90);
        } else if (r < 0.93f) {
            state = "GUITAR";
            velX = 0;
            stateTimer = 100 + random.nextInt(80);
        } else {
            state = "BOX";
            velX = 0;
            stateTimer = 90 + random.nextInt(80);
        }
    }

    private void updateSprite() {
        String frameName = "stand1";

        if ("FALL".equals(state)) {
            frameName = "fall1";
        } else if ("WALK".equals(state)) {
            String[] walkFrames = {"walk1", "walk2", "walk3", "walk4", "walk5"};
            int idx = (tickCount / 5) % walkFrames.length;
            frameName = walkFrames[idx];
        } else if ("CLIMB_LEFT".equals(state) || "CLIMB_RIGHT".equals(state)) {
            String[] climbFrames = {"climb1", "climb2"};
            int idx = (tickCount / 7) % climbFrames.length;
            frameName = climbFrames[idx];
        } else if ("SIT".equals(state)) {
            frameName = "sit1";
        } else if ("GUITAR".equals(state)) {
            String[] guitarFrames = {"guitar1", "guitar2", "guitar3"};
            int idx = (tickCount / 6) % guitarFrames.length;
            frameName = guitarFrames[idx];
        } else if ("BOX".equals(state)) {
            String[] boxFrames = {"box1", "box2", "box3"};
            int idx = (tickCount / 12) % boxFrames.length;
            frameName = boxFrames[idx];
        } else {
            // STAND
            String[] standFrames = {"stand1", "stand2", "stand1", "stand3"};
            int idx = (tickCount / 12) % standFrames.length;
            frameName = standFrames[idx];
        }

        Bitmap bmp = loadSkinBitmap(currentSkin.folder, frameName, facing);
        if (bmp != null) {
            ivSprite.setImageBitmap(bmp);
        }
    }

    private Bitmap loadSkinBitmap(String skinFolder, String frameName, int dir) {
        String cacheKey = skinFolder + "_" + frameName + "_" + dir;
        if (bitmapCache.containsKey(cacheKey)) {
            return bitmapCache.get(cacheKey);
        }

        try {
            String assetPath = "skins/" + skinFolder + "/" + frameName + ".png";
            InputStream is = getAssets().open(assetPath);
            Bitmap raw = BitmapFactory.decodeStream(is);
            is.close();

            if (raw == null) return null;

            Bitmap finalBmp;
            if (dir == -1) {
                // Voltear horizontalmente
                Matrix matrix = new Matrix();
                matrix.preScale(-1, 1);
                finalBmp = Bitmap.createBitmap(raw, 0, 0, raw.getWidth(), raw.getHeight(), matrix, false);
            } else {
                finalBmp = raw;
            }

            bitmapCache.put(cacheKey, finalBmp);
            return finalBmp;
        } catch (Exception e) {
            // Si falta el frame específico, intentar stand1 de fallback
            if (!"stand1".equals(frameName)) {
                return loadSkinBitmap(skinFolder, "stand1", dir);
            }
            return null;
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && intent.getAction() != null) {
            String action = intent.getAction();

            if (ACTION_STOP.equals(action)) {
                stopSelf();
                return START_NOT_STICKY;
            } else if (ACTION_SET_SKIN.equals(action)) {
                String skinId = intent.getStringExtra(EXTRA_SKIN);
                if (skinId != null) {
                    currentSkin = SkinData.get(skinId);
                    bitmapCache.clear();
                    updateSprite();
                    showRandomSpeech();
                    NotificationManager nm = getSystemService(NotificationManager.class);
                    if (nm != null) nm.notify(NOTIFICATION_ID, buildNotification());
                }
            } else if (ACTION_SET_SIZE.equals(action)) {
                int dp = intent.getIntExtra(EXTRA_SIZE_DP, 128);
                sizePx = dpToPx(dp);
                params.width = sizePx;
                ivSprite.getLayoutParams().width = sizePx;
                ivSprite.getLayoutParams().height = sizePx;
                ivSprite.requestLayout();
                windowManager.updateViewLayout(overlayView, params);
            } else if (ACTION_SET_GRAVITY.equals(action)) {
                zeroGravity = intent.getBooleanExtra(EXTRA_ZERO_GRAVITY, false);
                state = "FALL";
                velY = -dpToPx(4);
            } else if (ACTION_CENTER.equals(action)) {
                updateScreenDimensions();
                posX = screenWidth / 2f - (sizePx / 2f);
                posY = getFloorY();
                params.x = (int) posX;
                params.y = (int) posY;
                state = "STAND";
                velX = 0;
                velY = 0;
                windowManager.updateViewLayout(overlayView, params);
                triggerHaptic(20);
                say("¡Aquí estoy de nuevo! UwU", 2500);
            } else if (ACTION_TRIGGER.equals(action)) {
                String trig = intent.getStringExtra(EXTRA_TRIGGER_ACTION);
                if ("guitar".equals(trig)) {
                    state = "GUITAR";
                    stateTimer = 120;
                    say("¡Solo de guitarra épico! 🎸🎵", 2800);
                } else if ("box".equals(trig)) {
                    state = "BOX";
                    stateTimer = 120;
                    say("Modo caja seguro 📦", 2800);
                } else if ("talk".equals(trig)) {
                    showRandomSpeech();
                }
            }
        }
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        isRunning = false;
        if (handler != null && loopRunnable != null) {
            handler.removeCallbacks(loopRunnable);
        }
        if (overlayView != null && windowManager != null) {
            try {
                windowManager.removeView(overlayView);
            } catch (Exception ignored) {}
        }
        bitmapCache.clear();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private int dpToPx(float dp) {
        float density = getResources().getDisplayMetrics().density;
        return (int) (dp * density + 0.5f);
    }
}
