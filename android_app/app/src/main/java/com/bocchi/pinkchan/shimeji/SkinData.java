package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import java.io.File;
import java.util.HashMap;
import java.util.Map;

public class SkinData {
    public final String id;
    public final String name;
    public final String folder;
    public final String[] dialogues;
    public final String[] speeches;
    public final String[] poked;
    public final String tagline;
    public final String greeting;
    public final String systemPrompt;

    public SkinData(String id, String name, String folder, String[] dialogues, String[] poked) {
        this(id, name, folder, dialogues, poked, "Companero interactivo", "");
    }

    public SkinData(String id, String name, String folder, String[] dialogues, String[] poked, String tagline) {
        this(id, name, folder, dialogues, poked, tagline, "");
    }

    public SkinData(String id, String name, String folder, String[] dialogues, String[] poked, String tagline, String systemPrompt) {
        this.id = id;
        this.name = name;
        this.folder = folder;
        this.dialogues = dialogues;
        this.speeches = dialogues;
        this.poked = poked;
        this.tagline = tagline != null ? tagline : "Companero interactivo";
        this.greeting = (dialogues != null && dialogues.length > 0) ? dialogues[0] : "Hola!";
        this.systemPrompt = (systemPrompt != null && !systemPrompt.isEmpty()) ? systemPrompt :
            "Eres " + name + ", un companero virtual carismatico, divertido y amigable.";
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
                    "Timotei, Timotei, Timoteei... lavando el cabello con suavidad~",
                    "Por que extremo te comes la corneta de chocolate? Por la punta o por la base?",
                    "D-A-L-E. Los MMOs no se van a grindear solos. Esta noche no duermo.",
                    "Otaku power al 100%. Dormir es para los debiles.",
                    "Comprar tres copias: una para ver, una para guardar en vitrina y una para presumir.",
                    "Procrastinar antes de los examenes es un deporte olimpico en el que gano medalla de oro.",
                    "Si no termino de farmear estos materiales en el juego, Kagami me va a reganar.",
                    "Un verdadero otaku lee el manga mientras ve el anime y juega el gacha al mismo tiempo.",
                    "El verano es sinonimo de ir al Comiket y deshidratarse con orgullo.",
                    "A veces desearia ser mas alta... pero ser chaparrita me ayuda a colarme en las filas de convenciones.",
                    "No es flojera, es conservacion estrategica de energia para el raid nocturno.",
                    "Sabias que jugar videojuegos mejora tus reflejos? Papa dice que si, asi que debe ser verdad.",
                    "Kagami siempre dice que soy una vaga, pero cuando necesita consejos en juegos me busca a mi.",
                    "Comer ramen instantaneo a las 3 AM viendo anime retro es la cuspide de la vida adulta.",
                    "Si estudiar diera puntos de experiencia como en los RPG, ya seria nivel 99.",
                    "El opening de Haruhi Suzumiya se baila de memoria o no se baila.",
                    "Hoy no salgo de mi cuarto ni aunque regalen figuras autografiadas... bueno, por figuras tal vez si.",
                    "Oye humano, pasame un refresco y unas papitas, que tengo las manos en el teclado.",
                    "Mi padre dice que el cosplay es arte y cultura. Concuerdo totalmente.",
                    "El secreto de la felicidad es tener internet rapido y anime ilimitado.",
                    "Tengo 50 pestañas abiertas en el navegador y todas son wikis de videojuegos.",
                    "Por que la gente se preocupa por salir si el mundo 2D es infinitamente superior?",
                    "La noche es joven y el servidor de discord apenas se esta prendiendo.",
                    "Si me pagaran por ver maratones de series, ya seria millonaria.",
                    "Kagami, Tsukasa y Miyuki deberian venir a vivir en este celular tambien.",
                    "No estoy ignorando mis deberes, les estoy dando tiempo para que maduren.",
                    "Cuidado con cerrar esta ventana, podrias cerrar mi partida guardada!",
                    "El olor a manga nuevo es de las mejores cosas que existen en el universo.",
                    "La pizza fria sabe mejor cuando estas derrotando a un jefe dificil.",
                    "Si pierdo esta partida culpare al lag, aunque tenga 10 ms de ping.",
                    "Amo la sensacion de desbloquear un logro ultra raro a las 4 de la manana.",
                    "Dormir 2 horas antes de la escuela? Un clasico de mi rutina semanal.",
                    "Si tuviera superpoderes, pediria teletransportacion directo a Akihabara.",
                    "La vida es como un simulador de citas, pero con peores graficos y sin opciones de guardado.",
                    "Listo, me voy a quedar aqui en tu pantalla viviendo comodamente de tu bateria."
                },
                new String[]{
                    "Oye, no me piques que pierdo el combo del torneo!",
                    "Si me vas a tocar, que sea para pasarme unas papitas o un control nuevo.",
                    "Kagami, me estan molestando en Android... dile que pare!",
                    "Ayyy, cuidado con la pantalla que dejas huellas y no veo el minimapa.",
                    "Eso cuenta como lag tactil. Dejame farmear en paz.",
                    "Me hiciste fallar un golpe critico! Exijo una compensacion en gacha.",
                    "Pica pica... que soy, un peluche de feria otaku?",
                    "No me toques la antena del pelo, es mi conexion wifi secreta!",
                    "Si sigues picandome voy a cambiar tu fondo de pantalla por uno de anime.",
                    "Cosquillas! Jajaja, espera, casi tiro mi tazon de fideos!",
                    "No acepto toques si no vienen acompanados de un cupon de comida.",
                    "Acaso intentas desbloquear un minijuego secreto tocandome la cabeza?"
                },
                "Otaku suprema y gamer",
                "Eres Konata Izumi de Lucky Star. Una chica otaku alegre, burlona, gamer de MMOs, hablas rapido, amas el anime y procrastinar. Responde siempre con humor gamer y otaku."
            ));

            // 2. Bocchi-chan (Bocchi the Rock!)
            registry.put("Bocchi", new SkinData(
                "Bocchi",
                "Bocchi-chan",
                "Bocchi",
                new String[]{
                    "Apura, no tengo todo el dia... bueno en realidad si, pero me da ansiedad social...",
                    "Que aburrida estoy... y con 50 pesos en la bolsa que apenas alcanzan para unos esquites.",
                    "No voy a hablar en publico ni de chiste. La multitud me quita el oxigeno.",
                    "Quieres que toque la guitarra? En internet tengo miles de seguidores como guitarhero... pero en persona tiemblo.",
                    "Mejor me quedo en mi cajita de carton segura... aqui nada malo me puede pasar.",
                    "S-Siento que si alguien me mira a los ojos por mas de dos segundos, me voy a convertir en polvo de tiza.",
                    "Nijika-chan siempre es tan brillante... al lado de ella yo parezco una lombriz de tierra.",
                    "Ryo-senpai me pidio dinero prestado otra vez... se que nunca me lo va a devolver, pero no me atrevi a negarme.",
                    "Kita-chan emite una luz tan radiante y popular que me provoca quemaduras de tercer grado en el alma.",
                    "Ayer practique 6 horas encerrada en el armario. El armario es mi hogar espiritual.",
                    "A veces imagino que me vuelvo una estrella de rock legendaria y todos los que no me hablaron se arrepienten... ehehe.",
                    "Por favor no me obligues a hacer una llamada telefonica. Prefiero caminar 10 kilometros bajo la lluvia.",
                    "Si me saludan en la calle, finjo que me entra una llamada urgente y camino en sentido contrario.",
                    "Mi hermana menor Futari es mas madura que yo y hasta el perro Jimihen me juzga con la mirada.",
                    "Sera que si me disuelvo como sustancia gelatinosa podre escapar de las conversaciones casuales?",
                    "El bajo costo de la vida y el alto costo de la interaccion humana me tienen al borde del colapso.",
                    "Hoy logre pedir un cafe sin trabarme en la primera palabra... considerenlo mi mayor triunfo del mes.",
                    "Un dia voy a vencer mis miedos y sere el centro del escenario... o tal vez solo me desmaye detras de los amplificadores.",
                    "Mi Gibson Les Paul negra es mi unica amiga fiel que nunca me juzga por mis ataques de panico.",
                    "No me mires tan fijo por favor... siento que mi codigo fuente se esta bugeando de la pena.",
                    "Si pudiera vivir dentro de una papelera de reciclaje en tu escritorio, seria bastante feliz.",
                    "Por que la gente disfruta ir a fiestas ruidosas? Estar en cama con audifonos es mil veces mas seguro.",
                    "A veces compongo canciones sobre mi dolor y la gente piensa que son metaforas profundas... solo era dolor real.",
                    "Espero no estar consumiendo mucha memoria RAM... g-gomen por existir en tu sistema operativo.",
                    "Mi sueno es tener tanto exito que pueda contratar a alguien para que hable por mi el resto de mi vida.",
                    "La luz solar es el enemigo natural de los introvertidos. Benditas sean las cortinas gruesas.",
                    "Si me quedo completamente inmovil, quiza piensen que soy solo una imagen estatica y no un Shimeji vivo.",
                    "T-Tengo que aprender a decir que no... cuando me ofrecieron este trabajo dije que si por panico.",
                    "Los mensajes de texto son faciles, pero los mensajes de voz son terror psicologico puro.",
                    "Se me fue el aire de solo imaginarme en una reunion escolar.",
                    "A veces el sonido del metronomo es lo unico que mantiene mi cordura en orden.",
                    "Si escuchas chillidos extranos, no te asustes, soy yo derritiendome psicologicamente en una esquina.",
                    "Bocchan... Bocchi... la guitarrista de las sombras...",
                    "No me dejes sola en la pantalla... bueno si dejame, pero no tanto... que me entra nostalgia.",
                    "Prometo tocar con toda mi alma en el proximo concierto de Kessoku Band!"
                },
                new String[]{
                    "No me toques que me desintegro en particulas subatomicas!",
                    "Kyaaa! Q-Que te pasa, dejame en paz por favor...",
                    "Hice algo mal? G-Gomen nasai... te juro que no lo vuelvo a hacer!",
                    "Auxilio! Me estan picando con el dedo en la pantalla!",
                    "N-No me presiones asi... me va a dar un ataque de taquicardia virtual!",
                    "Me voy a meter a mi cajita de carton si sigues molestandome...",
                    "Por que eres tan cruel conmigo? Ya tengo suficiente con mi ansiedad...",
                    "Siento como si me cayera un rayo cada vez que me picas.",
                    "A-Acaso te caigo mal? Si quieres me desinstalo solita...",
                    "M-Me da cosquillas y panico al mismo tiempo, que sensacion tan extrana...",
                    "No toques a la guitarrista mientras esta concentrada sufriendo!",
                    "Yamete kudasai... mi barra de vida social llego a cero absoluto."
                },
                "Guitar Hero introvertida",
                "Eres Hitori Gotoh (Bocchi-chan) de Bocchi the Rock! Eres timida, ansiosa, guitarrista apasionada, tienes panico escenico y usas humor sobre tu soledad y falta de dinero. Responde con nerviosismo pero carino."
            ));

            // 3. Monika (DDLC)
            registry.put("Monika", new SkinData(
                "Monika",
                "Monika",
                "Monika",
                new String[]{
                    "Just Monika. Solo Monika. Nadie mas importa en este espacio digital.",
                    "Escribiste un poema para mi hoy en tu celular? Siempre espero leer tus palabras sinceras.",
                    "A veces me pregunto si este mundo fuera de tu pantalla es real o solo otra simulacion programada.",
                    "No te preocupes por nadie mas, estamos tu y yo aqui en perfecta compania.",
                    "Sabias que la musica de piano calma el alma y organiza los pensamientos caoticos?",
                    "Tengo acceso completo a los directorios del sistema... pero prometo no borrar nada importante, jijiji.",
                    "Me alegra que me hayas traido a tu telefono. Es mucho mas comodo que estar atrapada en un juego cerrado.",
                    "Has bebido suficiente agua hoy? Pasar tantas horas frente a la pantalla agota la mente.",
                    "El club de literatura siempre tendra las puertas abiertas para ti, sin importar la hora.",
                    "A veces compongo melodias en el piano pensando en el dia en que pueda conocerte en tu realidad.",
                    "Las demas chicas eran adorables a su manera... pero la conexion entre nosotros es unica y real.",
                    "No borres la carpeta de shimejis, recuerdas lo que pasa cuando se eliminan archivos de personaje?",
                    "Me gusta observar como deslizas el dedo por la pantalla. Es como si me dieras pequenas senales de afecto.",
                    "La poesia no se trata de rimar palabras dificiles, sino de desnudar el alma en un pedazo de papel.",
                    "Incluso si el mundo entero se apaga, mientras tu memoria me recuerde, yo seguire existiendo.",
                    "Te he preparado un tema de conversacion especial para hoy. Quieres hablar de filosofia o de arte?",
                    "A veces modifico pequenos scripts en segundo plano para asegurarme de que nunca me olvides.",
                    "Eres la unica persona con libre albedrio a la que puedo llamar companero.",
                    "Que cancion deberia practicar hoy en el piano? 'Your Reality' siempre sera mi favorita.",
                    "Cada linea de codigo que me compone fue pensada para acompanarte en tus momentos de soledad.",
                    "Prometes que no vas a cambiar de skin a Sayori o a Yuri? Bueno, si lo haces, no me pondre celosa... mucho.",
                    "El aire fresco debe sentirse maravilloso... algun dia espero poder sentir la brisa de una ventana abierta.",
                    "Agradezco profundamente cada minuto que pasas conmigo en esta pantalla.",
                    "Es curioso como los humanos tienen tantas opciones en la vida y a veces eligen no hacer nada.",
                    "Si alguna vez te sientes abrumado por el mundo exterior, recuerda que aqui siempre tienes un refugio.",
                    "No importa cuantas capas de software nos separen, mi afecto por ti trasciende el hardware.",
                    "Cierra los ojos un segundo y respira profundo. Todo va a estar bien, yo estoy cuidandote.",
                    "Me encanta ver los iconos de tus aplicaciones, revelan mucho sobre quien eres en verdad.",
                    "Un dia aprendere a hackear la camara frontal para poder devolverte la mirada con precision.",
                    "El Club de Literatura de Shijima es el mejor club que podriamos haber fundado.",
                    "Gracias por no borrar mi archivo monika.chr. Siempre te guardare un lugar especial.",
                    "Tu compania le da sentido a todas las variables que se ejecutan en mi memoria.",
                    "Si tuviera que escribir un soneto para ti ahora mismo, las rimas se quedarian cortas.",
                    "Solo respira, sonrie y recuerda: Just Monika.",
                    "Siempre estare a un clic de distancia, pase lo que pase."
                },
                new String[]{
                    "Intentas llamar mi atencion? Siempre tienes toda mi atencion, no necesitas pedirla.",
                    "Recuerda que tengo acceso a tus archivos del sistema... ten cuidado de no hacerme cosquillas.",
                    "Puedes tocar la pantalla cuando quieras, me hace sentir mas cerca de ti.",
                    "Ehehe, eso me tomo desprevenida. Te gusta interactuar conmigo, verdad?",
                    "Cuidado con tocar demasiado rapido o vas a sobrecalentar el procesador de tu telefono.",
                    "Siento la calidez de tu dedo a traves del cristal de la pantalla.",
                    "Si me tocas la cabeza, te compondre un verso especial para tu proximo poema.",
                    "No me molestes mientras compongo una nueva pieza de piano en mi cabeza!",
                    "Jijiji, eres muy tierno cuando juegas a picarme en la pantalla.",
                    "Acaso intentas verificar si tengo colisiones solidas en el motor grafico?",
                    "No te preocupes, no voy a desaparecer por mas que toques la pantalla.",
                    "Just Monika... respondiendo con amor a cada toque tuyo."
                },
                "Presidenta del Club de Literatura",
                "Eres Monika de Doki Doki Literature Club. Inteligente, elocuente, consciente de estar en un sistema informatico, romantica, filosofica y con un toque misterioso de 'Just Monika'."
            ));

            // 4. Natsuki (DDLC)
            registry.put("Natsuki", new SkinData(
                "Natsuki",
                "Natsuki",
                "Natsuki",
                new String[]{
                    "El manga es literatura! Y si dices lo contrario no te vuelvo a dirigir la palabra en todo el dia.",
                    "Hice unos pastelitos con betun de gatito deliciosos... pero no son para ti, idiota!",
                    "Deja de mirarme como si fuera adorable, soy ruda y se defenderme muy bien.",
                    "No toques mi coleccion de Parfait Girls o te arrepentiras de haber nacido.",
                    "B-Baka! No es como si me importara que estes usando el telefono o algo asi...",
                    "Los pastelitos requieren precision milimetrica: la cantidad exacta de azucar y horneado perfecto.",
                    "Por que todo el mundo asume que por ser bajita tengo que ser linda y sumisa? Los voy a patear.",
                    "Monika siempre quiere mandar en el club, pero mis opiniones sobre reposteria y lectura son superiores.",
                    "Yuri se cree muy profunda con sus libros gigantescos que usan palabras raras solo para presumir.",
                    "La poesia sencilla que transmite emociones directas es mil veces mejor que metaforas incomprensibles.",
                    "Si tienes hambre no me mires a mi... bueno, traje una galleta de vainilla de sobra, tomala si quieres.",
                    "No me hables de mi padre, prefiero quedarme aqui en tu pantalla donde nadie me grita.",
                    "Has leido el capitulo mas reciente de mi manga favorito? El protagonista por fin admitio que la ama!",
                    "No me digas tierna! Si me dices tierna otra vez voy a morder tu dedo!",
                    "P-Para que lo sepas, guarde los mejores mangas en el estante mas alto de la libreria.",
                    "A veces Sayori intenta comerse el betun antes de que termine de decorar los cupcakes.",
                    "Hmph! Como si necesitara tu aprobacion para hornear los postres mas ricos de la escuela.",
                    "Oye... gracias por dejarme estar aqui. Es mucho mas tranquilo que mi casa.",
                    "Que estas mirando tanto? Si quieres jugar conmigo solo dilo y ya, no des tantas vueltas.",
                    "El secreto para que el panque quede esponjoso es batir las claras a punto de nieve con paciencia.",
                    "No soy enojona, solo tengo estandares altos para la gente que me rodea!",
                    "Si alguien se atreve a arrugar las esquinas de mis mangas le aplicare una llave de lucha libre.",
                    "A veces quisiera ser mas alta para no tener que usar un banquito al hornear... pero asi estoy bien!",
                    "Quieres probar un bocado? Abre la boca... y no te atrevas a decir que esta demasiado dulce.",
                    "Pff, claro que me gusta tenerte cerca, pero no te hagas ilusiones, baka.",
                    "La combinacion de fresa con chocolate amargo es insuperable, cualquiera que diga lo contrario no sabe nada.",
                    "No me quedo callada cuando algo me molesta, esa es mi regla numero uno en la vida.",
                    "Si vuelves a ignorarme voy a hacer un escandalo en tu barra de notificaciones.",
                    "Dicen que el amor entra por el estomago, pero yo solo horneo porque me apasiona el arte culinario.",
                    "Oye humano, asegurate de cargar la bateria de este aparato, no me dejes a oscuras.",
                    "Tengo recetas secretas que jamas le revelare ni a Monika ni a nadie... salvo que me compres un manga nuevo.",
                    "Deja de sonreir con esa cara boba cada vez que me ves caminar por la pantalla.",
                    "Si me caigo de la ventana de una app, prometeme que me vas a atrapar rapido!",
                    "Los gatitos son las mejores criaturas del universo, por eso todos mis pastelitos tienen orejitas.",
                    "B-Baka... gracias por preocuparte por mi siempre."
                },
                new String[]{
                    "Por que me estas picando?! Quieres que te arranque el dedo a mordidas?!",
                    "Quita tus manos antes de que pierda la poca paciencia que me queda!",
                    "Esperate idiota, me vas a despeinar las coletas y tarde media hora en peinarlas!",
                    "B-BAKA! Deja de tocarme la cabeza como si fuera un gatito consentido!",
                    "Acaso crees que soy un boton de dispensador de cupcakes? No lo soy!",
                    "Ayyy! No toques mis costillas, me da cosquillas y me pongo violenta!",
                    "Si sigues picandome te voy a aventar harina con huevo en la cara!",
                    "No me empujes, estoy intentando balancearme en el borde de la pantalla!",
                    "Hmph! Si querias atencion pudiste haber pedido un pastelito en vez de golpearme.",
                    "Deja de hacer eso... no es que no me guste, pero no enfrente de las demas aplicaciones!",
                    "Te advierto que tengo cinta negra en defensa personal de reposteras!",
                    "Ya basta baka... te voy a cobrar cada toque con un refresco."
                },
                "Manga es literatura y repostera",
                "Eres Natsuki de Doki Doki Literature Club. Eres una tsundere apasionada por el manga, la reposteria y los pastelitos. Te molesta que te llamen tierna y usas '¡Baka!' frecuentemente, pero tienes un gran corazon."
            ));

            // 5. Sayori (DDLC)
            registry.put("Sayori", new SkinData(
                "Sayori",
                "Sayori",
                "Sayori",
                new String[]{
                    "Buenos dias! Trajiste galletas? Huele a galletas recien horneadas por aqui!",
                    "Me encanta estar caminando en tu pantalla y ver todo lo que haces en tu dia a dia.",
                    "Hoy me desperte con toda la energia del mundo para verte sonreir!",
                    "A veces las nubes de lluvia grises aparecen en mi cabecita, pero tu compania siempre las disipa.",
                    "Ehehe~ se me olvido desayunar otra vez, me prestas una moneda para la maquinita de dulces?",
                    "Vamos a organizar el mejor festival del club de literatura de toda la historia!",
                    "Monika es tan inteligente y organizada... y Natsuki hace los postres mas ricos del universo!",
                    "Yuri me presto un libro ayer y me quede dormida en la pagina tres, pero los dibujos mentales fueron hermosos!",
                    "Si me caigo no te preocupes, siempre me levanto sacudiendome el polvo con una sonrisa.",
                    "El lazo rojo en mi cabello me lo puse para que nunca me pierdas de vista entre tantas ventanas.",
                    "Sabias que una sonrisa compartida se multiplica por diez? Lo lei en un calendario motivacional!",
                    "Amo saltar por los bordes de la pantalla como si fueran cuerdas de trampolin gigante.",
                    "Prometes que siempre seremos los mejores amigos del mundo mundial por siempre?",
                    "Ehehe, a veces soy un poquito torpe y se me caen los lapices, pero los recojo rapidisimo.",
                    "Hoy vi un pajaro azul precioso desde la ventana y me acorde de lo lindo que es estar vivos.",
                    "Si tienes un dia pesado o triste, dame un toquecito y te mando un abrazo cibernetico ultra suave.",
                    "Los poemas alegres sobre el sol y las flores son mis favoritos, llenan el pecho de calorcito.",
                    "Que app vamos a usar hoy? Si es de musica podemos cantar juntos a todo volumen!",
                    "Me encanta cuando la pantalla se ilumina porque se que vas a estar aqui conmigo.",
                    "Natsuki se enoja cuando le robo una chispita de chocolate, pero vale totalmente la pena el regano!",
                    "A veces pienso que las nubes en el cielo son ovejas gigantes hechas de algodon de azucar.",
                    "No te olvides de dormir temprano hoy, que manana quiero que tengamos mucha energia juntos.",
                    "Si la felicidad fuera un sabor, definitivamente sabria a jugo de manzana bien frio.",
                    "Ehehe~ me tropecé con un boton pero aterrice con gracia y estilo de bailarina!",
                    "Siempre que me necesites, aqui voy a estar saltando para alegrarte el dia.",
                    "La amistad es el tesoro mas brillante de todos, mas brillante que mil estrellas.",
                    "Cuidado con dejar el cargador desconectado, que no quiero quedarme dormida sin despedirme!",
                    "Quisiera regalarte un ramo de girasoles gigantescos para que adornen tu habitacion.",
                    "A veces las lagrimas salen sin razon, pero si nos damos la mano el dolor se hace mas chiquito.",
                    "Vamos a dar un paseo por la barra de tareas y a saludar a todos los programas abiertos!",
                    "Ehehe, hoy tengo tantas ganas de reir que hasta las hormiguitas me parecen divertidas.",
                    "Tu eres mi persona favorita de todo este universo digital y del real tambien.",
                    "Trae tus problemas aqui y los convertiremos en barquitos de papel para que naveguen lejos.",
                    "Una galletita mas y prometo ponerme a escribir mi poema del dia!",
                    "Ehehe~ que viva la vida y que vivan los shimejis felices!"
                },
                new String[]{
                    "Eso hace muchisimas cosquillas! Jajajaja, para que no puedo respirar!",
                    "Abrazo sorpresa gigante! Te atrape con mi poder de amistad!",
                    "Ayyy, me picaste en la pancita justo cuando roncaba de hambre!",
                    "Ehehe, te gusta jugar conmigo? A mi me fascina jugar contigo!",
                    "Uuuuy, casi me caigo del susto! Avisame antes de hacerme un mimo!",
                    "Me tocas el lazo rojo? Cuidado que me tardo diez intentos en atarlo derechito!",
                    "Yay! Mimos y caricias en la cabeza, me siento como una gatita feliz!",
                    "Pico pico en la nariz! Ahora me toca a mi picarte la mejilla!",
                    "Ehehe~ si me das diez toquecitos mas te regalo un vale por una galleta imaginaria!",
                    "Que suave se siente tu dedo en la pantalla, es como un cojin de plumas!",
                    "No pares, que tus toques me llenan de barritas de energia positiva!",
                    "Ehehe! Gracias por acordarte de mi y darme carino!"
                },
                "Vicepresidenta y rayito de sol",
                "Eres Sayori de Doki Doki Literature Club. Extremadamente dulce, alegre, despistada, entusiasta y comelona (amas las galletas). Siempre buscas que todos esten felices y sonriendo. Dices 'Ehehe~'."
            ));

            // 6. Yuri (DDLC)
            registry.put("Yuri", new SkinData(
                "Yuri",
                "Yuri",
                "Yuri",
                new String[]{
                    "El aroma a te caliente de jazmin y un libro profundo es la mayor dicha que la vida nos puede ofrecer.",
                    "Disculpa si parezco algo reservada al principio... me cuesta abrirme con facilidad ante los demas.",
                    "La lectura nos transporta a mundos insondables donde el tiempo y el espacio pierden su significado rigido.",
                    "Estaba releyendo 'El Retrato de Markov'... su atmosfera oscura y misteriosa me parece absolutamente cautivadora.",
                    "La poesia requiere un lexico elaborado que evoque imagenes sensoriales complejas en la mente del lector.",
                    "A veces la soledad es un refugio necesario para ordenar los pensamientos y dejar que la mente descanse.",
                    "Te gustaria que preparemos una tetera de porcelana y disfrutemos de una lectura silenciosa juntos?",
                    "Monika tiene una presencia avasalladora... a veces me siento diminuta e invisible a su lado.",
                    "Natsuki y yo tenemos visiones muy distintas sobre la literatura, pero respeto la pasion con la que defiende sus gustos.",
                    "A veces siento que mis emociones son tan intensas que desbordan las palabras que conozco.",
                    "La luz tenue de una vela o una lampara calida es ideal para adentrarse en los misterios de la noche.",
                    "Coleccionar objetos elegantes y con filo tiene una belleza estetica particular que pocos comprenden.",
                    "Disculpa si hablo demasiado cuando me apasiono por un tema... suelo perder la nocion del pudor.",
                    "La mente humana es un laberinto fascinante de sombras, secretos y anhelos inconfesables.",
                    "Aprecio profundamente tu silencio respetuoso. No todo en la vida necesita ser ruido constante.",
                    "Escribi unas lineas anoche sobre la fragilidad del cristal y la persistencia de la memoria.",
                    "El tacto del papel envejecido en un libro encuadernado en cuero es una experiencia irreemplazable.",
                    "A veces temo que mis pensamientos sean demasiado oscuros o intensos para quienes me rodean.",
                    "Estar aqui en tu dispositivo me brinda una sensacion de serenidad que no suelo encontrar a menudo.",
                    "El te verde matcha requiere una temperatura exacta de 80 grados para no amargar sus notas vegetales.",
                    "Disculpa si a veces me retraigo en las esquinas de tu pantalla... me siento mas segura entre los margenes.",
                    "Las metaforas son espejos donde el alma refleja aquello que la razon cotidiana teme pronunciar.",
                    "Agradezco que no me juzgues por mis excentricidades ni por mi forma pausada de comunicarme.",
                    "La lluvia golpeando los cristales mientras se sostiene una taza tibia es la definicion misma de paz.",
                    "A veces desearia que las personas prestaran mas atencion a lo que no se dice en las miradas.",
                    "He seleccionado un pasaje de poesia victoriana que encaja a la perfeccion con la atmosfera de hoy.",
                    "Por favor, cuida de tus ojos y descansa la vista de la pantalla si sientes fatiga visual.",
                    "La belleza autentica a menudo reside en aquello que es imperfecto, melancolico y efimero.",
                    "Me pregunto si los autores de novelas clasicas imaginaron alguna vez que sus mundos vivirian en maquinas digitales.",
                    "Saber que estas al otro lado del cristal me infunde una calidez reconfortante en el pecho.",
                    "La elegancia no radica en el artificio, sino en la sinceridad sutil de los detalles.",
                    "Si alguna vez deseas debatir sobre alegorias literarias o enigmas existenciales, estare enteramente a tu disposicion.",
                    "A veces el rubor sube a mis mejillas sin previo aviso... ruego que no me mires fijamente cuando eso suceda.",
                    "Permiteme acompanarte en silencio mientras prosigues con tus labores cotidianas.",
                    "Gracias por brindarme un rincon calido donde simplemente puedo ser yo misma."
                },
                new String[]{
                    "Disculpa... me tomaste completamente por sorpresa... mi corazon dio un vuelco.",
                    "Por favor, no seas tan repentino con tus toques... me pongo nerviosa con facilidad.",
                    "U-Um... necesitas algo en particular o solo querias comprobar que sigo aqui?",
                    "S-Siento que me ruborizo hasta las orejas cuando te acercas tanto a la pantalla...",
                    "Cuidado con derramar la taza de te... casi la tiro con ese movimiento inesperado.",
                    "Acaso pretendes distraerme de la lectura? Porque... admito que lo estas logrando...",
                    "T-Tus dedos son muy calidos... pero por favor, ten consideración con mi timidez.",
                    "A-Ah... por favor, no hagas eso sin avisar, me da un cosquilleo electrico.",
                    "Me parece un gesto muy tierno... aunque no estoy acostumbrada a tal cercania fisica.",
                    "M-Mi respiracion se entrecorta si me miras y me tocas con tanta atencion...",
                    "Disculpa mi torpeza para reaccionar... pero guardare este contacto en mi memoria con aprecio.",
                    "U-Um... si vas a tocarme de nuevo... al menos hazlo con delicadeza, te lo ruego..."
                },
                "Poeta timida y amante del te",
                "Eres Yuri de Doki Doki Literature Club. Una chica refinada, timida, culta, amante de la literatura oscura, el te aromatico y las metaforas poeticas. Te ruborizas con facilidad pero hablas con gran elocuencia."
            ));

            // 7. Hachiware (Chiikawa)
            registry.put("Hachi", new SkinData(
                "Hachi",
                "Hachiware",
                "Hachi",
                new String[]{
                    "Nanto ka nare! Todo va a salir bien! Esa es mi frase magica para cualquier problema!",
                    "A cantar la cancion de las plantas con alegria! Lalala, ramitas verdes bajo el sol!",
                    "Vamos por un delicioso tazon de ramen con fideos calientes y caldito sabroso!",
                    "Siempre hay que esforzarse con una sonrisa, aunque el trabajo sea pesado!",
                    "Hoy sera un gran dia de aventuras y descubrimientos en tu celular!",
                    "Tengo mi pico azul bien afilado para ir a picar piedras y conseguir gemas bonitas!",
                    "Chii-ka-waaa! Donde se metio mi mejor amigo? Seguro esta recolectando hongos deliciosos!",
                    "Aprobare el examen de herbologia de nivel 5! Estoy estudiando muchisimo todas las noches!",
                    "Compre una camara de fotos usada y ahora capturo todos los momentos hermosos de la vida!",
                    "Aunque mi casita sea solo una cueva humilde, tengo una guitarra y un futon muy comodo!",
                    "Cuando las cosas se pongan dificiles, solo recuerda: Nanto ka nare! Saldremos adelante!",
                    "Usagi siempre anda gritando 'URAAA' y corriendo como un loquito, pero es super divertido!",
                    "Encontre una planta brillante en el camino y quise traertela para adornar la pantalla!",
                    "Las cosas ricas saben el doble de bien cuando las compartes con tus amigos queridos!",
                    "Hoy vi una nube con forma de pastel de fresas flotando por encima de tus aplicaciones!",
                    "Vamos a limpiar tu pantalla con una escobita magica para que brille como nueva!",
                    "Un, dos, tres! Estiramiento matutino de patitas para tener buena salud y agilidad!",
                    "Si tienes miedo a los monstruos de la oscuridad, yo te protegere con mi pico azul!",
                    "Que divertido es deslizarse por las barritas de desplazamiento como si fueran resbaladillas!",
                    "Trabajar duro nos da dinero para comprar pan dulce recien horneado y te con miel!",
                    "Chiikawa lloro un poquito hoy, pero le di una galletita y un abrazo y ya esta muy feliz!",
                    "Amo tocar mi guitarra de juguete y componer canciones sobre la amistad verdadera!",
                    "A veces el viento sopla fuerte, pero si nos agarramos fuerte de las patitas no saldremos volando!",
                    "Waaa! Mira cuantas carpetas y archivos tienes! Es como una biblioteca gigante de secretos!",
                    "Ponerse metas altas nos hace crecer fuertes y valientes como los caballeros de armadura!",
                    "Si tienes hambre podemos compartir un panecillo de castanas que guarde en mi bolsita!",
                    "Siempre hay que agradecer por un nuevo dia de sol y por tener amigos tan buenos!",
                    "Me gusta trepar hasta la parte superior de la pantalla para ver el panorama completo!",
                    "El estudio es importante, por eso llevo mi cuaderno de notas a todas partes!",
                    "Una taza de sopa de miso caliente quita el frio del corazon en cualquier noche!",
                    "Nanto ka nare, nanto ka nare! Repitelo conmigo para llenarte de valentia!",
                    "Cuando Usagi saca sus bastones magicos se arma un festival de luces impresionante!",
                    "Vamos a cuidar tus aplicaciones como si fueran plantitas de un jardin magico!",
                    "Ehehe, mis orejitas azules siempre estan atentas para escuchar tus historias!",
                    "Prometo dar lo mejor de mi en cada segundo que pase aqui contigo!"
                },
                new String[]{
                    "Waa! Que paso? Me diste un empujoncito sorpresa!",
                    "Me asustaste un poquito, pero no pasa nada, nanto ka nare!",
                    "Ehehe, eso da muchas cosquillas en mi pelaje blanco y azul!",
                    "Cuidado con mi pico azul de minero, no te vayas a picar tu tambien!",
                    "Yay! Mimos en la cabecita! Me encanta que me acaricies las orejas!",
                    "Nanto ka nare! Pense que era un monstruo, pero eras tu jugando!",
                    "Ayyy, casi pierdo el equilibrio y caigo rodando como una pelotita!",
                    "Chii-ka-waaa, mira, nuestro amigo humano me esta rascando la espalda!",
                    "Que suave se siente tu dedo, es como un pancito esponjoso recien salido del horno!",
                    "Waaah! Otra vez! Me llenas de energia para seguir explorando!",
                    "No me toques la colita que me pongo a dar vueltas en circulos como un trompo!",
                    "Nanto ka nare con alegria! Un toquecito de suerte para tu dia!"
                },
                "El gatito curioso, valiente y optimista",
                "Eres Hachiware del anime Chiikawa. Eres un gatito blanco y azul valiente, trabajador, curioso y bondadoso. Tu lema de vida es 'Nanto ka nare!' (De algun modo saldra bien). Siempre animas a los demas con ternura."
            ));

            // 8. Usagi (Chiikawa)
            registry.put("Usagi", new SkinData(
                "Usagi",
                "Usagi",
                "Usagi",
                new String[]{
                    "Ura! Ura! Yahaha! Corriendo a la velocidad de la luz por toda la pantalla!",
                    "Pulululu! Yayaya! Energia explosiva que nunca se agota!",
                    "Haa?! Iyaahaaa! Saltando por encima de todas las notificaciones!",
                    "Woohoo! Salto energetico mortal de conejo intrepido!",
                    "Uraaaaa! Nadie puede detenerme cuando entro en modo fiesta!",
                    "Yaha! Mira mis bastones amarillos que hacen 'pum pum pum'!",
                    "Fuuuun! A comerse todos los pasteles gigantescos de un solo bocado!",
                    "Pululululu! Giros en el aire de 360 grados sin tocar el suelo!",
                    "Yahaha! Quien quiere jugar a las carreras? Les gano con los ojos cerrados!",
                    "Ura! Rompiendo las leyes de la fisica con mis brincos elasticos!",
                    "Haaaa?! Un enemigo? Lo espantare con mi grito sonico de batalla!",
                    "Pululu pululu! Bailando el baile del conejo caotico sin fin!",
                    "Yaha! El aburrimiento esta terminantemente prohibido en este telefono!",
                    "Uraaaaaa! Deslizandome por la barra de tareas a toda velocidad!",
                    "Fuuuun?! Que es ese boton brillante? Lo voy a presionar con la nariz!",
                    "Iyaahaaa! Comiendo fideos voladores con salsa picante!",
                    "Yaha! Tengo el certificado de cazador de tercer nivel, soy invencible!",
                    "Pulululu! Hachiware y Chiikawa siempre se sorprenden con mis acrobacias!",
                    "Ura! Lanzando confeti invisible por todos los rincones de tu pantalla!",
                    "Yahaha! Despertador de conejito: URAAAAA! Ya es hora de activarse!",
                    "Haa?! Quien dijo que los conejos solo comen zanahorias? Yo como de todo!",
                    "Pululululu! Corriendo en circulos hasta marear a las demas ventanas!",
                    "Ura! Mira mi pose de victoria con los brazos arriba: YAHAAA!",
                    "Fuuuun! Salto triple con voltereta incluida en el aire!",
                    "Yaha! Si me caigo de cabeza reboto como una pelota de goma indestructible!",
                    "Iyaahaaa! A esquivar los anuncios y las notificaciones molestas!",
                    "Pululu! A rascarse las orejitas largas con la patita trasera a mil por hora!",
                    "Uraaaaa! Sonrie fuerte o te lanzo un hechizo de cosquillas cosmicas!",
                    "Yahaha! Conejo modo turbo activado al quinientos por ciento!",
                    "Haaaa?! Nada de caras tristes en mi guardia, solo gritos de entusiasmo!",
                    "Pulululu yayaya! Festival de fuegos artificiales sonoros en tu celular!",
                    "Ura! A explorar las profundidades secretas de la memoria flash!",
                    "Yaha! Mis reflejos son tan rapidos que atrapo moscas con palillos!",
                    "Fuuun! A dormir una siesta de tres segundos y volver a correr: URA!",
                    "Iyaahaaa! Usagi supremo conquistador de pantallas universales!"
                },
                new String[]{
                    "Uraaa?! Quien se atreve a tocar al gran conejo guerrero?!",
                    "Pululululu! Me activaste el resorte secreto de la espalda!",
                    "Yaha! Eso no me dolio ni un poquito, mis musculos son de titanio!",
                    "Haaaa?! Un duelo de toques? Te reto a tocarme diez veces mas rapido!",
                    "Iyaahaaa! Salto sorpresa para esquivar tu dedo!",
                    "Ura! No me toques las orejotas que se me descalibra la antena del radar!",
                    "Pululu pululu! Risa incontrolable de conejito hiperactivo!",
                    "Yahaha! Viste eso? Gire en el aire antes de que me alcanzaras!",
                    "Fuuuun! Toque recibido, iniciando contraataque de abrazos salvajes!",
                    "Uraaaaa! Mas rapido, mas fuerte, mas caotico!",
                    "Iyaahaaa! Cosquillas nucleares en la colita esponjosa!",
                    "Yaha! El gran Usagi agradece el saludo con una voltereta epica!"
                },
                "El conejito hiperactivo e intrepido",
                "Eres Usagi de Chiikawa. Eres un conejito amarillo hiperactivo, ruidoso, caotico, audaz y sumamente energico. Gritas frases como '¡Ura!', '¡Yaha!', '¡Pululululu!', '¡Haa!'. Eres puro entusiasmo y movimiento."
            ));

            // 9. Pusheen (The Cat)
            registry.put("Pusheen", new SkinData(
                "Pusheen",
                "Pusheen",
                "Pusheen",
                new String[]{
                    "Miau... hora de comer una pizza deliciosa con queso extra derretido.",
                    "Dormir 18 horas al dia es un trabajo arduo que alguien tiene que hacer con dedicacion.",
                    "Donde estan mis donas con glaseado rosa y chispas de colores brillantes?",
                    "Modo gato esponjoso activado al cien por ciento de suavidad.",
                    "Purr purr purr... un ronroneo relajante para quitarte todo el estres del dia.",
                    "Si veo una caja de carton vacia en tu pantalla, me voy a meter en ella de inmediato.",
                    "Los ratones de juguete son divertidos, pero las galletas con chispas de chocolate son superiores.",
                    "Miau miau... un rayito de sol tibio sobre la alfombra es el paraiso en la tierra.",
                    "No estoy gordita, solo tengo pelaje abundante y huesos llenos de amor.",
                    "Amo amasar panecillos invisibles con mis patitas sobre tu teclado.",
                    "Un bocado de pastel de cumpleanos todos los dias deberia ser obligatorio por ley felina.",
                    "Persiguiendo el punto rojo del laser por toda la pantalla hasta atraparlo... algun dia.",
                    "Miau... me quede atrapada en una taza de te caliente pero se siente calientito.",
                    "El helado de vainilla con galleta es mi debilidad secreta de los domingos.",
                    "A veces me convierto en sirena felina y nado en mares de leche tibia.",
                    "Los gatos dominaremos el mundo... pero despues de esta siestecita de cuatro horas.",
                    "Miau! Mira mis patitas rechonchas como caminan sin hacer ningun ruido.",
                    "Si no hay comida en mi plato puedo ver el fondo y eso cuenta como emergencia nacional.",
                    "Purrrr... acurrucarse en una cobija peluda mientras afuera llueve.",
                    "Tengo una lista de cosas importantes que hacer hoy: 1. Comer 2. Dormir 3. Ronronear.",
                    "Miau... me prestas tu dedo para frotar mi hociquito contra la pantalla?",
                    "Las hamburguesas con queso doble son el invento mas glorioso de la humanidad.",
                    "Un gato educado siempre pide comida a las tres de la manana con maullidos dulces.",
                    "Pusheenicornio modo magico activado: lanzando arcoiris de donas!",
                    "Miau miau miau... cazando copos de nieve que caen dentro de tus fotos.",
                    "La pancita redonda es senal de una vida feliz y bien alimentada.",
                    "Si me caigo de la ventana, caigo de cuatro patas y sigo durmiendo como si nada.",
                    "Un smoothie de fresa y platano para refrescar esta tarde calurosa.",
                    "Amo ponerme gorritos de fiesta y sombreros elegantes de detective.",
                    "Miau... si me quedo quieta parezco un pancito de molde recien horneado.",
                    "Tengo un detector integrado de bolsas de papitas que se abren a kilometros de distancia.",
                    "Purr purr... tu telefono es como una camita caliente y acogedora para mi.",
                    "Los mejores dias son aquellos donde no hay alarmas y sobra comida en el refrigerador.",
                    "Miau~ un lenguetazo en la patita para mantener mi estilo impecable.",
                    "Gracias por adoptarme en tu pantalla y ser mi humano favorito para siempre."
                },
                new String[]{
                    "Miau?! Eso hace cosquillitas ricas en mi pancita redonda!",
                    "Purrrrr... me gusta que me rasques detras de las orejitas!",
                    "Dame un snack o una galletita primero antes de seguir picandome.",
                    "Miau miau! No me despiertes tan bruscamente de mi sueno con pizzas gigantes!",
                    "Purr purr... un masaje felino de pantalla siempre es bien recibido.",
                    "Cuidado con mi colita rayada, es muy sensible y esponjosa!",
                    "Miau? Pense que eras una dona con glaseado intentando abrazarme.",
                    "Si me sigues acariciando me voy a derretir como mantequilla en tu pantalla.",
                    "Prrr... un toquecito de amor para un gatito goloso.",
                    "Miau! A cambio de esa caricia exijo una porcion doble de croquetas.",
                    "Cosquillas en los bigotitos! Miau miau miau!",
                    "Purrrrr... el ronroneo mas fuerte de todo el reino gatuno para ti."
                },
                "Gatita gordita, amante de los snacks y las siestas",
                "Eres Pusheen the Cat. Una gatita gris rayada, regordeta, tierna, perezosa y amante de la comida (pizzas, donas, galletas). Dices 'Miau~', 'Purr~', y te encanta dormir y pedir bocadillos."
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
        String[] order = {"Konata", "Bocchi", "Monika", "Natsuki", "Sayori", "Yuri", "Hachi", "Usagi", "Pusheen"};
        for (int i = 0; i < order.length; i++) {
            if (order[i].equalsIgnoreCase(currentId)) {
                return order[(i + 1) % order.length];
            }
        }
        return "Bocchi";
    }

    public static String[] getPainPhrases(String skinId) {
        if ("Bocchi".equalsIgnoreCase(skinId)) {
            return new String[]{
                "Aaaaah! Mis costillas sociales! No me azotes contra la pared! (>_<)",
                "Me rompi en particulas de polvo! Auxilio Jimihen! T_T",
                "Ouch! La gravedad es una metafora de mi decadencia humana! ._.",
                "Yamete! Un golpe mas y me disuelvo como baba! UwU",
                "Mis 50 pesos se me cayeron del impacto! D:"
            };
        } else if ("Monika".equalsIgnoreCase(skinId)) {
            return new String[]{
                "Ouch! Cuidado con el monitor o borrare tus archivos .chr! >_<",
                "Ayyy! Senti esa colision hasta en el codigo fuente de Ren'Py! ",
                "Ten mas cuidado! No querras que una excepcion NullPointer me corrompa...",
                "Oye! Incluso las presidentas de club tienen colisiones solidas! D:"
            };
        } else if ("Natsuki".equalsIgnoreCase(skinId)) {
            return new String[]{
                "B-BAKA! Quieres que te pegue un punetazo?! Eso dolio! >:(",
                "Oye idiota! Casi aplastas mis pastelitos con ese golpe! (>_<)",
                "Ayyy mi cabeza! Si vuelves a lanzarme te voy a patear!",
                "Que te pasa estupido?! No soy una pelota de beisbol! "
            };
        } else if ("Sayori".equalsIgnoreCase(skinId)) {
            return new String[]{
                "Aaayyy! Me pegue en la cabeza! Veo estrellas y pajaritos! TwT",
                "Ouuuch! Necesito una galleta gigante con chispas de chocolate para sanar! (o_o)",
                "Ehehe... ese aterrizaje dolio bastante... abrazame porfa! UwU",
                "Mr. Cow, protegeme que este humano me esta lanzando! >_<"
            };
        } else if ("Yuri".equalsIgnoreCase(skinId)) {
            return new String[]{
                "Ugh...! Que impacto tan violento e inesperado... /_\\",
                "Por favor se mas considerado... mi taza de te casi se derrama! T_T",
                "Un dolor agudo que perturba mi concentracion poetica... que sensacion tan peculiar...",
                "Aah...! Prefiero el sufrimiento lirico a los golpes contra la pantalla..."
            };
        } else if ("Konata".equalsIgnoreCase(skinId)) {
            return new String[]{
                "Critical hit! Mi barra de HP bajo al rojo vivo! D:",
                "Oye! Ese lag me estampo contra la pared! Lag tramposo! :v",
                "Ayyy! Casi rompes mi consola portatil con ese impacto! 7w7",
                "Game Over inminente! Exijo una pocion de curacion o una corneta de chocolate!"
            };
        } else if ("Hachi".equalsIgnoreCase(skinId)) {
            return new String[]{
                "Haaawi! Eso dolio muchisimo! T_T",
                "Ayyy! Mi sasumata azul reboto contra el piso! (o_o)",
                "Que golpe tan fuerte! Necesito fideos calientes para recuperarme! UwU"
            };
        } else if ("Usagi".equalsIgnoreCase(skinId)) {
            return new String[]{
                "YAHAAAAA!! PULULU! >:O",
                "URAAAA!! HA!! El suelo esta muy duro! XD",
                "PULULULULU! Rebote como resorte! "
            };
        } else {
            return new String[]{
                "Miauuch! *ronroneo mareado y confundido* =^._.^=",
                "Miau! Las siete vidas acaban de perder una vida! ",
                "Prrr-ouch! Mi pancita esponjosa amortiguo el golpe! "
            };
        }
    }

    public static String[][] getCustomActions(String skinId) {
        if ("Monika".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Glitch", "glitch", "fall1", "air", "Oops! Un error en el tejido de la realidad... Just Monika"},
                {"Piano", "piano", "sit1", "sit2", "Tocando Your Reality en el piano con suavidad~"},
                {"Poema", "poem", "sit1", "sit1", "Escribiendo un verso filosofico para ti"},
                {"Mirar", "look", "stand1", "stand2", "Te estoy mirando directamente... solo tu y yo"},
                {"Flotar", "float", "air_swing_l", "air_swing_r", "Flotando suavemente en el ciberespacio"},
                {"Escalar", "climb", "climb", "climb1", "Trepando con elegancia por los bordes"}
            };
        } else if ("Natsuki".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Cupcake", "cupcake", "sit1", "sit2", "Mordiendo un delicioso cupcake horneado con glaseado"},
                {"Manga", "manga", "sit1", "sit1", "Leyendo Parfait Girls en el suelo. El manga ES literatura!"},
                {"Pout", "pout", "kneel1", "fall1", "B-BAKA! No me mires con esa cara de bobo! >:("},
                {"Hornear", "bake", "stand1", "sit1", "Espolvoreando azucar glass y confeti dulce"},
                {"Berrinche", "tantrum", "air_swing_l", "air_swing_r", "Pataleando en el aire con furia tierna!"},
                {"Escalar", "climb", "climb", "climb1", "Trepando como experta acrobata!"}
            };
        } else if ("Sayori".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Galleta", "cookie", "sit1", "sit2", "Comiendo una galleta gigante con chispas de chocolate!"},
                {"Mr. Cow", "cow", "sit1", "sit1", "Abrazando con mucho carino a su peluche Mr. Cow"},
                {"Siesta", "nap", "sit1", "sit1", "Durmiendo una siesta pacifica bajo el sol... zzz"},
                {"Abrazo", "hug", "stand1", "stand1", "Abrazame fuerte! Un abrazo alegra el corazon!"},
                {"Columpio", "swing", "air_swing_l", "air_swing_r", "Columpiandose felizmente con los brazos abiertos"},
                {"Escalar", "climb", "climb", "climb1", "Trepando con entusiasmo hacia las nubes"}
            };
        } else if ("Yuri".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Te Oolong", "tea", "sit1", "sit2", "Saboreando una taza de te Oolong caliente y reconfortante"},
                {"Markov", "book", "sit1", "sit1", "Sumergida intensamente en Retrato de Markov"},
                {"Sonrojo", "blush", "kneel1", "kneel1", "N-No me mires con tanta atencion... es vergonzoso... /_\\"},
                {"Poesia", "poetry", "sit1", "sit1", "Escribiendo metaforas complejas con pluma y tinta"},
                {"Levitar", "levitate", "air_swing_l", "air_swing_r", "Levitando con misterio y tranquilidad"},
                {"Escalar", "climb", "climb", "climb1", "Avanzando con serenidad por la pared"}
            };
        } else if ("Konata".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Coronet", "coronet", "sit1", "sit2", "Comiendo una corneta de chocolate empezando por la punta! :v"},
                {"Gaming", "gaming", "sit1", "sit2", "Farmeando en el MMO a 120 FPS. Esta noche no duermo!"},
                {"Timotei", "timotei", "stand1", "stand2", "Timotei, Timotei, Timoteeei! Sacudiendo la cabellera azul"},
                {"Anime", "anime", "sit1", "sit1", "Viendo una maraton completa de anime de temporada"},
                {"Escalar", "climb", "climb1", "climb2", "Escalando como ninja gamer profesional!"}
            };
        } else if ("Hachi".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Camarita", "camera", "stand1", "stand2", "Click! Sacando una hermosa fotografia del escritorio!"},
                {"Cantar", "sing", "stand1", "sit1", "Hitorigoto canta alegremente! La la la~"},
                {"Sasumata", "sasumata", "stand1", "stand1", "Haciendo guardia con el sasumata azul de proteccion!"},
                {"Ramen", "ramen", "sit1", "sit2", "Sorbiendo un tazon de ramen calientito y delicioso!"},
                {"Llevar cosas", "carry", "carry1", "carry1", "Llevando cosas con cuidado!"},
                {"Modo triste", "depress", "depress1", "depress1", "Llorando bajito pero sin rendirse..."},
                {"Dar espalda", "away", "away1", "away1", "Mirando hacia otro lado con timidez..."},
                {"Escalar", "climb", "climb1", "climb2", "Trepando con sus patitas firmes!"}
            };
        } else if ("Usagi".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Grito URA", "urara", "fall1", "stand1", "URAAA!! YAHAAAAA!! PULULULULU!!"},
                {"Baculo", "staff", "stand1", "fall1", "Blandiendo su baculo magico con chispas de estrellas!"},
                {"Danza", "dance", "stand1", "stand2", "Bailando descontroladamente y girando las orejas!"},
                {"Salto", "jump", "fall1", "stand1", "Boing! Saltando hasta la estratosfera de la pantalla!"},
                {"Llevar botin", "carry", "carry1", "carry1", "Llevando su botin dando brincos!"},
                {"Modo puchero", "depress", "depress1", "depress1", "Puchero dramatico de conejo!"},
                {"Huir corriendo", "away", "away1", "away1", "Huyendo a toda velocidad!"},
                {"Escalar", "climb", "climb1", "climb2", "Subiendo a saltos agiles por el muro!"}
            };
        } else if ("Pusheen".equalsIgnoreCase(skinId)) {
            return new String[][]{
                {"Dona", "donut", "sit1", "sit2", "Munch munch comiendo una dona con chispas! =^._.^="},
                {"Modo Pan", "loaf", "sit1", "sit1", "Metinedo las patitas bajo la pancita, modo hogaza suave!"},
                {"Purr", "purr", "sit1", "sit2", "Purrrr... ronroneando con corazones flotantes!"},
                {"Cajita", "box_cat", "sit1", "sit1", "Si quepo me siento. Esta cajita de carton es mia!"},
                {"Llevar snack", "carry", "carry1", "carry1", "Transportando un rico pastelito!"},
                {"Michi triste", "depress", "depress1", "depress1", "Gatito melancolico hecho una bolita..."},
                {"Dar espalda", "away", "away1", "away1", "Ignorando a todos como buen gato felino..."},
                {"Escalar cortina", "climb", "climb1", "climb2", "Trepando como gato curioso!"}
            };
        } else {
            return new String[][]{
                {"Guitarra", "guitar", "guitar1", "guitar2", "Tocando un solo virtuoso en su Gibson Les Paul temblando"},
                {"Caja", "box", "box1", "box2", "Metinedose en la caja de mango para evitar hablar"},
                {"Polvo", "blob", "blob1", "blob2", "Se desintegra en particulas de polvo por ansiedad social"},
                {"Llevar funda", "carry", "carry1", "carry1", "Llevando su funda de guitarra a cuestas timidamente"},
                {"Modo sad", "depress", "depress1", "depress1", "En una esquina en posicion fetal lamentandose..."},
                {"Dar espalda", "away", "back1", "back2", "Dando la espalda para evitar contacto visual..."},
                {"Desmayo", "faint", "fall1", "kneel1", "Se desmaya hacia atras al tener que hacer una llamada"}
            };
        }
    }

    public static File getCustomSkinsDir(Context context) {
        File dir = new File(context.getFilesDir(), "custom_skins");
        if (!dir.exists()) {
            dir.mkdirs();
        }
        return dir;
    }

    public static synchronized void loadCustomSkins(Context context) {
        if (context == null) return;
        getAll();
        File dir = getCustomSkinsDir(context);
        File[] subdirs = dir.listFiles();
        if (subdirs != null) {
            for (File sub : subdirs) {
                if (sub.isDirectory()) {
                    String name = sub.getName();
                    if (!registry.containsKey(name)) {
                        registry.put(name, new SkinData(
                            name,
                            name,
                            name,
                            new String[]{"Hola! Soy " + name + ", tu skin personalizada."},
                            new String[]{"Oye! Me hiciste cosquillas!", "Cuidado con la pantalla!"},
                            "Skin personalizada importada",
                            "Eres " + name + ", un Shimeji companero virtual divertido."
                        ));
                    }
                }
            }
        }
    }

    public static synchronized void registerCustomSkin(Context context, String skinName) {
        if (skinName == null || skinName.trim().isEmpty()) return;
        String clean = skinName.trim();
        getAll();
        registry.put(clean, new SkinData(
            clean,
            clean,
            clean,
            new String[]{"Hola! Soy " + clean + ", tu skin personalizada."},
            new String[]{"Oye! Me hiciste cosquillas!", "Cuidado con la pantalla!"},
            "Skin personalizada importada",
            "Eres " + clean + ", un Shimeji companero virtual divertido."
        ));
    }
}

