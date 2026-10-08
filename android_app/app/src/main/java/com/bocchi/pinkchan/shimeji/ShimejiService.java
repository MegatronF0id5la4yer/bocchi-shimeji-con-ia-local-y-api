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
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Vibrator;
import android.util.DisplayMetrics;
import android.view.WindowManager;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
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
    public static final String ACTION_ADD_SHIMEJI = "com.bocchi.pinkchan.shimeji.ADD_SHIMEJI";
    public static final String ACTION_CLEAR_EXTRAS = "com.bocchi.pinkchan.shimeji.CLEAR_EXTRAS";
    public static final String ACTION_START_VOICE = "com.bocchi.pinkchan.shimeji.START_VOICE";

    public static final String EXTRA_SKIN = "extra_skin";
    public static final String EXTRA_SIZE_DP = "extra_size_dp";
    public static final String EXTRA_ZERO_GRAVITY = "extra_zero_gravity";
    public static final String EXTRA_TRIGGER_ACTION = "extra_trigger_action";

    private static final String CHANNEL_ID = "shimeji_overlay_channel";
    private static final int NOTIFICATION_ID = 1001;
    public static final int MAX_SHIMEJIS = 6;

    public static boolean isRunning = false;

    private WindowManager windowManager;
    private Vibrator vibrator;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private Runnable loopRunnable;

    private int screenWidth;
    private int screenHeight;
    private int sizePx;
    private boolean zeroGravity = false;
    private SkinData currentSkin;

    private final List<ShimejiEntity> shimejiList = new ArrayList<>();
    private final Map<String, Bitmap> bitmapCache = new HashMap<>();
    private VoiceAssistantManager voiceAssistantManager;
    private int nextEntityId = 1;
    private final Random random = new Random();

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

        setupVoiceAssistant();

        // Spawn inicial del primer Shimeji centrado
        float startX = screenWidth / 2f - (sizePx / 2f);
        float startY = screenHeight - sizePx - dpToPx(45);
        ShimejiEntity primary = new ShimejiEntity(this, nextEntityId++, currentSkin, startX, startY);
        shimejiList.add(primary);

        startPhysicsLoop();
    }

    private void setupVoiceAssistant() {
        voiceAssistantManager = new VoiceAssistantManager(this, new VoiceAssistantManager.AssistantCallback() {
            @Override
            public void onListeningStarted() {
                if (!shimejiList.isEmpty()) {
                    shimejiList.get(0).say("Escuchando... Di una orden o app.", 3500);
                }
            }

            @Override
            public void onSpeechResult(String recognizedText) {
                if (!shimejiList.isEmpty()) {
                    shimejiList.get(0).say("Tu: " + recognizedText, 2500);
                }
            }

            @Override
            public void onAssistantResponse(String responseText) {
                if (!shimejiList.isEmpty()) {
                    shimejiList.get(0).say(responseText, 3500);
                }
            }

            @Override
            public void onActionTriggered(String actionName) {
                triggerAction(actionName);
            }

            @Override
            public void onAddShimejiRequested() {
                spawnExtraShimeji(null);
            }

            @Override
            public void onClearExtrasRequested() {
                clearExtras();
            }

            @Override
            public void onStopRequested() {
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        stopSelf();
                    }
                }, 1200);
            }
        });
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "PinkChan Shimeji Overlay",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Control de Shimejis en pantalla");
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }

    public void updateNotification() {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) {
            nm.notify(NOTIFICATION_ID, buildNotification());
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

        int count = Math.max(1, shimejiList.size());
        String skinName = (currentSkin != null) ? currentSkin.name : "Konata";
        builder.setContentTitle("PinkChan Shimeji (" + count + " activos)")
            .setContentText("Principal: " + skinName + " | Toca para abrir")
            .setSmallIcon(R.drawable.ic_launcher)
            .setContentIntent(pOpen)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Detener", pStop)
            .setOngoing(true);

        return builder.build();
    }

    private void updateScreenDimensions() {
        DisplayMetrics realMetrics = new DisplayMetrics();
        windowManager.getDefaultDisplay().getRealMetrics(realMetrics);
        screenWidth = realMetrics.widthPixels;
        screenHeight = realMetrics.heightPixels;
    }

    private void startPhysicsLoop() {
        loopRunnable = new Runnable() {
            @Override
            public void run() {
                if (!isRunning) return;

                List<ShimejiEntity> copy = new ArrayList<>(shimejiList);
                for (ShimejiEntity entity : copy) {
                    entity.updatePhysics(screenWidth, screenHeight, zeroGravity);
                }

                handler.postDelayed(this, 40); // 25 FPS
            }
        };
        handler.post(loopRunnable);
    }

    public void spawnExtraShimeji(String skinId) {
        if (shimejiList.size() >= MAX_SHIMEJIS) {
            if (!shimejiList.isEmpty()) {
                shimejiList.get(0).say("Limite maximo: " + MAX_SHIMEJIS + " Shimejis.", 2500);
            }
            return;
        }

        String targetSkinId = skinId;
        if (targetSkinId == null) {
            String lastSkin = shimejiList.isEmpty() ? "Konata" : shimejiList.get(shimejiList.size() - 1).skin.id;
            targetSkinId = SkinData.getNextSkin(lastSkin);
        }
        SkinData skin = SkinData.get(targetSkinId);

        updateScreenDimensions();
        int safeW = Math.max(dpToPx(50), screenWidth - sizePx - dpToPx(30));
        int safeH = Math.max(dpToPx(80), screenHeight - sizePx - dpToPx(120));
        float startX = dpToPx(15) + random.nextInt(safeW);
        float startY = dpToPx(60) + random.nextInt(safeH);

        ShimejiEntity entity = new ShimejiEntity(this, nextEntityId++, skin, startX, startY);
        shimejiList.add(entity);
        updateNotification();
        triggerHaptic(35);
        entity.say("Holi, aqui estoy. Somos " + shimejiList.size() + ".", 2600);
    }

    public void removeShimeji(ShimejiEntity entity) {
        if (entity == null) return;
        entity.destroy();
        shimejiList.remove(entity);
        if (shimejiList.isEmpty()) {
            stopSelf();
        } else {
            updateNotification();
        }
    }

    public void clearExtras() {
        if (shimejiList.size() <= 1) return;
        for (int i = shimejiList.size() - 1; i >= 1; i--) {
            ShimejiEntity entity = shimejiList.remove(i);
            entity.destroy();
        }
        updateNotification();
        if (!shimejiList.isEmpty()) {
            shimejiList.get(0).say("Extras retirados. Queda solo uno.", 2500);
        }
    }

    public void triggerAction(String trig) {
        for (ShimejiEntity entity : shimejiList) {
            if ("guitar".equalsIgnoreCase(trig)) {
                entity.state = "GUITAR";
                entity.stateTimer = 140;
                entity.say("Solo de guitarra.", 2500);
            } else if ("box".equalsIgnoreCase(trig)) {
                entity.state = "BOX";
                entity.stateTimer = 140;
                entity.say("Modo caja seguro.", 2500);
            } else if ("roam".equalsIgnoreCase(trig)) {
                entity.state = "ROAM";
                entity.velY = -dpToPx(3.5f);
                entity.velX = (random.nextBoolean() ? 1 : -1) * dpToPx(2.5f);
                entity.say("Volando por la pantalla.", 2500);
            } else if ("pet".equalsIgnoreCase(trig)) {
                triggerHaptic(40);
                entity.state = "STAND";
                entity.say("Que calido... me agrada.", 2500);
            } else if ("talk".equalsIgnoreCase(trig)) {
                String[] dl = entity.skin.dialogues;
                if (dl.length > 0) {
                    entity.say(dl[random.nextInt(dl.length)], 2800);
                }
            } else if ("cycle_skin".equalsIgnoreCase(trig)) {
                entity.cycleSkin();
            }
        }
    }

    public void startVoiceAssistant() {
        if (voiceAssistantManager != null) {
            voiceAssistantManager.startListening();
        }
    }

    public Bitmap loadSkinBitmap(String skinFolder, String frameName, int dir) {
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
                Matrix matrix = new Matrix();
                matrix.preScale(-1, 1);
                finalBmp = Bitmap.createBitmap(raw, 0, 0, raw.getWidth(), raw.getHeight(), matrix, false);
            } else {
                finalBmp = raw;
            }

            bitmapCache.put(cacheKey, finalBmp);
            return finalBmp;
        } catch (Exception e) {
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
                    if (!shimejiList.isEmpty()) {
                        ShimejiEntity primary = shimejiList.get(0);
                        primary.skin = currentSkin;
                        primary.updateSprite();
                        primary.say("Skin: " + currentSkin.name, 2500);
                    }
                    updateNotification();
                }
            } else if (ACTION_SET_SIZE.equals(action)) {
                int dp = intent.getIntExtra(EXTRA_SIZE_DP, 128);
                sizePx = dpToPx(dp);
                for (ShimejiEntity entity : shimejiList) {
                    entity.updateSize(sizePx);
                }
            } else if (ACTION_SET_GRAVITY.equals(action)) {
                zeroGravity = intent.getBooleanExtra(EXTRA_ZERO_GRAVITY, false);
                for (ShimejiEntity entity : shimejiList) {
                    entity.zeroGravity = zeroGravity;
                    entity.state = "ROAM";
                    entity.velY = -dpToPx(3);
                    entity.velX = (random.nextBoolean() ? 1 : -1) * dpToPx(2);
                }
            } else if (ACTION_CENTER.equals(action)) {
                updateScreenDimensions();
                for (int i = 0; i < shimejiList.size(); i++) {
                    ShimejiEntity entity = shimejiList.get(i);
                    entity.posX = screenWidth / 2f - (sizePx / 2f) + (i * dpToPx(20));
                    entity.posY = screenHeight / 2f - (sizePx / 2f);
                    entity.currentFloorY = entity.posY;
                    entity.params.x = (int) entity.posX;
                    entity.params.y = (int) entity.posY;
                    entity.state = "STAND";
                    entity.velX = 0;
                    entity.velY = 0;
                    windowManager.updateViewLayout(entity.overlayView, entity.params);
                }
                triggerHaptic(20);
                if (!shimejiList.isEmpty()) {
                    shimejiList.get(0).say("Centrados en pantalla.", 2500);
                }
            } else if (ACTION_TRIGGER.equals(action)) {
                String trig = intent.getStringExtra(EXTRA_TRIGGER_ACTION);
                triggerAction(trig);
            } else if (ACTION_ADD_SHIMEJI.equals(action)) {
                String skinId = intent.getStringExtra(EXTRA_SKIN);
                spawnExtraShimeji(skinId);
            } else if (ACTION_CLEAR_EXTRAS.equals(action)) {
                clearExtras();
            } else if (ACTION_START_VOICE.equals(action)) {
                startVoiceAssistant();
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
        if (voiceAssistantManager != null) {
            voiceAssistantManager.destroy();
        }
        for (ShimejiEntity entity : shimejiList) {
            entity.destroy();
        }
        shimejiList.clear();
        bitmapCache.clear();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    public WindowManager getWindowManager() {
        return windowManager;
    }

    public int getSizePx() {
        return sizePx;
    }

    public int getScreenWidth() {
        return screenWidth;
    }

    public int getScreenHeight() {
        return screenHeight;
    }

    public int dpToPx(float dp) {
        float density = getResources().getDisplayMetrics().density;
        return (int) (dp * density + 0.5f);
    }

    public void triggerHaptic(long ms) {
        try {
            if (vibrator != null && vibrator.hasVibrator()) {
                vibrator.vibrate(ms);
            }
        } catch (Exception ignored) {}
    }
}
