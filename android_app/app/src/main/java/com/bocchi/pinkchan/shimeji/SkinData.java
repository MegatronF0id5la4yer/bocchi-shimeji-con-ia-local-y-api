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
                    "Timotei, Timotei, Timoteei...",
                    "Por que extremo te comes la corneta de chocolate?",
                    "D-A-L-E. Los MMOs no se van a grindear solos.",
                    "Otaku power al 100%. Dormir es para debiles.",
                    "Comprar 3 copias: una para ver, una para guardar y una para presumir.",
                    "Procrastinar antes de los examenes es un deporte olimpico."
                },
                new String[]{
                    "Oye, no me toques que pierdo el combo.",
                    "Si me tocas, que sea para invitar unas papitas.",
                    "Kagami, me estan molestando en Android..."
                }
            ));

            // 2. Bocchi-chan (Bocchi the Rock!)
            registry.put("Bocchi", new SkinData(
                "Bocchi",
                "Bocchi-chan",
                "Bocchi",
                new String[]{
                    "Apura, no tengo todo el dia...",
                    "Que aburrida estoy... y con 50 pesos en la bolsa.",
                    "No voy a hablar en publico ni de chiste.",
                    "Quieres que toque la guitarra?",
                    "Mejor me quedo en mi cajita de carton segura..."
                },
                new String[]{
                    "No me toques que me desintegro...",
                    "Que te pasa, dejame en paz...",
                    "Hice algo mal? Gomen..."
                }
            ));

            // 3. Monika (DDLC)
            registry.put("Monika", new SkinData(
                "Monika",
                "Monika",
                "Monika",
                new String[]{
                    "Just Monika. Solo Monika.",
                    "Escribiste un poema para mi hoy en tu celular?",
                    "A veces me pregunto si este mundo fuera de tu pantalla es real...",
                    "No te preocupes por nadie mas, estamos tu y yo aqui.",
                    "Sabias que la musica de piano calma el alma?"
                },
                new String[]{
                    "Intentas llamar mi atencion?",
                    "Recuerda que tengo acceso a tus archivos del sistema...",
                    "Puedes tocar la pantalla cuando quieras."
                }
            ));

            // 4. Natsuki (DDLC)
            registry.put("Natsuki", new SkinData(
                "Natsuki",
                "Natsuki",
                "Natsuki",
                new String[]{
                    "El manga es literatura. Y si dices lo contrario no te hablo.",
                    "Hice unos pastelitos deliciosos... pero no son para ti.",
                    "Deja de mirarme como si fuera adorable, soy ruda.",
                    "No toques mi coleccion de Parfait Girls."
                },
                new String[]{
                    "Por que me estas picando?",
                    "Quita tus manos antes de que te muerda.",
                    "Esperate, me vas a despeinar."
                }
            ));

            // 5. Sayori (DDLC)
            registry.put("Sayori", new SkinData(
                "Sayori",
                "Sayori",
                "Sayori",
                new String[]{
                    "Buenos dias. Trajiste galletas?",
                    "Me encanta estar caminando en tu pantalla.",
                    "Hoy me desperte con toda la energia."
                },
                new String[]{
                    "Eso hace cosquillas.",
                    "Abrazo sorpresa."
                }
            ));

            // 6. Yuri (DDLC)
            registry.put("Yuri", new SkinData(
                "Yuri",
                "Yuri",
                "Yuri",
                new String[]{
                    "El aroma a te caliente y un libro profundo es la mayor dicha.",
                    "Disculpa si parezco algo reservada...",
                    "La lectura nos transporta a mundos insondables..."
                },
                new String[]{
                    "Disculpa, me tomaste por sorpresa...",
                    "Por favor, no seas tan repentino..."
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

    public static String getNextSkin(String currentId) {
        String[] order = {"Konata", "Bocchi", "Monika", "Natsuki", "Sayori", "Yuri"};
        for (int i = 0; i < order.length; i++) {
            if (order[i].equalsIgnoreCase(currentId)) {
                return order[(i + 1) % order.length];
            }
        }
        return "Bocchi";
    }
}
