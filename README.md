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
- 😈 **Modo Troll Activable/Desactivable:**
  - **Interruptor ON/OFF:** Apágalo para que Bocchi sea una asistente dócil y formal, o enciéndelo para desatar el caos cómico.
  - **Travesuras seguras (sin alterar el sistema ni borrar archivos):**
    - Rickrolls sorpresa en el navegador.
    - Simulador de Pantallazo Azul (BSOD) y pantalla HackerTyper.
    - Terremoto de ventanas (sacudida rápida y desplazamiento de ventanas activas).
    - Minimizar ventanas inesperadamente.
    - Alertas y avisos falsos de Windows personalizados con tu nombre de usuario e IP real.
- 🪟 **Interfaz Limpia y Dinámica con el Sistema:**
  - Colores dinámicos adaptados automáticamente al color de acento de Windows (leído del Registro `DWM\ColorizationColor`) y soporte para Modo Oscuro/Claro nativo.
  - Ventana de **Personalización de Apariencia** en tiempo real: selector de colores (acento, superficie, fondo), control deslizante de transparencia (40% a 100%), familia y tamaño de fuentes tipográficas.
  - Sin colores morados estridentes fijos y estética profesional con iconos de texto limpios.
- 🤖 **Chatbot IA con dos modos:**
  - **Local:** Utiliza `HuggingFaceTB/SmolLM2-135M-Instruct` mediante Hugging Face Transformers.
  - **API:** Utiliza Google Gemini mediante API Key.
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

## ⌨️ Atajos de Comandos en el Chat (JARVIS)

Puedes escribirle en lenguaje natural o usar atajos directos en el chat:

| Comando | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `abre <app/distro>` | Abre app, programa o distro de WSL | `abre arch`, `abre chrome`, `abre calc` |
| `/alias <frase> = <comando>` | Guarda un alias/comando permanente | `/alias abre arch = wsl -d archlinux` |
| `/delcmd <frase>` | Elimina un alias/comando permanente | `/delcmd abre arch` |
| `/listcmd` | Lista los comandos personalizados guardados | `/listcmd` |
| `/addpath <carpeta>` | Añade carpeta de búsqueda para programas/archivos | `/addpath D:\MisJuegos` |
| `/delpath <carpeta>` | Elimina carpeta personalizada | `/delpath D:\MisJuegos` |
| `/listpaths` | Lista rutas de búsqueda configuradas | `/listpaths` |
| `/ps <comando>` | Ejecuta un comando en PowerShell | `/ps Get-Process` |
| `/web <búsqueda>` | Busca en Google / Navegador | `/web mejores animes 2024` |
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
