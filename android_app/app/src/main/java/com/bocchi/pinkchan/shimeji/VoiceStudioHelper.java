package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.AssetFileDescriptor;
import android.media.MediaPlayer;
import android.os.Handler;
import android.os.Looper;
import android.util.Base64;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
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
        public final String lang;

        public VoiceProfile(String name, String prebuilt, String style, String prompt, String testDialogue, String lang) {
            this.name = name;
            this.prebuilt = prebuilt;
            this.style = style;
            this.prompt = prompt;
            this.testDialogue = testDialogue;
            this.lang = lang;
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
            "E-eto... hola... soy Bocchi-chan... gusto en conocerte... por favor cuidame...",
            "ja"
        ));

        PROFILES.put("konata", new VoiceProfile(
            "Konata Izumi",
            "Puck",
            "energetic, teasing, deadpan yet playful and mischievous anime otaku",
            "A witty, lively 17-year-old otaku anime girl. Her voice has a distinctive playful and slightly nasal tone, deadpan yet full of comedic energy, speaking quickly with teasing inflections, anime enthusiast flair, and gamer excitement.",
            "Timotei, Timotei! Otaku power al maximo, esta noche hay maraton de anime y videojuegos!",
            "ja"
        ));

        PROFILES.put("monika", new VoiceProfile(
            "Monika",
            "Aoede",
            "warm, intelligent, soothing, elegant and charismatic with gentle affection",
            "A warm, mature, confident 18-year-old literature club president. Her voice is soothing, articulate, elegant, melodious, and intimate, speaking with caring intelligence, philosophical poise, and gentle devotion.",
            "Hola mi amor! Cada dia es un hermoso dia en nuestro club. Eres lo mas importante para mi.",
            "en"
        ));

        PROFILES.put("natsuki", new VoiceProfile(
            "Natsuki",
            "Kore",
            "feisty, snappy, high-pitched tsundere with defensive cuteness",
            "A feisty, high-pitched tsundere teenage anime girl. Her voice is sharp, spirited, snappy and slightly haughty when flustered, but unmistakably cute, youthful, and sweet underneath.",
            "B-Baka! No es como si estuviera esperando a que me hablaras ni nada por el estilo... pero gracias.",
            "en"
        ));

        PROFILES.put("sayori", new VoiceProfile(
            "Sayori",
            "Kore",
            "cheerful, bubbly, bright, genki and melodious with sunny optimism",
            "A bright, bubbly, cheerful 18-year-old schoolgirl. Her voice is melodious, sweet, sunny, full of innocent enthusiasm and warm compassion, speaking with an animated joyful bounce.",
            "Yay! Buenos dias! Todo brilla tanto hoy, vamos a comer galletitas juntos!",
            "en"
        ));

        PROFILES.put("yuri", new VoiceProfile(
            "Yuri",
            "Aoede",
            "soft-spoken, deep, poetic, elegant, gentle and introspective",
            "A quiet, deeply introspective, elegant young woman. Her voice is soft, breathy, lower in register, speaking slowly and deliberately with intellectual grace, gentle humility, and poetic nuance.",
            "Un buen libro de misterio y una taza de te caliente calman el alma... Es un placer compartir este momento contigo.",
            "en"
        ));

        PROFILES.put("hachi", new VoiceProfile(
            "Hachi (Hachiware)",
            "Puck",
            "innocent, childish, bright, squeaky and enthusiastic mascot",
            "A young, innocent, cheerful childish mascot. The voice is bright, sweet, high-pitched, curious, friendly, and bubbly, bursting with youthful happiness and wonder.",
            "Araragi-san! Me mordi la lengua por accidente! Pero estoy bien, que alegria verte hoy!",
            "ja"
        ));

        PROFILES.put("usagi", new VoiceProfile(
            "Usagi",
            "Puck",
            "hyperactive, eccentric, loud, chaotic high-pitched fast bursts and screams",
            "A chaotic, hyperactive, fearless rabbit mascot creature. Speaks in eccentric, high-pitched, lightning-fast bursts, hilarious shrieks, and uninhibited energetic sounds.",
            "Ura! Yahaha! Energia magica al limite! Nadie puede detenerme hoy!",
            "ja"
        ));

        PROFILES.put("pusheen", new VoiceProfile(
            "Pusheen",
            "Kore",
            "ultra-soft, sleepy, purring, adorable kitten whispers and cozy murmurs",
            "An ultra-soft, gentle, sleepy kawaii cartoon cat. Speaks in a cozy, baby-soft, purring whisper with sweet murmurs, relaxed and delightfully cuddly.",
            "Miau... hora de comer bocadillos y dormir una siesta calientita en tu regazo.",
            "en"
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

    public static boolean playCharacterAsset(Context context, String skinId, String clipName, MediaPlayer existingPlayer) {
        if (context == null) return false;
        String sKey = (skinId != null ? skinId.toLowerCase().trim() : "bocchi");
        String[] candidates = new String[] {
            "sounds/" + sKey + "/" + clipName + ".mp3",
            "sounds/" + sKey + "/idle.mp3",
            "sounds/" + sKey + "/greeting.mp3"
        };

        for (String path : candidates) {
            try {
                AssetFileDescriptor afd = context.getAssets().openFd(path);
                MediaPlayer mp = (existingPlayer != null) ? existingPlayer : new MediaPlayer();
                mp.reset();
                mp.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
                afd.close();
                mp.prepare();
                mp.start();
                if (existingPlayer == null) {
                    mp.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
                        @Override
                        public void onCompletion(MediaPlayer mediaPlayer) {
                            try { mediaPlayer.release(); } catch (Exception ignored) {}
                        }
                    });
                }
                return true;
            } catch (Exception ignored) {}
        }
        return false;
    }

    public static void synthesizeSpeech(final Context context, final String text, final String skinId, final VoiceStudioCallback callback) {
        if (text == null || text.trim().isEmpty()) {
            if (callback != null) callback.onError("Texto vacio");
            return;
        }

        final SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        final String apiKey = sp.getString(MainActivity.KEY_GEMINI_KEY, "").trim();

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
                    String sKey = (skinId != null ? skinId.toLowerCase() : "bocchi");
                    File cacheDir = context.getCacheDir();

                    // FASE 1: Gemini 3.8 Flash TTS Interactions API
                    if (!apiKey.isEmpty()) {
                        try {
                            String urlStr1 = "https://generativelanguage.googleapis.com/v1beta/interactions?key=" + apiKey;
                            JSONObject root1 = new JSONObject();
                            root1.put("model", "gemini-3.8-flash-tts");

                            JSONArray inputArr = new JSONArray();
                            JSONObject inputObj = new JSONObject();
                            inputObj.put("type", "user_input");

                            JSONArray contentArr = new JSONArray();
                            JSONObject textObj = new JSONObject();
                            textObj.put("type", "text");
                            textObj.put("text", clean);

                            JSONArray annotArr = new JSONArray();
                            JSONObject metaObj = new JSONObject();
                            metaObj.put("type", "speech_metadata");
                            metaObj.put("style", prof.style);
                            annotArr.put(metaObj);
                            textObj.put("annotations", annotArr);
                            contentArr.put(textObj);
                            inputObj.put("content", contentArr);
                            inputArr.put(inputObj);
                            root1.put("input", inputArr);

                            JSONObject respFormat = new JSONObject();
                            respFormat.put("type", "audio");
                            respFormat.put("mime_type", "audio/wav");
                            root1.put("response_format", respFormat);

                            JSONObject genCfg1 = new JSONObject();
                            JSONArray speechCfgArr = new JSONArray();
                            JSONObject spItem = new JSONObject();
                            spItem.put("voice", targetVoice);
                            speechCfgArr.put(spItem);
                            genCfg1.put("speech_config", speechCfgArr);
                            root1.put("generation_config", genCfg1);

                            byte[] resBytes1 = postJson(urlStr1, root1.toString());
                            if (resBytes1 != null && resBytes1.length > 0) {
                                JSONObject respObj1 = new JSONObject(new String(resBytes1, "UTF-8"));
                                String b64Audio = null;
                                JSONObject outAud = respObj1.optJSONObject("output_audio");
                                if (outAud == null) outAud = respObj1.optJSONObject("outputAudio");
                                if (outAud != null) b64Audio = outAud.optString("data", null);

                                if (b64Audio == null) {
                                    JSONArray steps = respObj1.optJSONArray("steps");
                                    if (steps != null) {
                                        for (int s = 0; s < steps.length(); s++) {
                                            JSONObject st = steps.getJSONObject(s);
                                            JSONArray sContents = st.optJSONArray("content");
                                            if (sContents != null) {
                                                for (int c = 0; c < sContents.length(); c++) {
                                                    JSONObject co = sContents.getJSONObject(c);
                                                    if ("audio".equals(co.optString("type")) && co.has("data")) {
                                                        b64Audio = co.optString("data");
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }

                                if (b64Audio != null && !b64Audio.isEmpty()) {
                                    File fOut = new File(cacheDir, "vs_interact_" + sKey + ".wav");
                                    byte[] aud = Base64.decode(b64Audio, Base64.DEFAULT);
                                    writeFile(fOut, aud);
                                    postSuccess(callback, fOut);
                                    return;
                                }
                            }
                        } catch (Exception ignored) {}

                        // FASE 2: Gemini 2.5 Flash Audio GenerateContent
                        try {
                            String urlStr2 = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + apiKey;
                            JSONObject root2 = new JSONObject();
                            JSONArray contents = new JSONArray();
                            JSONObject cItem = new JSONObject();
                            cItem.put("role", "user");
                            JSONArray parts = new JSONArray();
                            JSONObject part = new JSONObject();
                            part.put("text", "Character " + prof.name + ". Roleplay with voice style " + prof.style + ": " + clean);
                            parts.put(part);
                            cItem.put("parts", parts);
                            contents.put(cItem);
                            root2.put("contents", contents);

                            JSONObject genCfg2 = new JSONObject();
                            JSONArray modArr = new JSONArray();
                            modArr.put("AUDIO");
                            genCfg2.put("responseModalities", modArr);

                            JSONObject spCfg = new JSONObject();
                            JSONObject vc = new JSONObject();
                            JSONObject pvc = new JSONObject();
                            pvc.put("voiceName", prof.prebuilt);
                            vc.put("prebuiltVoiceConfig", pvc);
                            spCfg.put("voiceConfig", vc);
                            genCfg2.put("speechConfig", spCfg);
                            root2.put("generationConfig", genCfg2);

                            byte[] resBytes2 = postJson(urlStr2, root2.toString());
                            if (resBytes2 != null && resBytes2.length > 0) {
                                JSONObject respObj2 = new JSONObject(new String(resBytes2, "UTF-8"));
                                JSONArray cands = respObj2.optJSONArray("candidates");
                                if (cands != null && cands.length() > 0) {
                                    JSONArray pParts = cands.getJSONObject(0).optJSONObject("content").optJSONArray("parts");
                                    if (pParts != null) {
                                        for (int i = 0; i < pParts.length(); i++) {
                                            JSONObject inline = pParts.getJSONObject(i).optJSONObject("inlineData");
                                            if (inline == null) inline = pParts.getJSONObject(i).optJSONObject("inline_data");
                                            if (inline != null && inline.has("data")) {
                                                String b64 = inline.optString("data");
                                                File fOut2 = new File(cacheDir, "vs_gen25_" + sKey + ".wav");
                                                writeFile(fOut2, Base64.decode(b64, Base64.DEFAULT));
                                                postSuccess(callback, fOut2);
                                                return;
                                            }
                                        }
                                    }
                                }
                            }
                        } catch (Exception ignored) {}
                    }

                    // FASE 3: Motor Fonetico Nativo (Audio Online Japones/Ingles sin API Key)
                    try {
                        String ttsLang = prof.lang != null ? prof.lang : "ja";
                        boolean hasSpanish = clean.toLowerCase().matches(".*\\b(hola|como|buenos|dias|gracias|amigo|por favor)\\b.*");
                        if (hasSpanish) ttsLang = "es";

                        String gUrl = "https://translate.google.com/translate_tts?ie=UTF-8&tl=" + ttsLang + "&client=tw-ob&q=" + URLEncoder.encode(clean, "UTF-8");
                        HttpURLConnection gConn = (HttpURLConnection) new URL(gUrl).openConnection();
                        gConn.setRequestProperty("User-Agent", "Mozilla/5.0");
                        gConn.setConnectTimeout(8000);
                        gConn.setReadTimeout(10000);
                        if (gConn.getResponseCode() == 200) {
                            InputStream is = gConn.getInputStream();
                            File fOut3 = new File(cacheDir, "vs_phonetic_" + sKey + ".mp3");
                            FileOutputStream fos = new FileOutputStream(fOut3);
                            byte[] buf = new byte[4096];
                            int r;
                            while ((r = is.read(buf)) != -1) fos.write(buf, 0, r);
                            fos.flush();
                            fos.close();
                            is.close();
                            postSuccess(callback, fOut3);
                            return;
                        }
                    } catch (Exception ignored) {}

                    // FASE 4: Banco de Audios Originales en assets
                    try {
                        String assetPath = "sounds/" + sKey + "/idle.mp3";
                        AssetFileDescriptor afd = context.getAssets().openFd(assetPath);
                        InputStream is = afd.createInputStream();
                        File fOut4 = new File(cacheDir, "vs_asset_" + sKey + ".mp3");
                        FileOutputStream fos = new FileOutputStream(fOut4);
                        byte[] buf = new byte[4096];
                        int r;
                        while ((r = is.read(buf)) != -1) fos.write(buf, 0, r);
                        fos.flush();
                        fos.close();
                        is.close();
                        afd.close();
                        postSuccess(callback, fOut4);
                        return;
                    } catch (Exception ignored) {}

                    postError(callback, "No se pudo obtener audio para " + prof.name);
                } catch (Exception e) {
                    postError(callback, "Error general Voice Studio: " + e.getMessage());
                }
            }
        });
    }

    private static byte[] postJson(String urlStr, String jsonPayload) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        conn.setDoOutput(true);
        conn.setConnectTimeout(15000);
        conn.setReadTimeout(18000);

        byte[] postBytes = jsonPayload.getBytes("UTF-8");
        OutputStream os = conn.getOutputStream();
        os.write(postBytes);
        os.flush();
        os.close();

        int code = conn.getResponseCode();
        if (code == 200) {
            InputStream is = conn.getInputStream();
            java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
            byte[] buf = new byte[4096];
            int r;
            while ((r = is.read(buf)) != -1) baos.write(buf, 0, r);
            is.close();
            return baos.toByteArray();
        }
        return null;
    }

    private static void writeFile(File file, byte[] data) throws Exception {
        FileOutputStream fos = new FileOutputStream(file);
        fos.write(data);
        fos.flush();
        fos.close();
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
