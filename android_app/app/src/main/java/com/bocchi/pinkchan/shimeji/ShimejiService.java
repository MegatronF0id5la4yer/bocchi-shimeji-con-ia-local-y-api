package com.bocchi.pinkchan.shimeji;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.graphics.PixelFormat;
import android.media.MediaPlayer;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Vibrator;
import android.util.DisplayMetrics;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.ImageView;

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
    public static final String ACTION_DROP_ITEM = "com.bocchi.pinkchan.shimeji.DROP_ITEM";
    public static final String ACTION_SET_BUBBLE = "com.bocchi.pinkchan.shimeji.SET_BUBBLE";

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

    private static ShimejiService instance;
    private android.speech.tts.TextToSpeech textToSpeech;
    private android.speech.SpeechRecognizer wakeWordRecognizer;
    private boolean isWakeWordListening = false;

    public static ShimejiService getInstance() {
        return instance;
    }

    public FloatingChatManager getFloatingChatManager() {
        return floatingChatManager;
    }

    private final List<ShimejiEntity> shimejiList = new ArrayList<>();
    private final Map<String, Bitmap> bitmapCache = new HashMap<>();
    private VoiceAssistantManager voiceAssistantManager;
    private FloatingChatManager floatingChatManager;
    private int nextEntityId = 1;
    private final Random random = new Random();

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        isRunning = true;
        vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);

        SharedPreferences sp = getSharedPreferences(MainActivity.PREFS_NAME, MODE_PRIVATE);
        String savedSkin = sp.getString(MainActivity.KEY_SKIN, "Konata");
        currentSkin = SkinData.get(savedSkin);
        int savedSize = sp.getInt(MainActivity.KEY_SIZE, 128);
        sizePx = dpToPx(savedSize);
        zeroGravity = sp.getBoolean(MainActivity.KEY_ZERO_G, false);

        updateScreenDimensions();
        createNotificationChannel();
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIFICATION_ID, buildNotification(),
                android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE |
                android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE);
        } else if (Build.VERSION.SDK_INT >= 29) {
            startForeground(NOTIFICATION_ID, buildNotification(),
                android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        } else {
            startForeground(NOTIFICATION_ID, buildNotification());
        }

        initTts();
        syncWakeWordState();
        setupVoiceAssistant();

        // Spawn inicial del primer Shimeji centrado
        float startX = screenWidth / 2f - (sizePx / 2f);
        float startY = screenHeight - sizePx - dpToPx(45);
        ShimejiEntity primary = new ShimejiEntity(this, nextEntityId++, currentSkin, startX, startY);
        shimejiList.add(primary);
        playPopueSound();

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
        playPopueSound();
        updateNotification();
        triggerHaptic(35);
        entity.say("Holi, aqui estoy. Somos " + shimejiList.size() + ".", 2600);
    }

    public void removeShimeji(ShimejiEntity entity) {
        if (entity == null) return;
        playPopueSound();
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
        playPopueSound();
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
        if ("termux".equalsIgnoreCase(trig)) {
            openTermux();
            return;
        } else if ("create_file".equalsIgnoreCase(trig) || "files".equalsIgnoreCase(trig)) {
            createFilesAndFolder();
            return;
        } else if ("drop_item".equalsIgnoreCase(trig) || "item".equalsIgnoreCase(trig)) {
            dropRandomItem();
            return;
        } else if (trig != null && trig.startsWith("speech:")) {
            String text = trig.substring(7);
            if (!shimejiList.isEmpty()) {
                shimejiList.get(0).say(text, 3500);
            }
            return;
        }

        for (ShimejiEntity entity : shimejiList) {
            if ("guitar".equalsIgnoreCase(trig)) {
                entity.state = "GUITAR";
                entity.stateTimer = 140;
                entity.say("Solo de guitarra.", 2500);
            } else if ("box".equalsIgnoreCase(trig)) {
                entity.state = "BOX";
                entity.stateTimer = 140;
                entity.say("Modo caja seguro.", 2500);
            } else if ("dance".equalsIgnoreCase(trig)) {
                entity.state = "DANCE";
                entity.stateTimer = 130;
                entity.say("Bailando! Sigue el ritmo!", 2600);
                triggerHaptic(30);
            } else if ("roll".equalsIgnoreCase(trig)) {
                entity.state = "ROLL";
                entity.stateTimer = 110;
                entity.velX = (entity.facing != 0 ? entity.facing : 1) * dpToPx(5f);
                entity.say("Rodando por la pantalla!", 2500);
                triggerHaptic(30);
            } else if ("jump".equalsIgnoreCase(trig)) {
                entity.state = "JUMP";
                entity.velY = -dpToPx(7f);
                entity.say("Salto acrobatico! Boing!", 2400);
                triggerHaptic(35);
            } else if ("play".equalsIgnoreCase(trig)) {
                int game = random.nextInt(3);
                triggerHaptic(40);
                if (game == 0) {
                    entity.state = "DANCE";
                    entity.stateTimer = 130;
                    entity.say("A bailar juntos!", 2500);
                } else if (game == 1) {
                    entity.state = "ROLL";
                    entity.stateTimer = 110;
                    entity.velX = (random.nextBoolean() ? 1 : -1) * dpToPx(4.5f);
                    entity.say("Atrapame si puedes!", 2500);
                } else {
                    entity.state = "JUMP";
                    entity.velY = -dpToPx(7.5f);
                    entity.say("A jugar al salto alto!", 2500);
                }
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

    public void openTermux() {
        try {
            android.content.pm.PackageManager pm = getPackageManager();
            Intent launch = pm.getLaunchIntentForPackage("com.termux");
            if (launch != null) {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(launch);
                triggerHaptic(40);
                if (!shimejiList.isEmpty()) {
                    shimejiList.get(0).say("Termux iniciado con exito.", 2800);
                }
            } else {
                if (!shimejiList.isEmpty()) {
                    shimejiList.get(0).say("Termux no instalado (com.termux).", 3000);
                }
            }
        } catch (Exception e) {
            if (!shimejiList.isEmpty()) {
                shimejiList.get(0).say("Error al lanzar Termux.", 2500);
            }
        }
    }

    public void createFilesAndFolder() {
        try {
            java.io.File dir = new java.io.File(android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOCUMENTS), "Shijima");
            if (!dir.exists()) {
                dir.mkdirs();
            }
            java.io.File file = new java.io.File(dir, "shijima_quick_notes.txt");
            java.io.FileWriter writer = new java.io.FileWriter(file, false);
            writer.write("# Shijima Companion - Notas y Comandos Termux\n");
            writer.write("Generado: " + new java.util.Date() + "\n\n");
            writer.write("Comandos utiles para Termux:\n");
            writer.write("1. pkg update && pkg upgrade\n");
            writer.write("2. pkg install python git curl neofetch clang\n");
            writer.write("3. termux-setup-storage\n");
            writer.write("4. ls -la ~/storage/shared/Documents/Shijima/\n");
            writer.close();

            // Guardar tambien copia interna de respaldo
            java.io.File localDir = new java.io.File(getExternalFilesDir(null), "Shijima");
            if (!localDir.exists()) localDir.mkdirs();
            java.io.File localFile = new java.io.File(localDir, "shijima_quick_notes.txt");
            java.io.FileWriter localWriter = new java.io.FileWriter(localFile, false);
            localWriter.write("Notas creadas correctamente.\n");
            localWriter.close();

            triggerHaptic(50);
            if (!shimejiList.isEmpty()) {
                shimejiList.get(0).say("Archivo y carpeta creados en Documents/Shijima!", 3200);
            }
        } catch (Exception e) {
            if (!shimejiList.isEmpty()) {
                shimejiList.get(0).say("Guardado en almacenamiento de la app.", 2800);
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
            BitmapFactory.Options opts = new BitmapFactory.Options();
            opts.inPreferredConfig = Bitmap.Config.ARGB_8888;
            opts.inDither = true;
            Bitmap raw = BitmapFactory.decodeStream(is, null, opts);
            is.close();

            if (raw == null) return null;

            Bitmap finalBmp;
            if (dir == -1) {
                Matrix matrix = new Matrix();
                matrix.preScale(-1, 1);
                finalBmp = Bitmap.createBitmap(raw, 0, 0, raw.getWidth(), raw.getHeight(), matrix, true);
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
            } else if (ACTION_START.equals(action) || ACTION_SET_SKIN.equals(action)) {
                String skinId = intent.getStringExtra(EXTRA_SKIN);
                if (skinId != null) {
                    currentSkin = SkinData.get(skinId);
                    getSharedPreferences(MainActivity.PREFS_NAME, MODE_PRIVATE)
                        .edit().putString(MainActivity.KEY_SKIN, skinId).apply();

                    if (!shimejiList.isEmpty()) {
                        ShimejiEntity primary = shimejiList.get(0);
                        primary.setSkin(currentSkin);
                    } else {
                        float startX = screenWidth / 2f - (sizePx / 2f);
                        float startY = screenHeight - sizePx - dpToPx(45);
                        ShimejiEntity primary = new ShimejiEntity(this, nextEntityId++, currentSkin, startX, startY);
                        shimejiList.add(primary);
                    }
                    updateNotification();
                }
                int dp = intent.getIntExtra(EXTRA_SIZE_DP, 0);
                if (dp > 0) {
                    sizePx = dpToPx(dp);
                    for (ShimejiEntity entity : shimejiList) {
                        entity.updateSize(sizePx);
                    }
                }
                if (intent.hasExtra(EXTRA_ZERO_GRAVITY)) {
                    zeroGravity = intent.getBooleanExtra(EXTRA_ZERO_GRAVITY, false);
                    for (ShimejiEntity entity : shimejiList) {
                        entity.zeroGravity = zeroGravity;
                    }
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
            } else if (ACTION_DROP_ITEM.equals(action)) {
                dropRandomItem();
            } else if (ACTION_SET_BUBBLE.equals(action)) {
                for (ShimejiEntity entity : shimejiList) {
                    entity.applyBubbleStyle();
                }
            }
        }
        return START_STICKY;
    }

    public ShimejiEntity getPrimaryShimeji() {
        if (!shimejiList.isEmpty()) {
            return shimejiList.get(0);
        }
        return null;
    }

    public void showFloatingChat() {
        handler.post(new Runnable() {
            @Override
            public void run() {
                if (floatingChatManager == null) {
                    floatingChatManager = new FloatingChatManager(ShimejiService.this);
                }
                floatingChatManager.show();
            }
        });
    }

    public void hideFloatingChat() {
        handler.post(new Runnable() {
            @Override
            public void run() {
                if (floatingChatManager != null) {
                    floatingChatManager.hide();
                }
            }
        });
    }

    public void openChat() {
        showFloatingChat();
    }

    @Override
    public void onDestroy() {
        playPopueSound();
        isRunning = false;
        if (instance == this) {
            instance = null;
        }
        if (textToSpeech != null) {
            try {
                textToSpeech.shutdown();
            } catch (Exception ignored) {}
            textToSpeech = null;
        }
        stopWakeWordListener();
        if (handler != null && loopRunnable != null) {
            handler.removeCallbacks(loopRunnable);
        }
        if (floatingChatManager != null) {
            floatingChatManager.destroy();
            floatingChatManager = null;
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

    public void initTts() {
        if (textToSpeech == null) {
            textToSpeech = new android.speech.tts.TextToSpeech(getApplicationContext(), new android.speech.tts.TextToSpeech.OnInitListener() {
                @Override
                public void onInit(int status) {
                    if (status == android.speech.tts.TextToSpeech.SUCCESS && textToSpeech != null) {
                        applyTtsSettings();
                    }
                }
            });
        }
    }

    public void applyTtsSettings() {
        if (textToSpeech == null) return;
        SharedPreferences sp = getSharedPreferences(MainActivity.PREFS_NAME, MODE_PRIVATE);
        float rate = sp.getFloat("tts_rate", 1.0f);
        float pitch = sp.getFloat("tts_pitch", 1.0f);
        textToSpeech.setSpeechRate(rate);
        textToSpeech.setPitch(pitch);
        textToSpeech.setLanguage(new java.util.Locale("es", "ES"));
    }

    public void syncTtsSettings() {
        applyTtsSettings();
    }

    public Handler getHandler() {
        return handler;
    }

    public void switchSkin(String skinId) {
        SkinData skin = SkinData.get(skinId);
        if (skin != null) {
            currentSkin = skin;
            if (!shimejiList.isEmpty()) {
                shimejiList.get(0).setSkin(skin);
            }
        }
    }

    public void speakTts(String text) {
        SharedPreferences sp = getSharedPreferences(MainActivity.PREFS_NAME, MODE_PRIVATE);
        if (!sp.getBoolean("tts_enabled", false)) return;
        if (text == null || text.trim().isEmpty()) return;
        String clean = AgentToolExecutor.stripTags(text);
        if (textToSpeech != null) {
            textToSpeech.speak(clean, android.speech.tts.TextToSpeech.QUEUE_FLUSH, null, "shimeji_tts");
        } else {
            initTts();
        }
    }

    public void syncWakeWordState() {
        SharedPreferences sp = getSharedPreferences(MainActivity.PREFS_NAME, MODE_PRIVATE);
        boolean enabled = sp.getBoolean("wake_word_enabled", false);
        if (enabled) {
            startWakeWordListener();
        } else {
            stopWakeWordListener();
        }
    }

    public void startWakeWordListener() {
        if (isWakeWordListening) return;
        handler.post(new Runnable() {
            @Override
            public void run() {
                if (!android.speech.SpeechRecognizer.isRecognitionAvailable(ShimejiService.this)) return;
                try {
                    if (wakeWordRecognizer == null) {
                        wakeWordRecognizer = android.speech.SpeechRecognizer.createSpeechRecognizer(ShimejiService.this);
                    }
                    isWakeWordListening = true;
                    android.content.Intent intent = new android.content.Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                    intent.putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                    intent.putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE, "es-ES");
                    intent.putExtra(android.speech.RecognizerIntent.EXTRA_MAX_RESULTS, 1);
                    intent.putExtra("android.speech.extra.PREFER_OFFLINE", true);

                    wakeWordRecognizer.setRecognitionListener(new android.speech.RecognitionListener() {
                        @Override public void onReadyForSpeech(android.os.Bundle params) {}
                        @Override public void onBeginningOfSpeech() {}
                        @Override public void onRmsChanged(float rmsdB) {}
                        @Override public void onBufferReceived(byte[] buffer) {}
                        @Override public void onEndOfSpeech() {}
                        @Override
                        public void onError(int error) {
                            if (isWakeWordListening) {
                                handler.postDelayed(new Runnable() {
                                    @Override public void run() {
                                        if (isWakeWordListening) startWakeWordListener();
                                    }
                                }, 1500);
                            }
                        }
                        @Override
                        public void onResults(android.os.Bundle results) {
                            if (results != null) {
                                ArrayList<String> matches = results.getStringArrayList(android.speech.SpeechRecognizer.RESULTS_RECOGNITION);
                                if (matches != null && !matches.isEmpty()) {
                                    handleWakeWordSpoken(matches.get(0));
                                }
                            }
                            if (isWakeWordListening) {
                                handler.postDelayed(new Runnable() {
                                    @Override public void run() {
                                        if (isWakeWordListening) startWakeWordListener();
                                    }
                                }, 1000);
                            }
                        }
                        @Override public void onPartialResults(android.os.Bundle partialResults) {}
                        @Override public void onEvent(int eventType, android.os.Bundle params) {}
                    });
                    wakeWordRecognizer.startListening(intent);
                } catch (Exception e) {
                    isWakeWordListening = false;
                }
            }
        });
    }

    public void stopWakeWordListener() {
        isWakeWordListening = false;
        if (wakeWordRecognizer != null) {
            try {
                wakeWordRecognizer.stopListening();
                wakeWordRecognizer.cancel();
                wakeWordRecognizer.destroy();
            } catch (Exception ignored) {}
            wakeWordRecognizer = null;
        }
    }

    private void handleWakeWordSpoken(String raw) {
        if (raw == null) return;
        SharedPreferences sp = getSharedPreferences(MainActivity.PREFS_NAME, MODE_PRIVATE);
        String wakeWord = sp.getString("wake_word_phrase", "oye jarvis").toLowerCase().trim();
        String lower = raw.toLowerCase().trim();
        if (lower.contains(wakeWord)) {
            ShimejiEntity entity = getPrimaryShimeji();
            if (entity != null) entity.say("Te escucho", 5000);
            speakTts("Te escucho");

            int idx = lower.indexOf(wakeWord);
            String command = raw.substring(idx + wakeWord.length()).trim();
            if (!command.isEmpty()) {
                showFloatingChat();
                if (entity != null) {
                    AiEngineHelper.askAi(this, entity.skin.id, command, new AiEngineHelper.AiCallback() {
                        @Override
                        public void onSuccess(String reply) {
                            ShimejiEntity ent = getPrimaryShimeji();
                            if (ent != null) ent.say(reply, 8000);
                            speakTts(reply);
                        }
                        @Override
                        public void onError(String errorMsg) {
                            ShimejiEntity ent = getPrimaryShimeji();
                            if (ent != null) ent.say("[!] " + errorMsg, 5000);
                        }
                    });
                }
            }
        }
    }

    public void playPopueSound() {
        try {
            MediaPlayer mp = MediaPlayer.create(this, R.raw.popue);
            if (mp != null) {
                mp.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
                    @Override
                    public void onCompletion(MediaPlayer mediaPlayer) {
                        try {
                            mediaPlayer.release();
                        } catch (Exception ignored) {}
                    }
                });
                mp.start();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void dropRandomItem() {
        try {
            updateScreenDimensions();
            String[] itemFiles = getAssets().list("items");
            if (itemFiles == null || itemFiles.length == 0) return;

            String chosen = itemFiles[random.nextInt(itemFiles.length)];
            final boolean isBomb;
            boolean tempBomb = false;
            try {
                String clean = chosen.replace(".png", "");
                String[] parts = clean.split("_");
                int row = Integer.parseInt(parts[1]);
                tempBomb = (row >= 3);
            } catch (Exception e) {
                tempBomb = false;
            }
            isBomb = tempBomb;

            InputStream is = getAssets().open("items/" + chosen);
            Bitmap bmp = BitmapFactory.decodeStream(is);
            is.close();
            if (bmp == null) return;

            final int itemSize = dpToPx(52);
            final ImageView itemIv = new ImageView(this);
            itemIv.setImageBitmap(bmp);
            itemIv.setScaleType(ImageView.ScaleType.FIT_CENTER);

            final WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                itemSize, itemSize,
                Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                    ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                    : WindowManager.LayoutParams.TYPE_PHONE,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
                PixelFormat.TRANSLUCENT
            );
            params.gravity = Gravity.TOP | Gravity.LEFT;
            final int startX = dpToPx(20) + random.nextInt(Math.max(10, screenWidth - itemSize - dpToPx(40)));
            params.x = startX;
            params.y = dpToPx(30);

            windowManager.addView(itemIv, params);
            playPopueSound();

            final float floorY = screenHeight - itemSize - dpToPx(50);
            final float[] state = new float[]{params.y, 0f, 0f}; // [y, vy, bounces]

            final Runnable itemPhysics = new Runnable() {
                @Override
                public void run() {
                    if (!isRunning) {
                        try { windowManager.removeView(itemIv); } catch (Exception ignored) {}
                        return;
                    }
                    state[1] += dpToPx(1.8f);
                    state[0] += state[1];

                    if (state[0] >= floorY) {
                        state[0] = floorY;
                        if (state[2] < 2) {
                            state[1] = -state[1] * 0.4f;
                            state[2] += 1;
                        } else {
                            state[1] = 0;
                        }
                    }

                    params.y = (int) state[0];
                    try {
                        windowManager.updateViewLayout(itemIv, params);
                    } catch (Exception ignored) {
                        return;
                    }

                    for (ShimejiEntity entity : shimejiList) {
                        float dist = Math.abs((entity.posX + sizePx / 2f) - (startX + itemSize / 2f));
                        float yDist = Math.abs((entity.posY + sizePx / 2f) - (state[0] + itemSize / 2f));

                        if (dist < dpToPx(75) && yDist < dpToPx(85)) {
                            playPopueSound();
                            try { windowManager.removeView(itemIv); } catch (Exception ignored) {}

                            if (isBomb) {
                                entity.velY = -dpToPx(16);
                                entity.takeDamage(35);
                            } else {
                                entity.state = "SIT";
                                entity.heal(30, "snack delicioso");
                            }
                            return;
                        }
                    }

                    if (state[1] != 0 || state[2] < 3) {
                        handler.postDelayed(this, 25);
                    } else {
                        handler.postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                try { windowManager.removeView(itemIv); } catch (Exception ignored) {}
                            }
                        }, 6000);
                    }
                }
            };
            handler.postDelayed(itemPhysics, 25);
        } catch (Exception e) {
            e.printStackTrace();
        }
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
