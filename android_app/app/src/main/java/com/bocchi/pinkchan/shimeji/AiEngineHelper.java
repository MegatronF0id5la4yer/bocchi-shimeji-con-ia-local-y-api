package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AiEngineHelper {

    public interface AiCallback {
        void onSuccess(String reply);
        void onError(String errorMsg);
    }

    private static final ExecutorService executor = Executors.newCachedThreadPool();
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());

    private static final String[] GEMINI_FALLBACK_MODELS = {
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-pro"
    };

    public static String discoverBestGeminiModel(String apiKey) {
        try {
            String urlStr = "https://generativelanguage.googleapis.com/v1beta/models?key=" + apiKey;
            URL url = new URL(urlStr);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(15000);
            conn.setReadTimeout(20000);
            if (conn.getResponseCode() == 200) {
                BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) sb.append(line);
                br.close();
                JSONObject obj = new JSONObject(sb.toString());
                JSONArray arr = obj.optJSONArray("models");
                if (arr != null) {
                    for (String pref : GEMINI_FALLBACK_MODELS) {
                        for (int i = 0; i < arr.length(); i++) {
                            JSONObject m = arr.getJSONObject(i);
                            String name = m.optString("name", "");
                            if (name.endsWith("/" + pref) || name.equals(pref)) {
                                return pref;
                            }
                        }
                    }
                }
            }
        } catch (Exception ignored) {}
        return "gemini-2.5-flash";
    }

    public static String buildAgentSystemPrompt(Context context, SkinData skin) {
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        String assistantName = sp.getString("assistant_name", "JARVIS");
        String extraPrompt = sp.getString("agent_extra_prompt", "");
        boolean useSkin = sp.getBoolean("agent_use_skin_persona", true);

        StringBuilder sb = new StringBuilder();
        if (useSkin && skin != null && skin.systemPrompt != null) {
            sb.append(skin.systemPrompt).append("\n\n");
        } else {
            sb.append("Eres '").append(assistantName).append("', un asistente virtual autonomo y eficiente.\n\n");
        }

        if (!extraPrompt.trim().isEmpty()) {
            sb.append("[PERSONALIDAD ADICIONAL]:\n").append(extraPrompt.trim()).append("\n\n");
        }

        sb.append("[HABILIDADES DE JARVIS EN ANDROID]:\n")
          .append("Tienes control total de funciones del sistema Android para ayudar al usuario mediante herramientas automatizadas.\n")
          .append("Cuando el usuario te pida una accion, responde brevemente con tu estilo y agrega al final la etiqueta correspondiente:\n")
          .append(" - Abrir aplicaciones instaladas: [JARVIS: OPEN \"tiktok\"]\n")
          .append(" - Abrir enlaces URL: [JARVIS: URL \"https://...\"]\n")
          .append(" - Buscar en Google / web: [JARVIS: SEARCH_WEB \"consulta\"]\n")
          .append(" - Buscar o reproducir en YouTube: [JARVIS: PLAY_YT \"cancion o video\"]\n")
          .append(" - Control de volumen: [JARVIS: VOLUME up|down|mute|50]\n")
          .append(" - Control de musica: [JARVIS: MEDIA play|pause|next|prev]\n")
          .append(" - Ajustar brillo de pantalla: [JARVIS: BRIGHTNESS 70]\n")
          .append(" - Linterna del telefono: [JARVIS: FLASHLIGHT on|off]\n")
          .append(" - Ajustes de Wi-Fi y Bluetooth: [JARVIS: WIFI] o [JARVIS: BLUETOOTH]\n")
          .append(" - Captura de pantalla: [JARVIS: SCREENSHOT]\n")
          .append(" - Bloquear pantalla: [JARVIS: LOCK]\n")
          .append(" - Temporizador: [JARVIS: TIMER 5m \"texto\"]\n")
          .append(" - Alarma: [JARVIS: ALARM \"07:30\" \"texto\"]\n")
          .append(" - Recordatorio programado: [JARVIS: REMIND \"10m\" \"texto\"]\n")
          .append(" - Listar / cancelar recordatorios: [JARVIS: LIST_REMINDERS] y [JARVIS: CANCEL_REMINDER 1]\n")
          .append(" - Gestion de archivos en JarvisFiles: [JARVIS: CREATE \"archivo\" :: \"contenido\"], [JARVIS: WRITE ...], [JARVIS: READ \"archivo\"], [JARVIS: DELETE \"archivo\"], [JARVIS: LIST \"carpeta\"]\n")
          .append(" - Ejecutar macros personalizadas: [JARVIS: RUN_MACRO \"nombre\"]\n")
          .append(" - Cambiar skin de personaje: [JARVIS: SKIN \"Bocchi\"]\n\n")
          .append("[BUCLE AUTONOMO MULTIPASO]:\n")
          .append("Puedes resolver tareas complejas paso a paso. Cuando emitas etiquetas, el sistema las ejecutara y te devolvera '[RESULTADOS DE HERRAMIENTAS]: ...' en el siguiente turno para que continúes o presentes tu respuesta final sin etiquetas.\n\n")
          .append("[REGLA ESTRICTA]: NO USES EMOJIS BAJO NINGUNA CIRCUNSTANCIA. Cero emojis pictograficos en tus respuestas.");

        return sb.toString();
    }

    public static String tryFastOfflineIntent(Context context, String rawInput) {
        if (rawInput == null) return null;
        String text = rawInput.toLowerCase().trim();
        if (text.equals("detener") || text.equals("stop")) {
            return "[i] Accion del agente detenida.";
        }
        if (text.startsWith("abre ") || text.startsWith("abrir ")) {
            String app = text.substring(text.indexOf(" ") + 1).trim();
            return AgentToolExecutor.openApp(context, app);
        }
        if (text.startsWith("sube el volumen") || text.startsWith("subir volumen")) {
            return AgentToolExecutor.setVolume(context, "up");
        }
        if (text.startsWith("baja el volumen") || text.startsWith("bajar volumen")) {
            return AgentToolExecutor.setVolume(context, "down");
        }
        if (text.equals("silencio") || text.equals("mute") || text.startsWith("silenciar")) {
            return AgentToolExecutor.setVolume(context, "mute");
        }
        if (text.contains("volumen al ") || text.contains("volumen a ")) {
            return AgentToolExecutor.setVolume(context, text);
        }
        if (text.contains("brillo al ") || text.contains("brillo a ")) {
            String num = text.replaceAll("[^0-9]", "");
            if (!num.isEmpty()) {
                return AgentToolExecutor.setBrightness(context, Integer.parseInt(num));
            }
        }
        if (text.contains("linterna") || text.contains("flash")) {
            boolean on = text.contains("enciende") || text.contains("prende") || text.contains("activa") || text.contains("on");
            return AgentToolExecutor.toggleFlashlight(context, on);
        }
        if (text.contains("captura") || text.contains("screenshot")) {
            return AgentToolExecutor.takeScreenshot(context);
        }
        if (text.contains("bloquea") && (text.contains("pantalla") || text.contains("telefono") || text.contains("celular"))) {
            return AgentToolExecutor.lockScreen(context);
        }
        if (text.contains("pausa la musica") || text.contains("pausar musica") || text.contains("reproduce musica")) {
            return AgentToolExecutor.mediaControl(context, "play");
        }
        if (text.contains("siguiente cancion") || text.contains("siguiente pista")) {
            return AgentToolExecutor.mediaControl(context, "next");
        }
        if (text.contains("anterior cancion") || text.contains("anterior pista")) {
            return AgentToolExecutor.mediaControl(context, "prev");
        }
        if (text.contains("temporizador de ") || text.contains("timer de ")) {
            String num = text.replaceAll("[^0-9]", "");
            int mins = num.isEmpty() ? 5 : Integer.parseInt(num);
            return AgentToolExecutor.setTimer(context, mins, "Temporizador JARVIS");
        }
        if (text.contains("alarma a las ") || text.contains("alarma para las ")) {
            Pattern p = Pattern.compile("(\\d{1,2}):(\\d{2})");
            Matcher m = p.matcher(text);
            if (m.find()) {
                return AgentToolExecutor.setAlarm(context, Integer.parseInt(m.group(1)), Integer.parseInt(m.group(2)), "Alarma JARVIS");
            }
        }
        if (text.contains("busca ") && text.contains(" en youtube")) {
            String q = text.substring(text.indexOf("busca ") + 6, text.indexOf(" en youtube")).trim();
            return AgentToolExecutor.searchYouTube(context, q);
        }
        if (text.contains("busca ") && (text.contains(" en google") || text.contains(" en la web") || text.contains(" en internet"))) {
            int endIdx = text.indexOf(" en google");
            if (endIdx < 0) endIdx = text.indexOf(" en la web");
            if (endIdx < 0) endIdx = text.indexOf(" en internet");
            String q = text.substring(text.indexOf("busca ") + 6, endIdx).trim();
            return AgentToolExecutor.searchWeb(context, q);
        }
        return null;
    }

    public static void askAi(final Context context, final String currentSkinId, final String userMessage, final AiCallback callback) {
        final SharedPreferences prefs = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        final String mode = prefs.getString(MainActivity.KEY_AI_MODE, "local");
        final SkinData skin = SkinData.get(currentSkinId);

        // 1. Deteccion rapida offline de intenciones
        String fastReply = tryFastOfflineIntent(context, userMessage);
        if (fastReply != null) {
            final String fReply = fastReply;
            mainHandler.post(new Runnable() {
                @Override
                public void run() {
                    if (callback != null) callback.onSuccess(fReply);
                }
            });
            return;
        }

        final String systemPrompt = buildAgentSystemPrompt(context, skin);

        if ("local".equalsIgnoreCase(mode)) {
            mainHandler.post(new Runnable() {
                @Override
                public void run() {
                    String reply = getLocalPersonaReply(skin, userMessage);
                    if (callback != null) callback.onSuccess(reply);
                }
            });
            return;
        }

        if ("gemini".equalsIgnoreCase(mode)) {
            final String apiKey = prefs.getString(MainActivity.KEY_GEMINI_KEY, "").trim();
            final String model = prefs.getString(MainActivity.KEY_GEMINI_MODEL, "gemini-2.5-flash").trim();

            if (apiKey.isEmpty()) {
                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        if (callback != null) {
                            callback.onError("Configura tu API Key de Gemini en Ajustes de la App.");
                        }
                    }
                });
                return;
            }

            executor.execute(new Runnable() {
                @Override
                public void run() {
                    requestGeminiAgentLoop(context, apiKey, model, systemPrompt, userMessage, skin, callback);
                }
            });
            return;
        }

        if ("cloud".equalsIgnoreCase(mode)) {
            final String endpoint = prefs.getString(MainActivity.KEY_CLOUD_ENDPOINT, "").trim();
            final String model = prefs.getString(MainActivity.KEY_CLOUD_MODEL, "llama3").trim();
            final String apiKey = prefs.getString(MainActivity.KEY_CLOUD_KEY, "").trim();

            if (endpoint.isEmpty()) {
                mainHandler.post(new Runnable() {
                    @Override
                    public void run() {
                        if (callback != null) {
                            callback.onError("Configura la URL Endpoint de Cloud/Ollama en Ajustes.");
                        }
                    }
                });
                return;
            }

            executor.execute(new Runnable() {
                @Override
                public void run() {
                    requestCloudAgentLoop(context, endpoint, model, apiKey, systemPrompt, userMessage, skin, callback);
                }
            });
            return;
        }

        // Por defecto fallback local
        mainHandler.post(new Runnable() {
            @Override
            public void run() {
                String reply = getLocalPersonaReply(skin, userMessage);
                if (callback != null) callback.onSuccess(reply);
            }
        });
    }

    public static void testConnection(final Context context, final String mode, final String apiKey, final String model, final String endpoint, final AiCallback callback) {
        executor.execute(new Runnable() {
            @Override
            public void run() {
                if ("local".equalsIgnoreCase(mode)) {
                    postSuccess(callback, "Modo Local Offline verificado con exito. Sin consumo de datos.");
                    return;
                }

                if ("gemini".equalsIgnoreCase(mode)) {
                    if (apiKey == null || apiKey.trim().isEmpty()) {
                        postError(callback, "Introduce tu Gemini API Key primero.");
                        return;
                    }
                    String targetModel = (model != null && !model.trim().isEmpty()) ? model.trim() : "gemini-2.5-flash";
                    requestGeminiAgentLoop(context, apiKey.trim(), targetModel, "Responde brevemente en una sola oracion.", "Hola, funcionas?", null, callback);
                    return;
                }

                if ("cloud".equalsIgnoreCase(mode)) {
                    if (endpoint == null || endpoint.trim().isEmpty()) {
                        postError(callback, "Introduce la URL Endpoint primero.");
                        return;
                    }
                    String targetModel = (model != null && !model.trim().isEmpty()) ? model.trim() : "llama3";
                    requestCloudAgentLoop(context, endpoint.trim(), targetModel, apiKey != null ? apiKey.trim() : "", "Responde brevemente en una oracion.", "Hola, prueba de conexion.", null, callback);
                    return;
                }

                postError(callback, "Modo de IA desconocido: " + mode);
            }
        });
    }

    private static void requestGeminiAgentLoop(Context context, String apiKey, String preferredModel, String systemPrompt, String userMessage, SkinData skin, final AiCallback callback) {
        SharedPreferences prefs = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        int maxSteps = prefs.getInt("agent_max_steps", 6);
        int timeoutSec = prefs.getInt("agent_timeout_sec", 60);

        String[] modelsToTry;
        if (preferredModel != null && !preferredModel.trim().isEmpty() && !"auto".equalsIgnoreCase(preferredModel.trim())) {
            modelsToTry = new String[]{preferredModel.trim(), "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"};
        } else {
            String best = discoverBestGeminiModel(apiKey);
            modelsToTry = new String[]{best, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"};
        }

        JSONArray contents = new JSONArray();
        try {
            JSONObject initUser = new JSONObject();
            initUser.put("role", "user");
            JSONArray parts = new JSONArray();
            JSONObject part = new JSONObject();
            part.put("text", "[Instrucciones de Sistema: " + systemPrompt + "]\n\nUsuario: " + userMessage);
            parts.put(part);
            initUser.put("parts", parts);
            contents.put(initUser);
        } catch (Exception ignored) {}

        String lastError = null;

        for (String m : modelsToTry) {
            try {
                int step = 1;
                while (step <= maxSteps) {
                    String urlStr = "https://generativelanguage.googleapis.com/v1beta/models/" + m + ":generateContent?key=" + apiKey;
                    URL url = new URL(urlStr);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("Content-Type", "application/json");
                    conn.setConnectTimeout(15000);
                    conn.setReadTimeout(timeoutSec * 1000);
                    conn.setDoOutput(true);

                    JSONObject root = new JSONObject();
                    root.put("contents", contents);

                    JSONObject genConfig = new JSONObject();
                    genConfig.put("temperature", 0.8);
                    genConfig.put("maxOutputTokens", 4096);
                    root.put("generationConfig", genConfig);

                    OutputStream os = conn.getOutputStream();
                    os.write(root.toString().getBytes("UTF-8"));
                    os.flush();
                    os.close();

                    int code = conn.getResponseCode();
                    if (code == 200) {
                        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                        StringBuilder sb = new StringBuilder();
                        String line;
                        while ((line = br.readLine()) != null) sb.append(line);
                        br.close();

                        JSONObject resObj = new JSONObject(sb.toString());
                        JSONArray candidates = resObj.optJSONArray("candidates");
                        if (candidates != null && candidates.length() > 0) {
                            JSONObject cand = candidates.getJSONObject(0);
                            JSONObject content = cand.optJSONObject("content");
                            if (content != null) {
                                JSONArray cParts = content.optJSONArray("parts");
                                if (cParts != null && cParts.length() > 0) {
                                    String reply = cleanAiReply(cParts.getJSONObject(0).optString("text", ""));
                                    List<String> tags = AgentToolExecutor.extractTags(reply);

                                    // Si no hay etiquetas o ya es la respuesta final
                                    if (tags.isEmpty() || step >= maxSteps) {
                                        postSuccess(callback, reply);
                                        return;
                                    }

                                    // Ejecutar herramientas en bucle multipaso
                                    StringBuilder toolResults = new StringBuilder("[RESULTADOS DE HERRAMIENTAS]:\n");
                                    for (String tag : tags) {
                                        String res = AgentToolExecutor.executeSingleTag(context, tag);
                                        toolResults.append(res).append("\n");
                                        ShimejiService svc = ShimejiService.getInstance();
                                        if (svc != null && svc.getFloatingChatManager() != null) {
                                            svc.getFloatingChatManager().addSystemMessage("[Paso " + step + "] " + res);
                                        }
                                    }

                                    // Anadir respuesta del modelo a la conversacion
                                    JSONObject modelTurn = new JSONObject();
                                    modelTurn.put("role", "model");
                                    JSONArray mParts = new JSONArray();
                                    JSONObject mPart = new JSONObject();
                                    mPart.put("text", reply);
                                    mParts.put(mPart);
                                    modelTurn.put("parts", mParts);
                                    contents.put(modelTurn);

                                    // Anadir resultados como nuevo turno de usuario
                                    JSONObject userTurn = new JSONObject();
                                    userTurn.put("role", "user");
                                    JSONArray uParts = new JSONArray();
                                    JSONObject uPart = new JSONObject();
                                    uPart.put("text", toolResults.toString().trim());
                                    uParts.put(uPart);
                                    userTurn.put("parts", uParts);
                                    contents.put(userTurn);

                                    step++;
                                    continue;
                                }
                            }
                        }
                        postSuccess(callback, "Gemini respondio sin texto legible.");
                        return;
                    } else {
                        BufferedReader errBr = new BufferedReader(new InputStreamReader(conn.getErrorStream() != null ? conn.getErrorStream() : conn.getInputStream(), "UTF-8"));
                        StringBuilder errSb = new StringBuilder();
                        String l;
                        while ((l = errBr.readLine()) != null) errSb.append(l);
                        errBr.close();
                        lastError = "HTTP " + code + " (" + m + "): " + errSb.toString();
                        if (code != 404 && code != 400) {
                            break;
                        }
                    }
                }
            } catch (Exception e) {
                lastError = e.getMessage();
            }
        }

        // Si todos los modelos fallaron
        if (skin != null) {
            postSuccess(callback, getLocalPersonaReply(skin, userMessage) + " [Offline]");
        } else {
            postError(callback, "Fallo conexion con Gemini: " + (lastError != null ? lastError : "Verifica tu conexion e API Key"));
        }
    }

    private static void requestCloudAgentLoop(Context context, String endpoint, String model, String apiKey, String systemPrompt, String userMessage, SkinData skin, final AiCallback callback) {
        SharedPreferences prefs = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        int maxSteps = prefs.getInt("agent_max_steps", 6);
        int timeoutSec = prefs.getInt("agent_timeout_sec", 60);

        try {
            String baseUrl = endpoint.endsWith("/") ? endpoint.substring(0, endpoint.length() - 1) : endpoint;
            if (!baseUrl.endsWith("/chat/completions")) {
                if (baseUrl.endsWith("/v1")) {
                    baseUrl += "/chat/completions";
                } else {
                    baseUrl += "/v1/chat/completions";
                }
            }

            JSONArray messages = new JSONArray();
            JSONObject sysMsg = new JSONObject();
            sysMsg.put("role", "system");
            sysMsg.put("content", systemPrompt);
            messages.put(sysMsg);

            JSONObject userMsg = new JSONObject();
            userMsg.put("role", "user");
            userMsg.put("content", userMessage);
            messages.put(userMsg);

            int step = 1;
            while (step <= maxSteps) {
                URL url = new URL(baseUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                if (apiKey != null && !apiKey.isEmpty()) {
                    conn.setRequestProperty("Authorization", "Bearer " + apiKey);
                }
                conn.setConnectTimeout(15000);
                conn.setReadTimeout(timeoutSec * 1000);
                conn.setDoOutput(true);

                JSONObject root = new JSONObject();
                root.put("model", model);
                root.put("messages", messages);
                root.put("max_tokens", 4096);
                root.put("temperature", 0.8);

                OutputStream os = conn.getOutputStream();
                os.write(root.toString().getBytes("UTF-8"));
                os.flush();
                os.close();

                int code = conn.getResponseCode();
                if (code == 200) {
                    BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) sb.append(line);
                    br.close();

                    JSONObject resObj = new JSONObject(sb.toString());
                    JSONArray choices = resObj.optJSONArray("choices");
                    if (choices != null && choices.length() > 0) {
                        JSONObject choice = choices.getJSONObject(0);
                        JSONObject msg = choice.optJSONObject("message");
                        if (msg != null) {
                            String reply = cleanAiReply(msg.optString("content", ""));
                            List<String> tags = AgentToolExecutor.extractTags(reply);

                            if (tags.isEmpty() || step >= maxSteps) {
                                postSuccess(callback, reply);
                                return;
                            }

                            StringBuilder toolResults = new StringBuilder("[RESULTADOS DE HERRAMIENTAS]:\n");
                            for (String tag : tags) {
                                String res = AgentToolExecutor.executeSingleTag(context, tag);
                                toolResults.append(res).append("\n");
                                ShimejiService svc = ShimejiService.getInstance();
                                if (svc != null && svc.getFloatingChatManager() != null) {
                                    svc.getFloatingChatManager().addSystemMessage("[Paso " + step + "] " + res);
                                }
                            }

                            JSONObject asst = new JSONObject();
                            asst.put("role", "assistant");
                            asst.put("content", reply);
                            messages.put(asst);

                            JSONObject toolTurn = new JSONObject();
                            toolTurn.put("role", "user");
                            toolTurn.put("content", toolResults.toString().trim());
                            messages.put(toolTurn);

                            step++;
                            continue;
                        }
                    }
                    postSuccess(callback, "Servidor Cloud respondio sin contenido legible.");
                    return;
                } else {
                    BufferedReader errBr = new BufferedReader(new InputStreamReader(conn.getErrorStream() != null ? conn.getErrorStream() : conn.getInputStream(), "UTF-8"));
                    StringBuilder errSb = new StringBuilder();
                    String l;
                    while ((l = errBr.readLine()) != null) errSb.append(l);
                    errBr.close();
                    String errStr = "Error Cloud/Ollama HTTP " + code + ": " + errSb.toString();
                    if (skin != null) {
                        postSuccess(callback, getLocalPersonaReply(skin, userMessage) + " [Offline]");
                    } else {
                        postError(callback, errStr);
                    }
                    return;
                }
            }
        } catch (Exception e) {
            if (skin != null) {
                postSuccess(callback, getLocalPersonaReply(skin, userMessage) + " [Sin conexion]");
            } else {
                postError(callback, "Excepcion conectando a Cloud/Ollama: " + e.getMessage());
            }
        }
    }

    private static String getLocalPersonaReply(SkinData skin, String userMessage) {
        if (skin == null || skin.speeches == null || skin.speeches.length == 0) {
            return "Entendido: '" + userMessage + "'.";
        }
        Random rand = new Random();
        return skin.speeches[rand.nextInt(skin.speeches.length)];
    }

    private static String cleanAiReply(String raw) {
        if (raw == null) return "";
        String cleaned = raw.trim()
                .replaceAll("\\*\\*", "")
                .replaceAll("^\"|\"$", "");
        // Eliminar emojis de la respuesta generada por la IA
        cleaned = cleaned.replaceAll("[\\p{So}\\p{Cn}\\p{Cs}\\x{1F000}-\\x{1FFFF}\\x{2600}-\\x{27BF}]", "");
        return cleaned.trim();
    }

    private static void postSuccess(final AiCallback callback, final String msg) {
        mainHandler.post(new Runnable() {
            @Override
            public void run() {
                if (callback != null) callback.onSuccess(msg);
            }
        });
    }

    private static void postError(final AiCallback callback, final String err) {
        mainHandler.post(new Runnable() {
            @Override
            public void run() {
                if (callback != null) callback.onError(err);
            }
        });
    }
}
