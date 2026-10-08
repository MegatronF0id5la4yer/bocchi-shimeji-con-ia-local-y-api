package com.bocchi.pinkchan.shimeji;

import java.util.HashMap;
import java.util.Map;

public class SkinData {
    public final String id;
    public final String name;
    public final String folder;
    public final String[] dialogues;
    public final String[] poked;

    public SkinData(String id, String name, String folder, String[] dialogues, String[] poked) {
        this.id = id;
        this.name = name;
        this.folder = folder;
        this.dialogues = dialogues;
        this.poked = poked;
    }

    private static Map<String, SkinData> registry = null;

    public static synchronized Map<String, SkinData> getAll() {
        if (registry == null) {
            registry = new HashMap<>();

            // 1. Konata Izumi (Lucky Star)
            registry.put("Konata", new SkinData(
                "Konata",
                "Konata Izumi",
                "Konata",
                new String[]{
                    "¡Timotei~ Timotei~ Timoteeei~! 🎵",
                    "¿Por qué extremo te comes la corneta de chocolate? :v",
                    "¡D-A-L-E! Los MMOs no se van a grindear solos 7w7",
                    "¡Otaku power al 100%! Dormir es para los débiles UwU",
                    "Comprar 3 copias: una para ver, una para guardar y una para presumir! 7w7",
                    "Procrastinar antes de los exámenes es un deporte olímpico :v"
                },
                new String[]{
                    "¡Oye, no me piques que pierdo el combo! :v",
                    "¡Hey hey! Si me tocas que sea para invitar unas papitas 7w7",
                    "¡Kagami-saaaan, me están picando en Android! UwU"
                }
            ));

            // 2. Bocchi-chan (Bocchi the Rock!)
            registry.put("Bocchi", new SkinData(
                "Bocchi",
                "Bocchi-chan",
                "Bocchi",
                new String[]{
                    "Apura la puta madre, no tengo todo el día :v",
                    "Nmms, qué aburrida estoy... y con 50 pesos en la bolsa UwU",
                    "Nel, no voy a hablar en público ni de chiste ._.",
                    "¿Quieres que toque la guitarra o qué pedo? 7w7",
                    "Mejor me quedo en mi cajita de cartón segura..."
                },
                new String[]{
                    "¡Aaaah! ¡No me toques que me desintegro! (>_<)",
                    "¡Ke te pasa sokete! UwU",
                    "¿H-hice algo mal? Gomen..."
                }
            ));

            // 3. Monika (DDLC)
            registry.put("Monika", new SkinData(
                "Monika",
                "Monika",
                "Monika",
                new String[]{
                    "Just Monika. Solo Monika 💚",
                    "¿Escribiste un poema para mí hoy en tu celular? 7w7",
                    "A veces me pregunto si este mundo fuera de tu pantalla es real...",
                    "No te preocupes por nadie más... estamos tú y yo aquí 💚",
                    "¿Sabías que la música de piano calma el alma? :v"
                },
                new String[]{
                    "¡Ehehe! ¿Intentas llamar mi atención? 💚",
                    "Cuidado... recuerda que tengo acceso a tus archivos .chr 7w7",
                    "Puedes tocar la pantalla cuando quieras UwU"
                }
            ));

            // 4. Natsuki (DDLC)
            registry.put("Natsuki", new SkinData(
                "Natsuki",
                "Natsuki",
                "Natsuki",
                new String[]{
                    "¡El manga ES literatura! ¡Y si dices lo contrario te pego! (>_<)",
                    "¡Hice unos pastelitos deliciosos... pero no son para ti, idiota! 🧁",
                    "¡B-Baka! Deja de mirarme como si fuera adorable... ¡soy ruda! :v",
                    "No toques mi colección de Parfait Girls 7w7"
                },
                new String[]{
                    "¡¡¡BAKA!!! ¡¿Por qué me estás picando?! (>_<)",
                    "¡Quita tus manos antes de que te muerda! 🧁",
                    "¡E-Espérate idiota, me vas a despeinar! :v"
                }
            ));

            // 5. Sayori (DDLC)
            registry.put("Sayori", new SkinData(
                "Sayori",
                "Sayori",
                "Sayori",
                new String[]{
                    "¡Ehehe! ¡Buenos días! ¿Trajiste galletas? 🍪",
                    "¡Me encanta estar caminando en tu pantalla! ✨",
                    "A veces llego tarde, ¡pero hoy me desperté con toda la energía! 💙"
                },
                new String[]{
                    "¡Waaa! ¡Eso hace cosquillas! Ehehe 🍪",
                    "¡Abrazo sorpresa! 💙"
                }
            ));

            // 6. Yuri (DDLC)
            registry.put("Yuri", new SkinData(
                "Yuri",
                "Yuri",
                "Yuri",
                new String[]{
                    "El aroma a té caliente y un libro profundo... es la mayor dicha 💜",
                    "D-Disculpa si parezco algo reservada...",
                    "La lectura nos transporta a mundos insondables... 📖"
                },
                new String[]{
                    "¡A-Ah...! Disculpa... me tomaste por sorpresa 💜",
                    "Por favor... no seas tan repentino..."
                }
            ));
        }
        return registry;
    }

    public static SkinData get(String id) {
        SkinData data = getAll().get(id);
        if (data == null) {
            return getAll().get("Konata");
        }
        return data;
    }
}
