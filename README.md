# 🌸 Bocchi Shimeji con IA local, API y Asistente JARVIS

Una mascota de escritorio interactiva inspirada en Bocchi-Chan (Hitori Gotoh). PinkChan camina por el escritorio, trepa paredes y techo, reproduce animaciones personalizadas, cuenta con detección de datos del sistema, asistente **JARVIS** para manipular archivos y ejecutar comandos de Windows, un **Modo Troll** interactivo con bromas seguras, e interfaz limpia y personalizable con colores dinámicos del sistema operativo.

---

## ✨ Características Principales

- 🐾 **Mascota de escritorio transparente y siempre activa:** Camina continuamente por el escritorio, trepa paredes y techo con física fluida e interactiva.
- 🎨 **Animaciones personalizadas** definidas en `Actions.xml` e imágenes en `img/Shimeji/`.
- 🧗 **Física y movimiento autónomo mejorado:** Inicia caminando de inmediato al abrir, con un 80% de probabilidad de movimiento activo (caminar, caminar de espaldas, escalar paredes y caminar por el techo) intercalado con divertidas poses.
- 🎸 **Poses y modos manuales (clic derecho):** Menú contextual con clic derecho completamente funcional y fluido para activar poses: tocar guitarra, modo blob, fantasma, caja de cartón, arrodillarse, caminar de espaldas, etc.
- ⚡ **Asistente tipo JARVIS para Windows con control total:**
  - **Apertura de programas y archivos:** Abre programas por nombre o alias (*"abre bloc de notas"*, *"abre calculadora"*, *"abre chrome"*, *"abre spotify"*, *"abre discord"*, *"abre cmd"*, *"abre visual studio code"*) o archivos directos (*"abre documento.pdf"*, *"abre notas.txt"*).
  - **Integración con WSL (Linux) y PowerShell:** Abre terminales interactivas de tus distribuciones WSL al instante solo diciendo *"abre arch"*, *"abre archlinux"*, *"abre ubuntu"*, *"abre debian"*, *"abre kali"* o comandos de PowerShell (`/ps <comando>`, *"ejecuta en powershell <script>"*).
  - **Comandos y Aliases Personalizados Permanentes:** Guarda tus propios comandos para siempre en `config.json` para ejecutarlos cuando digas una frase (*"cuando diga abrir juego corre D:\Juegos\game.exe"*, *"agrega comando compilar = npm run build"*, `/alias abre arch = wsl -d archlinux`, `/delcmd`, `/listcmd`).
  - **Rutas personalizadas para programas en carpetas raras:** Añade carpetas extra al escaneo del asistente para encontrar ejecutables y archivos estés donde estés (`/addpath D:\ProgramasRaros`, `/delpath`, `/listpaths`).
  - **Búsqueda rápida de archivos:** Encuentra archivos en tu Escritorio, Documentos, Descargas, rutas personalizadas o disco (*"busca tesis.docx"*, *"busca archivo notas.txt"*, `/find notas.txt`).
  - **Búsqueda en la Web y YouTube:** Abre búsquedas al instante (*"busca en web recetas de cocina"*, *"busca en google tutorial python"*, *"busca en youtube bocchi the rock"*, `/web <query>`, `/yt <query>`).
  - **Manipulación de archivos:** Crea, lee, escribe, modifica y renombra archivos tanto en lenguaje natural (*"hey haz que x archivo ahora se llame caca"*, *"crea notas.txt con hola mundo"*) como mediante atajos directos (`/create`, `/rename`, `/write`, `/read`, `/delete`, `/list`, `/open`, `/cmd`).
  - **Integración con IA:** Al conversar con Gemini o SmolLM, la IA puede emitir etiquetas de control del sistema (`[JARVIS: OPEN ...]`, `[JARVIS: SEARCH ...]`, `[JARVIS: ADD_CMD ...]`, `[JARVIS: PS ...]`, etc.) que se ejecutan automáticamente en Windows.
- 🖼️ **Fondos de Chat Personalizados (Imágenes o GIFs animados):**
  - Añade cualquier imagen (`.png`, `.jpg`, `.webp`) o **GIF animado (`.gif`)** como wallpaper de fondo del chat de Bocchi.
  - Reproducción continua y fluida de GIFs animados sin consumo de CPU excesivo.
  - El fondo permanece fijo en el visor estilo wallpaper moderno mientras los mensajes se desplazan con suavidad.
  - Burbujas de chat estilo tarjeta con contraste automático para una lectura perfecta sin importar el fondo elegido.
  - Botón directo `[IMG] Fondo` en la barra superior del chat, sección en la ventana de **Apariencia** y atajos `/fondo` y `/fondo clear`.
