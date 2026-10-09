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
import java.util.Random;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class AiEngineHelper {

    public interface AiCallback {
        void onSuccess(String reply);
        void onError(String errorMsg);
    }

    private static final ExecutorService executor = Executors.newCachedThreadPool();
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());

    private static final String[] GEMINI_FALLBACK_MODELS = {
        "gemini-1.5-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-pro"
    };

    public static void askAi(final Context context, final String currentSkinId, final String userMessage, final AiCallback callback) {
        final SharedPreferences prefs = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        final String mode = prefs.getString(MainActivity.KEY_AI_MODE, "local");

        final SkinData skin = SkinData.get(currentSkinId);
        final String systemPrompt = (skin != null && skin.systemPrompt != null) ? skin.systemPrompt :
                "Eres un companero virtual divertido, amable y elocuente.";

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
            final String model = prefs.getString(MainActivity.KEY_GEMINI_MODEL, "gemini-1.5-flash").trim();

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
                    requestGemini(apiKey, model, systemPrompt, userMessage, skin, callback);
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
                    requestCloudOpenAi(endpoint, model, apiKey, systemPrompt, userMessage, skin, callback);
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
                    String targetModel = (model != null && !model.trim().isEmpty()) ? model.trim() : "gemini-1.5-flash";
                    requestGemini(apiKey.trim(), targetModel, "Responde brevemente en una sola oracion.", "Hola, funcionas?", null, callback);
                    return;
                }

                if ("cloud".equalsIgnoreCase(mode)) {
                    if (endpoint == null || endpoint.trim().isEmpty()) {
                        postError(callback, "Introduce la URL Endpoint primero.");
                        return;
                    }
                    String targetModel = (model != null && !model.trim().isEmpty()) ? model.trim() : "llama3";
                    requestCloudOpenAi(endpoint.trim(), targetModel, apiKey != null ? apiKey.trim() : "", "Responde brevemente en una oracion.", "Hola, prueba de conexion.", null, callback);
                    return;
                }

                postError(callback, "Modo de IA desconocido: " + mode);
            }
        });
    }

    private static void requestGemini(String apiKey, String preferredModel, String systemPrompt, String userMessage, SkinData skin, final AiCallback callback) {
        String[] modelsToTry;
        if (preferredModel != null && !preferredModel.trim().isEmpty()) {
            modelsToTry = new String[]{preferredModel.trim(), "gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-pro"};
        } else {
            modelsToTry = GEMINI_FALLBACK_MODELS;
        }

        String lastError = null;

        for (String m : modelsToTry) {
            try {
                // Direccion estandar y comprobada de Gemini Google API
                String urlStr = "https://generativelanguage.googleapis.com/v1beta/models/" + m + ":generateContent?key=" + apiKey;
                URL url = new URL(urlStr);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setConnectTimeout(8000);
                conn.setReadTimeout(12000);
                conn.setDoOutput(true);

                JSONObject root = new JSONObject();

                // Construir mensaje contextual con la personalidad del personaje
                String combinedPrompt = (systemPrompt != null && !systemPrompt.isEmpty())
                        ? "[Contexto e Instrucciones de Rol: " + systemPrompt + "]\n\nMensaje: " + userMessage
                        : userMessage;

                JSONArray contents = new JSONArray();
                JSONObject userContent = new JSONObject();
                userContent.put("role", "user");
                JSONArray parts = new JSONArray();
                JSONObject partObj = new JSONObject();
                partObj.put("text", combinedPrompt);
                parts.put(partObj);
                userContent.put("parts", parts);
                contents.put(userContent);
                root.put("contents", contents);

                JSONObject genConfig = new JSONObject();
                genConfig.put("temperature", 0.8);
                genConfig.put("maxOutputTokens", 300);
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
                    while ((line = br.readLine()) != null) {
                        sb.append(line);
                    }
                    br.close();

                    JSONObject resObj = new JSONObject(sb.toString());
                    JSONArray candidates = resObj.optJSONArray("candidates");
                    if (candidates != null && candidates.length() > 0) {
                        JSONObject cand = candidates.getJSONObject(0);
                        JSONObject content = cand.optJSONObject("content");
                        if (content != null) {
                            JSONArray cParts = content.optJSONArray("parts");
                            if (cParts != null && cParts.length() > 0) {
                                String reply = cParts.getJSONObject(0).optString("text", "");
                                reply = cleanAiReply(reply);
                                postSuccess(callback, reply);
                                return;
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
                        // Si es error de cuota o autenticacion (401, 403, 429), no continuar intentando otros modelos
                        break;
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

    private static void requestCloudOpenAi(String endpoint, String model, String apiKey, String systemPrompt, String userMessage, SkinData skin, final AiCallback callback) {
        try {
            String baseUrl = endpoint.endsWith("/") ? endpoint.substring(0, endpoint.length() - 1) : endpoint;
            if (!baseUrl.endsWith("/chat/completions")) {
                if (baseUrl.endsWith("/v1")) {
                    baseUrl += "/chat/completions";
                } else {
                    baseUrl += "/v1/chat/completions";
                }
            }

            URL url = new URL(baseUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            if (apiKey != null && !apiKey.isEmpty()) {
                conn.setRequestProperty("Authorization", "Bearer " + apiKey);
            }
            conn.setConnectTimeout(8000);
            conn.setReadTimeout(15000);
            conn.setDoOutput(true);

            JSONObject root = new JSONObject();
            root.put("model", model);
            JSONArray messages = new JSONArray();

            if (systemPrompt != null && !systemPrompt.isEmpty()) {
                JSONObject sysMsg = new JSONObject();
                sysMsg.put("role", "system");
                sysMsg.put("content", systemPrompt);
                messages.put(sysMsg);
            }

            JSONObject userMsg = new JSONObject();
            userMsg.put("role", "user");
            userMsg.put("content", userMessage);
            messages.put(userMsg);

            root.put("messages", messages);
            root.put("max_tokens", 250);
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
                        String reply = msg.optString("content", "");
                        reply = cleanAiReply(reply);
                        postSuccess(callback, reply);
                        return;
                    }
                }
                postSuccess(callback, "Servidor Cloud respondio sin contenido.");
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
        return raw.trim()
                .replaceAll("\\*\\*", "")
                .replaceAll("^\"|\"$", "");
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
