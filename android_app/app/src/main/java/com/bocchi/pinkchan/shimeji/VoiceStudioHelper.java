package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import android.util.Base64;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class VoiceStudioHelper {

    public interface VoiceStudioCallback {
        void onSuccess(File audioFile);
        void onError(String error);
    }

    public static class VoiceProfile {
        public final String name;
        public final String prebuilt;
        public final String style;
        public final String prompt;
        public final String testDialogue;

        public VoiceProfile(String name, String prebuilt, String style, String prompt, String testDialogue) {
            this.name = name;
            this.prebuilt = prebuilt;
            this.style = style;
            this.prompt = prompt;
            this.testDialogue = testDialogue;
        }
    }

    private static final ExecutorService executor = Executors.newCachedThreadPool();
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());
    private static final Map<String, VoiceProfile> PROFILES = new HashMap<>();

    static {
        PROFILES.put("bocchi", new VoiceProfile(
            "Bocchi (Hitori Gotoh)",
            "Kore",
            "shy, trembling, quiet whispers with hesitant anxious stutters",
            "A timid, socially anxious 16-year-old Japanese high school girl guitarist. Her voice is soft, breathy, trembling, quiet, prone to hesitant stutters, flustered squeaks, and nervous whispers, yet deeply endearing, sweet, and sincere.",
            "E-eto... hola... soy Bocchi-chan... gusto en conocerte... por favor cuidame..."
        ));

        PROFILES.put("konata", new VoiceProfile(
            "Konata Izumi",
            "Puck",
            "energetic, teasing, deadpan yet playful and mischievous anime otaku",
            "A witty, lively 17-year-old otaku anime girl. Her voice has a distinctive playful and slightly nasal tone, deadpan yet full of comedic energy, speaking quickly with teasing inflections, anime enthusiast flair, and gamer excitement.",
            "Timotei, Timotei! Otaku power al maximo, esta noche hay maraton de anime y videojuegos!"
        ));

        PROFILES.put("monika", new VoiceProfile(
            "Monika",
            "Aoede",
            "warm, intelligent, soothing, elegant and charismatic with gentle affection",
            "A warm, mature, confident 18-year-old literature club president. Her voice is soothing, articulate, elegant, melodious, and intimate, speaking with caring intelligence, philosophical poise, and gentle devotion.",
            "Hola mi amor! Cada dia es un hermoso dia en nuestro club. Eres lo mas importante para mi."
        ));

        PROFILES.put("natsuki", new VoiceProfile(
            "Natsuki",
            "Kore",
            "feisty, snappy, high-pitched tsundere with defensive cuteness",
            "A feisty, high-pitched tsundere teenage anime girl. Her voice is sharp, spirited, snappy and slightly haughty when flustered, but unmistakably cute, youthful, and sweet underneath.",
            "B-Baka! No es como si estuviera esperando a que me hablaras ni nada por el estilo... pero gracias."
        ));

        PROFILES.put("sayori", new VoiceProfile(
            "Sayori",
            "Kore",
            "cheerful, bubbly, bright, genki and melodious with sunny optimism",
            "A bright, bubbly, cheerful 18-year-old schoolgirl. Her voice is melodious, sweet, sunny, full of innocent enthusiasm and warm compassion, speaking with an animated joyful bounce.",
            "Yay! Buenos dias! Todo brilla tanto hoy, vamos a comer galletitas juntos!"
        ));

        PROFILES.put("yuri", new VoiceProfile(
            "Yuri",
            "Aoede",
            "soft-spoken, deep, poetic, elegant, gentle and introspective",
            "A quiet, deeply introspective, elegant young woman. Her voice is soft, breathy, lower in register, speaking slowly and deliberately with intellectual grace, gentle humility, and poetic nuance.",
            "Un buen libro de misterio y una taza de te caliente calman el alma... Es un placer compartir este momento contigo."
        ));

        PROFILES.put("hachi", new VoiceProfile(
            "Hachi (Hachiware)",
            "Puck",
            "innocent, childish, bright, squeaky and enthusiastic mascot",
            "A young, innocent, cheerful childish mascot. The voice is bright, sweet, high-pitched, curious, friendly, and bubbly, bursting with youthful happiness and wonder.",
            "Araragi-san! Me mordi la lengua por accidente! Pero estoy bien, que alegria verte hoy!"
        ));

        PROFILES.put("usagi", new VoiceProfile(
            "Usagi",
            "Puck",
            "hyperactive, eccentric, loud, chaotic high-pitched fast bursts and screams",
            "A chaotic, hyperactive, fearless rabbit mascot creature. Speaks in eccentric, high-pitched, lightning-fast bursts, hilarious shrieks, and uninhibited energetic sounds.",
            "Ura! Yahaha! Energia magica al limite! Nadie puede detenerme hoy!"
        ));

        PROFILES.put("pusheen", new VoiceProfile(
            "Pusheen",
            "Kore",
            "ultra-soft, sleepy, purring, adorable kitten whispers and cozy murmurs",
            "An ultra-soft, gentle, sleepy kawaii cartoon cat. Speaks in a cozy, baby-soft, purring whisper with sweet murmurs, relaxed and delightfully cuddly.",
            "Miau... hora de comer bocadillos y dormir una siesta calientita en tu regazo."
        ));
    }

    public static VoiceProfile getProfile(String skinId) {
        if (skinId == null) return PROFILES.get("bocchi");
        String lower = skinId.toLowerCase().trim();
        for (Map.Entry<String, VoiceProfile> e : PROFILES.entrySet()) {
            if (lower.contains(e.getKey())) {
                return e.getValue();
            }
        }
        return PROFILES.get("bocchi");
    }

    public static Map<String, VoiceProfile> getAllProfiles() {
        return PROFILES;
    }

    public static void synthesizeSpeech(final Context context, final String text, final String skinId, final VoiceStudioCallback callback) {
        if (text == null || text.trim().isEmpty()) {
            if (callback != null) callback.onError("Texto vacio");
            return;
        }

        final SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        final String apiKey = sp.getString(MainActivity.KEY_GEMINI_KEY, "").trim();
        if (apiKey.isEmpty()) {
            if (callback != null) callback.onError("Sin Gemini API Key");
            return;
        }

        executor.execute(new Runnable() {
            @Override
            public void run() {
                try {
                    String clean = AgentToolExecutor.stripTags(text).trim();
                    if (clean.isEmpty()) {
                        postError(callback, "Texto vacio despues de limpiar etiquetas");
                        return;
                    }

                    final VoiceProfile prof = getProfile(skinId);
                    String customVoiceId = sp.getString("voice_studio_id_" + (skinId != null ? skinId.toLowerCase() : "bocchi"), "");
                    String targetVoice = (!customVoiceId.trim().isEmpty()) ? customVoiceId.trim() : prof.prebuilt;

                    String urlStr = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent?key=" + apiKey;
                    URL url = new URL(urlStr);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
                    conn.setDoOutput(true);
                    conn.setConnectTimeout(25000);
                    conn.setReadTimeout(30000);

                    JSONObject root = new JSONObject();
                    JSONArray contents = new JSONArray();
                    JSONObject contentItem = new JSONObject();
                    contentItem.put("role", "user");

                    JSONArray parts = new JSONArray();
                    JSONObject part = new JSONObject();
                    part.put("text", clean);

                    JSONObject speechMeta = new JSONObject();
                    speechMeta.put("style", prof.style);
                    part.put("speech_metadata", speechMeta);
                    parts.put(part);

                    contentItem.put("parts", parts);
                    contents.put(contentItem);
                    root.put("contents", contents);

                    JSONObject genConfig = new JSONObject();
                    JSONArray modal = new JSONArray();
                    modal.put("AUDIO");
                    genConfig.put("responseModalities", modal);

                    JSONObject speechConfig = new JSONObject();
                    JSONObject voiceConfig = new JSONObject();
                    voiceConfig.put("voice", targetVoice);
                    speechConfig.put("voiceConfig", voiceConfig);
                    genConfig.put("speechConfig", speechConfig);

                    root.put("generationConfig", genConfig);

                    byte[] postBytes = root.toString().getBytes("UTF-8");
                    OutputStream os = conn.getOutputStream();
                    os.write(postBytes);
                    os.flush();
                    os.close();

                    int responseCode = conn.getResponseCode();
                    if (responseCode == 200) {
                        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                        StringBuilder sb = new StringBuilder();
                        String line;
                        while ((line = br.readLine()) != null) sb.append(line);
                        br.close();

                        JSONObject respObj = new JSONObject(sb.toString());
                        JSONArray candidates = respObj.optJSONArray("candidates");
                        if (candidates == null || candidates.length() == 0) {
                            postError(callback, "Respuesta sin candidatos de audio");
                            return;
                        }

                        JSONObject firstCand = candidates.getJSONObject(0);
                        JSONObject candContent = firstCand.optJSONObject("content");
                        if (candContent == null) {
                            postError(callback, "Candidato sin contenido");
                            return;
                        }

                        JSONArray candParts = candContent.optJSONArray("parts");
                        if (candParts == null || candParts.length() == 0) {
                            postError(callback, "Contenido sin partes");
                            return;
                        }

                        String b64Audio = null;
                        for (int i = 0; i < candParts.length(); i++) {
                            JSONObject p = candParts.getJSONObject(i);
                            JSONObject inline = p.optJSONObject("inlineData");
                            if (inline == null) inline = p.optJSONObject("inline_data");
                            if (inline != null) {
                                b64Audio = inline.optString("data", null);
                                if (b64Audio != null) break;
                            }
                        }

                        if (b64Audio == null || b64Audio.isEmpty()) {
                            postError(callback, "No se recibieron datos de audio");
                            return;
                        }

                        byte[] audioBytes = Base64.decode(b64Audio, Base64.DEFAULT);
                        String sKey = (skinId != null ? skinId.toLowerCase() : "bocchi");
                        File cacheDir = context.getCacheDir();
                        File audioFile = new File(cacheDir, "vs_" + sKey + ".wav");

                        FileOutputStream fos = new FileOutputStream(audioFile);
                        fos.write(audioBytes);
                        fos.flush();
                        fos.close();

                        postSuccess(callback, audioFile);
                    } else {
                        BufferedReader errBr = new BufferedReader(new InputStreamReader(
                            conn.getErrorStream() != null ? conn.getErrorStream() : conn.getInputStream(), "UTF-8"));
                        StringBuilder errSb = new StringBuilder();
                        String el;
                        while ((el = errBr.readLine()) != null) errSb.append(el);
                        errBr.close();
                        postError(callback, "Error HTTP " + responseCode + ": " + errSb.toString());
                    }
                } catch (Exception e) {
                    postError(callback, "Excepcion Voice Studio: " + e.getMessage());
                }
            }
        });
    }

    private static void postSuccess(final VoiceStudioCallback callback, final File file) {
        mainHandler.post(new Runnable() {
            @Override
            public void run() {
                if (callback != null) callback.onSuccess(file);
            }
        });
    }

    private static void postError(final VoiceStudioCallback callback, final String error) {
        mainHandler.post(new Runnable() {
            @Override
            public void run() {
                if (callback != null) callback.onError(error);
            }
        });
    }
}

