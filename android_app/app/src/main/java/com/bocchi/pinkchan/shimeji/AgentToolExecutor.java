package com.bocchi.pinkchan.shimeji;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.hardware.camera2.CameraManager;
import android.media.AudioManager;
import android.net.Uri;
import android.os.Build;
import android.provider.AlarmClock;
import android.provider.Settings;
import android.view.KeyEvent;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AgentToolExecutor {

    public static final String PREF_REMINDERS = "agent_reminders_list";
    public static final String PREF_MACROS = "agent_macros_list";

    private static final Pattern TAG_PATTERN = Pattern.compile("\\[JARVIS:\\s*([A-Z_]+)(?:\\s+(.*?))?\\]", Pattern.DOTALL);

    // ==========================================
    // 1. GESTION DE PERMISOS
    // ==========================================
    public static boolean checkPermission(Context context, String category) {
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        switch (category.toLowerCase()) {
            case "apps":
            case "url":
                return sp.getBoolean("perm_apps", true);
            case "system":
            case "volume":
            case "media":
            case "brightness":
            case "flashlight":
            case "lock":
            case "screenshot":
                return sp.getBoolean("perm_system", true);
            case "reminders":
            case "timer":
            case "alarm":
                return sp.getBoolean("perm_reminders", true);
            case "files_write":
            case "files_create":
                return sp.getBoolean("perm_files_write", true);
            case "files_delete":
                return sp.getBoolean("perm_files_delete", false); // Requiere confirmación por defecto
            case "shell":
            case "cmd":
                return sp.getBoolean("perm_shell", false); // Requiere confirmación por defecto
            default:
                return true;
        }
    }

    // ==========================================
    // 2. HERRAMIENTAS DEL SISTEMA ANDROID
    // ==========================================

    public static String openApp(Context context, String appQuery) {
        if (!checkPermission(context, "apps")) {
            return "[!] Permiso denegado por el usuario para abrir aplicaciones";
        }
        if (appQuery == null || appQuery.trim().isEmpty()) {
            return "[!] Nombre de aplicacion no especificado";
        }
        String cleanQuery = normalizeString(appQuery.replace("\"", "").trim());
        PackageManager pm = context.getPackageManager();
        Intent intent = new Intent(Intent.ACTION_MAIN, null);
        intent.addCategory(Intent.CATEGORY_LAUNCHER);

        List<ResolveInfo> list = pm.queryIntentActivities(intent, 0);
        String bestPackage = null;
        String bestLabel = null;

        for (ResolveInfo info : list) {
            String label = normalizeString(info.loadLabel(pm).toString());
            String pkg = info.activityInfo.packageName.toLowerCase();

            if (label.equals(cleanQuery) || pkg.endsWith("." + cleanQuery)) {
                bestPackage = info.activityInfo.packageName;
                bestLabel = info.loadLabel(pm).toString();
                break;
            } else if (label.startsWith(cleanQuery)) {
                bestPackage = info.activityInfo.packageName;
                bestLabel = info.loadLabel(pm).toString();
            } else if (bestPackage == null && (label.contains(cleanQuery) || pkg.contains(cleanQuery))) {
                bestPackage = info.activityInfo.packageName;
                bestLabel = info.loadLabel(pm).toString();
            }
        }

        if (bestPackage != null) {
            Intent launchIntent = pm.getLaunchIntentForPackage(bestPackage);
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(launchIntent);
                return "[+] Aplicacion abierta: " + bestLabel;
            }
        }
        return "[!] No se encontro la aplicacion: " + appQuery;
    }

    public static String setVolume(Context context, String level) {
        if (!checkPermission(context, "system")) {
            return "[!] Permiso denegado para modificar volumen";
        }
        AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
        if (am == null) return "[!] AudioManager no disponible";

        int max = am.getStreamMaxVolume(AudioManager.STREAM_MUSIC);
        String arg = level.trim().toLowerCase();

        if (arg.equals("up") || arg.contains("sube")) {
            am.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_RAISE, AudioManager.FLAG_SHOW_UI);
            return "[+] Volumen aumentado";
        } else if (arg.equals("down") || arg.contains("baja")) {
            am.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_LOWER, AudioManager.FLAG_SHOW_UI);
            return "[+] Volumen reducido";
        } else if (arg.equals("mute") || arg.contains("silencio")) {
            am.setStreamVolume(AudioManager.STREAM_MUSIC, 0, AudioManager.FLAG_SHOW_UI);
            return "[+] Audio silenciado";
        } else {
            try {
                int pct = Integer.parseInt(arg.replaceAll("[^0-9]", ""));
                pct = Math.max(0, Math.min(100, pct));
                int target = (pct * max) / 100;
                am.setStreamVolume(AudioManager.STREAM_MUSIC, target, AudioManager.FLAG_SHOW_UI);
                return "[+] Volumen establecido en " + pct + "%";
            } catch (Exception e) {
                return "[!] Formato de volumen no valido (usa up, down, mute o 0-100)";
            }
        }
    }

    public static String mediaControl(Context context, String action) {
        if (!checkPermission(context, "system")) {
            return "[!] Permiso denegado para control de medios";
        }
        AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
        if (am == null) return "[!] AudioManager no disponible";

        String act = action.trim().toLowerCase();
        int keyCode = KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE;
        String desc = "Reproduccion alternada";

        if (act.contains("next") || act.contains("siguiente")) {
            keyCode = KeyEvent.KEYCODE_MEDIA_NEXT;
            desc = "Pista siguiente";
        } else if (act.contains("prev") || act.contains("anterior")) {
            keyCode = KeyEvent.KEYCODE_MEDIA_PREVIOUS;
            desc = "Pista anterior";
        } else if (act.contains("stop") || act.contains("deten")) {
            keyCode = KeyEvent.KEYCODE_MEDIA_STOP;
            desc = "Reproduccion detenida";
        }

        am.dispatchMediaKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN, keyCode));
        am.dispatchMediaKeyEvent(new KeyEvent(KeyEvent.ACTION_UP, keyCode));
        return "[+] " + desc;
    }

    public static String setBrightness(Context context, int percent) {
        if (!checkPermission(context, "system")) {
            return "[!] Permiso denegado para modificar brillo";
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.System.canWrite(context)) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS);
                intent.setData(Uri.parse("package:" + context.getPackageName()));
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(intent);
                return "[!] Concede el permiso de modificar ajustes del sistema que se abrio en pantalla";
            }
        }
        try {
            int val = Math.max(1, Math.min(255, (percent * 255) / 100));
            Settings.System.putInt(context.getContentResolver(), Settings.System.SCREEN_BRIGHTNESS, val);
            return "[+] Brillo establecido al " + percent + "%";
        } catch (Exception e) {
            return "[!] Error al cambiar brillo: " + e.getMessage();
        }
    }

    public static String toggleFlashlight(Context context, boolean enable) {
        if (!checkPermission(context, "system")) {
            return "[!] Permiso denegado para linterna";
        }
        CameraManager cm = (CameraManager) context.getSystemService(Context.CAMERA_SERVICE);
        if (cm == null) return "[!] CameraManager no disponible";

        try {
            String[] ids = cm.getCameraIdList();
            for (String id : ids) {
                try {
                    cm.setTorchMode(id, enable);
                    return enable ? "[+] Linterna encendida" : "[+] Linterna apagada";
                } catch (Exception ignored) {
                }
            }
            return "[!] No se encontro flash en las camaras";
        } catch (Exception e) {
            return "[!] Error al alternar linterna: " + e.getMessage();
        }
    }

    public static String openWifiSettings(Context context) {
        try {
            Intent intent;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                intent = new Intent(Settings.Panel.ACTION_WIFI);
            } else {
                intent = new Intent(Settings.ACTION_WIFI_SETTINGS);
            }
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "[+] Panel de configuracion Wi-Fi abierto";
        } catch (Exception e) {
            return "[!] Error abriendo Wi-Fi: " + e.getMessage();
        }
    }

    public static String openBluetoothSettings(Context context) {
        try {
            Intent intent = new Intent(Settings.ACTION_BLUETOOTH_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "[+] Ajustes de Bluetooth abiertos";
        } catch (Exception e) {
            return "[!] Error abriendo Bluetooth: " + e.getMessage();
        }
    }

    public static String takeScreenshot(Context context) {
        if (!JarvisAccessibilityService.isAvailable()) {
            openAccessibilitySettings(context);
            return "[!] Servicio de accesibilidad JARVIS no activado. Activalo en el menu que aparecio";
        }
        boolean ok = JarvisAccessibilityService.takeScreenshot();
        return ok ? "[+] Captura de pantalla tomada" : "[!] No se pudo tomar la captura (requiere Android 9+)";
    }

    public static String lockScreen(Context context) {
        if (!JarvisAccessibilityService.isAvailable()) {
            openAccessibilitySettings(context);
            return "[!] Servicio de accesibilidad JARVIS no activado. Activalo en el menu que aparecio";
        }
        boolean ok = JarvisAccessibilityService.lockScreen();
        return ok ? "[+] Pantalla bloqueada" : "[!] No se pudo bloquear la pantalla (requiere Android 9+)";
    }

    public static void openAccessibilitySettings(Context context) {
        try {
            Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
        } catch (Exception ignored) {
        }
    }

    // ==========================================
    // 3. TEMPORIZADORES, ALARMAS Y RECORDATORIOS
    // ==========================================

    public static String setTimer(Context context, int minutes, String message) {
        if (!checkPermission(context, "reminders")) {
            return "[!] Permiso denegado para temporizadores";
        }
        try {
            Intent intent = new Intent(AlarmClock.ACTION_SET_TIMER)
                .putExtra(AlarmClock.EXTRA_LENGTH, minutes * 60)
                .putExtra(AlarmClock.EXTRA_MESSAGE, message != null ? message : "Temporizador JARVIS")
                .putExtra(AlarmClock.EXTRA_SKIP_UI, true)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "[+] Temporizador de " + minutes + " minutos configurado";
        } catch (Exception e) {
            return "[!] Error al configurar temporizador: " + e.getMessage();
        }
    }

    public static String setAlarm(Context context, int hour, int minute, String message) {
        if (!checkPermission(context, "reminders")) {
            return "[!] Permiso denegado para alarmas";
        }
        try {
            Intent intent = new Intent(AlarmClock.ACTION_SET_ALARM)
                .putExtra(AlarmClock.EXTRA_HOUR, hour)
                .putExtra(AlarmClock.EXTRA_MINUTES, minute)
                .putExtra(AlarmClock.EXTRA_MESSAGE, message != null ? message : "Alarma JARVIS")
                .putExtra(AlarmClock.EXTRA_SKIP_UI, true)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            String minStr = minute < 10 ? "0" + minute : String.valueOf(minute);
            return "[+] Alarma configurada para las " + hour + ":" + minStr;
        } catch (Exception e) {
            return "[!] Error al configurar alarma: " + e.getMessage();
        }
    }

    public static String addReminder(Context context, long delayMillis, String text) {
        if (!checkPermission(context, "reminders")) {
            return "[!] Permiso denegado para recordatorios";
        }
        AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return "[!] AlarmManager no disponible";

        long triggerAt = System.currentTimeMillis() + delayMillis;
        int reqCode = (int) (triggerAt % 1000000);

        Intent intent = new Intent(context, ReminderReceiver.class);
        intent.putExtra("text", text);
        PendingIntent pi = PendingIntent.getBroadcast(
            context,
            reqCode,
            intent,
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT : PendingIntent.FLAG_UPDATE_CURRENT
        );

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAt, pi);
        } else {
            am.setExact(AlarmManager.RTC_WAKEUP, triggerAt, pi);
        }

        // Guardar recordatorio persistente
        saveReminderEntry(context, reqCode, triggerAt, text);
        long mins = delayMillis / 60000;
        return "[+] Recordatorio guardado para dentro de " + (mins > 0 ? mins + " min" : (delayMillis / 1000) + " seg") + ": \"" + text + "\"";
    }

    public static String listReminders(Context context) {
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        String raw = sp.getString(PREF_REMINDERS, "[]");
        try {
            JSONArray arr = new JSONArray(raw);
            if (arr.length() == 0) return "[i] No hay recordatorios activos programados";
            StringBuilder sb = new StringBuilder("[RECORDATORIOS ACTIVOS]:\n");
            long now = System.currentTimeMillis();
            for (int i = 0; i < arr.length(); i++) {
                JSONObject obj = arr.getJSONObject(i);
                long trig = obj.optLong("trigger", 0);
                long diff = (trig - now) / 60000;
                sb.append("  ").append(i + 1).append(". \"").append(obj.optString("text")).append("\" (en ")
                    .append(diff > 0 ? diff + " min" : "pocos segundos").append(")\n");
            }
            return sb.toString().trim();
        } catch (Exception e) {
            return "[!] Error leyendo recordatorios: " + e.getMessage();
        }
    }

    public static String cancelReminder(Context context, int index) {
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        String raw = sp.getString(PREF_REMINDERS, "[]");
        try {
            JSONArray arr = new JSONArray(raw);
            if (index < 1 || index > arr.length()) return "[!] Indice de recordatorio no valido";

            JSONObject target = arr.getJSONObject(index - 1);
            int reqCode = target.optInt("code", 0);

            AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
            if (am != null && reqCode != 0) {
                Intent intent = new Intent(context, ReminderReceiver.class);
                PendingIntent pi = PendingIntent.getBroadcast(
                    context, reqCode, intent,
                    Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0
                );
                am.cancel(pi);
            }

            JSONArray newArr = new JSONArray();
            for (int i = 0; i < arr.length(); i++) {
                if (i != (index - 1)) newArr.put(arr.get(i));
            }
            sp.edit().putString(PREF_REMINDERS, newArr.toString()).apply();
            return "[+] Recordatorio #" + index + " cancelado";
        } catch (Exception e) {
            return "[!] Error cancelando recordatorio: " + e.getMessage();
        }
    }

    private static void saveReminderEntry(Context context, int code, long trigger, String text) {
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        String raw = sp.getString(PREF_REMINDERS, "[]");
        try {
            JSONArray arr = new JSONArray(raw);
            JSONObject obj = new JSONObject();
            obj.put("code", code);
            obj.put("trigger", trigger);
            obj.put("text", text);
            arr.put(obj);
            sp.edit().putString(PREF_REMINDERS, arr.toString()).apply();
        } catch (Exception ignored) {
        }
    }

    // ==========================================
    // 4. OPERACIONES DE ARCHIVOS SEGURAS
    // ==========================================

    public static File getJarvisDir(Context context) {
        File dir = new File(context.getExternalFilesDir(null), "JarvisFiles");
        if (!dir.exists()) dir.mkdirs();
        return dir;
    }

    public static String createFile(Context context, String filename, String content) {
        if (!checkPermission(context, "files_write")) {
            return "[!] Permiso denegado para crear archivos";
        }
        try {
            File f = new File(getJarvisDir(context), filename);
            FileOutputStream fos = new FileOutputStream(f, false);
            fos.write(content.getBytes("UTF-8"));
            fos.close();
            return "[+] Archivo creado: " + f.getAbsolutePath();
        } catch (Exception e) {
            return "[!] Error al crear archivo: " + e.getMessage();
        }
    }

    public static String appendFile(Context context, String filename, String content) {
        if (!checkPermission(context, "files_write")) {
            return "[!] Permiso denegado para modificar archivos";
        }
        try {
            File f = new File(getJarvisDir(context), filename);
            FileOutputStream fos = new FileOutputStream(f, true);
            fos.write(("\n" + content).getBytes("UTF-8"));
            fos.close();
            return "[+] Contenido anadido a: " + f.getName();
        } catch (Exception e) {
            return "[!] Error al anadir a archivo: " + e.getMessage();
        }
    }

    public static String readFile(Context context, String filename) {
        try {
            File f = new File(getJarvisDir(context), filename);
            if (!f.exists()) return "[!] Archivo no encontrado: " + filename;
            FileInputStream fis = new FileInputStream(f);
            byte[] buf = new byte[(int) Math.min(64000, f.length())];
            int read = fis.read(buf);
            fis.close();
            return new String(buf, 0, Math.max(0, read), "UTF-8");
        } catch (Exception e) {
            return "[!] Error leyendo archivo: " + e.getMessage();
        }
    }

    public static String deleteFile(Context context, String filename) {
        if (!checkPermission(context, "files_delete")) {
            return "[!] Permiso denegado para borrar archivos (requiere confirmacion)";
        }
        try {
            File f = new File(getJarvisDir(context), filename);
            if (f.exists() && f.delete()) {
                return "[+] Archivo eliminado: " + filename;
            }
            return "[!] No se pudo eliminar o no existe: " + filename;
        } catch (Exception e) {
            return "[!] Error borrando archivo: " + e.getMessage();
        }
    }

    public static String listFiles(Context context) {
        File dir = getJarvisDir(context);
        File[] files = dir.listFiles();
        if (files == null || files.length == 0) return "[i] La carpeta JarvisFiles esta vacia";
        StringBuilder sb = new StringBuilder("[ARCHIVOS EN JarvisFiles]:\n");
        for (File f : files) {
            sb.append(" - ").append(f.getName()).append(" (").append(f.length()).append(" bytes)\n");
        }
        return sb.toString().trim();
    }

    // ==========================================
    // 5. NAVEGACION WEB Y YOUTUBE
    // ==========================================

    public static String openUrl(Context context, String url) {
        if (!checkPermission(context, "url")) {
            return "[!] Permiso denegado para abrir URLs";
        }
        try {
            String u = url.trim().replace("\"", "");
            if (!u.startsWith("http://") && !u.startsWith("https://")) {
                u = "https://" + u;
            }
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(u));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "[+] URL abierta en navegador: " + u;
        } catch (Exception e) {
            return "[!] Error abriendo URL: " + e.getMessage();
        }
    }

    public static String searchYouTube(Context context, String query) {
        try {
            String q = query.replace("\"", "").trim();
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://www.youtube.com/results?search_query=" + Uri.encode(q)));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "[+] Buscando en YouTube: " + q;
        } catch (Exception e) {
            return "[!] Error buscando en YouTube: " + e.getMessage();
        }
    }

    public static String searchWeb(Context context, String query) {
        try {
            String q = query.replace("\"", "").trim();
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://www.google.com/search?q=" + Uri.encode(q)));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "[+] Buscando en la web: " + q;
        } catch (Exception e) {
            return "[!] Error buscando en Google: " + e.getMessage();
        }
    }

    // ==========================================
    // 6. MACROS Y EJECUCION DE ETIQUETAS
    // ==========================================

    public static String runMacro(Context context, String macroName) {
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        String raw = sp.getString(PREF_MACROS, "{}");
        try {
            JSONObject macros = new JSONObject(raw);
            String norm = normalizeString(macroName.replace("\"", "").trim());
            for (java.util.Iterator<String> it = macros.keys(); it.hasNext(); ) {
                String k = it.next();
                if (normalizeString(k).equals(norm)) {
                    JSONArray steps = macros.getJSONArray(k);
                    StringBuilder sb = new StringBuilder("[+] Ejecutando macro '" + k + "' (" + steps.length() + " pasos):\n");
                    for (int s = 0; s < steps.length(); s++) {
                        String stepTag = steps.getString(s);
                        if (stepTag.startsWith("WAIT ")) {
                            try {
                                int secs = Integer.parseInt(stepTag.substring(5).trim());
                                Thread.sleep(secs * 1000L);
                                sb.append(" [Pausa ").append(secs).append("s]\n");
                            } catch (Exception ignored) {
                            }
                        } else {
                            String res = executeSingleTag(context, stepTag.startsWith("[") ? stepTag : "[JARVIS: " + stepTag + "]");
                            sb.append(" ").append(res).append("\n");
                        }
                    }
                    return sb.toString().trim();
                }
            }
            return "[!] Macro '" + macroName + "' no encontrada";
        } catch (Exception e) {
            return "[!] Error ejecutando macro: " + e.getMessage();
        }
    }

    public static String executeSingleTag(Context context, String tagText) {
        Matcher m = TAG_PATTERN.matcher(tagText);
        if (!m.find()) return "[!] Etiqueta no reconocida: " + tagText;

        String action = m.group(1).toUpperCase();
        String args = m.group(2) != null ? m.group(2).trim() : "";

        try {
            switch (action) {
                case "OPEN":
                    return openApp(context, args);
                case "URL":
                    return openUrl(context, args);
                case "SEARCH_WEB":
                    return searchWeb(context, args);
                case "PLAY_YT":
                case "SEARCH_YT":
                    return searchYouTube(context, args);
                case "VOLUME":
                    return setVolume(context, args);
                case "MEDIA":
                    return mediaControl(context, args);
                case "BRIGHTNESS":
                    return setBrightness(context, Integer.parseInt(args.replaceAll("[^0-9]", "")));
                case "FLASHLIGHT":
                    return toggleFlashlight(context, args.toLowerCase().contains("on") || args.toLowerCase().contains("enciende") || args.equals("1"));
                case "WIFI":
                    return openWifiSettings(context);
                case "BLUETOOTH":
                    return openBluetoothSettings(context);
                case "SCREENSHOT":
                    return takeScreenshot(context);
                case "LOCK":
                    return lockScreen(context);
                case "TIMER": {
                    int mins = 5;
                    String text = "Temporizador";
                    Pattern p = Pattern.compile("(\\d+)[m]?\\s*(?:\"([^\"]*)\")?");
                    Matcher pm = p.matcher(args);
                    if (pm.find()) {
                        mins = Integer.parseInt(pm.group(1));
                        if (pm.group(2) != null) text = pm.group(2);
                    }
                    return setTimer(context, mins, text);
                }
                case "ALARM": {
                    int h = 7, min = 0;
                    String text = "Alarma";
                    Pattern p = Pattern.compile("(\\d{1,2}):(\\d{2})\\s*(?:\"([^\"]*)\")?");
                    Matcher pm = p.matcher(args);
                    if (pm.find()) {
                        h = Integer.parseInt(pm.group(1));
                        min = Integer.parseInt(pm.group(2));
                        if (pm.group(3) != null) text = pm.group(3);
                    }
                    return setAlarm(context, h, min, text);
                }
                case "REMIND": {
                    long delay = 600000; // 10 min
                    String text = "Recordatorio";
                    Pattern p = Pattern.compile("(?:(\\d+)[m]?|(\\d{1,2}):(\\d{2}))\\s*(?:\"([^\"]*)\")?");
                    Matcher pm = p.matcher(args);
                    if (pm.find()) {
                        if (pm.group(1) != null) {
                            delay = Long.parseLong(pm.group(1)) * 60000L;
                        }
                        if (pm.group(4) != null) text = pm.group(4);
                    }
                    return addReminder(context, delay, text);
                }
                case "LIST_REMINDERS":
                    return listReminders(context);
                case "CANCEL_REMINDER":
                    return cancelReminder(context, Integer.parseInt(args.replaceAll("[^0-9]", "")));
                case "CREATE":
                case "WRITE": {
                    String[] parts = args.split("::", 2);
                    String fname = parts[0].replace("\"", "").trim();
                    String content = parts.length > 1 ? parts[1].replace("\"", "").trim() : "";
                    return createFile(context, fname, content);
                }
                case "APPEND": {
                    String[] parts = args.split("::", 2);
                    String fname = parts[0].replace("\"", "").trim();
                    String content = parts.length > 1 ? parts[1].replace("\"", "").trim() : "";
                    return appendFile(context, fname, content);
                }
                case "READ":
                    return readFile(context, args.replace("\"", "").trim());
                case "DELETE":
                    return deleteFile(context, args.replace("\"", "").trim());
                case "LIST":
                    return listFiles(context);
                case "RUN_MACRO":
                    return runMacro(context, args);
                case "SKIN": {
                    ShimejiService s = ShimejiService.getInstance();
                    if (s != null) {
                        s.switchSkin(args.replace("\"", "").trim());
                        return "[+] Skin cambiada a " + args;
                    }
                    return "[!] Servicio Shimeji no disponible";
                }
                default:
                    return "[!] Accion desconocida: " + action;
            }
        } catch (Exception e) {
            return "[!] Error ejecutando " + action + ": " + e.getMessage();
        }
    }

    public static List<String> extractTags(String text) {
        List<String> list = new ArrayList<>();
        if (text == null) return list;
        Matcher m = TAG_PATTERN.matcher(text);
        while (m.find()) {
            list.add(m.group(0));
        }
        return list;
    }

    public static String stripTags(String text) {
        if (text == null) return "";
        return TAG_PATTERN.matcher(text).replaceAll("").trim();
    }

    private static String normalizeString(String s) {
        if (s == null) return "";
        return Normalizer.normalize(s, Normalizer.Form.NFD)
            .replaceAll("\\p{InCombiningDiacriticalMarks}+", "")
            .toLowerCase()
            .trim();
    }
}

