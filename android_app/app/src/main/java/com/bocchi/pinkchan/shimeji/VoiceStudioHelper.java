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
        public final String styleEs;
        public final String promptEs;
        public final String testDialogueEs;
        public final String styleEn;
        public final String promptEn;
        public final String testDialogueEn;

        public VoiceProfile(String name, String prebuilt, String style, String prompt, String testDialogue, String lang,
                            String styleEs, String promptEs, String testDialogueEs,
                            String styleEn, String promptEn, String testDialogueEn) {
            this.name = name;
            this.prebuilt = prebuilt;
            this.style = style;
            this.prompt = prompt;
            this.testDialogue = testDialogue;
            this.lang = lang;
            this.styleEs = styleEs;
            this.promptEs = promptEs;
            this.testDialogueEs = testDialogueEs;
            this.styleEn = styleEn;
            this.promptEn = promptEn;
            this.testDialogueEn = testDialogueEn;
        }

        public String getDialogueForLang(String dubLang) {
            if ("es".equalsIgnoreCase(dubLang)) return testDialogueEs != null ? testDialogueEs : testDialogue;
            if ("en".equalsIgnoreCase(dubLang)) return testDialogueEn != null ? testDialogueEn : testDialogue;
            return testDialogue;
        }

        public String getPromptForLang(String dubLang) {
            if ("es".equalsIgnoreCase(dubLang)) return promptEs != null ? promptEs : prompt;
            if ("en".equalsIgnoreCase(dubLang)) return promptEn != null ? promptEn : prompt;
            return prompt;
        }

        public String getStyleForLang(String dubLang) {
            if ("es".equalsIgnoreCase(dubLang)) return styleEs != null ? styleEs : style;
            if ("en".equalsIgnoreCase(dubLang)) return styleEn != null ? styleEn : style;
            return style;
        }
    }

    private static final ExecutorService executor = Executors.newCachedThreadPool();
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());
    private static final Map<String, VoiceProfile> PROFILES = new HashMap<>();

    static {
        PROFILES.put("bocchi", new VoiceProfile(
            "Bocchi (Hitori Gotoh)", "Kore",
            "shy, trembling, quiet whispers with hesitant anxious stutters",
            "A timid, socially anxious 16-year-old Japanese high school girl guitarist. Soft, breathy, trembling, quiet whispers.",
            "E-eto... Bocchi desu... yoroshiku onegaishimasu...", "ja",
            "timida, tartamudeando nerviosa, susurros timidos en doblaje latino",
            "Actriz de doblaje latino para Bocchi: voz timida, dulce, temblorosa, con tartamudeos nerviosos adorables de chica de preparatoria.",
            "E-eto... h-hola... soy Bocchi... por favor no me mires tan fijamente...",
            "shy, stammering, nervous cute anxious high-school girl in English anime dub",
            "English anime dub voice actress for Bocchi: soft, breathy, nervous stammering, sweet socially anxious high school girl.",
            "U-um... hello... I'm Bocchi... please don't look at me too much..."
        ));

        PROFILES.put("konata", new VoiceProfile(
            "Konata Izumi", "Puck",
            "energetic, teasing, deadpan yet playful and mischievous anime otaku",
            "A witty, lively 17-year-old otaku anime girl. Distinctive playful, slightly nasal tone, anime enthusiast flair.",
            "Timotei, Timotei! Otaku power zenkai de iku yo!", "ja",
            "energetica, picara, bromista, tono otaku gamer en doblaje latino",
            "Actriz de doblaje latino para Konata Izumi de Lucky Star: voz aguda, energica, divertida, otaku con comentarios rapidos y picaros.",
            "Hola, que onda! Listo para un maraton de anime y videojuegos toda la noche?",
            "energetic, witty, playful, sarcastic otaku anime girl in English dub",
            "English dub voice actress for Konata Izumi: iconic witty, deadpan and lively anime otaku gamer girl.",
            "Yo! Ready for an all-night anime and gaming marathon?"
        ));

        PROFILES.put("monika", new VoiceProfile(
            "Monika", "Aoede",
            "warm, intelligent, soothing, elegant and charismatic with gentle affection",
            "A warm, mature, confident 18-year-old literature club president. Caring intelligence, philosophical poise.",
            "Every day, I imagine a future where I can be with you. Just Monika.", "en",
            "calida, inteligente, dulce, elegante, carismatica en doblaje latino",
            "Actriz de doblaje latino para Monika de DDLC: voz calida, melodiosa, madura, inteligente y tierna con devocion romantica.",
            "Hola mi amor! Cada dia es hermoso en nuestro club. Eres lo mas importante para mi. Solo Monika.",
            "warm, intelligent, soothing, elegant, romantic devotion in English",
            "Official English voice for Monika from Doki Doki Literature Club: soothing, mature, caring, poetic.",
            "Hi there! I am so glad you are here with me in our Literature Club. Just Monika."
        ));

        PROFILES.put("natsuki", new VoiceProfile(
            "Natsuki", "Kore",
            "feisty, snappy, high-pitched tsundere with defensive cuteness",
            "A feisty, high-pitched tsundere teenage anime girl. Sharp, spirited, snappy and cute.",
            "B-Baka! Why are you staring at me like that? Manga is literature!", "en",
            "tsundere energica, voz aguda, desafiante y tierna en doblaje latino",
            "Actriz de doblaje latino para Natsuki de DDLC: voz tsundere aguda, caprichosa, picante y tierna con orgullo juvenil.",
            "Oye! No es como si me alegrara de verte ni nada de eso... b-baka! Pero toma un pastelito.",
            "feisty, snappy, high-pitched tsundere with defensive cuteness in English",
            "English dub voice for Natsuki from DDLC: sharp, spirited, cute tsundere teenage girl.",
            "Hey! It's not like I wanted to see you or anything... b-baka! But here is a cupcake."
        ));

        PROFILES.put("sayori", new VoiceProfile(
            "Sayori", "Kore",
            "cheerful, bubbly, bright, genki and melodious with sunny optimism",
            "A bright, bubbly, cheerful 18-year-old schoolgirl. Melodious, sweet, sunny enthusiasm.",
            "Good morning! Having fun with you is the best thing ever!", "en",
            "alegre, tierna, infantil, entusiasta en doblaje latino",
            "Actriz de doblaje latino para Sayori de DDLC: voz alegre, infantil, dulce, melodiosa y llena de sol y optimismo.",
            "Yay! Buenos dias! El sol brilla hermoso hoy, vamos a comer galletitas juntos!",
            "cheerful, bubbly, bright, sunny optimism in English",
            "English voice for Sayori from DDLC: sweet, cheerful, sunny and innocent high school friend.",
            "Yay! Good morning! The sun is shining and everything is bright, let's get cookies!"
        ));

        PROFILES.put("yuri", new VoiceProfile(
            "Yuri", "Aoede",
            "soft-spoken, deep, poetic, elegant, gentle and introspective",
            "A quiet, deeply introspective, elegant young woman. Breathy, lower register, intellectual grace.",
            "Lost in the pages of this book... The atmosphere is wonderfully tranquil.", "en",
            "voz suave, elegante, profunda, poetica y timida en doblaje latino",
            "Actriz de doblaje latino para Yuri de DDLC: voz suave, elegante, intelectual, profunda, pausada y con gracia poetica.",
            "Buenos dias... Una taza de te caliente y un buen libro calman el alma... Es un placer estar contigo.",
            "soft-spoken, deep, poetic, elegant and introspective in English",
            "English voice for Yuri from DDLC: gentle, breathy, introspective, articulate and elegant young woman.",
            "Good day... A warm cup of jasmine tea and a good book brings true peace to the soul."
        ));

        PROFILES.put("hachi", new VoiceProfile(
            "Hachi (Hachiware)", "Puck",
            "innocent, childish, bright, squeaky and enthusiastic mascot",
            "A young, innocent, cheerful childish mascot. Bright, sweet, high-pitched, curious, friendly.",
            "Nanto ka nare! Hachiware da yo! Kyou mo issho ni ganbarou!", "ja",
            "mascota inocente, voz infantil aguda, tierna y entusiasta en doblaje latino",
            "Actriz de doblaje latino para Hachiware de Chiikawa: voz muy tierna, infantil, positiva, curiosa y amistosa.",
            "Hola! Soy Hachiware! Que gran alegria verte hoy! De alguna manera todo saldra bien!",
            "innocent, childish, bright mascot voice in English dub",
            "English dub voice for Hachiware: bright, squeaky, friendly, pure-hearted cute creature.",
            "Hi there! I'm Hachiware! It is so wonderful to see you today! Keep smiling!"
        ));

        PROFILES.put("usagi", new VoiceProfile(
            "Usagi", "Puck",
            "hyperactive, eccentric, loud, chaotic high-pitched fast bursts and screams",
            "A chaotic, hyperactive, fearless rabbit mascot creature. Eccentric bursts, hilarious shrieks.",
            "Urrr-a! Yaha! Pululululu! Yahaha!", "ja",
            "conejo hiperactivo, caos divertido, energia magica en doblaje latino",
            "Voz de doblaje latino para Usagi de Chiikawa: gritos comicos veloces, hiperactividad, excentrico y lleno de energia magica.",
            "Yahaaa! Urrr-aaa! Energia de conejo magica al maximo! Nadie puede detenerme!",
            "hyperactive, eccentric, hilarious bursts in English dub",
            "English dub voice for Usagi: fast, chaotic, fearless energetic bunny screaming with joy.",
            "Yaha! Urrr-a! Maximum rocket rabbit power engaged! Let's go!"
        ));

        PROFILES.put("pusheen", new VoiceProfile(
            "Pusheen", "Kore",
            "ultra-soft, sleepy, purring, adorable kitten whispers and cozy murmurs",
            "An ultra-soft, gentle, sleepy kawaii cartoon cat. Cozy baby-soft purring whispers.",
            "Miau... prrr... purrrr... sleepy cozy kitten nap time.", "en",
            "gatita dulce, maullidos tiernos y susurros adorables en doblaje latino",
            "Voz de doblaje latino para la gatita Pusheen: susurros de bebe gatito, ronroneos suaves, mimos y amor por los bocadillos.",
            "Miau! Hola amiguito, hora de mimos y comidita rica calientita en tu regazo!",
            "ultra-soft, sleepy kitten whispers and cozy murmurs in English",
            "English voice for Pusheen the cat: cozy baby kitten whispers, soft purrs and snack love.",
            "Meow! Hello friend, time for sweet cuddles, cozy catnaps and yummy snacks!"
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
        SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        String dubLang = sp.getString("voice_dub_lang", "es");
        return playCharacterAsset(context, skinId, clipName, dubLang, existingPlayer);
    }

    public static boolean playCharacterAsset(Context context, String skinId, String clipName, String dubLang, MediaPlayer existingPlayer) {
        if (context == null) return false;
        String sKey = (skinId != null ? skinId.toLowerCase().trim() : "bocchi");
        String lang = (dubLang != null ? dubLang.toLowerCase().trim() : "es");

        java.util.List<String> candidates = new java.util.ArrayList<>();
        if ("es".equals(lang)) {
            candidates.add("sounds/" + sKey + "/" + clipName + "_es.mp3");
            candidates.add("sounds/" + sKey + "/" + clipName + ".mp3");
            candidates.add("sounds/" + sKey + "/" + clipName + "_en.mp3");
        } else if ("en".equals(lang)) {
            candidates.add("sounds/" + sKey + "/" + clipName + "_en.mp3");
            candidates.add("sounds/" + sKey + "/" + clipName + ".mp3");
            candidates.add("sounds/" + sKey + "/" + clipName + "_es.mp3");
        } else {
            candidates.add("sounds/" + sKey + "/" + clipName + ".mp3");
            candidates.add("sounds/" + sKey + "/" + clipName + "_es.mp3");
            candidates.add("sounds/" + sKey + "/" + clipName + "_en.mp3");
        }
        candidates.add("sounds/" + sKey + "/idle.mp3");
        candidates.add("sounds/" + sKey + "/greeting.mp3");

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
                    String dubLang = sp.getString("voice_dub_lang", "es");
                    String customVoiceId = sp.getString("voice_studio_id_" + (skinId != null ? skinId.toLowerCase() : "bocchi"), "");
                    String targetVoice = (!customVoiceId.trim().isEmpty()) ? customVoiceId.trim() : prof.prebuilt;
                    String sKey = (skinId != null ? skinId.toLowerCase() : "bocchi");
                    File cacheDir = context.getCacheDir();

                    String roleStyle = prof.getStyleForLang(dubLang);
                    String rolePrompt = prof.getPromptForLang(dubLang);

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
                            metaObj.put("style", roleStyle);
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
                                    File fOut = new File(cacheDir, "vs_interact_" + sKey + "_" + dubLang + ".wav");
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
                            part.put("text", "Character " + prof.name + ". Roleplay with voice style " + roleStyle + ". " + rolePrompt + ": " + clean);
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
                                                File fOut2 = new File(cacheDir, "vs_gen25_" + sKey + "_" + dubLang + ".wav");
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

                    // FASE 3: Motor Fonetico Nativo (Audio Online segun Doblaje)
                    try {
                        String ttsLang = "es".equals(dubLang) ? "es" : ("en".equals(dubLang) ? "en" : (prof.lang != null ? prof.lang : "ja"));

                        String gUrl = "https://translate.google.com/translate_tts?ie=UTF-8&tl=" + ttsLang + "&client=tw-ob&q=" + URLEncoder.encode(clean, "UTF-8");
                        HttpURLConnection gConn = (HttpURLConnection) new URL(gUrl).openConnection();
                        gConn.setRequestProperty("User-Agent", "Mozilla/5.0");
                        gConn.setConnectTimeout(8000);
                        gConn.setReadTimeout(10000);
                        if (gConn.getResponseCode() == 200) {
                            InputStream is = gConn.getInputStream();
                            File fOut3 = new File(cacheDir, "vs_phonetic_" + sKey + "_" + dubLang + ".mp3");
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

                    // FASE 4: Banco de Audios de Personaje en assets
                    String[] assetCandidates = new String[] {
                        "sounds/" + sKey + "/idle_" + dubLang + ".mp3",
                        "sounds/" + sKey + "/idle.mp3",
                        "sounds/" + sKey + "/greeting_" + dubLang + ".mp3",
                        "sounds/" + sKey + "/greeting.mp3"
                    };
                    for (String aPath : assetCandidates) {
                        try {
                            AssetFileDescriptor afd = context.getAssets().openFd(aPath);
                            InputStream is = afd.createInputStream();
                            File fOut4 = new File(cacheDir, "vs_asset_" + sKey + "_" + dubLang + ".mp3");
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
                    }

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