- 😈 **Modo Troll Activable/Desactivable:**
  - **Interruptor ON/OFF:** Apágalo para que Bocchi sea una asistente dócil y formal, o enciéndelo para desatar el caos cómico.
  - **Travesuras seguras y 100% efectivas (sin alterar el sistema ni borrar archivos):**
    - **Pantallazo Azul (BSOD) Nativo a Pantalla Completa:** Simulación ultra-realista de Windows con carita triste `:(`, porcentaje de carga animado progresivo (0% a 100%), código QR y stop code con tu nombre de usuario real. Se descarta al instante con cualquier tecla, clic o tras 7 segundos con Bocchi riéndose.
    - Terremoto de ventanas: restaura y sacude ventanas activas incluso si están maximizadas, con fallback para sacudir a Bocchi si no hay otras ventanas abiertas.
    - Mover ventanas activas o teletransportar a Bocchi por la pantalla.
    - Rickrolls y screamers seguros en el navegador con apertura garantizada.
    - Alertas y avisos de error falsos de Windows con tu nombre de usuario e IP real.
    - Simulador HackerTyper.
    - Minimizar ventanas inesperadamente (con soporte para minimizar la ventana de chat si no hay otra).
- 🪟 **Interfaz Limpia y Dinámica con el Sistema:**
  - Colores dinámicos adaptados automáticamente al color de acento de Windows (leído del Registro `DWM\ColorizationColor`) y soporte para Modo Oscuro/Claro nativo.
  - Ventana de **Personalización de Apariencia** en tiempo real: selector de colores (acento, superficie, fondo), control deslizante de transparencia (40% a 100%), selector de wallpaper para el chat, familia y tamaño de fuentes tipográficas.
  - Sin colores morados estridentes fijos y estética profesional con iconos de texto limpios.
- 🤖 **Chatbot IA con dos modos:**
  - **Local (Offline):** Utiliza **`Qwen/Qwen2.5-0.5B-Instruct`** (modelo ligero de ~0.5B parámetros de última generación) mediante Hugging Face Transformers. Especializado **exclusivamente en charla y conversación casual** (con filtro estricto anti-código, sin tecnicismos), fluido en español, con selector de modelos integrado en la interfaz (`Qwen 0.5B`, `Qwen 1.5B`, `SmolLM2-360M`) y atajo `/modelo <nombre>`.
  - **API:** Utiliza Google Gemini mediante API Key para capacidades completas de JARVIS y control extendido.
- 🌐 **Doxx / Panel de Información Real:**
  - Consulta tu usuario de Windows, nombre de equipo, IP pública real, IP local, proveedor de internet y geolocalización aproximada.

---

## 🛠️ Requisitos

- Windows 10 u 11 (recomendado para soporte nativo de APIs de ventanas, DWM y registro).
- Python 3.10 o posterior (o utilizar el ejecutable standalone compilado).
- Dependencias de Python:
  ```bash
  pip install pillow requests pywin32 winshell
  ```
  *(Opcional para IA local: `pip install transformers torch`)*

---

## 🚀 Instalación y Uso

### Método 1: Lanzador automático (.bat)
Haz doble clic en `iniciar.bat`.
- Si existe `PinkChan.exe`, lo iniciará directamente sin consola.
- Si no, verificará Python, instalará librerías faltantes y abrirá `PinkChan.pyw` de forma transparente.

### Método 2: Ejecutable Standalone (PinkChan.exe)
Puedes compilar o ejecutar el binario directamente con PyInstaller:
```bash
pyinstaller PinkChan.spec
```

### Método 3: Ejecutar con Python
```bash
pythonw PinkChan.pyw
```

---

---

## 🎭 Personajes & Skins Animadas

Elige entre 6 personajes con físicas completas, personalidad y diálogos únicos (puedes cambiar de skin desde el menú contextual con clic derecho, el comando `/skin <nombre>` o el botón `[🎭] Skins` en el dock):

