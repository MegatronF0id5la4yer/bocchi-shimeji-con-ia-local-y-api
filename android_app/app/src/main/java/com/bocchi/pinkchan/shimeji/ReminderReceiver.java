package com.bocchi.pinkchan.shimeji;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.speech.tts.TextToSpeech;
import java.util.Locale;

public class ReminderReceiver extends BroadcastReceiver {

    public static final String CHANNEL_ID = "jarvis_reminders_channel";
    private static TextToSpeech reminderTts;

    @Override
    public void onReceive(final Context context, Intent intent) {
        final String text = intent != null && intent.getStringExtra("text") != null
            ? intent.getStringExtra("text")
            : "Recordatorio programado de JARVIS";

        createNotificationChannel(context);

        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(context, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(context);
        }

        builder.setContentTitle("Recordatorio de JARVIS")
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_launcher)
            .setAutoCancel(true);

        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) {
            nm.notify((int) System.currentTimeMillis(), builder.build());
        }

        // Si el servicio de Shimeji está activo, hacer que hable en pantalla
        ShimejiService service = ShimejiService.getInstance();
        if (service != null) {
            ShimejiEntity entity = service.getPrimaryShimeji();
            if (entity != null) {
                entity.say("Recordatorio: " + text, 12000);
            }
            service.triggerHaptic(60);
        }

        // Sintetizar voz TTS
        boolean ttsEnabled = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE)
            .getBoolean("tts_enabled", false);
        if (ttsEnabled) {
            try {
                if (reminderTts == null) {
                    reminderTts = new TextToSpeech(context.getApplicationContext(), new TextToSpeech.OnInitListener() {
                        @Override
                        public void onInit(int status) {
                            if (status == TextToSpeech.SUCCESS && reminderTts != null) {
                                reminderTts.setLanguage(new Locale("es", "ES"));
                                reminderTts.speak("Atención, recordatorio: " + text, TextToSpeech.QUEUE_FLUSH, null, "reminder_tts");
                            }
                        }
                    });
                } else {
                    reminderTts.speak("Atención, recordatorio: " + text, TextToSpeech.QUEUE_FLUSH, null, "reminder_tts");
                }
            } catch (Exception ignored) {
            }
        }
    }

    private void createNotificationChannel(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm != null && nm.getNotificationChannel(CHANNEL_ID) == null) {
                NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Recordatorios JARVIS",
                    NotificationManager.IMPORTANCE_HIGH
                );
                channel.setDescription("Notificaciones de recordatorios y alarmas de JARVIS");
                channel.enableVibration(true);
                nm.createNotificationChannel(channel);
            }
        }
    }
}
