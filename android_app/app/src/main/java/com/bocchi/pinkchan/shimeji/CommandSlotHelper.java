package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.provider.Settings;

import org.json.JSONArray;

import java.io.File;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class CommandSlotHelper {

    public interface ExecutionCallback {
        void onExecuted(boolean success, String reply);
    }

    public static List<String> getSlots(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        String json = prefs.getString(MainActivity.KEY_CUSTOM_SLOTS, "[]");
        List<String> list = new ArrayList<>();
        try {
            JSONArray arr = new JSONArray(json);
            for (int i = 0; i < arr.length(); i++) {
                list.add(arr.getString(i));
            }
        } catch (Exception ignored) {}
        return list;
    }

    public static boolean addSlot(Context context, String slot) {
        if (slot == null || slot.trim().isEmpty()) return false;
        String clean = slot.trim().toLowerCase();
        List<String> current = getSlots(context);
        if (!current.contains(clean)) {
            current.add(clean);
            saveSlots(context, current);
            return true;
        }
        return false;
    }

    public static void removeSlot(Context context, int index) {
        List<String> current = getSlots(context);
        if (index >= 0 && index < current.size()) {
            current.remove(index);
            saveSlots(context, current);
        }
    }

    public static void removeSlot(Context context, String slot) {
        if (slot == null) return;
        List<String> current = getSlots(context);
        if (current.remove(slot.trim().toLowerCase())) {
            saveSlots(context, current);
        }
    }

    private static void saveSlots(Context context, List<String> slots) {
        SharedPreferences prefs = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        JSONArray arr = new JSONArray();
        for (String s : slots) {
            arr.put(s);
        }
        prefs.edit().putString(MainActivity.KEY_CUSTOM_SLOTS, arr.toString()).apply();
    }

    /**
     * Intenta interpretar el comando contra los atajos prefabricados o registrar una nueva ranura.
     * Retorna true si fue procesado por el motor de ranuras prefabricadas.
     */
    public static boolean matchAndExecute(Context context, String rawInput, ExecutionCallback callback) {
        if (rawInput == null) return false;
        String trimmed = rawInput.trim();
        String lower = trimmed.toLowerCase();

        // 1. Registro directo via chat/voz: agregar-abrirapp-[X], agregar-ejecutarcomando-[X], etc.
        if (lower.startsWith("agregar-") || lower.startsWith("agregar ")) {
            String toAdd = lower.replaceFirst("^agregar[- ]+", "").trim();
            if (toAdd.startsWith("abrirapp-") || toAdd.startsWith("ejecutarcomando-") ||
                toAdd.startsWith("decir-") || toAdd.startsWith("buscar-") ||
                toAdd.startsWith("accion-") || toAdd.startsWith("crearcarpeta-")) {

                boolean added = addSlot(context, toAdd);
                if (callback != null) {
                    if (added) {
                        callback.onExecuted(true, "Ranura '" + toAdd + "' guardada y lista para usarse.");
                    } else {
                        callback.onExecuted(true, "La ranura '" + toAdd + "' ya estaba registrada.");
                    }
                }
                return true;
            }
        }

        // 2. Comprobacion de ejecucion directa de plantillas con o sin guion
        String matchedSlotType = null;
        String paramX = null;

        String[] prefixes = {"abrirapp-", "abrirapp ", "ejecutarcomando-", "ejecutarcomando ", "decir-", "decir ", "buscar-", "buscar ", "accion-", "accion ", "crearcarpeta-", "crearcarpeta "};
        for (String pref : prefixes) {
            if (lower.startsWith(pref)) {
                matchedSlotType = pref.trim().replace("-", "");
                paramX = trimmed.substring(pref.length()).trim();
                break;
            }
        }

        // Comprobacion de si coincide exactamente con alguna ranura guardada en la lista
        if (matchedSlotType == null) {
            List<String> savedSlots = getSlots(context);
            for (String slot : savedSlots) {
                if (lower.equals(slot)) {
                    int dash = slot.indexOf('-');
                    if (dash > 0) {
                        matchedSlotType = slot.substring(0, dash);
                        paramX = slot.substring(dash + 1).trim();
                        break;
                    }
                }
            }
        }

        if (matchedSlotType != null && paramX != null && !paramX.isEmpty()) {
            executeSlotAction(context, matchedSlotType, paramX, callback);
            return true;
        }

        return false;
    }

    private static void executeSlotAction(Context context, String type, String param, ExecutionCallback callback) {
        if ("abrirapp".equals(type)) {
            String reply = launchAppByQuery(context, param);
            if (callback != null) callback.onExecuted(true, reply);
            return;
        }

        if ("ejecutarcomando".equals(type)) {
            executeCommandTermuxOrShell(context, param, callback);
            return;
        }

        if ("decir".equals(type)) {
            if (ShimejiService.isRunning) {
                Intent it = new Intent(context, ShimejiService.class);
                it.setAction(ShimejiService.ACTION_TRIGGER);
                it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, "speech:" + param);
                context.startService(it);
            }
            if (callback != null) callback.onExecuted(true, "Shimeji dice: \"" + param + "\"");
            return;
        }

        if ("buscar".equals(type)) {
            try {
                String query = URLEncoder.encode(param, "UTF-8");
                Intent ytIntent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://www.youtube.com/results?search_query=" + query));
                ytIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(ytIntent);
                if (callback != null) callback.onExecuted(true, "Buscando '" + param + "' en YouTube / Web.");
            } catch (Exception e) {
                if (callback != null) callback.onExecuted(false, "Error al buscar: " + e.getMessage());
            }
            return;
        }

        if ("accion".equals(type)) {
            String act = param.toLowerCase();
            String mapped = "roam";
            if (act.contains("guitar")) mapped = "guitar";
            else if (act.contains("caja") || act.contains("box")) mapped = "box";
            else if (act.contains("bail") || act.contains("dance")) mapped = "dance";
            else if (act.contains("rued") || act.contains("roll")) mapped = "roll";
            else if (act.contains("brinc") || act.contains("jump")) mapped = "jump";
            else if (act.contains("jueg") || act.contains("play")) mapped = "play";
            else if (act.contains("item") || act.contains("comida") || act.contains("snack")) {
                if (ShimejiService.isRunning) {
                    Intent it = new Intent(context, ShimejiService.class);
                    it.setAction(ShimejiService.ACTION_DROP_ITEM);
                    context.startService(it);
                }
                if (callback != null) callback.onExecuted(true, "Soltando snack/item.");
                return;
            }

            if (ShimejiService.isRunning) {
                Intent it = new Intent(context, ShimejiService.class);
                it.setAction(ShimejiService.ACTION_TRIGGER);
                it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, mapped);
                context.startService(it);
            }
            if (callback != null) callback.onExecuted(true, "Accion '" + mapped + "' activada.");
            return;
        }

        if ("crearcarpeta".equals(type)) {
            try {
                File docs = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS);
                File target = new File(docs, "Shijima/" + param);
                boolean ok = target.mkdirs() || target.exists();
                if (callback != null) {
                    callback.onExecuted(ok, ok ? "Carpeta creada: Documents/Shijima/" + param : "No se pudo crear la carpeta.");
                }
            } catch (Exception e) {
                if (callback != null) callback.onExecuted(false, "Error: " + e.getMessage());
            }
            return;
        }

        if (callback != null) callback.onExecuted(false, "Tipo de ranura desconocido: " + type);
    }

    private static String launchAppByQuery(Context context, String query) {
        PackageManager pm = context.getPackageManager();
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        Set<String> allowedSet = sp.getStringSet(MainActivity.KEY_ALLOWED_APPS, null);

        String clean = query.toLowerCase().replace(" ", "");

        if (clean.equals("camara") || clean.equals("fotos")) {
            Intent intent = new Intent(MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            if (intent.resolveActivity(pm) != null) {
                context.startActivity(intent);
                return "Abriendo la camara.";
            }
        }

        if (clean.equals("ajustes") || clean.equals("configuracion")) {
            Intent intent = new Intent(Settings.ACTION_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "Abriendo ajustes.";
        }

        List<ApplicationInfo> apps = pm.getInstalledApplications(PackageManager.GET_META_DATA);
        ApplicationInfo bestMatch = null;
        for (ApplicationInfo app : apps) {
            String label = pm.getApplicationLabel(app).toString().toLowerCase();
            String cleanLabel = label.replace(" ", "");
            if (cleanLabel.equals(clean)) {
                bestMatch = app;
                break;
            } else if (cleanLabel.contains(clean) || clean.contains(cleanLabel)) {
                if (pm.getLaunchIntentForPackage(app.packageName) != null) {
                    bestMatch = app;
                }
            }
        }

        if (bestMatch != null) {
            String appLabel = pm.getApplicationLabel(bestMatch).toString();
            if (allowedSet != null && !allowedSet.contains(bestMatch.packageName)) {
                return "La app '" + appLabel + "' esta bloqueada en el filtro.";
            }
            Intent launch = pm.getLaunchIntentForPackage(bestMatch.packageName);
            if (launch != null) {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(launch);
                return "Abriendo " + appLabel + ".";
            }
        }
        return "No encontre ninguna aplicacion llamada '" + query + "'.";
    }

    private static void executeCommandTermuxOrShell(final Context context, final String cmd, final ExecutionCallback callback) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                // Primero intentamos enviar a Termux via Intent si esta disponible
                PackageManager pm = context.getPackageManager();
                Intent termuxIntent = pm.getLaunchIntentForPackage("com.termux");
                if (termuxIntent != null) {
                    try {
                        Intent runIntent = new Intent("com.termux.RUN_COMMAND");
                        runIntent.setClassName("com.termux", "com.termux.app.RunCommandService");
                        runIntent.putExtra("com.termux.RUN_COMMAND_PATH", "/data/data/com.termux/files/usr/bin/bash");
                        runIntent.putExtra("com.termux.RUN_COMMAND_ARGUMENTS", new String[]{"-c", cmd});
                        runIntent.putExtra("com.termux.RUN_COMMAND_IN_BACKGROUND", false);
                        context.startService(runIntent);
                        if (callback != null) {
                            callback.onExecuted(true, "Comando enviado a Termux: " + cmd);
                        }
                        return;
                    } catch (Exception ignored) {}
                }

                // Fallback: Ejecucion basica por ProcessBuilder
                try {
                    Process process = Runtime.getRuntime().exec(new String[]{"sh", "-c", cmd});
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    StringBuilder output = new StringBuilder();
                    String line;
                    int count = 0;
                    while ((line = reader.readLine()) != null && count < 10) {
                        output.append(line).append("\n");
                        count++;
                    }
                    reader.close();
                    process.waitFor();

                    String res = output.toString().trim();
                    if (res.isEmpty()) res = "Comando '" + cmd + "' ejecutado.";
                    if (callback != null) callback.onExecuted(true, res);
                } catch (Exception e) {
                    if (callback != null) callback.onExecuted(false, "Error ejecutando '" + cmd + "': " + e.getMessage());
                }
            }
        }).start();
    }
}
