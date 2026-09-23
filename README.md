# 🌸 Bocchi Shimeji con IA local y API

Una mascota de escritorio inspirada en Bocchi-Chan. PinkChan puede caminar por el escritorio, trepar paredes y techo, reproducir animaciones personalizadas, mostrar mensajes y conversar mediante una IA local o la API de Google Gemini.

> ⚠️ **Proyecto experimental para Windows.** Algunas acciones pueden mover, minimizar, cerrar o enviar elementos a la papelera. Revisa siempre la acción antes de ejecutarla y mantén desactivados los modos autónomos si no quieres que PinkChan interactúe con tu escritorio automáticamente.

## ✨ Características

- 🐾 Mascota de escritorio transparente y siempre visible.
- 🎨 Animaciones personalizadas definidas en `Actions.xml` y almacenadas en `img/Shimeji/`.
- 🧗 Movimiento autónomo por el suelo, las paredes y el techo.
- 🎸 Acciones manuales como tocar la guitarra, modo blob, fantasma, truco de caja, arrodillarse y más.
- 🤖 Chat con dos modos:
  - **Local:** utiliza `HuggingFaceTB/SmolLM2-135M-Instruct` mediante Transformers.
  - **API:** utiliza Google Gemini mediante una API key.
- 🪟 Acciones sobre ventanas de Windows: minimizar, maximizar/restaurar, cerrar o arrastrar una ventana seleccionada.
- 🖥️ Acciones sobre iconos del escritorio: mezclar, dispersar, ordenar, mover o enviar un icono a la papelera.
- 👁️ Modo para seguir el cursor.
- 😈 Modos autónomos opcionales para ventanas y escritorio.

## 🛠️ Requisitos

- Windows 10 o posterior para disponer de todas las funciones de ventanas y escritorio.
- Python 3.10 o posterior.
- `pip` disponible en el PATH.
- Las imágenes de `img/Shimeji/` y `Actions.xml` deben permanecer junto a `PinkChan.pyw`.

Las funciones relacionadas con Windows requieren `pywin32` y no están disponibles en otros sistemas operativos. El modo local puede necesitar memoria adicional para descargar y ejecutar el modelo de Transformers.

## 🚀 Instalación y uso

### Opción recomendada: Windows

1. Descarga o clona el repositorio:

   ```bash
   git clone https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api.git
   cd bocchi-shimeji-con-ia-local-y-api
   ```

2. Comprueba que Python está instalado:

   ```bash
   python --version
   ```

3. Ejecuta `iniciar.bat` con doble clic. El script instala automáticamente `Pillow`, `requests` y `pywin32` si no están instalados, y después inicia PinkChan sin mostrar una consola permanente.

También puedes instalar las dependencias manualmente:

```bash
python -m pip install pillow requests pywin32 transformers torch winshell
```

4. Inicia la aplicación directamente si lo prefieres:

   ```bash
   pythonw PinkChan.pyw
   ```

### Linux y otros sistemas

El repositorio incluye `iniciar.sh`, pero el código utiliza APIs específicas de Windows (`pywin32`, ventanas y el escritorio de Windows). Por tanto, las funciones completas requieren Windows y el script de Linux no garantiza compatibilidad.

## 💬 Usar el chatbot

1. Haz clic derecho sobre PinkChan.
2. Selecciona **🤖 Preguntarle algo**.
3. Elige uno de los modos disponibles:
   - **Local (SmolLM):** descarga el modelo la primera vez y funciona sin conexión después de tenerlo disponible.
   - **API (Gemini):** introduce tu API key de Google AI Studio.
4. Pulsa **🔍 Verificar Estado / Probar IA** antes de enviar mensajes.

La API key se introduce durante la ejecución y no debe guardarse en el repositorio ni compartirse públicamente.

## 🎮 Controles

### Clic izquierdo

- Mantén pulsado para arrastrar a PinkChan.
- Haz doble clic para mostrar una frase.

### Clic derecho

- 🎸 Animaciones y acciones especiales.
- 🧗 Escalar paredes o ir al techo.
- 🪟 Acciones sobre ventanas de Windows.
- 🖥️ Acciones sobre iconos del escritorio.
- 👁️ Activar o desactivar el seguimiento del cursor.
- 🤖 Abrir el chatbot.
- ✕ Cerrar la aplicación.

Para las acciones que indican **“apuntar”**, selecciona la ventana con el cursor después de activar la opción. Pulsa `Esc` para cancelar la selección cuando corresponda.

## ⚙️ Personalización

- Modifica `Actions.xml` para cambiar el mapeo de animaciones y sus frames.
- Añade o reemplaza imágenes PNG en `img/Shimeji/` respetando los nombres usados por `Actions.xml`.
- Ajusta constantes como `SIZE`, `FPS`, `WALK_SPEED` y `CLIMB_SPEED` en `PinkChan.pyw`.
- La personalidad y los mensajes del chatbot se pueden modificar en `PinkChan.pyw`, dentro de `SYSTEM_PROMPT`, `SPEECHES` y `POKED_SPEECHES`.

> El programa espera actualmente los recursos desde la carpeta del proyecto. Si mueves el repositorio a otra ubicación, revisa las rutas configuradas en `PinkChan.pyw` antes de ejecutarlo.

## 🗂️ Estructura del proyecto

```text
.
├── img/
│   └── Shimeji/          # Imágenes PNG de las animaciones
├── Actions.xml           # Acciones y frames de animación
├── Behaviors.xml         # Configuración adicional de comportamientos
├── PinkChan.pyw          # Aplicación principal
├── iniciar.bat           # Instalación de dependencias e inicio en Windows
├── iniciar.sh            # Script de inicio experimental
├── leeme uwu antes de todo .txt
└── README.md             # Documentación
```

## ⚠️ Seguridad y precauciones

- Desactiva **Autonomía** antes de dejar la aplicación funcionando sin supervisión.
- Las acciones de cierre pueden cerrar ventanas con trabajo no guardado.
- La acción de papelera utiliza la papelera de reciclaje, pero comprueba el resultado antes de usarla.
- Haz copias de seguridad de archivos importantes y prueba las acciones en un entorno controlado.
- No ejecutes el programa como administrador salvo que sea estrictamente necesario.
- No incluyas API keys en `PinkChan.pyw`, commits, capturas de pantalla o incidencias públicas.
- Descarga dependencias y modelos únicamente desde fuentes confiables.

## 🐛 Problemas conocidos

- Las funciones de ventanas y escritorio solo funcionan correctamente en Windows con `pywin32` instalado.
- El primer uso del modo local puede tardar porque Transformers debe descargar el modelo.
- Si las animaciones no aparecen, verifica que `img/Shimeji/` esté junto a `PinkChan.pyw` y que los nombres de `Actions.xml` coincidan con los archivos PNG.
- Si `iniciar.bat` no encuentra Python, instala Python y activa la opción **Add Python to PATH**.

## 🤝 Contribuciones

Las mejoras son bienvenidas:

1. Crea un fork del repositorio.
2. Crea una rama para tu cambio.
3. Prueba la modificación en Windows.
4. Actualiza la documentación si cambias el comportamiento o la instalación.
5. Abre un pull request explicando los cambios y las precauciones necesarias.

## 📜 Licencia

Este proyecto se distribuye actualmente con fines de entretenimiento. Antes de redistribuirlo, añade una licencia concreta y revisa las licencias de las imágenes, modelos y dependencias utilizadas.
