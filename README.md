# bocchi-shimeji-con-ia-local-y-api
shimeji custom con bastantes acciones y action events como cerrar ventanas de windows 
Un Shimeji (mascota de escritorio) interactivo para Windows basado en Bocchi-Chan, con inteligencia artificial integrada (Local y API), autonomía de escritorio y animaciones personalizadas.
✨ Características

    🤖 IA Dual (Chatbot Integrado):

        Modo Local: Corre un modelo ultraligero (SmolLM2-135M) directamente en tu procesador/tarjeta gráfica usando transformers, 100% offline y gratis.

        Modo API: Conexión opcional a la API de Google Gemini.

    🪟 Trolling y Control de Ventanas:

        Minimiza, maximiza, cierra o arrastra ventanas de tu sistema.

        Modo autónomo donde la Shimeji interactúa sola con tus ventanas de vez en cuando.

    🖥️ Autonomía en el Escritorio:

        Desordena, mezcla o envía iconos del escritorio a la papelera.

        Sigue el cursor del ratón por la pantalla.

    🎨 Interfaz Personalizada:

        Transparencia al 70% en el chat para no estorbar.

        Ocultación rápida de API Key con la tecla Enter.

        Animaciones basadas en acciones escritas en Actions.xml (escalar paredes, ir al techo, modo blob, tocar guitarra, etc.).

🛠️ Requisitos Previos

Necesitas tener Python 3.10+ instalado en tu sistema.

Dependencias necesarias de Python:
Bash

pip install pillow requests pywin32 winshell transformers torch

🚀 Instalación y Uso
Opción 1: Ejecutar desde el código fuente

    Clona este repositorio:
    Bash

    git clone https://github.com/tu-usuario/PinkChan-Shimeji.git
    cd PinkChan-Shimeji

    Ejecuta el script con Python:
    Bash

    pythonw PinkChan.pyw

    (O usa el script ejecutable incluido iniciar.bat en Windows).

Opción 2: Compilar a un ejecutable .exe

Si quieres empaquetarlo en un solo archivo ejecutable para correrlo sin abrir consola:

    Instala pyinstaller:
    Bash

    pip install pyinstaller

    Compila el script:
    Bash

    pyinstaller --noconsole --onefile PinkChan.pyw

    Mueve el ejecutable generado en dist/PinkChan.exe a la raíz del proyecto (junto a las carpetas img/ y el archivo Actions.xml).

🎮 Controles del Menú (Clic Derecho)

Al hacer clic derecho sobre Bocchi, se despliega un menú interactivo con las siguientes funciones:

    🎸 Animaciones: Tocar guitarra, modo blob, fantasma, truco de caja, arrodillarse, escalar paredes/techo.

    🪟 Ventanas: Minimizar, cerrar, maximizar o arrastrar ventanas del sistema.

    🖥️ Escritorio: Dispersar, mezclar, ordenar o tirar iconos a la papelera.

    👁️ Seguir cursor: Activa o desactiva el modo donde Bocchi camina hacia tu ratón.

    🤖 Preguntarle algo: Abre la ventana del chatbot (Local / API).

📁 Estructura del Proyecto
Plaintext

├── img/
│   └── Shimeji/          # Frames PNG para cada animación
├── Actions.xml           # Configuración de mapeo de animaciones
├── PinkChan.pyw          # Código fuente principal de la aplicación
├── iniciar.bat           # Launcher rápido para Windows
└── README.md             # Documentación del proyecto

📜 Licencia

Proyecto desarrollado con fines de entretenimiento. Libre de modificar y redistribuir.
