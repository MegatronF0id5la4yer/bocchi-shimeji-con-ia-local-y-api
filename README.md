# 🌸 Bocchi Shimeji con IA local, API y Asistente JARVIS

Una mascota interactiva para escritorio (Windows) y dispositivos móviles (Android) inspirada en Bocchi-Chan (*Hitori Gotoh*) y personajes icónicos como Konata Izumi y las chicas de Doki Doki Literature Club. Camina por la pantalla, trepa paredes y techo, reproduce animaciones fluidas, cuenta con detección de datos del sistema, asistente **JARVIS** para manipular archivos y ejecutar comandos, control por voz, un **Modo Troll** interactivo con bromas seguras, y soporte **Multi-Shimeji**.

---

## 📥 Descargas Directas / Releases

Descarga directamente los ejecutables listos para usar sin necesidad de configurar entornos:

| Plataforma | Archivo | Descripción | Enlace de Descarga Directa |
| :--- | :--- | :--- | :--- |
| **Windows 10 / 11** | `PinkChan.exe` | Ejecutable Standalone portable (36.8 MB, no requiere instalar Python) | [📥 Descargar PinkChan.exe](https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/raw/main/PinkChan.exe) |
| **Android (APK Nativo)** | `PinkChan_Shimeji.apk` | App nativa con superposición de pantalla, Multi-Shimeji y Asistente de Voz (4.5 MB) | [📱 Descargar PinkChan_Shimeji.apk](https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/raw/main/PinkChan_Shimeji.apk) |
| **Android (Port B / Web)** | `portb.html` | Port universal HTML5 / Termux / Navegador (Android 8 hasta el más reciente) | [🌐 Ver Port B (portb.html)](https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/blob/main/portb.html) |
| **GitHub Releases** | Releases Oficiales | Repositorio de versiones, notas de parche y assets | [🏷️ Ver GitHub Releases](https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/releases) |

---

## ✨ Características Principales

### 🖥️ Versión de Escritorio (Windows)
- 🐾 **Mascota de escritorio transparente y siempre activa:** Camina continuamente por el escritorio, trepa paredes y techo con física fluida e interactiva.
- 🎨 **Animaciones personalizadas** definidas en `Actions.xml` e imágenes en `img/Shimeji/` y `img/Konata/`.
- 🧗 **Física y movimiento autónomo mejorado:** Inicia caminando de inmediato al abrir, con un 80% de probabilidad de movimiento activo (caminar, caminar de espaldas, escalar paredes y caminar por el techo) intercalado con divertidas poses.
- 🎸 **Poses y modos manuales (clic derecho):** Menú contextual con clic derecho completamente funcional y fluido para activar poses: tocar guitarra, modo blob, fantasma, caja de cartón, arrodillarse, caminar de espaldas, etc.
- ⚡ **Asistente tipo JARVIS para Windows con control total:**
  - **Apertura de programas y archivos:** Abre programas por nombre o alias (*"abre bloc de notas"*, *"abre calculadora"*, *"abre chrome"*, *"abre spotify"*, *"abre discord"*, *"abre cmd"*, *"abre visual studio code"*) o archivos directos (*"abre documento.pdf"*, *"abre notas.txt"*).
  - **Integración con WSL (Linux) y PowerShell:** Abre terminales interactivas de tus distribuciones WSL al instante diciendo *"abre arch"*, *"abre archlinux"*, *"abre ubuntu"*, *"abre debian"*, *"abre kali"* o comandos de PowerShell (`/ps <comando>`, *"ejecuta en powershell <script>"*).
  - **Atajos rápidos de terminal preconstruidos:** Ejecución con un clic o comando para `wsl arch`, `hyfetch`, `sudo pacman -S <programa>` y `winget <programa>` / `winget search <programa>`.
  - **Comandos y Aliases Personalizados Permanentes:** Guarda tus propios comandos para siempre en `config.json` para ejecutarlos cuando digas una frase (*"cuando diga abrir juego corre D:\Juegos\game.exe"*, *"agrega comando compilar = npm run build"*, `/alias abre arch = wsl -d archlinux`, `/delcmd`, `/listcmd`).
  - **Rutas personalizadas para programas en carpetas raras:** Añade carpetas extra al escaneo del asistente para encontrar ejecutables y archivos estés donde estés (`/addpath D:\ProgramasRaros`, `/delpath`, `/listpaths`).
  - **Búsqueda rápida de archivos:** Encuentra archivos en tu Escritorio, Documentos, Descargas, rutas personalizadas o disco (*"busca tesis.docx"*, *"busca archivo notas.txt"*, `/find notas.txt`).
  - **Búsqueda en la Web y YouTube:** Abre búsquedas al instante (*"busca en web recetas de cocina"*, *"busca en google tutorial python"*, *"busca en youtube bocchi the rock"*, `/web <query>`, `/yt <query>`).
  - **Manipulación de archivos:** Crea, lee, escribe, modifica y renombra archivos tanto en lenguaje natural (*"hey haz que x archivo ahora se llame caca"*, *"crea notas.txt con hola mundo"*) como mediante atajos directos (`/create`, `/rename`, `/write`, `/read`, `/delete`, `/list`, `/open`, `/cmd`).
  - **Integración con IA:** Al conversar con Gemini o modelos locales, la IA puede emitir etiquetas de control del sistema (`[JARVIS: OPEN ...]`, `[JARVIS: SEARCH ...]`, `[JARVIS: ADD_CMD ...]`, `[JARVIS: PS ...]`, etc.) que se ejecutan automáticamente en Windows.
