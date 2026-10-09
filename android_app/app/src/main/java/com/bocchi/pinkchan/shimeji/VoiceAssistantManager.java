package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.provider.Settings;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.widget.Toast;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class VoiceAssistantManager {

    public interface AssistantCallback {
        void onListeningStarted();
        void onSpeechResult(String recognizedText);
        void onAssistantResponse(String responseText);
        void onActionTriggered(String actionName);
        void onAddShimejiRequested();
        void onClearExtrasRequested();
        void onStopRequested();
    }

    private final Context context;
    private final AssistantCallback callback;
    private SpeechRecognizer speechRecognizer;
    private boolean isListening = false;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    public VoiceAssistantManager(Context context, AssistantCallback callback) {
        this.context = context;
        this.callback = callback;
    }

    public void startListening() {
        mainHandler.post(new Runnable() {
            @Override
            public void run() {
                if (!SpeechRecognizer.isRecognitionAvailable(context)) {
                    if (callback != null) {
                        callback.onAssistantResponse("Reconocimiento de voz no disponible en este dispositivo.");
                    }
                    return;
                }

                if (speechRecognizer == null) {
                    speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context);
                    speechRecognizer.setRecognitionListener(new RecognitionListener() {
                        @Override
                        public void onReadyForSpeech(Bundle params) {
                            isListening = true;
                            if (callback != null) callback.onListeningStarted();
                        }

                        @Override
                        public void onBeginningOfSpeech() {}

                        @Override
                        public void onRmsChanged(float rmsdB) {}

                        @Override
                        public void onBufferReceived(byte[] buffer) {}

                        @Override
                        public void onEndOfSpeech() {
                            isListening = false;
                        }

                        @Override
                        public void onError(int error) {
                            isListening = false;
                            String msg = "No entendi, intenta de nuevo.";
                            if (error == SpeechRecognizer.ERROR_NO_MATCH) {
                                msg = "No escuche ninguna orden.";
                            }
                            if (callback != null) callback.onAssistantResponse(msg);
                        }

                        @Override
                        public void onResults(Bundle results) {
                            isListening = false;
                            ArrayList<String> matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                            if (matches != null && !matches.isEmpty()) {
                                String text = matches.get(0);
                                processCommand(text);
                            }
                        }

                        @Override
                        public void onPartialResults(Bundle partialResults) {}

                        @Override
                        public void onEvent(int eventType, Bundle params) {}
                    });
                }

                Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES");
                intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1);
                intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false);

                try {
                    speechRecognizer.startListening(intent);
                } catch (Exception e) {
                    if (callback != null) {
                        callback.onAssistantResponse("Error al iniciar microfono.");
                    }
                }
            }
        });
    }

    public void stopListening() {
        if (speechRecognizer != null) {
            try {
                speechRecognizer.stopListening();
                speechRecognizer.cancel();
            } catch (Exception ignored) {}
        }
        isListening = false;
    }

    public void destroy() {
        if (speechRecognizer != null) {
            try {
                speechRecognizer.destroy();
            } catch (Exception ignored) {}
            speechRecognizer = null;
        }
    }

    public void processCommand(String rawCommand) {
        if (rawCommand == null) return;
        String cmd = rawCommand.toLowerCase().trim();

        if (callback != null) {
            callback.onSpeechResult(rawCommand);
        }

        // 1. Saludos simples
        if (cmd.contains("hola") || cmd.contains("buenos dias") || cmd.contains("buenas tardes") || cmd.contains("buenas noches") || cmd.contains("que tal")) {
            if (callback != null) {
                callback.onAssistantResponse("Hola. En que puedo ayudarte hoy?");
            }
            return;
        }

        // 2. Preguntar la hora
        if (cmd.contains("hora") || cmd.contains("que hora es")) {
            SimpleDateFormat sdf = new SimpleDateFormat("hh:mm a", Locale.getDefault());
            String timeStr = sdf.format(new Date());
            if (callback != null) {
                callback.onAssistantResponse("Son las " + timeStr + ".");
            }
            return;
        }

        // 3. Abrir aplicaciones por comando de voz
        if (cmd.startsWith("abre ") || cmd.startsWith("abrir ") || cmd.startsWith("inicia ") || cmd.startsWith("iniciar ") || cmd.startsWith("lanzar ") || cmd.startsWith("lanza ")) {
            String appQuery = cmd
                .replaceFirst("^(abre|abrir|inicia|iniciar|lanzar|lanza)\\s+", "")
                .replace("la aplicacion de ", "")
                .replace("la app de ", "")
                .replace("el ", "")
                .replace("la ", "")
                .trim();

            String responseMsg = launchAppByQuery(appQuery);
            if (callback != null) {
                callback.onAssistantResponse(responseMsg);
            }
            return;
        }

        // 4. Invocar / clonar otro Shimeji
        if (cmd.contains("invoca otro") || cmd.contains("otro shimeji") || cmd.contains("agrega shimeji") || cmd.contains("clon") || cmd.contains("clonar") || cmd.contains("duplicar") || cmd.contains("mas shimejis")) {
            if (callback != null) {
                callback.onAddShimejiRequested();
                callback.onAssistantResponse("Nuevo Shimeji invocado en pantalla.");
            }
            return;
        }

        // 5. Limpiar extras
        if (cmd.contains("limpiar extras") || cmd.contains("quitar extras") || cmd.contains("solo uno")) {
            if (callback != null) {
                callback.onClearExtrasRequested();
                callback.onAssistantResponse("Shimejis extras removidos.");
            }
            return;
        }

        // 6. Soltar item / comida
        if (cmd.contains("item") || cmd.contains("comida") || cmd.contains("snack") || cmd.contains("objeto") || cmd.contains("alimento")) {
            if (callback != null) {
                callback.onActionTriggered("drop_item");
                callback.onAssistantResponse("Soltando item para el Shimeji.");
            }
            return;
        }

        // 7. Acciones fisicas
        if (cmd.contains("guitarra") || cmd.contains("toca")) {
            if (callback != null) {
                callback.onActionTriggered("guitar");
                callback.onAssistantResponse("A tocar guitarra.");
            }
            return;
        }

        if (cmd.contains("caja") || cmd.contains("cajita") || cmd.contains("escondete")) {
            if (callback != null) {
                callback.onActionTriggered("box");
                callback.onAssistantResponse("Modo caja activado.");
            }
            return;
        }

        if (cmd.contains("baila") || cmd.contains("bailar") || cmd.contains("danza")) {
            if (callback != null) {
                callback.onActionTriggered("dance");
                callback.onAssistantResponse("Bailando! Sigue el ritmo.");
            }
            return;
        }

        if (cmd.contains("rueda") || cmd.contains("girar") || cmd.contains("vuelta")) {
            if (callback != null) {
                callback.onActionTriggered("roll");
                callback.onAssistantResponse("Vuelta acrobatica!");
            }
            return;
        }

        if (cmd.contains("brinca") || cmd.contains("salto alto")) {
            if (callback != null) {
                callback.onActionTriggered("jump");
                callback.onAssistantResponse("Salto acrobatico!");
            }
            return;
        }

        if (cmd.contains("juega") || cmd.contains("jugar") || cmd.contains("minijuego")) {
            if (callback != null) {
                callback.onActionTriggered("play");
                callback.onAssistantResponse("A jugar juntos!");
            }
            return;
        }

        if (cmd.contains("termux") || cmd.contains("consola") || cmd.contains("terminal")) {
            if (callback != null) {
                callback.onActionTriggered("termux");
                callback.onAssistantResponse("Iniciando comandos de Termux.");
            }
            return;
        }

        if (cmd.contains("crea carpeta") || cmd.contains("crear carpeta") || cmd.contains("crea archivo") || cmd.contains("crear archivo") || cmd.contains("notas")) {
            if (callback != null) {
                callback.onActionTriggered("create_file");
                callback.onAssistantResponse("Creando carpeta y notas en Documents/Shijima.");
            }
            return;
        }

        if (cmd.contains("salta") || cmd.contains("muevete") || cmd.contains("vuela") || cmd.contains("flotar")) {
            if (callback != null) {
                callback.onActionTriggered("roam");
                callback.onAssistantResponse("Moviendose por toda la pantalla.");
            }
            return;
        }

        if (cmd.contains("acariciar") || cmd.contains("mimar") || cmd.contains("te quiero")) {
            if (callback != null) {
                callback.onActionTriggered("pet");
                callback.onAssistantResponse("Que lindo detalle.");
            }
            return;
        }

        if (cmd.contains("cambiar skin") || cmd.contains("cambia personaje") || cmd.contains("siguiente skin")) {
            if (callback != null) {
                callback.onActionTriggered("cycle_skin");
                callback.onAssistantResponse("Cambiando de personaje.");
            }
            return;
        }

        if (cmd.contains("detener") || cmd.contains("cerrar") || cmd.contains("apagar") || cmd.contains("adios")) {
            if (callback != null) {
                callback.onAssistantResponse("Hasta pronto.");
                callback.onStopRequested();
            }
            return;
        }

        // Respuesta general si no hubo coincidencia directa
        if (callback != null) {
            callback.onAssistantResponse("Entendi: '" + rawCommand + "'. Prueba decir: 'abre whatsapp', 'guitarra', 'salta' o 'invoca otro'.");
        }
    }

    private String launchAppByQuery(String query) {
        PackageManager pm = context.getPackageManager();
        android.content.SharedPreferences sp = context.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        java.util.Set<String> allowedSet = sp.getStringSet(MainActivity.KEY_ALLOWED_APPS, null);

        // 1. Accesos rapidos a apps del sistema conocidas
        if (query.equals("camara") || query.equals("fotos")) {
            Intent intent = new Intent(MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            if (intent.resolveActivity(pm) != null) {
                context.startActivity(intent);
                return "Abriendo la camara.";
            }
        }

        if (query.equals("ajustes") || query.equals("configuracion")) {
            Intent intent = new Intent(Settings.ACTION_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
            return "Abriendo ajustes del sistema.";
        }

        if (query.equals("calculadora")) {
            String[] calcPackages = {
                "com.google.android.calculator",
                "com.coloros.calculator",
                "com.sec.android.app.popupcalculator",
                "com.android.calculator2"
            };
            for (String pkg : calcPackages) {
                if (allowedSet != null && !allowedSet.contains(pkg)) continue;
                Intent launch = pm.getLaunchIntentForPackage(pkg);
                if (launch != null) {
                    launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    context.startActivity(launch);
                    return "Abriendo la calculadora.";
                }
            }
        }

        // 2. Busqueda exhaustiva en todas las aplicaciones instaladas
        List<ApplicationInfo> apps = pm.getInstalledApplications(PackageManager.GET_META_DATA);
        String cleanQuery = query.toLowerCase().replace(" ", "");

        ApplicationInfo bestMatch = null;
        for (ApplicationInfo app : apps) {
            String label = pm.getApplicationLabel(app).toString().toLowerCase();
            String cleanLabel = label.replace(" ", "");

            if (cleanLabel.equals(cleanQuery)) {
                bestMatch = app;
                break;
            } else if (cleanLabel.contains(cleanQuery) || cleanQuery.contains(cleanLabel)) {
                if (pm.getLaunchIntentForPackage(app.packageName) != null) {
                    bestMatch = app;
                }
            }
        }

        if (bestMatch != null) {
            String appLabel = pm.getApplicationLabel(bestMatch).toString();
            if (allowedSet != null && !allowedSet.contains(bestMatch.packageName)) {
                return "La app '" + appLabel + "' esta bloqueada en el filtro de aplicaciones permitidas.";
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
}