| Personaje | Animación | Origen / Descripción | Comando |
| :---: | :---: | :--- | :---: |
| **Bocchi** *(Hitori Gotoh)* | <img src="img/gifs/bocchi.gif" width="96" height="96" alt="Bocchi" /> | *Bocchi the Rock!* - La guitarrista introvertida | `/skin bocchi` |
| **Konata Izumi** | <img src="img/gifs/konata.gif" width="96" height="96" alt="Konata" /> | *Lucky Star* - Otaku gamer legendaria | `/skin konata` |
| **Monika** | <img src="img/gifs/monika.gif" width="96" height="96" alt="Monika" /> | *Doki Doki Literature Club!* - Presidenta del club | `/skin monika` |
| **Natsuki** | <img src="img/gifs/natsuki.gif" width="96" height="96" alt="Natsuki" /> | *Doki Doki Literature Club!* - Fan del manga y la repostería | `/skin natsuki` |
| **Sayori** | <img src="img/gifs/sayori.gif" width="96" height="96" alt="Sayori" /> | *Doki Doki Literature Club!* - Dulce y siempre alegre | `/skin sayori` |
| **Yuri** | <img src="img/gifs/yuri.gif" width="96" height="96" alt="Yuri" /> | *Doki Doki Literature Club!* - Lectora apasionada y tímida | `/skin yuri` |

---

## ⌨️ Atajos de Comandos en el Chat (JARVIS)

Puedes escribirle en lenguaje natural o usar atajos directos en el chat:

| Comando | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `abre <app/distro>` | Abre app, programa o distro de WSL | `abre arch`, `abre chrome`, `abre calc` |
| `wsl arch` / `arch` | Abre terminal de WSL Arch Linux | `wsl arch` |
| `hyfetch` | Muestra resumen visual del sistema con HyFetch | `hyfetch` |
| `sudo pacman -S <p>` | Instala paquete en Arch Linux con pacman | `sudo pacman -S neovim` o `pacman git` |
| `winget <programa>` | Instala aplicación de Windows con winget | `winget vlc` o `winget install discord` |
| `winget search <p>` | Busca programas disponibles en repositorios winget | `winget search obsidian` |
| `/skin <nombre>` | Cambia el personaje activo | `/skin konata` o `pon a monika` |
| `/skins` | Muestra la lista de personajes disponibles | `/skins` |
| `/shortcuts` / `/atajos` | Guía completa de atajos de sistema y herramientas | `/atajos` |
| `/bat <código>` | Ejecuta un script BAT al vuelo y captura la salida | `/bat echo hola mundo` |
| `/alias <frase> = <comando>` | Guarda un alias/comando permanente | `/alias abre arch = wsl -d archlinux` |
| `/delcmd <frase>` | Elimina un alias/comando permanente | `/delcmd abre arch` |
| `/listcmd` | Lista los comandos personalizados guardados | `/listcmd` |
| `/addpath <carpeta>` | Añade carpeta de búsqueda para programas/archivos | `/addpath D:\MisJuegos` |
| `/delpath <carpeta>` | Elimina carpeta personalizada | `/delpath D:\MisJuegos` |
| `/listpaths` | Lista rutas de búsqueda configuradas | `/listpaths` |
| `/fondo` / `/bg` | Abre selector para fondo de chat (imagen o GIF) | `/fondo` |
| `/fondo clear` | Quita el fondo personalizado del chat | `/fondo clear` |
| `/bsod` / `/pantallazo` | Simula pantalla azul de la muerte (BSOD) | `/bsod` |
| `/shake` / `/sacudir` | Sacude la ventana activa o a Bocchi | `/shake` |
| `/ps <comando>` | Ejecuta un comando en PowerShell | `/ps Get-Process` |
| `/web <búsqueda>` | Busca en Google / Navegador (Chrome o Brave) | `/web mejores animes 2024` |
| `/yt <búsqueda>` | Busca directamente en YouTube | `/yt bocchi guitar solo` |
| `/find <archivo>` | Busca archivos en el sistema | `/find notas.txt` |
| `/rename <viejo> <nuevo>` | Renombra un archivo | `/rename notas.txt caca.txt` |
| `/create <archivo> [texto]` | Crea un archivo en el Escritorio | `/create lista.txt Huevos, Leche` |
| `/write <archivo> <texto>` | Sobrescribe texto en archivo | `/write lista.txt Pan` |
| `/append <archivo> <texto>` | Añade texto al final | `/append lista.txt Queso` |
| `/read <archivo>` | Lee el contenido de un archivo | `/read lista.txt` |
| `/delete <archivo>` | Envía archivo a la papelera | `/delete lista.txt` |
| `/list [carpeta]` | Muestra archivos del directorio | `/list` |
| `/open <ruta/app/url>` | Abre un archivo, programa o enlace | `/open calc` o `/open https://youtube.com` |
| `/cmd <comando>` | Ejecuta un comando en CMD | `/cmd ipconfig` |
| `/troll on` / `/troll off` | Activa o desactiva el Modo Troll | `/troll on` |

---

## 📜 Licencia y Advertencia
Proyecto de entretenimiento y experimentación. El modo troll no destruye archivos ni altera el registro del sistema operativo.