- 🖼️ **Fondos de Chat Personalizados (Imágenes o GIFs animados):**
  - Añade cualquier imagen (`.png`, `.jpg`, `.webp`) o **GIF animado (`.gif`)** como wallpaper de fondo del chat de Bocchi.
  - Reproducción continua y fluida de GIFs animados sin consumo de CPU excesivo.
  - Botón directo `[IMG] Fondo` en la barra superior del chat, sección en la ventana de **Apariencia** y atajos `/fondo` y `/fondo clear`.
- 😈 **Modo Troll Activable/Desactivable:**
  - **Interruptor ON/OFF:** Apágalo para que Bocchi sea una asistente dócil y formal, o enciéndelo para desatar el caos cómico.
  - **Travesuras seguras y 100% efectivas:**
    - **Pantallazo Azul (BSOD) Nativo a Pantalla Completa:** Simulación ultra-realista de Windows con carita triste `:(`, porcentaje de carga animado progresivo (0% a 100%), código QR y stop code con tu nombre de usuario real. Se descarta al instante con cualquier tecla, clic o tras 7 segundos.
    - Terremoto de ventanas: restaura y sacude ventanas activas incluso si están maximizadas.
    - Rickrolls y screamers seguros en el navegador con apertura garantizada (Chrome / Brave prioritarios, bloqueando Edge por defecto).
    - Alertas falsas del sistema y simulador HackerTyper.
- 🪟 **Interfaz Limpia y Dinámica con el Sistema:**
  - Colores dinámicos adaptados automáticamente al color de acento de Windows y soporte para Modo Oscuro/Claro nativo.
  - Ventana de **Personalización de Apariencia** en tiempo real: selector de colores, transparencia (40% a 100%), wallpapers y fuentes.
- 🤖 **Chatbot IA con dos modos:**
  - **Local (Offline):** Modelos ligeros mediante Hugging Face Transformers (`Qwen 0.5B`, `Qwen 1.5B`, `SmolLM2-360M`).
  - **API:** Google Gemini mediante API Key para capacidades completas de JARVIS.

---

### 📱 Versión Móvil para Android (App Nativa APK)
- 🪟 **Superposición completa sobre otras apps:** Shimeji flota y camina libremente por encima de cualquier app activa (WhatsApp, YouTube, navegador, juegos).
- 📲 **Compatibilidad Total Android 15 (API 35):** Cumple estrictamente con los nuevos requisitos de seguridad y servicios en primer plano (`SPECIAL_USE` foreground service type).
- 🌌 **Atmósfera Shijima & Interfaz de 4 Pantallas:**
  - **Featured:** Cuadrícula de personajes con badges premium, chips de categorías y previsualización animada.
  - **Installed:** Lista interactiva de mascotas instaladas con soporte de importación y gestión de carpetas.
  - **Inspector:** Vista de diagnóstico de la mascota activa con controles rápidos de interacción y decoraciones estilizadas.
  - **Settings:** Sliders táctiles con perillas naturales (tamaño de Shimeji, tasa de refresco, número máximo de mascotas) y paleta dinámica de colores de acento en tiempo real.
- 👥 **Soporte Multi-Shimeji:** Invoca hasta **6 Shimejis simultáneos** en pantalla. Cada uno cuenta con física 2D independiente, escalada de paredes, caminata por el techo y gravedad/flote.
- 🎙️ **Asistente de Voz y Ejecución de Apps:**
  - Reconocimiento de voz nativo en español (`SpeechRecognizer`).
  - **Abrir aplicaciones por voz:** Di *"abre whatsapp"*, *"abre youtube"*, *"abre camara"*, *"abre chrome"*, *"abre calculadora"* o cualquier app instalada y el Shimeji la abrirá de inmediato.
  - **Comandos de voz:** Consulta de hora (*"que hora es"*), saludos (*"hola"*, *"buenos dias"*), acciones físicas (*"guitarra"*, *"caja"*, *"salta"*, *"flotar"*, *"acariciar"*), clonación (*"invoca otro"*, *"limpiar extras"*) y cierre (*"detener"*).
- 🎁 **Sistema de Items y Snacks (Sprite Sheet de 40 objetos):** Suelta comida o bombas desde el sprite sheet `items.png` en Windows (clic derecho o `/item`) y en Android (menú flotante o Inspector). Los personajes comen los snacks felices o reaccionan en pánico ante bombas.
- 🔊 **Efectos de Sonido Popue (`popue.wav`):** Audio nativo al aparecer (spawn, invocar clon) y desaparecer (cerrar, retirar extras) los Shimejis en Windows y Android.
- 🛠️ **Comandos Termux y Gestión de Archivos:** Integración para ejecutar comandos útiles de Termux y crear directorios o archivos en `Documents/Shijima`.
- 👆 **Menú Contextual (Long-Press):** Mantén presionado al Shimeji en pantalla para desplegar su menú flotante con animaciones, items y mini-juegos (baile, rodar, saltar).
- 🚫 **Cero Emojis:** Interfaz limpia con tipografía e iconografía nativa elegante.

---

## 🎭 Personajes & Skins Animadas

Elige entre 9 personajes con físicas completas, personalidad y sprites de alta resolución (en PC desde el menú contextual con clic derecho; en Android desde el selector o el menú de pulsación prolongada):

| Personaje | Animación | Origen / Descripción | Comando |
| :---: | :---: | :--- | :---: |
| **Bocchi** *(Hitori Gotoh)* | <img src="img/gifs/bocchi.gif" width="96" height="96" alt="Bocchi" /> | *Bocchi the Rock!* - La guitarrista introvertida | `/skin bocchi` |
| **Konata Izumi** | <img src="img/gifs/konata.gif" width="96" height="96" alt="Konata" /> | *Lucky Star* - Otaku gamer legendaria (sprites limpios 128x128) | `/skin konata` |
| **Monika** | <img src="img/gifs/monika.gif" width="96" height="96" alt="Monika" /> | *Doki Doki Literature Club!* - Presidenta del club de literatura | `/skin monika` |
| **Natsuki** | <img src="img/gifs/natsuki.gif" width="96" height="96" alt="Natsuki" /> | *Doki Doki Literature Club!* - Fan del manga y la repostería | `/skin natsuki` |
| **Sayori** | <img src="img/gifs/sayori.gif" width="96" height="96" alt="Sayori" /> | *Doki Doki Literature Club!* - Dulce y siempre alegre | `/skin sayori` |
| **Yuri** | <img src="img/gifs/yuri.gif" width="96" height="96" alt="Yuri" /> | *Doki Doki Literature Club!* - Lectora apasionada y tímida | `/skin yuri` |
| **Hachi** *(Hachiware)* | 🐾 | *Chiikawa* - El gatito optimista y valiente | `/skin hachi` |
| **Usagi** | 🐰 | *Chiikawa* - El conejito hiperactivo e intrépido | `/skin usagi` |
| **Pusheen** | 🐱 | *Pusheen the Cat* - La gatita rechoncha y adorable | `/skin pusheen` |

---

## 🚀 Instalación y Uso

### En Windows

#### Opción 1: Ejecutable Standalone (Recomendado)
Descarga [`PinkChan.exe`](https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/raw/main/PinkChan.exe) y ejecútalo directamente. No requiere Python ni dependencias.

#### Opción 2: Lanzador automático (.bat)
Haz doble clic en `iniciar.bat`.
- Si detecta `PinkChan.exe`, lo inicia de inmediato.
- Si no, verificará Python, instalará las dependencias necesarias y abrirá `PinkChan.pyw`.

#### Opción 3: Código fuente en Python
```bash
pip install pillow requests pywin32 winshell
pythonw PinkChan.pyw
```

---

### En Android

#### Opción 1: App Nativa APK (Recomendado)
1. Descarga [`PinkChan_Shimeji.apk`](https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/raw/main/PinkChan_Shimeji.apk) en tu teléfono Android.
2. Instala el APK (permite la instalación de fuentes desconocidas si te lo solicita).
3. Abre la app y concede el **Permiso de Superposición** (Permitir mostrar sobre otras apps).
4. Otorga el permiso de **Micrófono** para el Asistente de Voz.
5. Toca **INICIAR** y disfruta de tus Shimejis flotantes.

#### Opción 2: Compilación manual con el script de build
Si tienes el Android SDK instalado en tu PC:
```powershell
powershell -ExecutionPolicy Bypass -File "android_app\build_apk.ps1"
```
El script generará y firmará automáticamente el APK en `PinkChan_Shimeji.apk`.

#### Opción 3: Port B (Universal Android 8 - 15 / Termux / Web)
Para dispositivos antiguos o entornos ligeros sin soporte de APK:
- Abre [`portb.html`](https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/blob/main/portb.html) directamente en Chrome o cualquier navegador móvil.
- O ejecuta en Termux:
  ```bash
  sh portb.sh
  ```

---

## ⌨️ Atajos de Comandos en el Chat (JARVIS)

Puedes escribirle en lenguaje natural o usar atajos directos en el chat de Windows:

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
Proyecto de entretenimiento y productividad. El modo troll no destruye archivos ni altera el registro del sistema operativo.
