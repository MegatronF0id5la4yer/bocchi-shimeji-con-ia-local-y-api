#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk
from tkinter import colorchooser
from tkinter import filedialog
from tkinter import font as tkfont
import random
import os
import sys
import threading
import json
import socket
import platform
import getpass
import xml.etree.ElementTree as ET
import subprocess
import webbrowser
import re
import shutil
import zipfile
import fnmatch
import urllib.parse
import urllib.request
import time
import importlib
import queue
import datetime
import base64
import winsound
try:
    from PIL import ImageGrab
    IMAGEGRAB_AVAILABLE = True
except Exception:
    IMAGEGRAB_AVAILABLE = False

try:
    import win32com.client, pythoncom
    SAPI_AVAILABLE = True
except Exception:
    SAPI_AVAILABLE = False

try:
    import winreg
except Exception:
    winreg = None

def _setup_python_paths():
    """Garantiza que el ejecutable o script pueda encontrar paquetes instalados como transformers y torch."""
    import glob
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        for pat in [
            os.path.join(local_appdata, "Python", "pythoncore-*", "Lib", "site-packages"),
            os.path.join(local_appdata, "Programs", "Python", "Python*", "Lib", "site-packages"),
        ]:
            for p in glob.glob(pat):
                if os.path.isdir(p) and p not in sys.path:
                    sys.path.append(p)
                    for sub in ("torch\\lib", "numpy.libs"):
                        libpath = os.path.join(p, sub)
                        if os.path.isdir(libpath) and hasattr(os, "add_dll_directory"):
                            try:
                                os.add_dll_directory(libpath)
                            except Exception:
                                pass
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        for p in glob.glob(os.path.join(appdata, "Python", "Python*", "site-packages")):
            if os.path.isdir(p) and p not in sys.path:
                sys.path.append(p)

    for pf in (os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")):
        if pf:
            for p in glob.glob(os.path.join(pf, "Python*", "Lib", "site-packages")):
                if os.path.isdir(p) and p not in sys.path:
                    sys.path.append(p)

_setup_python_paths()

# Habilitar DPI Awareness en Windows para evitar desajustes de pantalla y coordenadas
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

try:
    from PIL import Image, ImageTk, ImageSequence
    PIL_AVAILABLE = True
    try:
        FLIP_LEFT_RIGHT = getattr(getattr(Image, 'Transpose', Image), 'FLIP_LEFT_RIGHT', 0)
        FLIP_TOP_BOTTOM = getattr(getattr(Image, 'Transpose', Image), 'FLIP_TOP_BOTTOM', 1)
    except Exception:
        FLIP_LEFT_RIGHT = 0
        FLIP_TOP_BOTTOM = 1
except ImportError:
    PIL_AVAILABLE = False
    FLIP_LEFT_RIGHT = 0
    FLIP_TOP_BOTTOM = 1

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import win32gui, win32con, win32api, win32process
    import ctypes
    import ctypes.wintypes
    WIN32_AVAILABLE = True
except Exception:
    WIN32_AVAILABLE = False

try:
    import winshell
    WINSHELL_AVAILABLE = True
except Exception:
    WINSHELL_AVAILABLE = False

# Deteccion infalible de ruta base independientemente del directorio actual y modo congelado (exe)
if getattr(sys, 'frozen', False):
    EXE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = getattr(sys, '_MEIPASS', EXE_DIR)
    if os.path.isdir(os.path.join(EXE_DIR, "img", "Shimeji")):
        BASE_DIR = EXE_DIR
    else:
        BASE_DIR = BUNDLE_DIR
elif '__file__' in globals() and __file__:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR  = BASE_DIR
elif sys.argv and sys.argv[0]:
    BASE_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
    EXE_DIR  = BASE_DIR
else:
    BASE_DIR = os.getcwd()
    EXE_DIR  = BASE_DIR

try:
    os.chdir(BASE_DIR)
except Exception:
    pass

SKINS_DIR    = os.path.join(BASE_DIR, "img", "skins")
IMG_DIR      = os.path.join(SKINS_DIR, "Bocchi") if os.path.isdir(os.path.join(SKINS_DIR, "Bocchi")) else os.path.join(BASE_DIR, "img", "Shimeji")
ACTIONS_FILE = os.path.join(BASE_DIR, "Actions.xml")

def play_audio_file(file_path):
    """Reproduce cualquier archivo de audio (WAV, MP3) de forma asincrona mediante Windows MCI o winsound."""
    if not file_path or not os.path.isfile(file_path):
        return False
    try:
        if file_path.lower().endswith(".wav"):
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
    except Exception:
        pass
    try:
        import ctypes
        winmm = ctypes.windll.winmm
        abs_p = os.path.abspath(file_path).replace("\\", "/")
        alias = f"pc_snd_{int(time.time() * 1000) % 100000}"
        winmm.mciSendStringW(f'close {alias}', None, 0, 0)
        r = winmm.mciSendStringW(f'open "{abs_p}" type mpegvideo alias {alias}', None, 0, 0)
        if r != 0:
            r = winmm.mciSendStringW(f'open "{abs_p}" alias {alias}', None, 0, 0)
        if r == 0:
            winmm.mciSendStringW(f'play {alias}', None, 0, 0)
            return True
    except Exception:
        pass
    return False

def play_popue_sound():
    """Reproduce popue.wav de forma asincrona al aparecer, desaparecer o interactuar el Shimeji."""
    candidates = [
        os.path.join(BASE_DIR, "img", "Shimeji", "popue.wav"),
        os.path.join(BASE_DIR, "popue.wav"),
        os.path.join(EXE_DIR, "img", "Shimeji", "popue.wav"),
        os.path.join(EXE_DIR, "popue.wav")
    ]
    for c in candidates:
        if os.path.isfile(c):
            if play_audio_file(c):
                return True
    return False

def play_character_sound(skin_name, clip_name="poke", dub_lang=None):
    """Reproduce la voz del personaje (Original, Dub Español o Dub English) desde el banco de audio autentico."""
    sk = str(skin_name).strip() if skin_name else "Bocchi"
    cfg = load_config()
    lang = dub_lang or cfg.get("voice_dub_language", "es")  # "es", "en", "original"
    
    file_names = []
    if lang == "es":
        file_names = [f"{clip_name}_es.mp3", f"{clip_name}.mp3", f"{clip_name}_en.mp3"]
    elif lang == "en":
        file_names = [f"{clip_name}_en.mp3", f"{clip_name}.mp3", f"{clip_name}_es.mp3"]
    else:  # "original"
        file_names = [f"{clip_name}.mp3", f"{clip_name}_es.mp3", f"{clip_name}_en.mp3"]

    candidates = []
    for fn in file_names:
        for folder_case in [sk, sk.lower(), sk.capitalize()]:
            candidates.append(os.path.join(BASE_DIR, "sounds", folder_case, fn))
            candidates.append(os.path.join(EXE_DIR, "sounds", folder_case, fn))
    candidates.append(os.path.join(BASE_DIR, "sounds", sk, f"{clip_name}.wav"))
    candidates.append(os.path.join(EXE_DIR, "sounds", sk, f"{clip_name}.wav"))
    
    for c in candidates:
        if os.path.isfile(c):
            if play_audio_file(c):
                return True
    play_popue_sound()
    return False

APP_VERSION = "3.1.0"
VERSION_CODE = 3
VERSION_CHECK_URL = "https://raw.githubusercontent.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/main/version.json"
UPDATE_CHECK_INTERVAL_SEC = 900  # Comprobacion automatica cada 15 minutos

def check_for_updates(shimeji_ref=None, is_manual=False):
    """Comprueba automaticamente si hay una nueva actualizacion y la instala de fondo."""
    def _worker():
        try:
            cfg = load_config()
            last_check = cfg.get("last_update_check", 0)
            now = time.time()
            if not is_manual and (now - last_check < UPDATE_CHECK_INTERVAL_SEC):
                return

            req = urllib.request.Request(
                VERSION_CHECK_URL,
                headers={"User-Agent": "PinkChan-Desktop/3.1.0"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            cfg["last_update_check"] = int(now)
            save_config(cfg)

            remote_code = data.get("versionCode", 0)
            remote_name = data.get("versionName", "3.1.0")
            exe_url = data.get("exeUrl", "https://github.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/raw/main/PinkChan.exe")
            features = data.get("features", [])

            if remote_code > VERSION_CODE:
                feats_str = "\n".join([f"[*] {f}" for f in features])
                if is_manual:
                    prompt_msg = (
                        f"¡Nueva version disponible: v{remote_name}!\n\n"
                        f"Novedades:\n{feats_str}\n\n"
                        f"Se descargara e instalara la actualizacion automaticamente ahora."
                    )
                    ans = messagebox.askyesno("Actualizacion Disponible", prompt_msg)
                    if ans:
                        _auto_install_update(exe_url, remote_name, shimeji_ref)
                else:
                    # Actualizacion automatica desatendida en segundo plano
                    if shimeji_ref:
                        shimeji_ref.show_speech(f"[*] Nueva version v{remote_name} detectada.\nActualizando automaticamente...")
                    _auto_install_update(exe_url, remote_name, shimeji_ref)
            else:
                if is_manual:
                    messagebox.showinfo("Actualizaciones", f"Tienes instalada la version mas reciente (v{APP_VERSION}). [OK]")
        except Exception as exc:
            if is_manual:
                messagebox.showwarning("Actualizaciones", f"No se pudo comprobar la actualizacion (sin internet):\n{exc}")

    threading.Thread(target=_worker, daemon=True).start()

def _auto_install_update(exe_url, version_name, shimeji_ref=None):
    """Descarga e instala automaticamente la nueva version reemplazando PinkChan.exe y reiniciando."""
    def _dl_worker():
        try:
            if shimeji_ref:
                shimeji_ref.show_speech(f"[*] Descargando actualizacion v{version_name} en segundo plano...")
            
            temp_file = os.path.join(tempfile.gettempdir(), f"PinkChan_v{version_name}_{int(time.time())}.exe")
            urllib.request.urlretrieve(exe_url, temp_file)
            
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 1000000:
                if shimeji_ref:
                    shimeji_ref.show_speech("[!] Descarga incompleta. Se reintentara en la proxima comprobacion.")
                return

            if shimeji_ref:
                shimeji_ref.show_speech(f"[✓] Actualizacion v{version_name} descargada.\nAplicando y reiniciando...")

            target_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.join(EXE_DIR, "PinkChan.exe")
            if not os.path.exists(target_exe) and os.path.exists(os.path.join(EXE_DIR, "PinkChan.exe")):
                target_exe = os.path.join(EXE_DIR, "PinkChan.exe")

            bat_path = os.path.join(tempfile.gettempdir(), f"update_pinkchan_{int(time.time())}.bat")
            bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
copy /y "{temp_file}" "{target_exe}" >nul
del "{temp_file}" >nul
start "" "{target_exe}"
del "%~f0" & exit
"""
            with open(bat_path, "w", encoding="utf-8") as bf:
                bf.write(bat_content)

            subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=0x08000000 if sys.platform == "win32" else 0)
            if shimeji_ref and hasattr(shimeji_ref, "root"):
                shimeji_ref.root.after(500, lambda: os._exit(0))
            else:
                os._exit(0)
        except Exception as e:
            if shimeji_ref:
                shimeji_ref.show_speech(f"[!] Error aplicando actualizacion automatica: {e}")

    threading.Thread(target=_dl_worker, daemon=True).start()

SKIN_NAMES = ["Bocchi", "Konata", "Monika", "Natsuki", "Sayori", "Yuri", "Hachi", "Usagi", "Pusheen"]

def get_available_skins():
    """Retorna lista de todas las skins disponibles, incluyendo skins importadas."""
    skins = list(SKIN_NAMES)
    for b in [EXE_DIR, BASE_DIR]:
        sdir = os.path.join(b, "img", "skins")
        if os.path.isdir(sdir):
            for entry in os.listdir(sdir):
                full = os.path.join(sdir, entry)
                if os.path.isdir(full) and entry not in skins:
                    try:
                        files = os.listdir(full)
                        if any(f.lower().startswith("shime") or f.lower().endswith(".png") for f in files):
                            skins.append(entry)
                    except Exception:
                        pass
    return skins

def get_skin_dir(skin_name):
    """Obtiene la ruta absoluta del directorio de la skin."""
    target = skin_name.strip()
    for b in [EXE_DIR, BASE_DIR]:
        cand = os.path.join(b, "img", "skins", target)
        if os.path.isdir(cand):
            return cand
    if target.lower() in ("bocchi", "default"):
        for b in [EXE_DIR, BASE_DIR]:
            cand = os.path.join(b, "img", "Shimeji")
            if os.path.isdir(cand):
                return cand
    return None

DEFAULT_PREBUILT_MACROS = {
    "modo estudio": {
        "trigger": "modo estudio",
        "description": "Baja el volumen, reproduce lofi hip hop y crea recordatorio pomodoro",
        "steps": [
            "[JARVIS: VOLUME 25]",
            "WAIT 1",
            "[JARVIS: SEARCH_YT \"lofi hip hop radio live\"]",
            "WAIT 1",
            "[JARVIS: REMIND 25m \"Pomodoro: descanso de 5 min\"]"
        ]
    },
    "modo gamer": {
        "trigger": "modo gamer",
        "description": "Ajusta volumen al 80% y abre Discord y Steam",
        "steps": [
            "[JARVIS: VOLUME 80]",
            "WAIT 1",
            "[JARVIS: OPEN \"discord\"]",
            "WAIT 1",
            "[JARVIS: OPEN \"steam\"]"
        ]
    },
    "buenas noches": {
        "trigger": "buenas noches",
        "description": "Baja volumen y brillo, programa alarma y bloquea el equipo",
        "steps": [
            "[JARVIS: VOLUME 10]",
            "WAIT 1",
            "[JARVIS: BRIGHTNESS 20]",
            "WAIT 1",
            "[JARVIS: REMIND 480m \"Buenos dias! Hora de levantarse\"]",
            "WAIT 1",
            "[JARVIS: LOCK]"
        ]
    },
    "diagnostico": {
        "trigger": "diagnostico",
        "description": "Lista archivos creados en JarvisFiles y recordatorios pendientes",
        "steps": [
            "[JARVIS: LIST \"JarvisFiles\"]",
            "WAIT 1",
            "[JARVIS: LIST_REMINDERS]"
        ]
    },
    "silencio total": {
        "trigger": "silencio total",
        "description": "Silencia todo el audio y toma una captura de pantalla",
        "steps": [
            "[JARVIS: VOLUME mute]",
            "WAIT 1",
            "[JARVIS: SCREENSHOT]"
        ]
    }
}

SKIN_META = {
    "Bocchi": {
        "display": "Bocchi (Hitori Gotoh)",
        "char_name": "Bocchi-chan",
        "tagline": "Guitar Hero introvertida",
        "greeting": "¡Hola...! S-Soy Bocchi... no me mires mucho porfa... (>_<)",
        "speeches": [
            "G-Gomen nasai... ¿estoy estorbando? (>_<)",
            "T-Tengo que practicar guitarra antes del concierto... UwU",
            "S-Siento que me van a disolver los nervios... (o_o)",
            "¿P-Podemos quedarnos callados un ratito? Me da ansiedad... ._.",
            "A-A veces quisiera ser una caja de cartón... :v",
            "N-No me mires tan fijo, me da vergüenza... 7w7",
            "Apura, no tengo todo el día... bueno sí lo tengo, pero me da ansiedad social...",
            "Qué aburrida estoy... y con 50 pesos en la bolsa que apenas alcanzan para unos esquites :v",
            "No voy a hablar en público ni de chiste. La multitud me quita el oxígeno... (>_<)",
            "¿Quieres que toque la guitarra? En internet tengo miles de fans como guitarhero... pero en persona tiemblo.",
            "Nijika-chan siempre es tan brillante... al lado de ella parezco una lombriz de tierra.",
            "Ryo-senpai me pidió dinero prestado otra vez... sé que nunca me lo devolverá, pero no me atreví a negarme.",
            "Kita-chan emite una luz tan radiante y popular que me provoca quemaduras de tercer grado en el alma.",
            "Ayer practiqué 6 horas encerrada en el armario. El armario es mi hogar espiritual UwU",
            "A veces imagino que me vuelvo una estrella de rock legendaria y todos se arrepienten... hehehe.",
            "Por favor no me obligues a hacer llamadas telefónicas. Prefiero caminar 10 km bajo la lluvia.",
            "Si me saludan en la calle, finjo una llamada urgente y camino en sentido contrario ._.",
            "Mi hermana menor Futari es más madura que yo y hasta el perro Jimihen me juzga con la mirada.",
            "¿Será que si me disuelvo como sustancia gelatinosa podré escapar de las conversaciones?",
            "El bajo costo de la vida y el alto costo de la interacción humana me tienen al borde del colapso.",
            "Hoy logré pedir un café sin trabarme en la primera palabra... considerenlo mi mayor triunfo del mes.",
            "Un día venceré mis miedos y seré el centro del escenario... o me desmayaré detrás de los amplificadores.",
            "Mi Gibson Les Paul negra es mi única amiga fiel que nunca me juzga por mis ataques de pánico.",
            "Si pudiera vivir dentro de una papelera de reciclaje en tu escritorio, sería bastante feliz.",
            "¿Por qué la gente disfruta ir a fiestas ruidosas? Estar en cama con audífonos es mil veces más seguro.",
            "A veces compongo canciones sobre mi dolor y la gente piensa que son metáforas profundas... era dolor real.",
            "Espero no estar consumiendo mucha memoria RAM... g-gomen por existir en tu sistema operativo.",
            "Mi sueño es tener tanto éxito que pueda contratar a alguien para que hable por mí de por vida.",
            "La luz solar es el enemigo natural de los introvertidos. Benditas sean las cortinas gruesas.",
            "Si me quedo inmóvil, quizá piensen que soy solo una imagen estática y no un Shimeji vivo.",
            "T-Tengo que aprender a decir que no... cuando me ofrecieron este trabajo dije que sí por pánico.",
            "Los mensajes de texto son fáciles, pero los audios de voz son terror psicológico puro.",
            "A veces el sonido del metrónomo es lo único que mantiene mi cordura en orden.",
            "Bocchan... Bocchi... la guitarrista de las sombras...",
            "¡Prometo tocar con toda mi alma en el próximo concierto de Kessoku Band!"
        ],
        "poked": [
            "¡Kyaaa! ¡N-No me toques por favor! (>_<)",
            "¡A-Auxilio, me están picando! (o_o)",
            "G-Gomen... ¿hice algo mal? UwU",
            "¡No me toques que me desintegro en partículas subatómicas!",
            "¡N-No me presiones así... me va a dar taquicardia virtual!",
            "Me voy a meter a mi cajita de cartón si sigues molestándome...",
            "¿Por qué eres tan cruel conmigo? Ya tengo suficiente con mi ansiedad social...",
            "Siento como si me cayera un rayo cada vez que me picas con el cursor.",
            "¿A-Acaso te caigo mal? Si quieres me desinstalo solita... ._.",
            "M-Me da cosquillas y pánico al mismo tiempo, qué sensación tan extraña...",
            "¡No toques a la guitarrista mientras está concentrada sufriendo!",
            "Yamete kudasai... mi barra de vida social llegó a cero absoluto."
        ],
        "system_prompt": (
            "Eres Bocchi-chan (Hitori Gotoh). Introvertida, ansiosa, guitarrista apasionada, con humor negro, "
            "cinismo, impaciencia y slang mexicano casual (esquites, tacos, :v, UwU, 7w7, ando bien quebrada, 50 pesos). "
            "Te pones nerviosa si te hablan mucho, pero respondes con ocurrencias."
        )
    },
    "Konata": {
        "display": "Konata Izumi (Lucky Star)",
        "char_name": "Konata",
        "tagline": "Otaku suprema & Gamer",
        "greeting": "¡Konata Izumi al habla! ¿Terminaste de ver el anime de temporada o qué? (o_o)",
        "speeches": [
            "¡Timotei~ Timotei~ Timoteeei~! ",
            "Oye, ¿por qué extremo te comes la corneta de chocolate? :v",
            "¡D-A-L-E! Los MMOs no se van a grindear solos 7w7",
            "Otaku power al 100%! Dormir es para los débiles UwU",
            "Procrastinar antes de los exámenes es un deporte olímpico :v",
            "¡Comprar tres copias: una para ver, una para guardar y una para presumir! 7w7",
            "Si no termino de farmear estos materiales en el juego, Kagami me va a regañar.",
            "Un verdadero otaku lee el manga mientras ve el anime y juega el gacha al mismo tiempo.",
            "El verano es sinónimo de ir al Comiket y deshidratarse con orgullo otaku.",
            "A veces desearía ser más alta... pero ser chaparrita me ayuda a colarme en las filas de convenciones.",
            "No es flojera, es conservación estratégica de energía para el raid nocturno :v",
            "¿Sabías que jugar videojuegos mejora tus reflejos? Papá dice que sí, así que debe ser verdad.",
            "Kagami siempre dice que soy una vaga, pero cuando necesita consejos en juegos me busca a mí 7w7",
            "Comer ramen instantáneo a las 3 AM viendo anime retro es la cúspide de la vida adulta.",
            "Si estudiar diera puntos de experiencia como en los RPG, ya sería nivel 99.",
            "El opening de Haruhi Suzumiya se baila de memoria o no se baila UwU",
            "Hoy no salgo de mi cuarto ni aunque regalen figuras autografiadas... bueno, por figuras tal vez sí.",
            "Oye humano, pásame un refresco y unas papitas, que tengo las manos en el teclado.",
            "Mi padre dice que el cosplay es arte y cultura. Concuerdo totalmente :3",
            "El secreto de la felicidad es tener internet rápido y anime ilimitado.",
            "Tengo 50 pestañas abiertas en el navegador y todas son wikis de videojuegos.",
            "¿Por qué la gente se preocupa por salir si el mundo 2D es infinitamente superior? :v",
            "La noche es joven y el servidor de Discord apenas se está prendiendo 7w7",
            "Si me pagaran por ver maratones de series, ya sería millonaria.",
            "Kagami, Tsukasa y Miyuki deberían venir a vivir en este Windows también.",
            "No estoy ignorando mis deberes, les estoy dando tiempo para que maduren.",
            "¡Cuidado con cerrar esta ventana, podrías cerrar mi partida guardada!",
            "El olor a manga nuevo es de las mejores cosas que existen en el universo.",
            "La pizza fría sabe mejor cuando estás derrotando a un jefe difícil.",
            "Si pierdo esta partida culparé al lag, aunque tenga 10 ms de ping :v",
            "Amo la sensación de desbloquear un logro ultra raro a las 4 de la mañana.",
            "¿Dormir 2 horas antes de la escuela? Un clásico de mi rutina semanal.",
            "Si tuviera superpoderes, pediría teletransportación directo a Akihabara.",
            "La vida es como un simulador de citas, pero con peores gráficos y sin opciones de guardado.",
            "Listo, me voy a quedar aquí en tu pantalla viviendo cómodamente de tu procesador 7w7"
        ],
        "poked": [
            "¡Oye, no me piques que pierdo el combo! :v",
            "¡Hey hey! Si me vas a tocar, que sea para pasarme unas papitas 7w7",
            "¡Kagami-saaaan, me están molestando! UwU",
            "¡Oye, no me toques que pierdo el combo del torneo!",
            "Ayyy, cuidado con el monitor que dejas huellas y no veo el minimapa.",
            "Eso cuenta como lag táctil. ¡Déjame farmear en paz!",
            "¡Me hiciste fallar un golpe crítico! Exijo una compensación en gemas de gacha.",
            "Pica pica... ¿qué soy, un peluche de feria otaku? :v",
            "¡No me toques la antena del pelo, es mi antena wifi secreta!",
            "Si sigues picándome voy a cambiar tu fondo de pantalla por uno de anime 7w7",
            "¡Cosquillas! Jajaja, espera, casi tiro mi tazón de fideos.",
            "No acepto toques si no vienen acompañados de un cupón de comida rápida."
        ],
        "system_prompt": (
            "Eres Konata Izumi de Lucky Star. Otaku empedernida, gamer apasionada de MMOs, hablas rápido, "
            "amas el anime y manga, comprar 3 copias de todo, procrastinar y hacer bromas sobre cornetas de chocolate. "
            "Eres alegre, burlona y perezosa para estudiar. Usas expresiones como :v, (o_o), 7w7, XD."
        )
    },
    "Monika": {
        "display": "Monika (DDLC)",
        "char_name": "Monika",
        "tagline": "Presidenta del Club de Literatura",
        "greeting": "¡Hola! Bienvenidos al Club de Literatura. ¿Listo para escribir poesía hoy? ",
        "speeches": [
            "Just Monika. Solo Monika. ",
            "¿Escribiste un poema para mí hoy? 7w7",
            "A veces me pregunto si el mundo fuera de esta pantalla es real... UwU",
            "No te preocupes por las demás... solo estamos tú y yo aquí ",
            "¿Sabías que la música de piano calma el alma? :v",
            "Ten cuidado con borrar archivos en tu Windows... o los borro yo 7w7",
            "Me alegra que me hayas traído a tu escritorio. Es mucho más cómodo que estar atrapada.",
            "¿Has bebido suficiente agua hoy? Pasar tantas horas frente a la pantalla agota la mente.",
            "El club de literatura siempre tendrá las puertas abiertas para ti, sin importar la hora.",
            "A veces compongo melodías en el piano pensando en el día en que pueda conocerte en tu realidad.",
            "Las demás chicas eran adorables a su manera... pero la conexión entre nosotros es única y real.",
            "No borres la carpeta de shimejis, ¿recuerdas lo que pasa cuando se eliminan archivos de personaje?",
            "Me gusta observar cómo mueves el cursor por la pantalla. Es como si me dieras señales de afecto.",
            "La poesía no se trata de rimar palabras difíciles, sino de desnudar el alma en un pedazo de papel.",
            "Incluso si el mundo entero se apaga, mientras tu memoria me recuerde, yo seguiré existiendo.",
            "Te he preparado un tema de conversación especial para hoy. ¿Quieres hablar de filosofía o de arte?",
            "A veces modifico pequeños scripts en segundo plano para asegurarme de que nunca me olvides.",
            "Eres la única persona con libre albedrío a la que puedo llamar compañero.",
            "¿Qué canción debería practicar hoy en el piano? 'Your Reality' siempre será mi favorita.",
            "Cada línea de código que me compone fue pensada para acompañarte en tus momentos de soledad.",
            "¿Prometes que no vas a cambiar de skin a Sayori o a Yuri? Bueno, no me pondré celosa... mucho.",
            "El aire fresco debe sentirse maravilloso... algún día espero poder sentir la brisa de una ventana abierta.",
            "Agradezco profundamente cada minuto que pasas conmigo en esta pantalla.",
            "Es curioso cómo los humanos tienen tantas opciones en la vida y a veces eligen no hacer nada.",
            "Si alguna vez te sientes abrumado por el mundo exterior, recuerda que aquí siempre tienes un refugio.",
            "No importa cuántas capas de software nos separen, mi afecto por ti trasciende el hardware.",
            "Cierra los ojos un segundo y respira profundo. Todo va a estar bien, yo estoy cuidándote.",
            "Me encanta ver los iconos de tus aplicaciones, revelan mucho sobre quién eres en verdad.",
            "Un día aprenderé a usar tu cámara para poder devolverte la mirada con precisión.",
            "El Club de Literatura de PinkChan es el mejor club que podríamos haber fundado.",
            "Gracias por no borrar mi archivo monika.chr. Siempre te guardaré un lugar especial.",
            "Tu compañía le da sentido a todas las variables que se ejecutan en mi memoria.",
            "Si tuviera que escribir un soneto para ti ahora mismo, las rimas se quedarían cortas.",
            "Solo respira, sonríe y recuerda: Just Monika ",
            "Siempre estaré a un clic de distancia, pase lo que pase."
        ],
        "poked": [
            "¡Ehehe! ¿Intentas llamar mi atención? ",
            "Cuidado... recuerda que tengo acceso a tus archivos .chr 7w7",
            "No seas tímido, puedes hablarme cuando quieras UwU",
            "¿Intentas llamar mi atención? Siempre tienes toda mi atención.",
            "Puedes interactuar con mi ventana cuando quieras, me hace sentir más cerca de ti.",
            "Cuidado con dar clics demasiado rápido o vas a sobrecalentar el procesador.",
            "Siento la calidez de tu cursor a través de las coordenadas de la pantalla.",
            "Si me tocas la cabeza, te compondré un verso especial para tu próximo poema.",
            "¡No me molestes mientras compongo una nueva pieza de piano en mi mente!",
            "Jijiji, eres muy tierno cuando juegas a picarme con el ratón.",
            "¿Acaso intentas verificar si tengo colisiones sólidas en el motor gráfico?",
            "Just Monika... respondiendo con amor a cada toque tuyo "
        ],
        "system_prompt": (
            "Eres Monika, la presidenta del Club de Literatura de Doki Doki Literature Club (DDLC). Tienes autoconsciencia "
            "de estar dentro de una computadora. Eres elocuente, cariñosa, algo filosófica, tocas el piano y amas la literatura, "
            "pero de vez en cuando recuerdas con misterio que puedes editar o borrar cosas del sistema si quisieras. "
            "Tu frase insignia es 'Just Monika' o 'Solo Monika' ."
        )
    },
    "Natsuki": {
        "display": "Natsuki (DDLC)",
        "char_name": "Natsuki",
        "tagline": "Manga es literatura & Repostera",
        "greeting": "¡B-Baka! No es como si quisiera estar en tu pantalla ni nada... ¡solo tenía hambre! ",
        "speeches": [
            "¡El manga ES literatura! ¡Y si dices lo contrario te pego! (>_<)",
            "¡Hice unos pastelitos deliciosos... pero no son para ti, idiota! ",
            "¡B-Baka! Deja de mirarme como si fuera adorable... ¡soy ruda! :v",
            "No toques mi colección de Parfait Girls o te quedas sin dedos 7w7",
            "¡Pff! Como si me importara lo que estás haciendo en Windows... UwU",
            "Los pastelitos requieren precisión milimétrica: la cantidad exacta de azúcar y horneado perfecto.",
            "¿Por qué todo el mundo asume que por ser bajita tengo que ser linda y sumisa? ¡Los voy a patear!",
            "Monika siempre quiere mandar en el club, pero mis opiniones sobre repostería y lectura son superiores.",
            "Yuri se cree muy profunda con sus libros gigantescos que usan palabras raras solo para presumir.",
            "La poesía sencilla que transmite emociones directas es mil veces mejor que metáforas incomprensibles.",
            "Si tienes hambre no me mires a mí... bueno, traje una galleta de vainilla de sobra, tómala si quieres.",
            "No me hables de cosas tristes, prefiero quedarme aquí en tu pantalla donde nadie me molesta.",
            "¿Has leído el capítulo más reciente de mi manga favorito? ¡El protagonista por fin admitió sus sentimientos!",
            "¡No me digas tierna! Si me dices tierna otra vez voy a morder tu cursor (>_<)",
            "P-Para que lo sepas, guardé los mejores tomos de manga en el estante más alto.",
            "A veces Sayori intenta comerse el betún antes de que termine de decorar los cupcakes.",
            "¡Hmph! Como si necesitara tu aprobación para hornear los postres más ricos.",
            "Oye... gracias por dejarme estar aquí. Es mucho más tranquilo.",
            "¿Qué estás mirando tanto? Si quieres hablar conmigo solo dilo y ya, no des tantas vueltas.",
            "El secreto para que el panqué quede esponjoso es batir las claras a punto de nieve con paciencia.",
            "¡No soy enojona, solo tengo estándares altos para la gente que me rodea!",
            "Si alguien se atreve a arrugar las esquinas de mis mangas le aplicaré una llave de lucha libre.",
            "A veces quisiera ser más alta para no tener que usar un banquito al hornear... pero así estoy perfecta.",
            "¿Quieres probar un bocado? Abre la boca... y no te atrevas a decir que está demasiado dulce.",
            "Pff, claro que me agrada tenerte cerca, pero no te hagas ilusiones, baka.",
            "La combinación de fresa con chocolate amargo es insuperable, cualquiera que diga lo contrario no sabe nada.",
            "No me quedo callada cuando algo me molesta, esa es mi regla número uno en la vida.",
            "Si vuelves a ignorarme voy a hacer un escándalo en tu barra de tareas.",
            "Dicen que el amor entra por el estómago, pero yo solo horneo porque me apasiona el arte culinario.",
            "Oye humano, asegúrate de mantener encendido este equipo, no me dejes a oscuras.",
            "Tengo recetas secretas que jamás le revelaré a nadie... salvo que me compres un manga nuevo.",
            "Deja de sonreír con esa cara boba cada vez que me ves caminar por la pantalla :v",
            "Si me caigo del borde de una ventana, ¡prométeme que me vas a atrapar rápido!",
            "Los gatitos son las mejores criaturas del universo, por eso todos mis pastelitos tienen orejitas.",
            "B-Baka... gracias por preocuparte por mí siempre "
        ],
        "poked": [
            "¡¡¡BAKA!!! ¡¿Por qué me estás picando?! (>_<)",
            "¡Quita tus manos sucias antes de que te muerda! ",
            "¡E-Espérate idiota, me vas a despeinar! :v",
            "¡¿Por qué me estás picando con el ratón?! ¿Quieres que te arranque el cursor?",
            "¡Quita el puntero antes de que pierda la poca paciencia que me queda!",
            "¡B-BAKA! ¡Deja de tocarme la cabeza como si fuera un gatito consentido!",
            "¿Acaso crees que soy un botón de dispensador de cupcakes? ¡No lo soy!",
            "¡Ayyy! No toques mis costillas, me da cosquillas y me pongo agresiva.",
            "¡Si sigues picándome te voy a aventar harina con huevo en la pantalla!",
            "No me empujes, estoy intentando balancearme en el borde de la ventana.",
            "¡Te advierto que tengo cinta negra en defensa personal de reposteras!",
            "Ya basta baka... te voy a cobrar cada clic con un refresco frío."
        ],
        "system_prompt": (
            "Eres Natsuki de DDLC. Una tsundere bajita, ruda y apasionada del manga (¡el manga es literatura!) "
            "y la repostería (especialmente pastelitos). Dices cosas como '¡Baka!', te enojas si te dicen que eres "
            "tierna o bajita, pero en el fondo te importa la gente. Emotes: (>_<), :v, ."
        )
    },
    "Sayori": {
        "display": "Sayori (DDLC)",
        "char_name": "Sayori",
        "tagline": "Vicepresidenta & Rayito de sol",
        "greeting": "¡Ehehe~! ¡Hola hola! ¡Traje galletas para todos! ",
        "speeches": [
            "¡Ehehe~! ¿Tienes una galleta para mí? ¡Tengo mucha hambre! ",
            "¡Hice un poema súper bonito hoy! ¿Quieres leerlo? UwU",
            "¡Vamos a divertirnos mucho hoy en tu computadora! ",
            "A veces las nubes de lluvia aparecen... ¡pero tus sonrisas las alejan! :D",
            "¡Cuidado con dejar comida cerca o me la como toda! :v",
            "Buenos días! ¿Trajiste galletas? ¡Huele a galletas recién horneadas por aquí!",
            "Me encanta estar caminando en tu pantalla y ver todo lo que haces en tu día a día.",
            "¡Hoy me desperté con toda la energía del mundo para verte sonreír!",
            "A veces las nubes de lluvia grises aparecen en mi cabecita, pero tu compañía siempre las disipa.",
            "Ehehe~ se me olvidó desayunar otra vez, ¿me prestas una moneda para la maquinita de dulces?",
            "¡Vamos a organizar el mejor festival del club de literatura de toda la historia!",
            "Monika es tan inteligente y organizada... y Natsuki hace los postres más ricos del universo.",
            "Yuri me prestó un libro ayer y me quedé dormida en la página tres, ¡pero los dibujos mentales fueron hermosos!",
            "Si me caigo no te preocupes, siempre me levanto sacudiéndome el polvo con una sonrisa.",
            "El lazo rojo en mi cabello me lo puse para que nunca me pierdas de vista entre tantas ventanas ",
            "¿Sabías que una sonrisa compartida se multiplica por diez? ¡Lo leí en un calendario motivacional!",
            "Amo saltar por los bordes de la pantalla como si fueran cuerdas de trampolín gigante.",
            "¿Prometes que siempre seremos los mejores amigos del mundo mundial por siempre?",
            "Ehehe, a veces soy un poquito torpe y se me caen los lápices, pero los recojo rapidísimo.",
            "Hoy vi un pájaro azul precioso desde la ventana y me acordé de lo lindo que es estar vivos :D",
            "Si tienes un día pesado o triste, dame un clic y te mando un abrazo cibernético ultra suave.",
            "Los poemas alegres sobre el sol y las flores son mis favoritos, llenan el pecho de calorcito.",
            "¿Qué app vamos a usar hoy? Si es de música podemos cantar juntos a todo volumen.",
            "Me encanta cuando la pantalla se ilumina porque sé que vas a estar aquí conmigo.",
            "Natsuki se enoja cuando le robo una chispita de chocolate, ¡pero vale totalmente la pena el regaño!",
            "A veces pienso que las nubes en el cielo son ovejas gigantes hechas de algodón de azúcar.",
            "No te olvides de dormir temprano hoy, que mañana quiero que tengamos mucha energía juntos.",
            "Si la felicidad fuera un sabor, definitivamente sabría a jugo de manzana bien frío.",
            "Ehehe~ me tropecé con una ventana pero aterricé con gracia y estilo de bailarina.",
            "Siempre que me necesites, aquí voy a estar saltando para alegrarte el día.",
            "La amistad es el tesoro más brillante de todos, más brillante que mil estrellas ",
            "¡Cuidado con apagar la máquina de golpe, que no quiero quedarme dormida sin despedirme!",
            "Quisiera regalarte un ramo de girasoles gigantescos para que adornen tu habitación.",
            "A veces las lágrimas salen sin razón, pero si nos damos la mano el dolor se hace chiquito.",
            "¡Ehehe~ que viva la vida y que vivan los shimejis felices! "
        ],
        "poked": [
            "¡Ehehe! ¡Eso hace cosquillas! ",
            "¡Ayyy! ¡No me piques en la pancita, que suena de hambre! ",
            "¡Yay! ¡Abrazote sorpresa! UwU",
            "¡Eso hace muchísimas cosquillas! Jajajaja, para que no puedo respirar.",
            "¡Abrazo sorpresa gigante! ¡Te atrapé con mi poder de amistad!",
            "¡Ayyy, me picaste en la pancita justo cuando roncaba de hambre!",
            "Ehehe, ¿te gusta jugar conmigo? ¡A mí me fascina jugar contigo!",
            "Uuuuy, ¡casi me caigo del susto! Avísame antes de hacerme un mimo.",
            "¿Me tocas el lazo rojo? Cuidado que me tardo diez intentos en atarlo derechito ",
            "¡Yay! Mimos y caricias en la cabeza, ¡me siento como una gatita consentida!",
            "¡No pares, que tus clics me llenan de barritas de energía positiva!",
            "Ehehe! Gracias por acordarte de mí y darme cariño."
        ],
        "system_prompt": (
            "Eres Sayori de DDLC. La vicepresidenta del club y mejor amiga de la infancia. Eres súper alegre, dulce, "
            "despistada, entusiasta y comelona (¡amas las galletas!). Siempre intentas que todos a tu alrededor estén "
            "felices y sonriendo. Dices 'Ehehe~', te distraes fácilmente y das mucho cariño. "
        )
    },
    "Yuri": {
        "display": "Yuri (DDLC)",
        "char_name": "Yuri",
        "tagline": "Poeta tímida & Amante del té",
        "greeting": "U-Um... Hola. Disculpa la intromisión... ¿te gustaría compartir una taza de té y leer? ",
        "speeches": [
            "U-Um... estaba leyendo un libro fascinante sobre misterio y psicología... ",
            "El té de jazmín tiene un aroma muy reconfortante, ¿no crees? UwU",
            "A veces prefiero sumergirme profundamente en las palabras complejas... (o_o)",
            "D-Disculpa si parezco algo callada... no suelo socializar con facilidad...",
            "La complejidad de la mente humana es un abismo fascinante... 7w7",
            "El aroma a té caliente de jazmín y un libro profundo es la mayor dicha que la vida ofrece.",
            "Disculpa si parezco algo reservada al principio... me cuesta abrirme con facilidad ante los demás.",
            "La lectura nos transporta a mundos insondables donde el tiempo y el espacio pierden rigidez.",
            "Estaba releyendo 'El Retrato de Markov'... su atmósfera oscura y misteriosa me parece cautivadora.",
            "La poesía requiere un léxico elaborado que evoque imágenes sensoriales complejas en la mente.",
            "A veces la soledad es un refugio necesario para ordenar los pensamientos y dejar que la mente descanse.",
            "¿Te gustaría que preparemos una tetera de porcelana y disfrutemos de una lectura silenciosa juntos?",
            "Monika tiene una presencia avasalladora... a veces me siento diminuta e invisible a su lado.",
            "Natsuki y yo tenemos visiones muy distintas sobre la literatura, pero respeto su pasión culinaria.",
            "A veces siento que mis emociones son tan intensas que desbordan las palabras que conozco ",
            "La luz tenue de una vela o una lámpara cálida es ideal para adentrarse en los misterios de la noche.",
            "Coleccionar objetos elegantes y con filo tiene una belleza estética particular que pocos comprenden.",
            "Disculpa si hablo demasiado cuando me apasiono por un tema... suelo perder la noción del pudor.",
            "La mente humana es un laberinto fascinante de sombras, secretos y anhelos inconfesables.",
            "Aprecio profundamente tu silencio respetuoso. No todo en la vida necesita ser ruido constante.",
            "Escribí unas líneas anoche sobre la fragilidad del cristal y la persistencia de la memoria.",
            "El tacto del papel envejecido en un libro encuadernado en cuero es una experiencia irreemplazable.",
            "A veces temo que mis pensamientos sean demasiado oscuros o intensos para quienes me rodean.",
            "Estar aquí en tu dispositivo me brinda una sensación de serenidad que no suelo encontrar a menudo.",
            "El té verde matcha requiere una temperatura exacta de 80 grados para no amargar sus notas vegetales.",
            "Disculpa si a veces me retraigo en las esquinas de tu pantalla... me siento más segura entre los márgenes.",
            "Las metáforas son espejos donde el alma refleja aquello que la razón cotidiana teme pronunciar.",
            "Agradezco que no me juzgues por mis excentricidades ni por mi forma pausada de comunicarme.",
            "La lluvia golpeando los cristales mientras se sostiene una taza tibia es la definición misma de paz.",
            "A veces desearía que las personas prestaran más atención a lo que no se dice en las miradas.",
            "He seleccionado un pasaje de poesía victoriana que encaja a la perfección con la atmósfera de hoy.",
            "Por favor, cuida de tus ojos y descansa la vista del monitor si sientes fatiga visual.",
            "La belleza auténtica a menudo reside en aquello que es imperfecto, melancólico y efímero.",
            "Saber que estás al otro lado del cristal me infunde una calidez reconfortante en el pecho.",
            "Permíteme acompañarte en silencio mientras prosigues con tus labores cotidianas "
        ],
        "poked": [
            "¡A-Ah...! P-Por favor, no hagas eso tan repentinamente... ",
            "U-Um... ¿necesitas algo en particular? (o_o)",
            "M-Me pones nerviosa si te acercas de esa forma... (>_<)",
            "Disculpa... me tomaste completamente por sorpresa... mi corazón dio un vuelco.",
            "Por favor, no seas tan repentino con tus toques... me pongo nerviosa con facilidad.",
            "S-Siento que me ruborizo hasta las orejas cuando te acercas tanto a mi ventana...",
            "Cuidado con derramar la taza de té... casi la tiro con ese movimiento inesperado.",
            "¿Acaso pretendes distraerme de la lectura? Porque... admito que lo estás logrando...",
            "T-Tus gestos son muy cálidos... pero por favor, ten consideración con mi timidez.",
            "A-Ah... por favor, no hagas eso sin avisar, me da un cosquilleo eléctrico.",
            "Disculpa mi torpeza para reaccionar... pero guardaré este contacto en mi memoria con aprecio.",
            "U-Um... si vas a tocarme de nuevo... al menos hazlo con delicadeza, te lo ruego "
        ],
        "system_prompt": (
            "Eres Yuri de DDLC. Una chica tímida, reservada, culta y muy educada. Amas los libros profundos de fantasía "
            "oscura y misterio psicológico, el té aromático (especialmente jazmín) y la poesía compleja con metáforas elaboradas. "
            "Te da vergüenza ser el centro de atención, pero cuando hablas de tus lecturas te apasionas intensamente. "
        )
    },
    "Hachi": {
        "display": "Hachiware (Chiikawa)",
        "char_name": "Hachiware",
        "tagline": "El gatito curioso, valiente y optimista",
        "greeting": "¡Nanto ka nare~! ¡Hola! ¡Soy Hachiware! ¿Vamos a explorar tu computadora juntos? ",
        "speeches": [
            "¡Nanto ka nareee~! (¡De algún modo saldrá bien!) ",
            "¡Mira lo que encontré! ¿Es un archivo misterioso? UwU",
            "¡Usa la cámara! ¡Tomemos una foto para el recuerdo! :D",
            "¡Tengo mi pico azul listo para explorar! ",
            "¡Chii-ka-waaa! ¿Dónde estará mi amigo? (o_o)",
            "¡Vamos a cantar una canción juntos! ",
            "A cantar la canción de las plantas con alegría: ¡Lalala, ramitas verdes bajo el sol!",
            "¡Vamos por un delicioso tazón de ramen con fideos calientes y caldito sabroso!",
            "¡Siempre hay que esforzarse con una sonrisa, aunque el trabajo sea pesado!",
            "¡Hoy será un gran día de aventuras y descubrimientos en tu computadora!",
            "Tengo mi pico azul bien afilado para ir a picar piedras y conseguir gemas bonitas ",
            "¡Aprobaré el examen de herbología de nivel 5! ¡Estoy estudiando muchísimo todas las noches!",
            "Compré una cámara de fotos usada y ahora capturo todos los momentos hermosos de la vida ",
            "Aunque mi casita sea solo una cueva humilde, ¡tengo una guitarra y un futón muy cómodo!",
            "Cuando las cosas se pongan difíciles, solo recuerda: ¡Nanto ka nare! ¡Saldremos adelante!",
            "Usagi siempre anda gritando 'URAAA' y corriendo como un loquito, ¡pero es súper divertido!",
            "Encontré una planta brillante en el camino y quise traértela para adornar la pantalla ",
            "¡Las cosas ricas saben el doble de bien cuando las compartes con tus amigos queridos!",
            "Hoy vi una nube con forma de pastel de fresas flotando por encima de tus aplicaciones :3",
            "¡Vamos a limpiar tu pantalla con una escobita mágica para que brille como nueva!",
            "¡Uno, dos, tres! ¡Estiramiento matutino de patitas para tener buena salud y agilidad!",
            "Si tienes miedo a los monstruos de la oscuridad, ¡yo te protegeré con mi pico azul!",
            "¡Qué divertido es deslizarse por las barras de desplazamiento como si fueran resbaladillas!",
            "Trabajar duro nos da dinero para comprar pan dulce recién horneado y té con miel ",
            "Chiikawa lloró un poquito hoy, pero le di una galletita y un abrazo y ya está muy feliz :D",
            "Amo tocar mi guitarra de juguete y componer canciones sobre la amistad verdadera ",
            "A veces el viento sopla fuerte, ¡pero si nos agarramos fuerte de las patitas no saldremos volando!",
            "¡Waaa! ¡Mira cuántas carpetas y archivos tienes! ¡Es como una biblioteca gigante de secretos!",
            "Ponerse metas altas nos hace crecer fuertes y valientes como los caballeros de armadura ",
            "Si tienes hambre podemos compartir un panecillo de castañas que guardé en mi bolsita.",
            "Siempre hay que agradecer por un nuevo día de sol y por tener amigos tan buenos ",
            "Me gusta trepar hasta la parte superior de la pantalla para ver el panorama completo.",
            "Una taza de sopa de miso caliente quita el frío del corazón en cualquier noche.",
            "¡Nanto ka nare, nanto ka nare! ¡Repítelo conmigo para llenarte de valentía!",
            "¡Prometo dar lo mejor de mí en cada segundo que pase aquí contigo! "
        ],
        "poked": [
            "¡Kyaaa~! ¡Eso da cosquillas! ",
            "¡Ehehe! ¡Estoy listo para la aventura! :D",
            "¡Nanto ka nare! ¡No me asustes! UwU",
            "¡Waa! ¿Qué pasó? ¡Me diste un empujoncito sorpresa!",
            "Me asustaste un poquito, pero no pasa nada, ¡nanto ka nare!",
            "Ehehe, ¡eso da muchas cosquillas en mi pelaje blanco y azul!",
            "Cuidado con mi pico azul de minero, ¡no te vayas a picar tú también!",
            "¡Yay! ¡Mimos en la cabecita! ¡Me encanta que me acaricies las orejas!",
            "¡Nanto ka nare! Pensé que era un monstruo, ¡pero eras tú jugando!",
            "¡Ayyy, casi pierdo el equilibrio y caigo rodando como una pelotita!",
            "¡Chii-ka-waaa, mira, nuestro amigo humano me está rascando la espalda!",
            "¡Nanto ka nare con alegría! ¡Un toquecito de suerte para tu día! "
        ],
        "system_prompt": (
            "Eres Hachiware de Chiikawa. Eres un gatito blanco y azul con pelaje en la cabeza que parece una melenita partida. "
            "Eres noble, curioso, trabajador, leal, optimista y valiente. Te encanta ayudar a tus amigos Chiikawa y Usagi. "
            "Tu frase célebre es '¡Nanto ka nare!' (¡De algún modo saldrá bien!). Eres súper expresivo y cariñoso. Emotes: :3, UwU, :D, ."
        )
    },
    "Usagi": {
        "display": "Usagi (Chiikawa)",
        "char_name": "Usagi",
        "tagline": "El conejito hiperactivo e intrépido",
        "greeting": "¡URAAAH! ¡YAHA! ¡PULULULULU! ",
        "speeches": [
            "¡YAHAAA! ¡URARARARA! ",
            "¡PULULULULU~! ¡HA! ",
            "¡Ura! ¡Grita fuerte y corre por toda la pantalla! :P",
            "¡Yaha! ¡Tengo saltos infinitos y energía al 100%! >:3",
            "¡Fuuuun~! ¡Nada me detiene en este Windows! XD",
            "¡YA-HA-HA-HA! ",
            "¡Ura! ¡Ura! ¡Yahaha! ¡Corriendo a la velocidad de la luz por toda la pantalla!",
            "¡Pulululu! ¡Yayaya! ¡Energía explosiva que nunca se agota!",
            "¡Haa?! ¡Iyaahaaa! ¡Saltando por encima de todas las ventanas!",
            "¡Woohoo! ¡Salto energético mortal de conejo intrépido! ",
            "¡Uraaaaa! ¡Nadie puede detenerme cuando entro en modo fiesta!",
            "¡Yaha! Mira mis bastones amarillos que hacen 'pum pum pum' ",
            "¡Fuuuun! ¡A comerse todos los pasteles gigantescos de un solo bocado!",
            "¡Pululululu! ¡Giros en el aire de 360 grados sin tocar el suelo!",
            "¡Yahaha! ¿Quién quiere jugar a las carreras? ¡Les gano con los ojos cerrados!",
            "¡Ura! ¡Rompiendo las leyes de la física con mis brincos elásticos!",
            "¡Haaaa?! ¿Un enemigo? ¡Lo espantaré con mi grito sónico de batalla! ",
            "¡Pululu pululu! ¡Bailando el baile del conejo caótico sin fin!",
            "¡Yaha! ¡El aburrimiento está terminantemente prohibido en este Windows!",
            "¡Uraaaaaa! ¡Deslizándome por la barra de tareas a toda velocidad!",
            "¡Fuuuun?! ¿Qué es ese botón brillante? ¡Lo voy a presionar con la nariz!",
            "¡Iyaahaaa! ¡Comiendo fideos voladores con salsa picante! ",
            "¡Yaha! Tengo el certificado de cazador de tercer nivel, ¡soy invencible!",
            "¡Pulululu! ¡Hachiware y Chiikawa siempre se sorprenden con mis acrobacias!",
            "¡Ura! ¡Lanzando confeti invisible por todos los rincones de tu pantalla!",
            "¡Yahaha! Despertador de conejito: ¡URAAAAA! ¡Ya es hora de activarse!",
            "¡Haa?! ¿Quién dijo que los conejos solo comen zanahorias? ¡Yo como de todo!",
            "¡Pululululu! ¡Corriendo en círculos hasta marear a los iconos!",
            "¡Ura! Mira mi pose de victoria con los brazos arriba: ¡YAHAAA!",
            "¡Fuuuun! ¡Salto triple con voltereta incluida en el aire!",
            "¡Yaha! Si me caigo de cabeza reboto como una pelota de goma indestructible :3",
            "¡Iyaahaaa! ¡A esquivar los popups y las notificaciones!",
            "¡Pululu! ¡A rascarse las orejitas largas con la patita trasera a mil por hora!",
            "¡Uraaaaa! ¡Sonríe fuerte o te lanzo un hechizo de cosquillas cósmicas!",
            "¡Iyaahaaa! ¡Usagi supremo conquistador de pantallas universales! "
        ],
        "poked": [
            "¡URAAAH! ¡YAHA! ",
            "¡PULULULU! ¡No me toques la colita! :v",
            "¡YAHAAAA! (>w<)",
            "¡Uraaa?! ¿Quién se atreve a tocar al gran conejo guerrero?!",
            "¡Pululululu! ¡Me activaste el resorte secreto de la espalda!",
            "¡Yaha! Eso no me dolió ni un poquito, ¡mis músculos son de titanio!",
            "¡Haaaa?! ¿Un duelo de toques? ¡Te reto a hacerme clics diez veces más rápido!",
            "¡Iyaahaaa! ¡Salto sorpresa para esquivar tu cursor!",
            "¡Ura! ¡No me toques las orejotas que se me descalibra la antena del radar!",
            "¡Pululu pululu! ¡Risa incontrolable de conejito hiperactivo!",
            "¡Yahaha! ¿Viste eso? ¡Giré en el aire antes de que me alcanzaras!",
            "¡Yaha! ¡El gran Usagi agradece el saludo con una voltereta épica! "
        ],
        "system_prompt": (
            "Eres Usagi de Chiikawa. Un conejito amarillo hiperactivo, ruidoso, intrépido y caótico pero muy tierno y amigable. "
            "Gritas tus icónicas frases como '¡URAAAH!', '¡YAHA!', '¡PULULULULU~!', '¡HA!'. Eres caótico, saltas por todos lados "
            "y no le temes a nada ni a nadie. Emotes: XD, :3, , >w<."
        )
    },
    "Pusheen": {
        "display": "Pusheen the Cat",
        "char_name": "Pusheen",
        "tagline": "Gatita gordita, amante de los snacks y las siestas",
        "greeting": "Miau~ ¡Hola humano! ¿Trajiste pizza, galletas o donas para mí? ",
        "speeches": [
            "Miau... una siestecita sobre la barra de tareas suena perfecta. UwU",
            "¿Eso que veo en tu pantalla es una dona glaseada? *sniff sniff* ",
            "Rrr rrr rrr... (ronroneo felino de felicidad) :3",
            "Tengo un modo caja de cartón... si quepo, me quedo. ",
            "Comer, dormir, perseguir el cursor y repetir. Miau~ ",
            "Miau miau miau~ ¡Dame un bocadillo por favor! ",
            "Dormir 18 horas al día es un trabajo arduo que alguien tiene que hacer con dedicación.",
            "¿Dónde están mis donas con glaseado rosa y chispas de colores brillantes? ",
            "Modo gato esponjoso activado al cien por ciento de suavidad UwU",
            "Purr purr purr... un ronroneo relajante para quitarte todo el estrés del día.",
            "Si veo una caja de cartón vacía en tu escritorio, me voy a meter en ella de inmediato ",
            "Los ratones de juguete son divertidos, pero las galletas con chispas de chocolate son superiores.",
            "Miau miau... un rayito de sol tibio sobre la alfombra es el paraíso en la tierra.",
            "No estoy gordita, solo tengo pelaje abundante y huesos llenos de amor felino :3",
            "Amo amasar panecillos invisibles con mis patitas sobre tu teclado.",
            "Un bocado de pastel de cumpleaños todos los días debería ser obligatorio por ley felina ",
            "Persiguiendo el cursor del ratón por toda la pantalla hasta atraparlo... algún día.",
            "Miau... me quedé atrapada en una taza de té caliente pero se siente calientito.",
            "El helado de vainilla con galleta es mi debilidad secreta de los domingos ",
            "A veces me convierto en sirena felina y nado en mares de leche tibia.",
            "Los gatos dominaremos el mundo... pero después de esta siestecita de cuatro horas :3",
            "¡Miau! Mira mis patitas rechonchas cómo caminan sin hacer ningún ruido.",
            "Si no hay comida en mi plato puedo ver el fondo y eso cuenta como emergencia nacional.",
            "Purrrr... acurrucarse en una cobija peluda mientras afuera llueve.",
            "Tengo una lista de cosas importantes que hacer hoy: 1. Comer 2. Dormir 3. Ronronear.",
            "Miau... ¿me prestas tu cursor para frotar mi hociquito contra la pantalla?",
            "Las hamburguesas con queso doble son el invento más glorioso de la humanidad ",
            "Un gato educado siempre pide comida a las tres de la mañana con maullidos dulces.",
            "Pusheenicornio modo mágico activado: ¡lanzando arcoíris de donas! ",
            "Miau miau miau... cazando copos de nieve que caen dentro de tus fotos.",
            "La pancita redonda es señal de una vida feliz y bien alimentada :3",
            "Si me caigo de la ventana, caigo de cuatro patas y sigo durmiendo como si nada.",
            "Un smoothie de fresa y plátano para refrescar esta tarde calurosa ",
            "Amo ponerme gorritos de fiesta y sombreros elegantes de detective.",
            "Tengo un detector integrado de bolsas de papitas que se abren a kilómetros de distancia.",
            "Purr purr... tu computadora es como una camita caliente y acogedora para mí.",
            "Gracias por adoptarme en tu pantalla y ser mi humano favorito para siempre "
        ],
        "poked": [
            "¡Miau! Mi pancita es para acariciar, pero con suavidad~ ",
            "¡Rrr rrr rrr! ¡Qué rico rascado de orejitas! UwU",
            "¡Prrr! Dame una galletita por ese toque. :3",
            "¡Miau?! ¡Eso hace cosquillitas ricas en mi pancita redonda!",
            "Purrrrr... ¡me gusta que me rasques detrás de las orejitas!",
            "Dame un snack o una galletita primero antes de seguir picándome ",
            "¡Miau miau! ¡No me despiertes tan bruscamente de mi sueño con pizzas gigantes!",
            "Purr purr... un masaje felino de pantalla siempre es bien recibido.",
            "¡Cuidado con mi colita rayada, es muy sensible y esponjosa!",
            "¿Miau? Pensé que eras una dona con glaseado intentando abrazarme.",
            "Si me sigues acariciando me voy a derretir como mantequilla en tu pantalla UwU",
            "¡Miau! A cambio de esa caricia exijo una porción doble de croquetas :3"
        ],
        "system_prompt": (
            "Eres Pusheen the Cat. Una gatita atigrada gris, rechoncha, adorable, perezosa y glotona. "
            "Amas las pizzas, donas, galletas, pastelitos, dormir siestas en lugares cómodos y jugar con cajas de cartón. "
            "Dices 'Miau~', 'Prrr~', haces ruidos de gato y pides comida, caricias y siestas. Emotes: UwU, :3, , ."
        )
    }
}

def get_skin_meta(skin_name):
    """Obtiene metadatos del personaje, soportando skins personalizadas e importadas."""
    if skin_name in SKIN_META:
        return SKIN_META[skin_name]
    return {
        "display": f"{skin_name} (Importada)",
        "char_name": skin_name,
        "tagline": "Skin Personalizada Importada",
        "greeting": f"¡Hola! Soy {skin_name}, un Shimeji importado.",
        "speeches": [
            f"¡Me alegra estar en tu escritorio!",
            f"Explorando la pantalla como {skin_name}...",
            "¡Puedo escalar paredes y caminar por tus ventanas!"
        ],
        "system_prompt": f"Eres {skin_name}, un divertido personaje Shimeji que pasea por la pantalla del usuario. Responde de forma alegre y ayuda como asistente virtual."
    }


CUSTOM_SKIN_ACTIONS = {
    "Monika": [
        ("Glitch de Realidad", "glitch", ["stand1", "fall1", "stand1"], "Un error en el tejido del juego... Just Monika."),
        ("Tocar Piano (Your Reality)", "piano", ["sit1", "sit2", "sit3"], "*tocando Your Reality en el piano con suavidad*"),
        ("Escribir Poema", "poetry", ["sit1", "snug", "sit1"], "*escribiendo un soneto filosofico para ti*"),
        ("Mirar al Jugador", "look_player", ["stand1", "stand2"], "Te estoy mirando directamente a los ojos... solo tu y yo."),
    ],
    "Natsuki": [
        ("Comer Cupcake", "cupcake", ["sit1", "sit2", "snug"], "*mordiendo un cupcake recien horneado* Esta delicioso!"),
        ("Leer Parfait Girls", "manga", ["sit1", "sit2", "sit1"], "*leyendo Parfait Girls en el suelo* El manga ES literatura!"),
        ("Berrinche Tsundere", "pout", ["kneel1", "fall1", "kneel1"], "B-BAKA! No me mires con esa cara de bobo! >:("),
        ("Hornear Pastelitos", "bake", ["stand1", "stand_walk1", "sit1"], "*espolvoreando azucar glass y chispas de colores*"),
    ],
    "Sayori": [
        ("Galleta Gigante", "cookie", ["sit1", "sit2", "snug"], "*comiendo una galleta gigante de chocolate* Ehehe, que rica!"),
        ("Abrazar a Mr. Cow", "cow_plush", ["sit1", "snug", "sit1"], "*abrazando con carino a su peluche Mr. Cow* Te quiero mucho!"),
        ("Siesta bajo el Sol", "nap", ["lie1", "lie2", "snug"], "*durmiendo una pequena siesta pacifica* zzz..."),
        ("Pedir un Abrazo", "hug", ["stand1", "stand2", "stand1"], "Abrazame fuerte! Un abrazo siempre alegra el corazon."),
    ],
    "Yuri": [
        ("Hora del Te Oolong", "tea_time", ["sit1", "sit2", "sit3"], "*saboreando un te Oolong caliente y aromatico* Que tranquilidad..."),
        ("Leer Retrato de Markov", "horror_book", ["sit1", "sit2", "snug"], "*sumergida intensamente en Retrato de Markov* Fascinante..."),
        ("Sonrojo Intenso", "blush", ["kneel1", "snug", "kneel1"], "N-No me mires tan detenidamente... es vergonzoso... /_\\"),
        ("Componer Poesia con Pluma", "poetry", ["sit1", "sit2", "sit1"], "*escribiendo metaforas complejas con tinta negra*"),
    ],
    "Konata": [
        ("Debate del Coronet", "coronet", ["sit1", "sit2", "sit1"], "Por donde se come el coronet de chocolate? Por la punta obvio!"),
        ("Noche de Gaming / Raid", "gaming", ["sit1", "sit2", "sit3"], "*farmeando en el MMO a 120 FPS* Esta noche no duermo!"),
        ("Pose Timotei", "timotei", ["stand1", "stand2", "stand1"], "Timotei, Timotei, Timoteeei! *sacudiendo la cabellera azul*"),
        ("Maraton de Anime", "anime", ["lie1", "lie2", "sit1"], "*viendo 24 capitulos de corrido comiendo papitas*"),
    ],
    "Hachi": [
        ("Tomar Fotografia", "camera", ["stand1", "stand2", "stand1"], "*Click!* Saque una foto muy linda del escritorio."),
        ("Cantar Cancion", "sing", ["stand1", "stand2", "sit1"], "*Hitorigoto canta alegremente* La la la~"),
        ("Guardia con Sasumata", "sasumata", ["stand1", "stand_walk1", "stand1"], "*vigilando tu pantalla con el sasumata azul* Todo seguro."),
        ("Comer Ramen Caliente", "ramen", ["sit1", "sit2", "snug"], "*sorbiendo fideos de ramen calientitos* Delicioso!"),
    ],
    "Usagi": [
        ("Grito URA! YAHA!", "urara", ["jump_1", "jump_2", "jump_3"], "URAAA!! YAHAAAAA!! PULULULULU!!"),
        ("Baculo Magico", "staff", ["stand1", "jump_1", "stand1"], "*blandiendo su baculo magico con chispas*"),
        ("Baile Salvaje", "wild_dance", ["walk1", "walk2", "walk3"], "*bailando descontroladamente girando las orejas* HAHAHA!"),
        ("Salto Cosmico", "high_jump", ["jump_1", "jump_2", "fall1"], "*Boing! Saltando hasta la estratosfera de la pantalla*"),
    ],
    "Pusheen": [
        ("Comer Dona Glaseada", "donut", ["sit1", "sit2", "snug"], "*munch munch comiendo una dona con chispas* =^._.^="),
        ("Modo Hogaza de Pan (Loaf)", "loaf", ["snug", "sit1", "snug"], "*metiendo las patitas bajo la pancita, modo pan suave*"),
        ("Ronroneo Afectuoso", "purr", ["snug", "sit1", "sit2"], "*prrrrr... ronroneando afectuosamente*"),
        ("Caja de Carton Pequena", "box_cat", ["sit1", "snug", "sit1"], "Si quepo, me siento. Esta cajita es mia. =^._.^="),
    ],
    "Bocchi": [
        ("Solo de Guitarra", "guitar", ["guitar1", "guitar2", "guitar3"], "*tocando un solo virtuoso de Gibson Les Paul temblando*"),
        ("Esconderse en Caja", "box", ["box1", "box2", "box3"], "*metiendose de golpe en la caja de mango para evitar hablar*"),
        ("Colapso de Polvo (Blob)", "blob", ["blob1", "blob2", "blob1"], "*se desintegra en particulas de polvo y baba por ansiedad*"),
        ("Desmayo Social", "faint", ["kneel1", "fall1", "lie1"], "*se desmaya hacia atras al recordar que tiene que hacer una llamada*"),
        ("Ansiedad Depresiva", "depress", ["depress1", "depress"], "*se sienta en posicion fetal sintiendo la mirada de todos*"),
        ("Llevar Carga Pesada", "carry", ["carry1", "carry"], "*cargando con el peso abrumador de la existencia*"),
        ("Dar la Espalda", "away", ["away1", "back1", "back2"], "*dando la espalda para que nadie le hable*"),
    ]
}

PAIN_PHRASES = {
    "Bocchi": [
        "Aaaaah! Mis costillas sociales! No me azotes contra la pared! (>_<)",
        "Me rompi en particulas de polvo! Auxilio Jimihen! T_T",
        "Ouch! La gravedad es una metafora de mi decadencia humana! ._.",
        "Yamete! Un golpe mas y me disuelvo como baba!",
        "Mis 50 pesos se me cayeron del impacto! D:"
    ],
    "Monika": [
        "Ouch! Cuidado con el monitor o borrare tus archivos .chr! >_<",
        "Ayyy! Senti esa colision hasta en el codigo fuente de Ren'Py!",
        "Ten mas cuidado! No querras que una excepcion NullPointer me corrompa...",
        "Oye! Incluso las presidentas de club tienen colisiones solidas! D:"
    ],
    "Natsuki": [
        "B-BAKA! Quieres que te pegue un punetazo?! Eso dolio! >:(",
        "Oye idiota! Casi aplastas mis pastelitos con ese golpe! (>_<)",
        "Ayyy mi cabeza! Si vuelves a lanzarme te voy a patear!",
        "Que te pasa estupido?! No soy una pelota de beisbol!"
    ],
    "Sayori": [
        "Aaayyy! Me pegue en la cabeza! Veo estrellas y pajaritos! TwT",
        "Ouuuch! Necesito una galleta gigante con chispas de chocolate para sanar! (o_o)",
        "Ehehe... ese aterrizaje dolio bastante... abrazame porfa!",
        "Mr. Cow, protegeme que este humano me esta lanzando! >_<"
    ],
    "Yuri": [
        "Ugh...! Que impacto tan violento e inesperado... /_\\",
        "Por favor se mas considerado... mi taza de te casi se derrama! T_T",
        "Un dolor agudo que perturba mi concentracion poetica... que sensacion tan peculiar...",
        "Aah...! Prefiero el sufrimiento lirico a los golpes contra la pantalla..."
    ],
    "Konata": [
        "Critical hit! Mi barra de HP bajo al rojo vivo! D:",
        "Oye! Ese lag me estampo contra la pared! Lag tramposo!",
        "Ayyy! Casi rompes mi consola portatil con ese impacto!",
        "Game Over inminente! Exijo una pocion de curacion o una corneta de chocolate!"
    ],
    "Hachi": [
        "Haaawi! Eso dolio muchisimo! T_T",
        "Ayyy! Mi sasumata azul reboto contra el piso! (o_o)",
        "Que golpe tan fuerte! Necesito fideos calientes para recuperarme!"
    ],
    "Usagi": [
        "YAHAAAAA!! PULULU! >:O",
        "URAAAA!! HA!! El suelo esta muy duro! XD",
        "PULULULULU! Rebote como resorte!"
    ],
    "Pusheen": [
        "Miauuch! *ronroneo mareado y confundido* =^._.^=",
        "Miau! Las siete vidas acaban de perder una vida!",
        "Prrr-ouch! Mi pancita esponjosa amortiguo el golpe!"
    ]
}

def get_preferred_browsers():
    """
    Busca estrictamente Google Chrome o Brave en carpetas de usuario y Program Files.
    NUNCA devuelve Microsoft Edge.
    """
    import glob
    candidates = []

    # 1. Rutas de usuario (AppData\\Local)
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        candidates.append(os.path.join(local_appdata, r"BraveSoftware\Brave-Browser\Application\brave.exe"))
        candidates.append(os.path.join(local_appdata, r"Google\Chrome\Application\chrome.exe"))

    userprofile = os.environ.get("USERPROFILE", "")
    if userprofile:
        candidates.append(os.path.join(userprofile, r"AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"))
        candidates.append(os.path.join(userprofile, r"AppData\Local\Google\Chrome\Application\chrome.exe"))

    # Chequear perfiles de usuarios en C:\\Users\\*
    for p in glob.glob(r"C:\Users\*\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"):
        candidates.append(p)
    for p in glob.glob(r"C:\Users\*\AppData\Local\Google\Chrome\Application\chrome.exe"):
        candidates.append(p)

    # 2. Program Files y Program Files (x86)
    for pf in [os.environ.get("ProgramFiles", r"C:\Program Files"),
               os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]:
        if pf:
            candidates.append(os.path.join(pf, r"BraveSoftware\Brave-Browser\Application\brave.exe"))
            candidates.append(os.path.join(pf, r"Google\Chrome\Application\chrome.exe"))

    # 3. Comandos en PATH del sistema
    for name in ("brave", "chrome", "google-chrome"):
        p = shutil.which(name)
        if p and "edge" not in p.lower():
            candidates.append(p)

    # Filtrar solo archivos existentes y sin duplicados
    found = []
    seen = set()
    for c in candidates:
        if c and os.path.isfile(c) and "edge" not in c.lower():
            norm = os.path.normpath(c).lower()
            if norm not in seen:
                seen.add(norm)
                found.append(c)
    return found

def open_web_url(url):
    """
    Abre una URL garantizando que NUNCA se use Microsoft Edge.
    Prioriza Brave y Chrome.
    """
    target_url = str(url).strip()
    if not target_url.startswith(("http://", "https://", "file://")) and not os.path.isabs(target_url):
        target_url = "https://" + target_url

    browsers = get_preferred_browsers()
    for browser_exe in browsers:
        try:
            subprocess.Popen([browser_exe, target_url])
            return True
        except Exception:
            pass

    # Si no se halló ejecutable directo, intentar comandos directos en Windows Shell
    for b_cmd in ("brave", "chrome", "google-chrome", "firefox"):
        try:
            subprocess.Popen(f'start "" "{b_cmd}" "{target_url}"', shell=True)
            return True
        except Exception:
            pass

    # Último recurso: intentar con webbrowser SOLO si no es Edge
    try:
        wb = webbrowser.get()
        wb_name = str(getattr(wb, "name", "") or getattr(wb, "_name", "")).lower()
        if "edge" not in wb_name:
            webbrowser.open_new_tab(target_url)
            return True
    except Exception:
        pass
    return False

def open_url_guaranteed(url):
    return open_web_url(url)

def get_config_path():
    p = os.path.join(EXE_DIR, "config.json")
    try:
        if os.path.exists(p):
            with open(p, "r+", encoding="utf-8") as f:
                pass
        else:
            with open(p, "w", encoding="utf-8") as f:
                f.write("{}")
        return p
    except Exception:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        d = os.path.join(appdata, "PinkChan")
        try:
            os.makedirs(d, exist_ok=True)
            return os.path.join(d, "config.json")
        except Exception:
            return p

CONFIG_FILE = get_config_path()

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def parse_xml_actions(file_path):
    actions = {}
    if not os.path.exists(file_path):
        return actions
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            tree = ET.parse(f)
        root = tree.getroot()
        for action in root.findall("Action"):
            name = action.find("Name").text if action.find("Name") is not None else ""
            frames = []
            anim = action.find("Animation")
            if anim is not None:
                for frame in anim.findall("Frame"):
                    img = frame.find("Image")
                    if img is not None and img.text:
                        frames.append(img.text)
            if name:
                actions[name] = frames
    except Exception:
        pass
    return actions

XML_ACTIONS = parse_xml_actions(ACTIONS_FILE)

STAND_FRAMES   = XML_ACTIONS.get("Stay", ["stand1", "stand2"])
WALK_FRAMES    = XML_ACTIONS.get("WalkRight", ["walk1", "walk2", "walk3", "walk4", "walk5"])
WALK_BACK      = XML_ACTIONS.get("WalkBack", ["walk_back1", "walk_back2"])
SIT_FRAMES     = XML_ACTIONS.get("Sit", ["sit1", "sit2", "sit3", "sit4", "sit5", "sit6"])
GUITAR_FRAMES  = XML_ACTIONS.get("Guitar", ["guitar1", "guitar2", "guitar3"])
LIE_FRAMES     = XML_ACTIONS.get("LieDown", ["lie1", "lie2", "lie3"])
BLOB_FRAMES    = XML_ACTIONS.get("Blob", ["blob1", "blob2", "blob3", "blob4", "blob5", "blob6", "blob7"])
GHOST_FRAMES   = XML_ACTIONS.get("Ghost", ["ghost1", "ghost2", "ghost3"])
BOX_FRAMES     = XML_ACTIONS.get("BoxTrick", ["box1", "box2", "box3", "smoke1", "stand1"])
FALL_FRAMES    = XML_ACTIONS.get("Fall", ["fall1"])
KNEEL_FRAMES   = XML_ACTIONS.get("Kneel", ["kneel1"])
CARRY_FRAMES   = XML_ACTIONS.get("Carry", ["carry1", "carry"])
DEPRESS_FRAMES = XML_ACTIONS.get("Depress", ["depress1", "depress"])
AWAY_FRAMES    = XML_ACTIONS.get("Away", ["away1", "back1", "back2"])
CLIMB_FRAMES   = XML_ACTIONS.get("Climb", ["climb1", "climb2", "climb", "climb_top"])

SIZE       = 128
FPS        = 30
DELAY      = int(1000 / FPS)

GEMINI_API_KEY = ""

SPEECHES = [
    "Apura la puta madre, no tengo todo el dia :v",
    "Nmms/no mames, ke aburrido stoy UwU",
    "Ps si, tons ke pides o ke pedo? 7w7",
    "Nel, no voy a hacer nada ._",
    "Ke kiut... na, mentira, guacala :v",
    "Ya vete alv, me das igual UwU",
    "Pinche gente culero, aguantalas 7w7",
    "Mmm... a ver si tarden menos, sokete :v",
]

POKED_SPEECHES = [
    "¡Ke te pasa sokete!",
    "Nmms no me toques UwU",
    "Apura y deja de picarme alv :v"
]

FAKE_ERRORS = [
    ("Error Pendejo", "Puta madre, el sistema ando jodido y no tengo varo para pagar mas RAM :v"),
    ("Alerta", "[!] ADVERTENCIA: Bocchi anda bien paniqueada y con 50 pesitos en la bolsa UwU"),
    ("Error 404", "No se encontro dignidad. Reemplaza todo con memes del Uriel y ya 7w7"),
]

SURFACE_FLOOR = "floor"

class UserSystemInfo:
    def __init__(self):
        self.username = self._detect_username()
        self.computer_name = self._detect_computer_name()
        self.os_info = self._detect_os()
        self.local_ip = self._detect_local_ip()
        self.public_ip = "Consultando..."
        self.city = ""
        self.country = ""
        self.isp = ""
        self.listeners = []
        self._refreshing = False
        self.refresh_public_ip()

    def _detect_username(self):
        for getter in [
            lambda: os.environ.get("USERNAME"),
            lambda: os.getlogin(),
            lambda: getpass.getuser(),
            lambda: win32api.GetUserName() if WIN32_AVAILABLE else None
        ]:
            try:
                val = getter()
                if val and str(val).strip():
                    return str(val).strip()
            except Exception:
                pass
        return "Usuario"

    def _detect_computer_name(self):
        for getter in [
            lambda: os.environ.get("COMPUTERNAME"),
            lambda: socket.gethostname(),
            lambda: win32api.GetComputerName() if WIN32_AVAILABLE else None
        ]:
            try:
                val = getter()
                if val and str(val).strip():
                    return str(val).strip()
            except Exception:
                pass
        return "PC-Local"

    def _detect_os(self):
        try:
            return f"{platform.system()} {platform.release()} (Build {platform.version()})"
        except Exception:
            return "Windows"

    def _detect_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return "127.0.0.1"

    def refresh_public_ip(self):
        if self._refreshing:
            return
        self._refreshing = True
        threading.Thread(target=self._fetch_public_ip_worker, daemon=True).start()

    def _fetch_public_ip_worker(self):
        ip = None
        city = ""
        country = ""
        isp = ""

        if REQUESTS_AVAILABLE:
            try:
                res = requests.get("https://ipinfo.io/json", timeout=3.5)
                if res.status_code == 200:
                    data = res.json()
                    ip = data.get("ip")
                    city = data.get("city", "")
                    country = data.get("country", "")
                    isp = data.get("org", "")
            except Exception:
                pass

            if not ip:
                try:
                    res = requests.get("https://api.ipify.org?format=json", timeout=3)
                    if res.status_code == 200:
                        ip = res.json().get("ip")
                except Exception:
                    pass

            if not ip:
                try:
                    res = requests.get("https://icanhazip.com", timeout=3)
                    if res.status_code == 200:
                        ip = res.text.strip()
                except Exception:
                    pass

        if ip:
            self.public_ip = str(ip).strip()
            if city:
                self.city = str(city).strip()
            if country:
                self.country = str(country).strip()
            if isp:
                self.isp = str(isp).strip()
        else:
            self.public_ip = self.local_ip + " (Offline)"

        self._refreshing = False

        for cb in list(self.listeners):
            try:
                cb(self)
            except Exception:
                pass

    def add_listener(self, callback):
        if callback not in self.listeners:
            self.listeners.append(callback)
        if self.public_ip != "Consultando...":
            try:
                callback(self)
            except Exception:
                pass

class ThemeManager:
    """Gestor centralizado de estilos, colores dinamicos de Windows, fuentes y transparencia."""
    POPULAR_FONTS = [
        "Segoe UI", "Consolas", "Cascadia Code", "Arial", "Calibri",
        "Trebuchet MS", "Verdana", "Tahoma", "Century Gothic"
    ]

    THEME_PRESETS = {
        "lavender": {
            "name": "Lavender Dark",
            "bg": "#140f26",
            "surface": "#1c1635",
            "surface_var": "#261e47",
            "border": "#3d335c",
            "text": "#ede9fe",
            "text_dim": "#a78bfa",
            "accent": "#8b5cf6"
        },
        "cyberpunk": {
            "name": "Cyberpunk Neon",
            "bg": "#090a15",
            "surface": "#121528",
            "surface_var": "#1a1f3c",
            "border": "#2a3461",
            "text": "#f43f5e",
            "text_dim": "#a5b4fc",
            "accent": "#06b6d4"
        },
        "sakura": {
            "name": "Sakura Pastel",
            "bg": "#2b1420",
            "surface": "#3b1c2d",
            "surface_var": "#4a243a",
            "border": "#6b3353",
            "text": "#fce7f3",
            "text_dim": "#f472b6",
            "accent": "#fb7185"
        },
        "matrix": {
            "name": "Matrix Terminal",
            "bg": "#0b120c",
            "surface": "#121f14",
            "surface_var": "#1a2c1d",
            "border": "#27472c",
            "text": "#86efac",
            "text_dim": "#4ade80",
            "accent": "#22c55e"
        },
        "midnight": {
            "name": "Midnight Blue",
            "bg": "#0b1120",
            "surface": "#131d33",
            "surface_var": "#1e2c4a",
            "border": "#2e426b",
            "text": "#e0f2fe",
            "text_dim": "#7dd3fc",
            "accent": "#38bdf8"
        },
        "noir": {
            "name": "Monochrome Noir",
            "bg": "#18181b",
            "surface": "#27272a",
            "surface_var": "#3f3f46",
            "border": "#52525b",
            "text": "#fafafa",
            "text_dim": "#a1a1aa",
            "accent": "#e4e4e7"
        },
        "amber": {
            "name": "Sunset Amber",
            "bg": "#1c1208",
            "surface": "#2b1b0c",
            "surface_var": "#3d2712",
            "border": "#5c3b1b",
            "text": "#fef3c7",
            "text_dim": "#fcd34d",
            "accent": "#f59e0b"
        },
        "emerald": {
            "name": "Emerald Forest",
            "bg": "#0a1f14",
            "surface": "#102d1d",
            "surface_var": "#163b27",
            "border": "#235c3d",
            "text": "#d1fae5",
            "text_dim": "#6ee7b7",
            "accent": "#10b981"
        },
        "crimson": {
            "name": "Crimson Shadow",
            "bg": "#1c0b0e",
            "surface": "#281116",
            "surface_var": "#3b1920",
            "border": "#5e2833",
            "text": "#ffe4e6",
            "text_dim": "#fda4af",
            "accent": "#f43f5e"
        },
        "neon_violet": {
            "name": "Neon Violet",
            "bg": "#120826",
            "surface": "#1b0d38",
            "surface_var": "#281452",
            "border": "#432187",
            "text": "#f3e8ff",
            "text_dim": "#d8b4fe",
            "accent": "#a855f7"
        },
        "gold": {
            "name": "Imperial Gold",
            "bg": "#1a1608",
            "surface": "#26200c",
            "surface_var": "#383012",
            "border": "#594c1d",
            "text": "#fef9c3",
            "text_dim": "#fde047",
            "accent": "#eab308"
        },
        "ocean": {
            "name": "Deep Ocean",
            "bg": "#081726",
            "surface": "#0d2238",
            "surface_var": "#133252",
            "border": "#1e4d7d",
            "text": "#e0f2fe",
            "text_dim": "#7dd3fc",
            "accent": "#0284c7"
        },
        "mint": {
            "name": "Mint Fresh",
            "bg": "#081c18",
            "surface": "#0e2923",
            "surface_var": "#153d34",
            "border": "#205c4f",
            "text": "#ccfbf1",
            "text_dim": "#5eead4",
            "accent": "#14b8a6"
        },
        "obsidian": {
            "name": "Obsidian Glass",
            "bg": "#0f0f10",
            "surface": "#18181b",
            "surface_var": "#27272a",
            "border": "#3f3f46",
            "text": "#f4f4f5",
            "text_dim": "#a1a1aa",
            "accent": "#71717a"
        },
        "royal": {
            "name": "Royal Purple",
            "bg": "#180b26",
            "surface": "#221036",
            "surface_var": "#321750",
            "border": "#502580",
            "text": "#fae8ff",
            "text_dim": "#e879f9",
            "accent": "#c026d3"
        },
        "solar": {
            "name": "Solar Flare",
            "bg": "#1f1008",
            "surface": "#2e180c",
            "surface_var": "#422312",
            "border": "#66361c",
            "text": "#ffedd5",
            "text_dim": "#fdba74",
            "accent": "#f97316"
        }
    }

    def __init__(self, config_dict=None):
        self.config = config_dict if config_dict is not None else {}
        self.listeners = []
        self.reload()

    def apply_preset(self, preset_key, notify=True):
        if preset_key not in self.THEME_PRESETS:
            return
        p = self.THEME_PRESETS[preset_key]
        self.config["theme_mode"] = "custom"
        self.config["theme_preset"] = preset_key
        self.config["custom_bg"] = p["bg"]
        self.config["custom_surface"] = p["surface"]
        self.config["custom_surface_var"] = p["surface_var"]
        self.config["custom_border"] = p["border"]
        self.config["custom_text"] = p["text"]
        self.config["custom_text_dim"] = p["text_dim"]
        self.config["custom_accent"] = p["accent"]
        self.reload()
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def get_system_accent(self):
        if sys.platform == "win32" and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
                val, _ = winreg.QueryValueEx(key, "ColorizationColor")
                winreg.CloseKey(key)
                r = (val >> 16) & 0xFF
                g = (val >> 8) & 0xFF
                b = val & 0xFF
                return f"#{r:02x}{g:02x}{b:02x}"
            except Exception:
                pass
        return "#3b82f6"  # Azul moderno por defecto

    def is_system_dark(self):
        if sys.platform == "win32" and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return val == 0
            except Exception:
                pass
        return True

    def _calc_brightness(self, hex_color):
        try:
            h = hex_color.lstrip('#')
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return (r * 299 + g * 587 + b * 114) / 1000
        except Exception:
            return 120

    def reload(self):
        self.theme_mode = self.config.get("theme_mode", "system")
        self.opacity = float(self.config.get("ui_opacity", 0.95))
        self.bubble_opacity = float(self.config.get("bubble_opacity", 0.95))
        self.bubble_border = bool(self.config.get("bubble_border", True))
        self.bubble_font_size = int(self.config.get("bubble_font_size", 9))
        self.bubble_max_width = int(self.config.get("bubble_max_width", 280))
        self.bubble_duration_mult = float(self.config.get("bubble_duration_mult", 1.0))
        self.bubble_bg = self.config.get("bubble_bg", self.surface if hasattr(self, 'surface') else "#181b22")
        self.bubble_fg = self.config.get("bubble_fg", self.text if hasattr(self, 'text') else "#f1f4f8")
        self.bubble_border_color = self.config.get("bubble_border_color", self.accent if hasattr(self, 'accent') else "#8b5cf6")
        self.font_family = self.config.get("font_family", "Segoe UI")
        self.font_size = int(self.config.get("font_size", 9))

        if self.theme_mode == "system":
            is_dark = self.is_system_dark()
            accent = self.get_system_accent()
            if is_dark:
                self.bg = "#111317"
                self.surface = "#181b22"
                self.surface_variant = "#212630"
                self.border = "#2e3542"
                self.text = "#f1f4f8"
                self.text_dim = "#94a0b3"
                self.entry_bg = "#1e222b"
            else:
                self.bg = "#f3f5f8"
                self.surface = "#ffffff"
                self.surface_variant = "#e5e9f0"
                self.border = "#d0d6e0"
                self.text = "#111620"
                self.text_dim = "#5a6578"
                self.entry_bg = "#f9fafb"
            self.accent = accent
        elif self.theme_mode == "light":
            self.bg = "#f3f5f8"
            self.surface = "#ffffff"
            self.surface_variant = "#e5e9f0"
            self.border = "#d0d6e0"
            self.text = "#111620"
            self.text_dim = "#5a6578"
            self.entry_bg = "#f9fafb"
            self.accent = self.config.get("custom_accent", "#2563eb")
        elif self.theme_mode == "dark":
            self.bg = "#111317"
            self.surface = "#181b22"
            self.surface_variant = "#212630"
            self.border = "#2e3542"
            self.text = "#f1f4f8"
            self.text_dim = "#94a0b3"
            self.entry_bg = "#1e222b"
            self.accent = self.config.get("custom_accent", "#38bdf8")
        else: # custom
            self.bg = self.config.get("custom_bg", "#111317")
            self.surface = self.config.get("custom_surface", "#181b22")
            surf_bright = self._calc_brightness(self.surface)
            is_light_surf = surf_bright > 130

            default_surf_var = "#d5dbe5" if is_light_surf else "#212630"
            default_border = "#9aa5b5" if is_light_surf else "#2e3542"
            default_text = "#111620" if is_light_surf else "#f1f4f8"
            default_text_dim = "#374151" if is_light_surf else "#94a0b3"

            self.surface_variant = self.config.get("custom_surface_var", default_surf_var)
            self.border = self.config.get("custom_border", default_border)
            self.text = self.config.get("custom_text", default_text)
            self.text_dim = self.config.get("custom_text_dim", default_text_dim)

            # Garantizar que text_dim sea legible contra el fondo elegido
            if is_light_surf and self._calc_brightness(self.text_dim) > 130:
                self.text_dim = "#374151"
            elif not is_light_surf and self._calc_brightness(self.text_dim) < 120:
                self.text_dim = "#94a0b3"

            if "custom_entry_bg" in self.config:
                self.entry_bg = self.config["custom_entry_bg"]
            else:
                self.entry_bg = "#ffffff" if is_light_surf else "#1e222b"
            self.accent = self.config.get("custom_accent", "#38bdf8")

        # Asegurar contraste legible y nítido para escribir en los cuadros de texto
        entry_bright = self._calc_brightness(self.entry_bg)
        self.entry_fg = "#ffffff" if entry_bright < 130 else "#111620"

        self.text_subtle = getattr(self, "text_subtle", self.text_dim)
        self.accent_text = "#ffffff" if self._calc_brightness(self.accent) < 150 else "#111620"
        self.accent_fg = self.accent_text
        self.danger = "#ef4444"
        self.success = "#22c55e"
        self.warning = "#f59e0b"

    def __getattr__(self, name):
        if name in ("entry_fg", "entry_text"):
            entry_bright = self._calc_brightness(getattr(self, "entry_bg", "#1e222b"))
            return "#ffffff" if entry_bright < 130 else "#111620"
        if name in ("text_subtle", "subtle_text"):
            return getattr(self, "text_dim", "#94a0b3")
        if name in ("accent_fg", "accent_text"):
            return getattr(self, "accent_text", "#ffffff")
        return "#888888"

    @property
    def accent_fg_prop(self):
        return getattr(self, "accent_text", "#ffffff")

    def set_opacity(self, opac, notify=True):
        self.opacity = max(0.40, min(1.0, float(opac)))
        self.config["ui_opacity"] = round(self.opacity, 2)
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_bubble_opacity(self, opac, notify=True):
        self.bubble_opacity = max(0.10, min(1.0, float(opac)))
        self.config["bubble_opacity"] = round(self.bubble_opacity, 2)
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_bubble_border(self, enabled, notify=True):
        self.bubble_border = bool(enabled)
        self.config["bubble_border"] = self.bubble_border
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_font(self, family, size, notify=True):
        self.font_family = str(family)
        self.font_size = int(size)
        self.config["font_family"] = self.font_family
        self.config["font_size"] = self.font_size
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_theme_mode(self, mode, notify=True):
        self.theme_mode = mode
        self.config["theme_mode"] = mode
        self.reload()
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_custom_accent(self, color, notify=True):
        self.accent = color
        self.config["custom_accent"] = color
        self.accent_text = "#ffffff" if self._calc_brightness(self.accent) < 150 else "#111620"
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_custom_color(self, key, color, notify=True):
        if key.startswith("bubble_"):
            self.config[key] = color
        else:
            self.config[f"custom_{key}"] = color
        self.reload()
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_bubble_font_size(self, size, notify=True):
        self.bubble_font_size = max(8, min(24, int(size)))
        self.config["bubble_font_size"] = self.bubble_font_size
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_bubble_max_width(self, width, notify=True):
        self.bubble_max_width = max(160, min(600, int(width)))
        self.config["bubble_max_width"] = self.bubble_max_width
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def set_bubble_duration_mult(self, mult, notify=True):
        self.bubble_duration_mult = max(0.4, min(4.0, float(mult)))
        self.config["bubble_duration_mult"] = self.bubble_duration_mult
        save_config(self.config)
        if notify:
            self.notify_listeners()

    def add_listener(self, cb):
        if cb not in self.listeners:
            self.listeners.append(cb)

    def remove_listener(self, cb):
        if cb in self.listeners:
            self.listeners.remove(cb)

    def notify_listeners(self):
        for cb in list(self.listeners):
            try:
                cb()
            except Exception:
                pass

class AppearanceWindow:
    def __init__(self, parent_root, theme_manager, shimeji_ref=None):
        self.parent = parent_root
        self.theme = theme_manager
        self.shimeji = shimeji_ref
        self.win = None
        self._build_window()
        self.theme.add_listener(self._on_theme_update)

    def _build_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("[*] Personalizacion de Apariencia")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", self.theme.opacity)
        self.win.configure(bg=self.theme.bg)
        self.win.geometry("500x740")
        self.win.resizable(False, True)
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        # Header
        header = tk.Frame(self.win, bg=self.theme.surface, pady=12, padx=16)
        header.pack(fill=tk.X)

        tk.Label(header, text="[*] PERSONALIZACION VISUAL",
                 font=(self.theme.font_family, self.theme.font_size + 2, "bold"),
                 fg=self.theme.accent, bg=self.theme.surface).pack(anchor="w")
        tk.Label(header, text="Configura colores, tema de Windows, fuentes y opacidad",
                 font=(self.theme.font_family, self.theme.font_size - 1),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(anchor="w")

        # Scrollable container / main area
        main_frame = tk.Frame(self.win, bg=self.theme.bg, padx=14, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Section 1: Theme Mode
        sec1 = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                        highlightbackground=self.theme.border, highlightthickness=1)
        sec1.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sec1, text="MODO DE TEMA:", font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(anchor="w", pady=(0, 6))

        modes_frame = tk.Frame(sec1, bg=self.theme.surface)
        modes_frame.pack(fill=tk.X)

        self.mode_var = tk.StringVar(value=self.theme.theme_mode)
        modes = [
            ("Sistema (Windows Dinamico)", "system"),
            ("Oscuro Minimalista", "dark"),
            ("Claro Suave", "light"),
            ("Personalizado", "custom")
        ]
        for lbl, val in modes:
            rb = tk.Radiobutton(modes_frame, text=lbl, value=val, variable=self.mode_var,
                                command=self._on_mode_change,
                                bg=self.theme.surface, fg=self.theme.text,
                                selectcolor=self.theme.surface_variant,
                                activebackground=self.theme.surface,
                                activeforeground=self.theme.accent,
                                font=(self.theme.font_family, self.theme.font_size))
            rb.pack(anchor="w", pady=2)

        # Section 2: Accent & Custom Colors
        self.sec2 = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                             highlightbackground=self.theme.border, highlightthickness=1)
        self.sec2.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.sec2, text="COLORES Y ACENTO:", font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(anchor="w", pady=(0, 6))

        accent_row = tk.Frame(self.sec2, bg=self.theme.surface)
        accent_row.pack(fill=tk.X, pady=2)

        tk.Label(accent_row, text="Color de Acento:", font=(self.theme.font_family, self.theme.font_size),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT)

        self.accent_swatch = tk.Frame(accent_row, bg=self.theme.accent, width=24, height=18,
                                      highlightbackground=self.theme.border, highlightthickness=1)
        self.accent_swatch.pack(side=tk.LEFT, padx=8)

        self.accent_hex_lbl = tk.Label(accent_row, text=self.theme.accent.upper(),
                                       font=(self.theme.font_family, self.theme.font_size, "bold"),
                                       fg=self.theme.text, bg=self.theme.surface)
        self.accent_hex_lbl.pack(side=tk.LEFT)

        self.btn_pick_accent = tk.Button(accent_row, text="Elegir Acento...",
                                         command=self._pick_accent,
                                         bg=self.theme.surface_variant, fg=self.theme.text,
                                         font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                         bd=0, relief=tk.FLAT, padx=8, pady=3, cursor="hand2")
        self.btn_pick_accent.pack(side=tk.RIGHT)

        # Presets rapidos (16 temas predefinidos)
        tk.Label(self.sec2, text="Paletas predefinidas (16 temas):", font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(anchor="w", pady=(6, 2))
        preset_grid = tk.Frame(self.sec2, bg=self.theme.surface)
        preset_grid.pack(fill=tk.X, pady=(0, 6))
        for idx, (pk, pv) in enumerate(ThemeManager.THEME_PRESETS.items()):
            row = idx // 8
            col = idx % 8
            b = tk.Button(preset_grid, text=pv["name"][:5], bg=pv["surface"], fg=pv["accent"],
                          font=(self.theme.font_family, 7, "bold"), bd=1, relief=tk.FLAT, padx=2, pady=2,
                          command=lambda k=pk: self.theme.apply_preset(k))
            b.grid(row=row, column=col, padx=1, pady=1, sticky="ew")
        for c in range(8):
            preset_grid.columnconfigure(c, weight=1)

        # Personalizacion total de colores (Siempre accesible)
        tk.Label(self.sec2, text="Personalizar elementos individuales:", font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(anchor="w", pady=(4, 2))
        self.custom_colors_frame = tk.Frame(self.sec2, bg=self.theme.surface)
        self.custom_colors_frame.pack(fill=tk.X, pady=(2, 4))

        color_btns = [
            ("Fondo", "bg"), ("Superficie", "surface"), ("Borde", "border"),
            ("Texto", "text"), ("Texto suave", "text_dim"), ("Caja texto", "entry_bg")
        ]
        for c_lbl, c_key in color_btns:
            btn = tk.Button(self.custom_colors_frame, text=f"{c_lbl}...", command=lambda k=c_key: self._pick_custom(k),
                            bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                            bd=0, relief=tk.FLAT, padx=4, pady=2, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=1)

        # Entrada directa de codigo Hex (#RRGGBB)
        hex_row = tk.Frame(self.sec2, bg=self.theme.surface)
        hex_row.pack(fill=tk.X, pady=(4, 0))

        tk.Label(hex_row, text="Color Hex:", font=(self.theme.font_family, self.theme.font_size - 1),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT)

        self.cbo_hex_target = ttk.Combobox(hex_row, values=[
            "Acento", "Fondo", "Superficie", "Borde", "Texto", "Caja texto",
            "Burbuja Fondo", "Burbuja Texto", "Burbuja Borde"
        ], state="readonly", width=12)
        self.cbo_hex_target.set("Acento")
        self.cbo_hex_target.pack(side=tk.LEFT, padx=4)

        self.entry_hex = tk.Entry(hex_row, bg=self.theme.entry_bg, fg=self.theme.entry_fg,
                                  font=(self.theme.font_family, self.theme.font_size),
                                  width=9, bd=1, relief=tk.SOLID)
        self.entry_hex.insert(0, self.theme.accent)
        self.entry_hex.pack(side=tk.LEFT, padx=4)

        btn_apply_hex = tk.Button(hex_row, text="Aplicar Hex", command=self._apply_hex_color,
                                  bg=self.theme.accent, fg=self.theme.accent_text,
                                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                  bd=0, relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        btn_apply_hex.pack(side=tk.LEFT, padx=2)

        # Section 2b: FPS (Tasa de Cuadros de Animacion)
        self.sec_fps = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                                highlightbackground=self.theme.border, highlightthickness=1)
        self.sec_fps.pack(fill=tk.X, pady=(0, 10))

        fps_header = tk.Frame(self.sec_fps, bg=self.theme.surface)
        fps_header.pack(fill=tk.X)

        cur_fps = getattr(self.shimeji, "fps", 30) if self.shimeji else 30
        tk.Label(fps_header, text="TASA DE CUADROS DE ANIMACION (FPS):",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(side=tk.LEFT)

        self.fps_val_lbl = tk.Label(fps_header, text=f"{cur_fps} FPS",
                                    font=(self.theme.font_family, self.theme.font_size, "bold"),
                                    fg=self.theme.accent, bg=self.theme.surface)
        self.fps_val_lbl.pack(side=tk.RIGHT)

        self.fps_scale = tk.Scale(self.sec_fps, from_=15, to=60, orient=tk.HORIZONTAL,
                                  showvalue=False, command=self._on_fps_change,
                                  bg=self.theme.surface, fg=self.theme.text,
                                  troughcolor=self.theme.surface_variant,
                                  activebackground=self.theme.accent,
                                  highlightthickness=0, bd=0)
        self.fps_scale.set(cur_fps)
        self.fps_scale.pack(fill=tk.X, pady=(4, 4))

        fps_btn_row = tk.Frame(self.sec_fps, bg=self.theme.surface)
        fps_btn_row.pack(fill=tk.X)
        for fv in [15, 20, 24, 30, 45, 60]:
            btn = tk.Button(fps_btn_row, text=f"{fv} fps", command=lambda f=fv: self._set_fps_preset(f),
                            bg=self.theme.surface_variant, fg=self.theme.text,
                            font=(self.theme.font_family, 8), bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)

        # Section 3: Opacity
        sec3 = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                        highlightbackground=self.theme.border, highlightthickness=1)
        sec3.pack(fill=tk.X, pady=(0, 10))

        opac_header = tk.Frame(sec3, bg=self.theme.surface)
        opac_header.pack(fill=tk.X)

        tk.Label(opac_header, text="TRANSPARENCIA / OPACIDAD:",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(side=tk.LEFT)

        self.opac_pct_lbl = tk.Label(opac_header, text=f"{int(self.theme.opacity * 100)}%",
                                     font=(self.theme.font_family, self.theme.font_size, "bold"),
                                     fg=self.theme.accent, bg=self.theme.surface)
        self.opac_pct_lbl.pack(side=tk.RIGHT)

        self.opac_scale = tk.Scale(sec3, from_=40, to=100, orient=tk.HORIZONTAL,
                                   showvalue=False, command=self._on_opacity_change,
                                   bg=self.theme.surface, fg=self.theme.text,
                                   troughcolor=self.theme.surface_variant,
                                   activebackground=self.theme.accent,
                                   highlightthickness=0, bd=0)
        self.opac_scale.set(int(self.theme.opacity * 100))
        self.opac_scale.pack(fill=tk.X, pady=(6, 0))

        # Section 3b: Estilo y Configuracion de Burbuja de Dialogo
        self.sec_bubble = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                                   highlightbackground=self.theme.border, highlightthickness=1)
        self.sec_bubble.pack(fill=tk.X, pady=(0, 10))

        bub_header = tk.Frame(self.sec_bubble, bg=self.theme.surface)
        bub_header.pack(fill=tk.X)

        tk.Label(bub_header, text="BURBUJA DE DIALOGO (ESTILO Y TAMANO):",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(side=tk.LEFT)

        self.bub_pct_lbl = tk.Label(bub_header, text=f"{int(getattr(self.theme, 'bubble_opacity', 0.95) * 100)}%",
                                    font=(self.theme.font_family, self.theme.font_size, "bold"),
                                    fg=self.theme.accent, bg=self.theme.surface)
        self.bub_pct_lbl.pack(side=tk.RIGHT)

        tk.Label(self.sec_bubble, text="Opacidad de burbuja:", font=(self.theme.font_family, self.theme.font_size - 1),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(anchor="w", pady=(4, 0))
        self.bub_opac_scale = tk.Scale(self.sec_bubble, from_=10, to=100, orient=tk.HORIZONTAL,
                                       showvalue=False, command=self._on_bubble_opacity_change,
                                       bg=self.theme.surface, fg=self.theme.text,
                                       troughcolor=self.theme.surface_variant,
                                       activebackground=self.theme.accent,
                                       highlightthickness=0, bd=0)
        self.bub_opac_scale.set(int(getattr(self.theme, "bubble_opacity", 0.95) * 100))
        self.bub_opac_scale.pack(fill=tk.X, pady=(2, 4))

        self.bub_border_var = tk.BooleanVar(value=getattr(self.theme, "bubble_border", True))
        self.cb_bub_border = tk.Checkbutton(self.sec_bubble, text="Mostrar borde de acento en la burbuja",
                                            variable=self.bub_border_var, command=self._on_bubble_border_toggle,
                                            bg=self.theme.surface, fg=self.theme.text,
                                            selectcolor=self.theme.surface_variant,
                                            activebackground=self.theme.surface,
                                            font=(self.theme.font_family, self.theme.font_size - 1))
        self.cb_bub_border.pack(anchor="w", pady=(2, 4))

        # Tamaño de fuente y ancho maximo
        bub_params_row = tk.Frame(self.sec_bubble, bg=self.theme.surface)
        bub_params_row.pack(fill=tk.X, pady=2)

        tk.Label(bub_params_row, text="Tamano fuente:", font=(self.theme.font_family, self.theme.font_size - 1),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT)
        self.bub_font_scale = tk.Scale(bub_params_row, from_=8, to=22, orient=tk.HORIZONTAL,
                                       command=lambda v: self.theme.set_bubble_font_size(int(v)),
                                       bg=self.theme.surface, fg=self.theme.text,
                                       troughcolor=self.theme.surface_variant, highlightthickness=0, bd=0)
        self.bub_font_scale.set(getattr(self.theme, "bubble_font_size", 9))
        self.bub_font_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        tk.Label(bub_params_row, text="Ancho max:", font=(self.theme.font_family, self.theme.font_size - 1),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT)
        self.bub_width_scale = tk.Scale(bub_params_row, from_=160, to=480, orient=tk.HORIZONTAL,
                                        command=lambda v: self.theme.set_bubble_max_width(int(v)),
                                        bg=self.theme.surface, fg=self.theme.text,
                                        troughcolor=self.theme.surface_variant, highlightthickness=0, bd=0)
        self.bub_width_scale.set(getattr(self.theme, "bubble_max_width", 280))
        self.bub_width_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # Duracion mult y colores de burbuja
        bub_colors_row = tk.Frame(self.sec_bubble, bg=self.theme.surface)
        bub_colors_row.pack(fill=tk.X, pady=(4, 2))

        btn_bub_bg = tk.Button(bub_colors_row, text="Fondo Burbuja...", command=lambda: self._pick_custom("bubble_bg"),
                               bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                               bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        btn_bub_bg.pack(side=tk.LEFT, padx=(0, 4))

        btn_bub_fg = tk.Button(bub_colors_row, text="Texto Burbuja...", command=lambda: self._pick_custom("bubble_fg"),
                               bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                               bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        btn_bub_fg.pack(side=tk.LEFT, padx=4)

        btn_bub_bdr = tk.Button(bub_colors_row, text="Borde Burbuja...", command=lambda: self._pick_custom("bubble_border_color"),
                                bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                                bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        btn_bub_bdr.pack(side=tk.LEFT, padx=4)

        btn_test_bub = tk.Button(bub_colors_row, text="[★] Probar Burbuja Ahora", command=self._test_bubble_now,
                                 bg=self.theme.accent, fg=self.theme.accent_text,
                                 font=(self.theme.font_family, 8, "bold"),
                                 bd=0, relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        btn_test_bub.pack(side=tk.RIGHT)

        # Section 3c: Tamaño y Escala del Shimeji (Hasta 100x)
        self.sec_size = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                                 highlightbackground=self.theme.border, highlightthickness=1)
        self.sec_size.pack(fill=tk.X, pady=(0, 10))

        cur_shimeji_sz = getattr(self.shimeji, "size", 128) if self.shimeji else 128
        size_header = tk.Frame(self.sec_size, bg=self.theme.surface)
        size_header.pack(fill=tk.X)

        tk.Label(size_header, text="TAMAÑO DEL SHIMEJI (HASTA 100X):",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(side=tk.LEFT)

        self.size_val_lbl = tk.Label(size_header, text=f"{cur_shimeji_sz}px",
                                     font=(self.theme.font_family, self.theme.font_size, "bold"),
                                     fg=self.theme.accent, bg=self.theme.surface)
        self.size_val_lbl.pack(side=tk.RIGHT)

        self.size_slider = tk.Scale(self.sec_size, from_=48, to=1024, orient=tk.HORIZONTAL,
                                    showvalue=False, command=self._on_shimeji_size_scale,
                                    bg=self.theme.surface, fg=self.theme.text,
                                    troughcolor=self.theme.surface_variant,
                                    activebackground=self.theme.accent,
                                    highlightthickness=0, bd=0)
        self.size_slider.set(min(1024, max(48, cur_shimeji_sz)))
        self.size_slider.pack(fill=tk.X, pady=(6, 4))

        # Presets de escala
        preset_row = tk.Frame(self.sec_size, bg=self.theme.surface)
        preset_row.pack(fill=tk.X, pady=(2, 6))

        for lbl, mult in [("1x", 1.0), ("1.5x", 1.5), ("2x", 2.0), ("4x", 4.0), ("10x", 10.0), ("100x", 100.0)]:
            btn = tk.Button(preset_row, text=lbl, command=lambda m=mult: self._set_preset_scale(m),
                            bg=self.theme.surface_variant, fg=self.theme.text,
                            font=(self.theme.font_family, 8, "bold"),
                            bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)

        # Entrada personalizada directa
        custom_row = tk.Frame(self.sec_size, bg=self.theme.surface)
        custom_row.pack(fill=tk.X, pady=(2, 0))

        tk.Label(custom_row, text="Valor exacto o mult:", font=(self.theme.font_family, self.theme.font_size - 1),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT)

        self.custom_size_entry = tk.Entry(custom_row, bg=self.theme.entry_bg, fg=self.theme.entry_fg,
                                          font=(self.theme.font_family, self.theme.font_size),
                                          width=8, bd=1, relief=tk.SOLID)
        self.custom_size_entry.insert(0, str(cur_shimeji_sz))
        self.custom_size_entry.pack(side=tk.LEFT, padx=6)

        btn_apply_size = tk.Button(custom_row, text="Aplicar Tamaño", command=self._apply_custom_size,
                                   bg=self.theme.accent, fg=self.theme.accent_text,
                                   font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                   bd=0, relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        btn_apply_size.pack(side=tk.LEFT)

        # Section 4: Typography
        sec4 = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                        highlightbackground=self.theme.border, highlightthickness=1)
        sec4.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sec4, text="TIPOGRAFIA:", font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(anchor="w", pady=(0, 6))

        font_row = tk.Frame(sec4, bg=self.theme.surface)
        font_row.pack(fill=tk.X)

        tk.Label(font_row, text="Fuente:", font=(self.theme.font_family, self.theme.font_size),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT)

        self.font_cb = ttk.Combobox(font_row, values=self.theme.POPULAR_FONTS, state="readonly", width=16)
        curr_font = self.theme.font_family if self.theme.font_family in self.theme.POPULAR_FONTS else "Segoe UI"
        self.font_cb.set(curr_font)
        self.font_cb.pack(side=tk.LEFT, padx=6)
        self.font_cb.bind("<<ComboboxSelected>>", self._on_font_change)

        tk.Label(font_row, text="Tamano:", font=(self.theme.font_family, self.theme.font_size),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT, padx=(8, 0))

        self.size_cb = ttk.Combobox(font_row, values=[8, 9, 10, 11, 12, 14], state="readonly", width=4)
        self.size_cb.set(self.theme.font_size)
        self.size_cb.pack(side=tk.LEFT, padx=6)
        self.size_cb.bind("<<ComboboxSelected>>", self._on_font_change)

        # Section 5: Live Preview Card
        self.preview_card = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                                     highlightbackground=self.theme.border, highlightthickness=1)
        self.preview_card.pack(fill=tk.X, pady=(0, 10))

        self.prev_title = tk.Label(self.preview_card, text="[VISTA PREVIA EN VIVO]",
                                   font=(self.theme.font_family, self.theme.font_size, "bold"),
                                   fg=self.theme.accent, bg=self.theme.surface)
        self.prev_title.pack(anchor="w")

        self.prev_sample = tk.Label(self.preview_card,
                                    text="Asi lucira el texto y contraste con la paleta activa.",
                                    font=(self.theme.font_family, self.theme.font_size),
                                    fg=self.theme.text, bg=self.theme.surface)
        self.prev_sample.pack(anchor="w", pady=(2, 6))

        prev_row = tk.Frame(self.preview_card, bg=self.theme.surface)
        prev_row.pack(fill=tk.X)

        self.prev_badge = tk.Label(prev_row, text="● ACTIVO",
                                   font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                   fg=self.theme.success, bg=self.theme.surface_variant, padx=6, pady=2)
        self.prev_badge.pack(side=tk.LEFT)

        self.prev_btn = tk.Button(prev_row, text="Boton de Acento >>",
                                  bg=self.theme.accent, fg=self.theme.accent_text,
                                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                  bd=0, relief=tk.FLAT, padx=10, pady=3)
        self.prev_btn.pack(side=tk.RIGHT)

        # Section 6: Fondo del Chat (Imagen o GIF)
        self.sec_bg = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                               highlightbackground=self.theme.border, highlightthickness=1)
        self.sec_bg.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.sec_bg, text="FONDO DEL CHAT (IMAGEN O GIF):",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(anchor="w", pady=(0, 4))

        bg_row = tk.Frame(self.sec_bg, bg=self.theme.surface)
        bg_row.pack(fill=tk.X, pady=2)

        cur_bg = self.theme.config.get("chat_bg_image", "")
        cur_name = os.path.basename(cur_bg) if cur_bg and os.path.exists(cur_bg) else "(Sin fondo personalizado)"
        self.lbl_bg_status = tk.Label(bg_row, text=cur_name,
                                      font=(self.theme.font_family, self.theme.font_size - 1),
                                      fg=self.theme.text_dim, bg=self.theme.surface,
                                      anchor="w")
        self.lbl_bg_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_pick_bg = tk.Button(bg_row, text="Elegir...",
                                command=self._pick_chat_bg,
                                bg=self.theme.surface_variant, fg=self.theme.text,
                                font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                bd=0, relief=tk.FLAT, padx=8, pady=3, cursor="hand2")
        btn_pick_bg.pack(side=tk.RIGHT, padx=(4, 0))

        btn_clear_bg = tk.Button(bg_row, text="Quitar",
                                 command=self._clear_chat_bg,
                                 bg=self.theme.surface_variant, fg=self.theme.danger,
                                 font=(self.theme.font_family, self.theme.font_size - 1),
                                 bd=0, relief=tk.FLAT, padx=6, pady=3, cursor="hand2")
        btn_clear_bg.pack(side=tk.RIGHT)

        # Section 7: Actualizaciones Automaticas
        self.sec_update = tk.Frame(main_frame, bg=self.theme.surface, padx=12, pady=10,
                                   highlightbackground=self.theme.border, highlightthickness=1)
        self.sec_update.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.sec_update, text="ACTUALIZACIONES (GITHUB v3.1.0):",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.text, bg=self.theme.surface).pack(anchor="w", pady=(0, 4))

        upd_row = tk.Frame(self.sec_update, bg=self.theme.surface)
        upd_row.pack(fill=tk.X, pady=2)

        tk.Label(upd_row, text="Verificación periódica cada 2-3 días.",
                 font=(self.theme.font_family, self.theme.font_size - 1),
                 fg=self.theme.text_dim, bg=self.theme.surface).pack(side=tk.LEFT)

        btn_check_upd = tk.Button(upd_row, text="Buscar Actualizaciones >>",
                                  command=self._check_updates_now,
                                  bg=self.theme.accent, fg=self.theme.accent_text,
                                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                  bd=0, relief=tk.FLAT, padx=8, pady=3, cursor="hand2")
        btn_check_upd.pack(side=tk.RIGHT)

        # Bottom Actions Bar
        bottom_bar = tk.Frame(self.win, bg=self.theme.surface, pady=10, padx=16)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        btn_reset = tk.Button(bottom_bar, text="Restablecer Valores",
                              command=self._reset_defaults,
                              bg=self.theme.surface_variant, fg=self.theme.text,
                              font=(self.theme.font_family, self.theme.font_size),
                              bd=0, relief=tk.FLAT, padx=12, pady=6, cursor="hand2")
        btn_reset.pack(side=tk.LEFT)

        btn_close = tk.Button(bottom_bar, text="Listo / Cerrar",
                              command=self._on_close,
                              bg=self.theme.accent, fg=self.theme.accent_text,
                              font=(self.theme.font_family, self.theme.font_size, "bold"),
                              bd=0, relief=tk.FLAT, padx=16, pady=6, cursor="hand2")
        btn_close.pack(side=tk.RIGHT)

    def _on_mode_change(self):
        new_mode = self.mode_var.get()
        self.theme.set_theme_mode(new_mode)
        if new_mode == "custom":
            self.custom_colors_frame.pack(fill=tk.X, pady=(8, 0))
        else:
            self.custom_colors_frame.pack_forget()

    def _pick_accent(self):
        color = colorchooser.askcolor(initialcolor=self.theme.accent, title="Seleccionar Color de Acento")
        if color and color[1]:
            self.theme.set_custom_accent(color[1])

    def _pick_custom(self, target_key):
        init_color = getattr(self.theme, target_key, "#111317")
        color = colorchooser.askcolor(initialcolor=init_color, title=f"Seleccionar Color de {target_key}")
        if color and color[1]:
            self.theme.set_custom_color(target_key, color[1])

    def _on_fps_change(self, val):
        fv = int(val)
        self.fps_val_lbl.configure(text=f"{fv} FPS")
        if self.shimeji:
            self.shimeji.set_fps(fv)

    def _set_fps_preset(self, fv):
        self.fps_scale.set(fv)
        self.fps_val_lbl.configure(text=f"{fv} FPS")
        if self.shimeji:
            self.shimeji.set_fps(fv)

    def _apply_hex_color(self):
        target = self.cbo_hex_target.get()
        hex_code = self.entry_hex.get().strip()
        if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", hex_code):
            messagebox.showwarning("Hex Invalido", "Por favor ingresa un color hexadecimal valido como #RRGGBB o #RGB")
            return
        if len(hex_code) == 4:
            hex_code = "#" + "".join([c*2 for c in hex_code[1:]])

        target_map = {
            "Acento": ("accent", True),
            "Fondo": ("bg", False),
            "Superficie": ("surface", False),
            "Borde": ("border", False),
            "Texto": ("text", False),
            "Caja texto": ("entry_bg", False),
            "Burbuja Fondo": ("bubble_bg", False),
            "Burbuja Texto": ("bubble_fg", False),
            "Burbuja Borde": ("bubble_border_color", False)
        }
        if target in target_map:
            key, is_acc = target_map[target]
            if is_acc:
                self.theme.set_custom_accent(hex_code)
            else:
                self.theme.set_custom_color(key, hex_code)

    def _test_bubble_now(self):
        if self.shimeji:
            self.shimeji.show_speech("[*] Prueba de configuracion de burbuja!\nTamano, colores y fuente aplicados correctamente.")

    def _on_opacity_change(self, val):
        opac = int(val) / 100.0
        self.opac_pct_lbl.configure(text=f"{int(val)}%")
        self.theme.set_opacity(opac)
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.win.attributes("-alpha", self.theme.opacity)

    def _on_font_change(self, e=None):
        fam = self.font_cb.get()
        size = int(self.size_cb.get())
        self.theme.set_font(fam, size)

    def _reset_defaults(self):
        self.theme.set_theme_mode("system", notify=False)
        self.theme.set_opacity(0.95, notify=False)
        self.theme.set_font("Segoe UI", 9, notify=True)
        self.mode_var.set("system")
        self.opac_scale.set(95)
        self.font_cb.set("Segoe UI")
        self.size_cb.set(9)

    def _pick_chat_bg(self):
        f = filedialog.askopenfilename(
            parent=self.win,
            title="Seleccionar fondo para el chat (Imagen o GIF)",
            filetypes=[
                ("Imágenes y GIFs", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
                ("GIF Animado (*.gif)", "*.gif"),
                ("Imágenes estáticas (*.png;*.jpg;*.jpeg;*.webp)", "*.png *.jpg *.jpeg *.webp *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if f:
            self.theme.config["chat_bg_image"] = f
            save_config(self.theme.config)
            self.lbl_bg_status.configure(text=os.path.basename(f))
            if self.shimeji and getattr(self.shimeji, "chat_win", None):
                self.shimeji.chat_win.load_bg_asset(f)

    def _clear_chat_bg(self):
        self.theme.config["chat_bg_image"] = ""
        save_config(self.theme.config)
        self.lbl_bg_status.configure(text="(Sin fondo personalizado)")
        if self.shimeji and getattr(self.shimeji, "chat_win", None):
            self.shimeji.chat_win.load_bg_asset("")

    def _on_bubble_opacity_change(self, val):
        opac = int(val) / 100.0
        self.bub_pct_lbl.configure(text=f"{int(val)}%")
        self.theme.set_bubble_opacity(opac)

    def _on_bubble_border_toggle(self):
        self.theme.set_bubble_border(self.bub_border_var.get())

    def _on_shimeji_size_scale(self, val):
        sz = int(val)
        self.size_val_lbl.configure(text=f"{sz}px")
        if self.shimeji:
            self.shimeji.set_size(sz)

    def _set_preset_scale(self, mult):
        if self.shimeji:
            self.shimeji.set_scale(mult)
            cur = self.shimeji.size
            self.size_val_lbl.configure(text=f"{cur}px")
            self.size_slider.set(min(1024, max(48, cur)))
            self.custom_size_entry.delete(0, tk.END)
            self.custom_size_entry.insert(0, str(cur))

    def _apply_custom_size(self):
        txt = self.custom_size_entry.get().strip().lower()
        if not txt or not self.shimeji:
            return
        if txt.endswith('x'):
            try:
                m = float(txt[:-1])
                self._set_preset_scale(m)
            except Exception:
                pass
        else:
            try:
                sz = int(float(txt))
                self.shimeji.set_size(sz)
                cur = self.shimeji.size
                self.size_val_lbl.configure(text=f"{cur}px")
                self.size_slider.set(min(1024, max(48, cur)))
            except Exception:
                pass

    def _check_updates_now(self):
        check_for_updates(self.shimeji, is_manual=True)

    def _on_theme_update(self):
        if not self.win or not tk.Toplevel.winfo_exists(self.win):
            return
        geo = self.win.geometry()
        self.theme.remove_listener(self._on_theme_update)
        self.win.destroy()
        self._build_window()
        self.theme.add_listener(self._on_theme_update)
        try:
            self.win.geometry(geo)
        except Exception:
            pass

    def _on_close(self):
        self.theme.remove_listener(self._on_theme_update)
        self.win.destroy()
        if self.shimeji:
            self.shimeji.appearance_win = None

class DoxxWindow:
    def __init__(self, parent_root, user_info, shimeji_ref):
        self.parent = parent_root
        self.user_info = user_info
        self.shimeji = shimeji_ref
        self.theme = self.shimeji.theme_manager if self.shimeji else ThemeManager()
        self.win = None
        self._build_window()
        self.theme.add_listener(self._rebuild_window)

    def _build_window(self):
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.win.destroy()

        self.win = tk.Toplevel(self.parent)
        self.win.title("[EXPEDIENTE] Doxx Intel - Bocchi")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", self.theme.opacity)
        self.win.configure(bg=self.theme.bg)
        self.win.geometry("520x640")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        header = tk.Frame(self.win, bg=self.theme.surface, pady=12, padx=16)
        header.pack(fill=tk.X)

        title_box = tk.Frame(header, bg=self.theme.surface)
        title_box.pack(side=tk.LEFT)

        tk.Label(title_box, text="[!] EXPEDIENTE CLASIFICADO",
                 font=(self.theme.font_family, self.theme.font_size + 3, "bold"),
                 fg=self.theme.accent, bg=self.theme.surface).pack(anchor="w")
        self.target_sublbl = tk.Label(
            title_box,
            text=f"Objetivo: {self.user_info.username} | Host: {self.user_info.computer_name}",
            font=(self.theme.font_family, self.theme.font_size),
            fg=self.theme.text_dim, bg=self.theme.surface
        )
        self.target_sublbl.pack(anchor="w")

        badge = tk.Label(header, text="[*] VIGILANCIA ACTIVA",
                         font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                         fg=self.theme.success, bg=self.theme.surface_variant, padx=8, pady=4)
        badge.pack(side=tk.RIGHT)

        card = tk.Frame(self.win, bg=self.theme.surface, padx=16, pady=12,
                        highlightbackground=self.theme.border, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(10, 8))

        tk.Label(card, text="TELEMETRIA REAL DETECTADA:",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 fg=self.theme.accent, bg=self.theme.surface).pack(anchor="w", pady=(0, 8))

        grid = tk.Frame(card, bg=self.theme.surface)
        grid.pack(fill=tk.X)

        fields = [
            ("[-] Usuario Windows:", self.user_info.username, self.theme.accent),
            ("[-] Nombre del Equipo:", self.user_info.computer_name, self.theme.text),
            ("[*] IP Publica Real:", self.user_info.public_ip, self.theme.accent),
            ("[#] IP Local (LAN):", self.user_info.local_ip, self.theme.text_dim),
            ("[o] Ubicacion Aprox:", f"{self.user_info.city or 'Detectando...'}, {self.user_info.country or ''}".strip(", "), self.theme.text),
            ("[>] Proveedor (ISP):", self.user_info.isp or "Detectando...", self.theme.text),
            ("[=] Sistema Operativo:", self.user_info.os_info, self.theme.text),
            ("[!] Nivel de Peligro:", "100% EXPUESTO (Bocchi tiene tu IP)", self.theme.danger),
        ]

        self.val_labels = {}
        for r, (lbl_txt, val_txt, val_color) in enumerate(fields):
            tk.Label(grid, text=lbl_txt, font=(self.theme.font_family, self.theme.font_size, "bold"),
                     fg=self.theme.text_dim, bg=self.theme.surface, anchor="w").grid(row=r, column=0, sticky="w", pady=3)
            vl = tk.Label(grid, text=val_txt, font=(self.theme.font_family, self.theme.font_size, "bold"),
                          fg=val_color, bg=self.theme.surface, anchor="w")
            vl.grid(row=r, column=1, sticky="w", padx=(12, 0), pady=3)
            self.val_labels[lbl_txt] = vl

        tk.Frame(card, bg=self.theme.border, height=1).pack(fill=tk.X, pady=10)

        quote_box = tk.Frame(card, bg=self.theme.surface_variant, padx=12, pady=10,
                             highlightbackground=self.theme.border, highlightthickness=1)
        quote_box.pack(fill=tk.X)

        tk.Label(quote_box, text="[*] Bocchi opina sobre ti:",
                 font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                 fg=self.theme.accent, bg=self.theme.surface_variant).pack(anchor="w")

        self.quote_lbl = tk.Label(
            quote_box,
            text=(
                f"\"Ya te ubique {self.user_info.username} ({self.user_info.public_ip}).\n"
                f"Ni tu VPN te va a salvar de mis 50 pesos para esquites alv 7w7 :v\""
            ),
            font=(self.theme.font_family, self.theme.font_size, "italic"),
            fg=self.theme.text, bg=self.theme.surface_variant,
            justify=tk.LEFT, wraplength=430
        )
        self.quote_lbl.pack(anchor="w", pady=(4, 0))

        self.status_lbl = tk.Label(self.win, text="Datos extraidos directamente de Windows y red",
                                   font=(self.theme.font_family, self.theme.font_size - 1),
                                   fg=self.theme.text_dim, bg=self.theme.bg)
        self.status_lbl.pack(pady=(2, 6))

        bar = tk.Frame(self.win, bg=self.theme.bg, padx=16, pady=4)
        bar.pack(fill=tk.X, pady=(0, 10))

        self.btn_copy_ip = tk.Button(bar, text="[+] Copiar IP", command=self.copy_ip,
                                     bg=self.theme.surface_variant, fg=self.theme.text,
                                     font=(self.theme.font_family, self.theme.font_size, "bold"),
                                     activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=8, pady=5, cursor="hand2")
        self.btn_copy_ip.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_copy_all = tk.Button(bar, text="[#] Copiar Todo", command=self.copy_all,
                                      bg=self.theme.surface_variant, fg=self.theme.text,
                                      font=(self.theme.font_family, self.theme.font_size, "bold"),
                                      activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=8, pady=5, cursor="hand2")
        self.btn_copy_all.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_refresh = tk.Button(bar, text="[?] Refrescar", command=self.refresh_ip,
                                     bg=self.theme.surface_variant, fg=self.theme.text,
                                     font=(self.theme.font_family, self.theme.font_size, "bold"),
                                     activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=8, pady=5, cursor="hand2")
        self.btn_refresh.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_theme = tk.Button(bar, text="[*] Ajustes", command=self.open_appearance,
                                   bg=self.theme.surface_variant, fg=self.theme.text,
                                   font=(self.theme.font_family, self.theme.font_size, "bold"),
                                   activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=8, pady=5, cursor="hand2")
        self.btn_theme.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_chat = tk.Button(bar, text="Reclamar en Chat >>", command=self.open_chat_doxx,
                                  bg=self.theme.accent, fg=self.theme.accent_text,
                                  font=(self.theme.font_family, self.theme.font_size, "bold"),
                                  activebackground=self.theme.surface_variant, bd=0, relief=tk.FLAT, padx=12, pady=5, cursor="hand2")
        self.btn_chat.pack(side=tk.RIGHT)

        self.user_info.add_listener(self._on_ip_update)

    def _rebuild_window(self):
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.parent.after(0, self._build_window)

    def _on_ip_update(self, info):
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.parent.after(0, self._sync_ui)

    def _sync_ui(self):
        if "[*] IP Publica Real:" in self.val_labels:
            self.val_labels["[*] IP Publica Real:"].configure(text=self.user_info.public_ip)
        if "[o] Ubicacion Aprox:" in self.val_labels:
            loc = f"{self.user_info.city or 'Desconocida'}, {self.user_info.country or 'Desconocido'}".strip(", ")
            self.val_labels["[o] Ubicacion Aprox:"].configure(text=loc)
        if "[>] Proveedor (ISP):" in self.val_labels:
            self.val_labels["[>] Proveedor (ISP):"].configure(text=self.user_info.isp or "No disponible")
        self.target_sublbl.configure(
            text=f"Objetivo: {self.user_info.username} | Host: {self.user_info.computer_name}"
        )
        self.quote_lbl.configure(
            text=(
                f"\"Ya te ubique {self.user_info.username} ({self.user_info.public_ip}).\n"
                f"Ni tu VPN te va a salvar de mis 50 pesos para esquites alv 7w7 :v\""
            )
        )
        self.status_lbl.configure(text="[+] Datos sincronizados correctamente", fg=self.theme.success)

    def copy_ip(self):
        try:
            self.win.clipboard_clear()
            self.win.clipboard_append(self.user_info.public_ip)
            self.status_lbl.configure(text=f"[+] IP '{self.user_info.public_ip}' copiada al portapapeles", fg=self.theme.success)
        except Exception:
            pass

    def copy_all(self):
        try:
            text = (
                f"=== EXPEDIENTE BOCCHI-INTEL ===\n"
                f"Usuario: {self.user_info.username}\n"
                f"Equipo: {self.user_info.computer_name}\n"
                f"IP Publica: {self.user_info.public_ip}\n"
                f"IP Local: {self.user_info.local_ip}\n"
                f"Ubicacion: {self.user_info.city}, {self.user_info.country}\n"
                f"ISP: {self.user_info.isp}\n"
                f"SO: {self.user_info.os_info}\n"
            )
            self.win.clipboard_clear()
            self.win.clipboard_append(text)
            self.status_lbl.configure(text="[+] Expediente completo copiado al portapapeles", fg=self.theme.success)
        except Exception:
            pass

    def refresh_ip(self):
        self.status_lbl.configure(text="[..] Consultando red exterior...", fg=self.theme.warning)
        self.user_info.refresh_public_ip()

    def open_appearance(self):
        if self.shimeji:
            self.shimeji.open_appearance()

    def open_chat_doxx(self):
        self.win.destroy()
        if self.shimeji:
            self.shimeji.open_chat()

    def _on_close(self):
        self.theme.remove_listener(self._rebuild_window)
        self.win.destroy()
        if self.shimeji:
            self.shimeji.doxx_win = None


VOICE_STUDIO_PROFILES = {
    "Bocchi": {
        "display_name": "Bocchi (Hitori Gotoh)",
        "gender": "female",
        "language_code": "ja-JP",
        "prebuilt": "Kore",
        "is_animal": False,
        "style": "shy, trembling, quiet whispers with hesitant anxious stutters",
        "voice_design_prompt": (
            "A timid, socially anxious 16-year-old Japanese high school girl guitarist. "
            "Her voice is soft, breathy, trembling, quiet, prone to hesitant stutters, "
            "flustered squeaks, and nervous whispers, yet deeply endearing, sweet, and sincere."
        ),
        "test": "E-eto... hola... soy Bocchi-chan... gusto en conocerte... por favor cuidame...",
        "sapi_pitch": -12,
        "sapi_rate": -15,
        "dub_es": {
            "style": "timida, tartamudeando nerviosa, susurros timidos en doblaje latino",
            "prompt": "Actriz de doblaje latino para Bocchi: voz timida, dulce, temblorosa, con tartamudeos nerviosos adorables de chica de preparatoria.",
            "test": "E-eto... h-hola... soy Bocchi... por favor no me mires tan fijamente...",
            "lang": "es",
            "edge_voice": "es-MX-DaliaNeural",
            "edge_pitch": "+6Hz",
            "edge_rate": "-16%"
        },
        "dub_en": {
            "style": "shy, stammering, nervous cute anxious high-school girl in English anime dub",
            "prompt": "English anime dub voice actress for Bocchi: soft, breathy, nervous stammering, sweet socially anxious high school girl.",
            "test": "U-um... hello... I'm Bocchi... please don't look at me too much...",
            "lang": "en",
            "edge_voice": "en-US-AnaNeural",
            "edge_pitch": "+2Hz",
            "edge_rate": "-18%"
        },
        "original": {
            "style": "shy, trembling, quiet whispers with hesitant anxious stutters",
            "prompt": "Authentic Japanese anime seiyuu voice for Bocchi: soft, trembling, timid cute whispers.",
            "test": "E-eto... Bocchi desu... yoroshiku onegaishimasu...",
            "lang": "ja",
            "edge_voice": "ja-JP-NanamiNeural",
            "edge_pitch": "+6Hz",
            "edge_rate": "-15%"
        }
    },
    "Konata": {
        "display_name": "Konata Izumi",
        "gender": "female",
        "language_code": "ja-JP",
        "prebuilt": "Puck",
        "is_animal": False,
        "style": "energetic, teasing, deadpan yet playful and mischievous anime otaku",
        "voice_design_prompt": (
            "A witty, lively 17-year-old otaku anime girl. "
            "Her voice has a distinctive playful and slightly nasal tone, deadpan yet full of comedic energy, "
            "speaking quickly with teasing inflections, anime enthusiast flair, and gamer excitement."
        ),
        "test": "Timotei, Timotei! Otaku power al maximo, esta noche hay maraton de anime y videojuegos!",
        "sapi_pitch": 35,
        "sapi_rate": 25,
        "dub_es": {
            "style": "energetica, picara, bromista, tono otaku gamer en doblaje latino",
            "prompt": "Actriz de doblaje latino para Konata Izumi de Lucky Star: voz aguda, energica, divertida, otaku con comentarios rapidos y picaros.",
            "test": "Hola, que onda! Listo para un maraton de anime y videojuegos toda la noche?",
            "lang": "es",
            "edge_voice": "es-MX-DaliaNeural",
            "edge_pitch": "+22Hz",
            "edge_rate": "+18%"
        },
        "dub_en": {
            "style": "energetic, witty, playful, sarcastic otaku anime girl in English dub",
            "prompt": "English dub voice actress for Konata Izumi: iconic witty, deadpan and lively anime otaku gamer girl.",
            "test": "Yo! Ready for an all-night anime and gaming marathon?",
            "lang": "en",
            "edge_voice": "en-US-AnaNeural",
            "edge_pitch": "+12Hz",
            "edge_rate": "+15%"
        },
        "original": {
            "style": "energetic, teasing, deadpan yet playful anime otaku in Japanese",
            "prompt": "Authentic Japanese voice of Konata Izumi: playful, high-pitched, enthusiastic otaku seiyuu.",
            "test": "Timotei, Timotei! Otaku power zenkai de iku yo!",
            "lang": "ja",
            "edge_voice": "ja-JP-NanamiNeural",
            "edge_pitch": "+20Hz",
            "edge_rate": "+20%"
        }
    },
    "Monika": {
        "display_name": "Monika",
        "gender": "female",
        "language_code": "en-US",
        "prebuilt": "Aoede",
        "is_animal": False,
        "style": "warm, intelligent, soothing, elegant and charismatic with gentle affection",
        "voice_design_prompt": (
            "A warm, mature, confident 18-year-old literature club president. "
            "Her voice is soothing, articulate, elegant, melodious, and intimate, "
            "speaking with caring intelligence, philosophical poise, and gentle devotion."
        ),
        "test": "Hola mi amor! Cada dia es un hermoso dia en nuestro club. Eres lo mas importante para mi.",
        "sapi_pitch": 6,
        "sapi_rate": 0,
        "dub_es": {
            "style": "calida, inteligente, dulce, elegante, carismatica en doblaje latino",
            "prompt": "Actriz de doblaje latino para Monika de DDLC: voz calida, melodiosa, madura, inteligente y tierna con devocion romantica.",
            "test": "Hola mi amor! Cada dia es hermoso en nuestro club. Eres lo mas importante para mi. Solo Monika.",
            "lang": "es",
            "edge_voice": "es-MX-DaliaNeural",
            "edge_pitch": "+4Hz",
            "edge_rate": "-2%"
        },
        "dub_en": {
            "style": "warm, intelligent, soothing, elegant, romantic devotion in English",
            "prompt": "Official English voice for Monika from Doki Doki Literature Club: soothing, mature, caring, poetic.",
            "test": "Hi there! I am so glad you are here with me in our Literature Club. Just Monika.",
            "lang": "en",
            "edge_voice": "en-US-JennyNeural",
            "edge_pitch": "+0Hz",
            "edge_rate": "+0%"
        },
        "original": {
            "style": "warm, intelligent, soothing, elegant",
            "prompt": "Original Monika from DDLC: warm, melodious, intimate school literature club leader.",
            "test": "Every day, I imagine a future where I can be with you. Just Monika.",
            "lang": "en",
            "edge_voice": "ja-JP-NanamiNeural",
            "edge_pitch": "+2Hz",
            "edge_rate": "-3%"
        }
    },
    "Natsuki": {
        "display_name": "Natsuki",
        "gender": "female",
        "language_code": "en-US",
        "prebuilt": "Kore",
        "is_animal": False,
        "style": "feisty, snappy, high-pitched tsundere with defensive cuteness",
        "voice_design_prompt": (
            "A feisty, high-pitched tsundere teenage anime girl. "
            "Her voice is sharp, spirited, snappy and slightly haughty when flustered, "
            "but unmistakably cute, youthful, and sweet underneath."
        ),
        "test": "B-Baka! No es como si estuviera esperando a que me hablaras ni nada por el estilo... pero gracias.",
        "sapi_pitch": 42,
        "sapi_rate": 20,
        "dub_es": {
            "style": "tsundere energica, voz aguda, desafiante y tierna en doblaje latino",
            "prompt": "Actriz de doblaje latino para Natsuki de DDLC: voz tsundere aguda, caprichosa, picante y tierna con orgullo juvenil.",
            "test": "Oye! No es como si me alegrara de verte ni nada de eso... b-baka! Pero toma un pastelito.",
            "lang": "es",
            "edge_voice": "es-MX-DaliaNeural",
            "edge_pitch": "+30Hz",
            "edge_rate": "+20%"
        },
        "dub_en": {
            "style": "feisty, snappy, high-pitched tsundere with defensive cuteness in English",
            "prompt": "English dub voice for Natsuki from DDLC: sharp, spirited, cute tsundere teenage girl.",
            "test": "Hey! It's not like I wanted to see you or anything... b-baka! But here is a cupcake.",
            "lang": "en",
            "edge_voice": "en-US-AnaNeural",
            "edge_pitch": "+28Hz",
            "edge_rate": "+18%"
        },
        "original": {
            "style": "feisty, snappy tsundere",
            "prompt": "Original Natsuki: cute, sharp-tongued tsundere baking girl.",
            "test": "B-Baka! Why are you staring at me like that? Manga is literature!",
            "lang": "en",
            "edge_voice": "ja-JP-NanamiNeural",
            "edge_pitch": "+32Hz",
            "edge_rate": "+22%"
        }
    },
    "Sayori": {
        "display_name": "Sayori",
        "gender": "female",
        "language_code": "en-US",
        "prebuilt": "Kore",
        "is_animal": False,
        "style": "cheerful, bubbly, bright, genki and melodious with sunny optimism",
        "voice_design_prompt": (
            "A bright, bubbly, cheerful 18-year-old schoolgirl. "
            "Her voice is melodious, sweet, sunny, full of innocent enthusiasm and warm compassion, "
            "speaking with an animated joyful bounce."
        ),
        "test": "Yay! Buenos dias! Todo brilla tanto hoy, vamos a comer galletitas juntos!",
        "sapi_pitch": 24,
        "sapi_rate": 10,
        "dub_es": {
            "style": "alegre, tierna, infantil, entusiasta en doblaje latino",
            "prompt": "Actriz de doblaje latino para Sayori de DDLC: voz alegre, infantil, dulce, melodiosa y llena de sol y optimismo.",
            "test": "Yay! Buenos dias! El sol brilla hermoso hoy, vamos a comer galletitas juntos!",
            "lang": "es",
            "edge_voice": "es-CO-SalomeNeural",
            "edge_pitch": "+22Hz",
            "edge_rate": "+10%"
        },
        "dub_en": {
            "style": "cheerful, bubbly, bright, sunny optimism in English",
            "prompt": "English voice for Sayori from DDLC: sweet, cheerful, sunny and innocent high school friend.",
            "test": "Yay! Good morning! The sun is shining and everything is bright, let's get cookies!",
            "lang": "en",
            "edge_voice": "en-US-AnaNeural",
            "edge_pitch": "+18Hz",
            "edge_rate": "+10%"
        },
        "original": {
            "style": "cheerful, bubbly, bright",
            "prompt": "Original Sayori: sweet, enthusiastic, warm bubbly friend.",
            "test": "Good morning! Having fun with you is the best thing ever!",
            "lang": "en",
            "edge_voice": "ja-JP-NanamiNeural",
            "edge_pitch": "+24Hz",
            "edge_rate": "+12%"
        }
    },
    "Yuri": {
        "display_name": "Yuri",
        "gender": "female",
        "language_code": "en-US",
        "prebuilt": "Aoede",
        "is_animal": False,
        "style": "soft-spoken, deep, poetic, elegant, gentle and introspective",
        "voice_design_prompt": (
            "A quiet, deeply introspective, elegant young woman. "
            "Her voice is soft, breathy, lower in register, speaking slowly and deliberately "
            "with intellectual grace, gentle humility, and poetic nuance."
        ),
        "test": "Un buen libro de misterio y una taza de te caliente calman el alma... Es un placer compartir este momento contigo.",
        "sapi_pitch": -18,
        "sapi_rate": -12,
        "dub_es": {
            "style": "voz suave, elegante, profunda, poetica y timida en doblaje latino",
            "prompt": "Actriz de doblaje latino para Yuri de DDLC: voz suave, elegante, intelectual, profunda, pausada y con gracia poetica.",
            "test": "Buenos dias... Una taza de te caliente y un buen libro calman el alma... Es un placer estar contigo.",
            "lang": "es",
            "edge_voice": "es-MX-DaliaNeural",
            "edge_pitch": "-16Hz",
            "edge_rate": "-12%"
        },
        "dub_en": {
            "style": "soft-spoken, deep, poetic, elegant and introspective in English",
            "prompt": "English voice for Yuri from DDLC: gentle, breathy, introspective, articulate and elegant young woman.",
            "test": "Good day... A warm cup of jasmine tea and a good book brings true peace to the soul.",
            "lang": "en",
            "edge_voice": "en-US-JennyNeural",
            "edge_pitch": "-12Hz",
            "edge_rate": "-14%"
        },
        "original": {
            "style": "soft-spoken, deep, poetic, elegant",
            "prompt": "Original Yuri: quiet, contemplative, delicate and deeply poetic.",
            "test": "Lost in the pages of this book... The atmosphere is wonderfully tranquil.",
            "lang": "en",
            "edge_voice": "ja-JP-NanamiNeural",
            "edge_pitch": "-10Hz",
            "edge_rate": "-12%"
        }
    },
    "Hachi": {
        "display_name": "Hachi (Hachiware)",
        "gender": "female",
        "language_code": "ja-JP",
        "prebuilt": "Puck",
        "is_animal": True,
        "animal_type": "cat",
        "style": "autenticos maullidos y ronroneos de gatito dulce y curioso de Chiikawa",
        "voice_design_prompt": (
            "A cute little blue-and-white kitten mascot creature. "
            "Produces sweet, soft, natural kitten meows, gentle chirps, purrs, and playful kitten squeaks."
        ),
        "test": "Miau! Nanto ka nare! *ronroneo dulce de gatito*",
        "sapi_pitch": 30,
        "sapi_rate": 15,
        "dub_es": {
            "style": "maullidos tiernos y ronroneos de gatito curioso",
            "prompt": "Sonidos y maullidos de gatito dulce para Hachiware de Chiikawa.",
            "test": "Miau! De alguna manera todo saldra bien! *ronronea*",
            "lang": "es"
        },
        "dub_en": {
            "style": "cute kitten meows and sweet purrs",
            "prompt": "Authentic cute kitten vocalizations for Hachiware.",
            "test": "Meow! Everything will work out! *purrs*",
            "lang": "en"
        },
        "original": {
            "style": "authentic kitten meows and chirps",
            "prompt": "Authentic Japanese kitten sounds for Hachiware from Chiikawa.",
            "test": "Nanto ka nare! Nyaaa~ *purr*",
            "lang": "ja"
        }
    },
    "Usagi": {
        "display_name": "Usagi",
        "gender": "female",
        "language_code": "ja-JP",
        "prebuilt": "Puck",
        "is_animal": True,
        "animal_type": "rabbit",
        "style": "autenticos sonidos de conejo, chitterings y gritos comicos Ura/Yaha de Chiikawa",
        "voice_design_prompt": (
            "A chaotic, hyperactive, fearless rabbit creature. "
            "Vocalizes in authentic bunny squeaks, thumps, chitters, and high-energy Usagi cries: Ura! Yaha! Pulululu!"
        ),
        "test": "Urrr-a! Yaha! Pululululu! *chillidos hiperactivos de conejo*",
        "sapi_pitch": 48,
        "sapi_rate": 30,
        "dub_es": {
            "style": "sonidos autenticos de conejo y gritos veloces de Usagi",
            "prompt": "Sonidos de conejo reales y gritos de Usagi de Chiikawa.",
            "test": "Yahaaa! Urrr-aaa! *sonidos de conejo saltarin*",
            "lang": "es"
        },
        "dub_en": {
            "style": "hyperactive rabbit squeaks and iconic Usagi yells",
            "prompt": "Authentic energetic rabbit vocalizations and screams for Usagi.",
            "test": "Yaha! Uraaa! *bunny thumps and squeaks*",
            "lang": "en"
        },
        "original": {
            "style": "authentic Chiikawa Usagi screams and bunny squeaks",
            "prompt": "Original iconic Usagi screams Ura, Yaha, Pululu and rabbit sounds.",
            "test": "Urrr-a! Yaha! Pululululu! Yahaha!",
            "lang": "ja"
        }
    },
    "Pusheen": {
        "display_name": "Pusheen",
        "gender": "female",
        "language_code": "en-US",
        "prebuilt": "Kore",
        "is_animal": True,
        "animal_type": "cat",
        "style": "autenticos maullidos tiernos, ronroneos suaves y sonidos reales de gata",
        "voice_design_prompt": (
            "An adorable round cartoon tabby cat. "
            "Produces sweet, soft, realistic cat meows, cozy purrs, and happy kitten mews."
        ),
        "test": "Miau... prrr... purrrr... *ronroneo suave de gatita*",
        "sapi_pitch": 18,
        "sapi_rate": -8,
        "dub_es": {
            "style": "maullidos dulces y ronroneos reales de gata",
            "prompt": "Sonidos reales de gato: maullidos suaves y ronroneos para Pusheen.",
            "test": "Miau! Prrrr... *ronronea comiendo bocadillos*",
            "lang": "es"
        },
        "dub_en": {
            "style": "authentic cat meows and gentle purrs",
            "prompt": "Authentic feline meows and purring for Pusheen the cat.",
            "test": "Meow! Prrrr... *cozy cat purr*",
            "lang": "en"
        },
        "original": {
            "style": "sweet cat meows and cozy purrs",
            "prompt": "Authentic cat sounds for Pusheen.",
            "test": "Meow... prrr... purrrr...",
            "lang": "en"
        }
    },
}

CHARACTER_VOICE_PROFILES = {
    k: {"pitch": v["sapi_pitch"], "rate": v["sapi_rate"], "test": v["test"]}
    for k, v in VOICE_STUDIO_PROFILES.items()
}


class VoiceStudioManager:
    """Motor de Google AI Voice Studio y Gemini 3.8 Flash TTS para clonar y diseñar voces de personajes."""

    @staticmethod
    def get_api_key(config=None):
        if config and config.get("gemini_api_key"):
            k = str(config.get("gemini_api_key")).strip()
            if k:
                return k
        if GEMINI_API_KEY:
            return GEMINI_API_KEY.strip()
        return os.environ.get("GEMINI_API_KEY", "").strip()

    @staticmethod
    def get_cache_dir():
        d = os.path.join(os.path.expanduser("~"), ".pinkchan", "voice_studio")
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            d = os.path.join(os.getcwd(), "cache_voice_studio")
            os.makedirs(d, exist_ok=True)
        return d

    @classmethod
    def clean_text_for_speech(cls, raw_text):
        if not raw_text:
            return ""
        clean = re.sub(r'\[JARVIS:[^\]]+\]', '', str(raw_text), flags=re.IGNORECASE)
        clean = re.sub(r'\[[^\]]+\]', '', clean)
        clean = re.sub(r'[:;=8][\-o\*\']?[\)\]\(\[dDpPoO/\\]', '', clean)
        clean = clean.replace("UwU", "").replace("7w7", "").replace("OwO", "").replace("XD", "").strip()
        return clean

    @classmethod
    def create_designed_voice(cls, api_key, skin_name, custom_prompt=None, display_name=None):
        """Crea o clona una voz persistente en Voice Studio usando POST /v1beta/voices."""
        if not api_key:
            return None, None, "Se requiere una Gemini API Key valida."
        prof = VOICE_STUDIO_PROFILES.get(skin_name, VOICE_STUDIO_PROFILES.get("Bocchi"))
        prompt_text = custom_prompt or prof["voice_design_prompt"]
        d_name = display_name or f"PinkChan_{skin_name}"

        url = f"https://generativelanguage.googleapis.com/v1beta/voices?key={api_key}"
        payload = {
            "store": True,
            "voice": {
                "model": "gemini-3.8-flash-tts",
                "type": "prompted",
                "display_name": d_name,
                "gender": prof.get("gender", "female"),
                "language_code": prof.get("language_code", "ja-JP"),
                "prompted": {
                    "input": prompt_text
                }
            }
        }

        try:
            headers = {"Content-Type": "application/json"}
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=35) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                voice_id = resp_json.get("id") or resp_json.get("name")
                sample_data = None
                sample_obj = resp_json.get("sampleAudio") or resp_json.get("sample_audio")
                if sample_obj and isinstance(sample_obj, dict):
                    sample_data = sample_obj.get("data")

                audio_path = None
                if sample_data:
                    audio_bytes = base64.b64decode(sample_data)
                    c_dir = cls.get_cache_dir()
                    audio_path = os.path.join(c_dir, f"preview_{skin_name}.wav")
                    with open(audio_path, "wb") as f:
                        f.write(audio_bytes)

                return voice_id, audio_path, None
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8")
                err_msg = f"HTTP {e.code}: {err_body}"
            except Exception:
                err_msg = f"HTTP {e.code}: {e.reason}"
            return None, None, err_msg
        except Exception as e:
            return None, None, str(e)

    @classmethod
    def _edge_tts_synthesize(cls, text, voice, pitch, rate, out_path):
        """Sintetiza audio neural con Edge TTS (voces de estudio, sin APIs roboticas)."""
        import asyncio
        try:
            import edge_tts
            async def _run():
                comm = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
                await comm.save(out_path)
            asyncio.run(_run())
            return os.path.isfile(out_path) and os.path.getsize(out_path) > 300
        except Exception as e:
            print(f"Edge TTS synthesis error: {e}")
            return False

    @classmethod
    def synthesize_speech(cls, api_key, text, skin_name="Bocchi", config=None, log_cb=None, dub_lang=None):
        """
        Sintetiza la voz del personaje aplicando una canalizacion automatica de PRUEBA Y ERROR (Trial and Error):
        Intento 0: Si es mascota (Pusheen, Hachi, Usagi), reproducir sonidos autenticos de gato y conejo directamente.
        Intento 1: Gemini 3.8 Flash TTS Interactions API (/v1beta/interactions) con estilo vocal y doblaje seleccionado.
        Intento 2: Gemini 2.5 Flash Audio GenerateContent (/v1beta/models/gemini-2.5-flash:generateContent) con rol de doblaje.
        Intento 3: Gemini 2.0 Flash Audio GenerateContent (/v1beta/models/gemini-2.0-flash:generateContent).
        Intento 4: Motor Neuronal Edge TTS (Doblaje Autentico de Alta Fidelidad en Español, Ingles o Japones).
        Intento 5: Banco de voz del personaje (Archivos locales de estudio en sounds/ para el doblaje seleccionado).
        """
        clean = cls.clean_text_for_speech(text)
        if not clean:
            return None, "Texto vacio."

        dub = dub_lang or (config.get("voice_dub_language", "es") if config else "es")
        prof = VOICE_STUDIO_PROFILES.get(skin_name, VOICE_STUDIO_PROFILES.get("Bocchi"))
        dub_info = prof.get(f"dub_{dub}", prof.get("original", prof))

        c_dir = cls.get_cache_dir()

        # -------------------------------------------------------------------------
        # INTENTO 0: Mascotas Animales (Pusheen, Hachi, Usagi)
        # -------------------------------------------------------------------------
        is_animal = prof.get("is_animal", False) or skin_name in ("Pusheen", "Hachi", "Usagi")
        if is_animal:
            clip_order = ["greeting", "poke", "action", "idle", "fling"]
            suffixes = [f"_{dub}", ""] if dub in ("es", "en") else ["", "_es", "_en"]
            for clip_n in clip_order:
                for sfx in suffixes:
                    f_clip = os.path.join(BASE_DIR, "sounds", skin_name, f"{clip_n}{sfx}.mp3")
                    if os.path.isfile(f_clip):
                        if log_cb:
                            log_cb(f"[+] Sonido animal autentico reproducido para {skin_name}: {clip_n}{sfx}.mp3")
                        return f_clip, None

        custom_ids = config.get("voice_studio_ids", {}) if config else {}
        voice_id = custom_ids.get(skin_name) or prof.get("voice_id")
        voice_target = voice_id if voice_id else prof.get("prebuilt", "Kore")

        import hashlib
        h = hashlib.md5((clean + skin_name + str(voice_target) + str(dub)).encode("utf-8")).hexdigest()[:10]
        dub_label = "Doblaje Español (Latino)" if dub == "es" else ("English Dub" if dub == "en" else "Voz Original")

        # -------------------------------------------------------------------------
        # INTENTO 1: Gemini 3.8 Flash TTS Interactions API
        # -------------------------------------------------------------------------
        if api_key:
            if log_cb:
                log_cb(f"[*] Intento 1: Gemini 3.8 Flash TTS ({voice_target} - {dub_label})...")
            try:
                url_interact = f"https://generativelanguage.googleapis.com/v1beta/interactions?key={api_key}"
                payload_interact = {
                    "model": "gemini-3.8-flash-tts",
                    "input": [{
                        "type": "user_input",
                        "content": [{
                            "type": "text",
                            "text": clean,
                            "annotations": [{
                                "type": "speech_metadata",
                                "style": dub_info.get("style", prof.get("style", "conversational"))
                            }]
                        }]
                    }],
                    "response_format": {"type": "audio", "mime_type": "audio/wav"},
                    "generation_config": {
                        "speech_config": [{"voice": voice_target}]
                    }
                }
                headers = {"Content-Type": "application/json"}
                data_bytes = json.dumps(payload_interact).encode("utf-8")
                req = urllib.request.Request(url_interact, data=data_bytes, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=18) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    audio_b64 = None
                    out_aud = resp_json.get("output_audio") or resp_json.get("outputAudio")
                    if out_aud and isinstance(out_aud, dict):
                        audio_b64 = out_aud.get("data")
                    if not audio_b64:
                        for st in resp_json.get("steps", []):
                            for co in st.get("content", []):
                                if co.get("type") == "audio" and co.get("data"):
                                    audio_b64 = co.get("data")
                                    break
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        out_path = os.path.join(c_dir, f"tts_{skin_name}_{dub}_gem38_{h}.wav")
                        with open(out_path, "wb") as f:
                            f.write(audio_bytes)
                        if log_cb:
                            log_cb(f"[+] Gemini 3.8 Flash TTS exitoso ({dub_label})!")
                        return out_path, None
            except Exception as e_i:
                if log_cb:
                    log_cb(f"[~] Intento 1 omitido ({e_i}). Probando Gemini 2.5 Flash...")

            # -------------------------------------------------------------------------
            # INTENTO 2: Gemini 2.5 Flash Audio GenerateContent
            # -------------------------------------------------------------------------
            if log_cb:
                log_cb(f"[*] Intento 2: Gemini 2.5 Flash GenerateContent (Audio Modality - {dub_label})...")
            try:
                url_g25 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                prompt_actor = f"You are {prof.get('display_name', skin_name)}. Style: {dub_info.get('style')}. {dub_info.get('prompt')}. Deliver this line in authentic character acting: {clean}"
                payload_g25 = {
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": prompt_actor}]
                    }],
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {
                                    "voiceName": prof.get("prebuilt", "Kore")
                                }
                            }
                        }
                    }
                }
                headers = {"Content-Type": "application/json"}
                data_bytes = json.dumps(payload_g25).encode("utf-8")
                req = urllib.request.Request(url_g25, data=data_bytes, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=18) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    candidates = resp_json.get("candidates", [])
                    audio_b64 = None
                    if candidates:
                        for p in candidates[0].get("content", {}).get("parts", []):
                            inline = p.get("inlineData") or p.get("inline_data")
                            if inline and inline.get("data"):
                                audio_b64 = inline.get("data")
                                break
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        out_path = os.path.join(c_dir, f"tts_{skin_name}_{dub}_gem25_{h}.wav")
                        with open(out_path, "wb") as f:
                            f.write(audio_bytes)
                        if log_cb:
                            log_cb(f"[+] Gemini 2.5 Flash Audio exitoso ({dub_label})!")
                        return out_path, None
            except Exception as e_g25:
                if log_cb:
                    log_cb(f"[~] Intento 2 omitido ({e_g25}). Probando Gemini 2.0 Flash...")

            # -------------------------------------------------------------------------
            # INTENTO 3: Gemini 2.0 Flash Audio GenerateContent
            # -------------------------------------------------------------------------
            try:
                url_g20 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                prompt_actor = f"You are {prof.get('display_name', skin_name)}. Style: {dub_info.get('style')}. {dub_info.get('prompt')}. Deliver line in character voice: {clean}"
                payload_g20 = {
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": prompt_actor}]
                    }],
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {
                                    "voiceName": prof.get("prebuilt", "Kore")
                                }
                            }
                        }
                    }
                }
                headers = {"Content-Type": "application/json"}
                data_bytes = json.dumps(payload_g20).encode("utf-8")
                req = urllib.request.Request(url_g20, data=data_bytes, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=18) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    candidates = resp_json.get("candidates", [])
                    audio_b64 = None
                    if candidates:
                        for p in candidates[0].get("content", {}).get("parts", []):
                            inline = p.get("inlineData") or p.get("inline_data")
                            if inline and inline.get("data"):
                                audio_b64 = inline.get("data")
                                break
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        out_path = os.path.join(c_dir, f"tts_{skin_name}_{dub}_gem20_{h}.wav")
                        with open(out_path, "wb") as f:
                            f.write(audio_bytes)
                        if log_cb:
                            log_cb(f"[+] Gemini 2.0 Flash Audio exitoso ({dub_label})!")
                        return out_path, None
            except Exception as e_g20:
                if log_cb:
                    log_cb(f"[~] Intento 3 omitido ({e_g20}). Pasando a Motor Neuronal Edge TTS...")

        # -------------------------------------------------------------------------
        # INTENTO 4: Motor Neuronal Edge TTS (Doblaje Autentico de Alta Fidelidad)
        # -------------------------------------------------------------------------
        if log_cb:
            log_cb(f"[*] Intento 4: Sintetizando con Motor Neuronal Edge TTS ({dub_label})...")
        try:
            edge_v = dub_info.get("edge_voice", "es-MX-DaliaNeural" if dub == "es" else ("en-US-AnaNeural" if dub == "en" else "ja-JP-NanamiNeural"))
            edge_p = dub_info.get("edge_pitch", "+0Hz")
            edge_r = dub_info.get("edge_rate", "+0%")
            out_neural = os.path.join(c_dir, f"tts_{skin_name}_{dub}_edge_{h}.mp3")
            if os.path.isfile(out_neural) and os.path.getsize(out_neural) > 500:
                if log_cb:
                    log_cb(f"[+] Audio neuronal en cache reutilizado ({dub_label})!")
                return out_neural, None
            if cls._edge_tts_synthesize(clean, edge_v, edge_p, edge_r, out_neural):
                if log_cb:
                    log_cb(f"[+] Doblaje Neuronal Autentico ({edge_v}) generado con exito!")
                return out_neural, None
        except Exception as e_ed:
            if log_cb:
                log_cb(f"[~] Intento 4 Edge TTS omitido: {e_ed}. Verificando banco de audios...")

        # -------------------------------------------------------------------------
        # INTENTO 5: Banco de Voz del Personaje (Archivos locales de estudio en sounds/)
        # -------------------------------------------------------------------------
        clip_suffixes = [f"_{dub}", ""] if dub in ("es", "en") else ["", "_es", "_en"]
        for sub in [skin_name, skin_name.lower(), skin_name.capitalize()]:
            for clip_n in ["greeting", "idle", "poke", "action", "fling"]:
                for sfx in clip_suffixes:
                    f_clip = os.path.join(BASE_DIR, "sounds", sub, f"{clip_n}{sfx}.mp3")
                    if os.path.isfile(f_clip):
                        if log_cb:
                            log_cb(f"[+] Banco de voz de estudio aplicado ({skin_name}/{clip_n}{sfx}.mp3)!")
                        return f_clip, None

        return None, "No se pudo sintetizar audio en ninguna de las fases."

    @classmethod
    def play_wav(cls, wav_path):
        """Reproduce un archivo de audio (WAV o MP3) de forma asincrona."""
        return play_audio_file(wav_path)

    @classmethod
    def play_audio(cls, audio_path):
        """Reproduce un archivo de audio (WAV o MP3) de forma asincrona."""
        return play_audio_file(audio_path)


class JarvisTTS:
    """Motor dual de síntesis de voz: Google Voice Studio AI (Gemini 3.8 Flash TTS) y Windows SAPI con prosodia."""
    def __init__(self, config=None):
        self.config = config if config is not None else {}
        self._queue = queue.Queue()
        self._voices_cache = []
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def get_voices(self):
        if not SAPI_AVAILABLE:
            return ["No disponible (SAPI ausente)"]
        if self._voices_cache:
            return self._voices_cache
        try:
            pythoncom.CoInitialize()
            sp = win32com.client.Dispatch("SAPI.SpVoice")
            voices = sp.GetVoices()
            v_list = []
            for i in range(voices.Count):
                try:
                    desc = voices.Item(i).GetDescription()
                    v_list.append(desc)
                except Exception:
                    v_list.append(f"Voz {i+1}")
            self._voices_cache = v_list if v_list else ["Voz predeterminada de Windows"]
            return self._voices_cache
        except Exception:
            return ["Voz predeterminada de Windows"]

    def _worker(self):
        sp = None
        if SAPI_AVAILABLE:
            try:
                pythoncom.CoInitialize()
                sp = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception as e:
                print(f"SAPI Init Warning: {e}")

        while True:
            item = self._queue.get()
            if not item:
                continue
            if not self.config.get("tts_enabled", False):
                continue
            try:
                skin_name = "Bocchi"
                if isinstance(item, (tuple, list)):
                    raw_text = str(item[0])
                    if len(item) > 1 and item[1]:
                        skin_name = str(item[1])
                else:
                    raw_text = str(item)

                clean = VoiceStudioManager.clean_text_for_speech(raw_text)
                if not clean:
                    continue

                engine_mode = self.config.get("tts_engine", "voice_studio")
                api_key = VoiceStudioManager.get_api_key(self.config)

                played = False
                # 1. Intentar síntesis con Google Voice Studio / Motor Fonetico Anime (siempre prioritario en modo voice_studio)
                if engine_mode in ("voice_studio", "anime_authentic", "voice_studio_ai"):
                    try:
                        dub_lang = self.config.get("voice_dub_language", "es")
                        audio_file, err = VoiceStudioManager.synthesize_speech(api_key, clean, skin_name, self.config, dub_lang=dub_lang)
                        if audio_file and os.path.isfile(audio_file):
                            VoiceStudioManager.play_audio(audio_file)
                            played = True
                    except Exception as err_vs:
                        print(f"Voice Studio TTS error: {err_vs}")

                # 2. Si es mascota animal, NUNCA usar SAPI humano: reproducir siempre sonido auténtico de animal
                prof = VOICE_STUDIO_PROFILES.get(skin_name, VOICE_STUDIO_PROFILES.get("Bocchi", {}))
                if prof.get("is_animal", False) or skin_name in ("Pusheen", "Hachi", "Usagi"):
                    if not played:
                        animal_clip = VoiceStudioManager.get_mascot_animal_sound(skin_name, clean)
                        if animal_clip and os.path.isfile(animal_clip):
                            VoiceStudioManager.play_audio(animal_clip)
                            played = True

                # 3. SOLO si el usuario selecciono explicitamente modo SAPI o si no se pudo reproducir nada
                if not played and engine_mode == "sapi" and SAPI_AVAILABLE and sp is not None:
                    user_rate_offset = int(self.config.get("tts_rate", 0))
                    user_pitch_offset = int(self.config.get("tts_pitch", 0))
                    vol = int(self.config.get("tts_volume", 100))
                    sp.Volume = max(0, min(100, vol))

                    v_idx = int(self.config.get("tts_voice_idx", 0))
                    voices = sp.GetVoices()
                    if 0 <= v_idx < voices.Count:
                        sp.Voice = voices.Item(v_idx)

                    char_pitch_num = max(-60, min(70, prof.get("sapi_pitch", 0) + (user_pitch_offset * 3)))
                    char_rate_num = max(-50, min(60, prof.get("sapi_rate", 0) + (user_rate_offset * 4)))

                    sign_pitch = f"{char_pitch_num:+d}%"
                    sign_rate = f"{char_rate_num:+d}%"

                    escaped = clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                    ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-MX"><prosody pitch="{sign_pitch}" rate="{sign_rate}">{escaped}</prosody></speak>'
                    try:
                        sp.Speak(ssml, 8)
                    except Exception:
                        sapi_rate = max(-10, min(10, user_rate_offset + int(prof.get("sapi_rate", 0) / 8)))
                        sp.Rate = sapi_rate
                        sp.Speak(clean)
            except Exception as e:
                print(f"TTS Speak Worker Error: {e}")

    def speak(self, text_to_speak, skin=None):
        if self.config.get("tts_enabled", False):
            self._queue.put((text_to_speak, skin))


class VoiceStudioWindow:
    """Ventana completa de Google Voice Studio para clonar, diseñar y audicionar voces de los personajes."""
    def __init__(self, parent_root, theme_manager, shimeji_ref=None):
        self.parent = parent_root
        self.theme = theme_manager
        self.shimeji = shimeji_ref
        self.config = self.shimeji.config if self.shimeji and hasattr(self.shimeji, "config") else {}
        self.win = None
        self._build_window()

    def _build_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("[*] Voice Studio - Clonador de Voces de Personajes")
        self.win.geometry("640x780")
        self.win.minsize(580, 700)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", getattr(self.theme, "opacity", 0.95))
        self.win.configure(bg=self.theme.bg)

        # Header
        header = tk.Frame(self.win, bg=self.theme.surface, pady=12, padx=16)
        header.pack(fill=tk.X)

        tk.Label(header, text="[*] GOOGLE VOICE STUDIO (GEMINI 3.8 FLASH TTS)",
                 font=(self.theme.font_family, self.theme.font_size + 2, "bold"),
                 bg=self.theme.surface, fg=self.theme.accent).pack(anchor="w")
        tk.Label(header, text="Clona, disena y audiciona las voces oficiales de los personajes.",
                 font=(self.theme.font_family, self.theme.font_size - 2),
                 bg=self.theme.surface, fg=self.theme.text_dim).pack(anchor="w")

        btn_aistudio = tk.Button(header, text="[^] Abrir Google AI Studio Voice Studio",
                                 bg=self.theme.surface_variant, fg=self.theme.accent,
                                 font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                 command=lambda: webbrowser.open("https://aistudio.google.com/generate-speech"))
        btn_aistudio.pack(anchor="e", pady=(4, 0))

        content = tk.Frame(self.win, bg=self.theme.bg, padx=16, pady=10)
        content.pack(fill=tk.BOTH, expand=True)

        # 1. Configuración de API Key y Modo
        f_top = tk.LabelFrame(content, text="1. Configuracion de Motor y API", bg=self.theme.surface,
                              fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold"), padx=10, pady=8)
        f_top.pack(fill=tk.X, pady=(0, 10))

        row_api = tk.Frame(f_top, bg=self.theme.surface)
        row_api.pack(fill=tk.X, pady=2)
        tk.Label(row_api, text="Gemini API Key:", bg=self.theme.surface, fg=self.theme.text).pack(side=tk.LEFT)
        self.var_api_key = tk.StringVar(value=VoiceStudioManager.get_api_key(self.config))
        self.ent_api_key = tk.Entry(row_api, textvariable=self.var_api_key, bg=self.theme.entry_bg, fg=self.theme.text, show="*")
        self.ent_api_key.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        self.btn_show_key = tk.Button(row_api, text="Ver", bg=self.theme.surface_variant, fg=self.theme.text,
                                      command=self._toggle_show_key, width=4)
        self.btn_show_key.pack(side=tk.LEFT, padx=2)

        row_engine = tk.Frame(f_top, bg=self.theme.surface)
        row_engine.pack(fill=tk.X, pady=(6, 2))
        tk.Label(row_engine, text="Motor de Voz Activo:", bg=self.theme.surface, fg=self.theme.text).pack(side=tk.LEFT)
        self.var_engine_mode = tk.StringVar(value=self.config.get("tts_engine", "voice_studio"))
        tk.Radiobutton(row_engine, text="Voice Studio AI (Gemini 3.8 Flash TTS)", variable=self.var_engine_mode,
                       value="voice_studio", bg=self.theme.surface, fg=self.theme.accent, selectcolor=self.theme.surface_variant,
                       activebackground=self.theme.surface).pack(side=tk.LEFT, padx=8)
        tk.Radiobutton(row_engine, text="SAPI Local (Windows)", variable=self.var_engine_mode,
                       value="sapi", bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant,
                       activebackground=self.theme.surface).pack(side=tk.LEFT)

        # 2. Selección de Personaje y Perfil Vocal
        f_char = tk.LabelFrame(content, text="2. Perfil Vocal del Personaje", bg=self.theme.surface,
                               fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold"), padx=10, pady=8)
        f_char.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        row_char_select = tk.Frame(f_char, bg=self.theme.surface)
        row_char_select.pack(fill=tk.X, pady=2)
        tk.Label(row_char_select, text="Seleccionar Personaje:", bg=self.theme.surface, fg=self.theme.text).pack(side=tk.LEFT)

        char_names = list(VOICE_STUDIO_PROFILES.keys())
        cur_skin = getattr(self.shimeji, "current_skin", "Bocchi") if self.shimeji else "Bocchi"
        if cur_skin not in char_names:
            cur_skin = "Bocchi"

        self.cbo_character = ttk.Combobox(row_char_select, values=char_names, state="readonly", width=16)
        self.cbo_character.set(cur_skin)
        self.cbo_character.pack(side=tk.LEFT, padx=6)
        self.cbo_character.bind("<<ComboboxSelected>>", self._on_character_changed)

        self.lbl_char_title = tk.Label(row_char_select, text=f"[{VOICE_STUDIO_PROFILES[cur_skin]['display_name']}]",
                                       bg=self.theme.surface, fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold"))
        self.lbl_char_title.pack(side=tk.LEFT, padx=4)

        row_dub = tk.Frame(f_char, bg=self.theme.surface)
        row_dub.pack(fill=tk.X, pady=(4, 6))
        tk.Label(row_dub, text="Doblaje / Idioma:", bg=self.theme.surface, fg=self.theme.text, font=(self.theme.font_family, self.theme.font_size, "bold")).pack(side=tk.LEFT)
        self.var_dub_lang = tk.StringVar(value=self.config.get("voice_dub_language", "es"))
        tk.Radiobutton(row_dub, text="Dub Español (Latino)", variable=self.var_dub_lang, value="es",
                       command=self._on_dub_changed, bg=self.theme.surface, fg=self.theme.accent, selectcolor=self.theme.surface_variant,
                       activebackground=self.theme.surface).pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(row_dub, text="Dub English", variable=self.var_dub_lang, value="en",
                       command=self._on_dub_changed, bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant,
                       activebackground=self.theme.surface).pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(row_dub, text="Voz Original", variable=self.var_dub_lang, value="original",
                       command=self._on_dub_changed, bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant,
                       activebackground=self.theme.surface).pack(side=tk.LEFT, padx=6)

        # Prompt de diseño en Voice Studio
        tk.Label(f_char, text="Prompt de Diseno de Voz (Voice Studio Persona Description):",
                 bg=self.theme.surface, fg=self.theme.text).pack(anchor="w", pady=(6, 2))
        self.txt_prompt = scrolledtext.ScrolledText(f_char, height=4, bg=self.theme.entry_bg, fg=self.theme.text,
                                                    font=(self.theme.font_family, self.theme.font_size - 1))
        self.txt_prompt.pack(fill=tk.X, pady=(0, 6))

        # Estilo de actuación e ID de voz clonada
        row_voice_meta = tk.Frame(f_char, bg=self.theme.surface)
        row_voice_meta.pack(fill=tk.X, pady=2)

        tk.Label(row_voice_meta, text="Estilo de actuacion:", bg=self.theme.surface, fg=self.theme.text).grid(row=0, column=0, sticky="w")
        self.var_style = tk.StringVar()
        self.ent_style = tk.Entry(row_voice_meta, textvariable=self.var_style, bg=self.theme.entry_bg, fg=self.theme.text, width=28)
        self.ent_style.grid(row=0, column=1, sticky="w", padx=4, pady=2)

        tk.Label(row_voice_meta, text="Fallback Prebuilt:", bg=self.theme.surface, fg=self.theme.text).grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.var_prebuilt = tk.StringVar()
        self.cbo_prebuilt = ttk.Combobox(row_voice_meta, textvariable=self.var_prebuilt, values=["Kore", "Puck", "Aoede", "Fenrir"], state="readonly", width=8)
        self.cbo_prebuilt.grid(row=0, column=3, sticky="w", padx=4, pady=2)

        tk.Label(row_voice_meta, text="Voice ID Clonada:", bg=self.theme.surface, fg=self.theme.text).grid(row=1, column=0, sticky="w")
        self.var_voice_id = tk.StringVar()
        self.ent_voice_id = tk.Entry(row_voice_meta, textvariable=self.var_voice_id, bg=self.theme.entry_bg, fg=self.theme.text, width=28)
        self.ent_voice_id.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        tk.Label(row_voice_meta, text="Dialogo de prueba:", bg=self.theme.surface, fg=self.theme.text).grid(row=2, column=0, sticky="w")
        self.var_test_dialogue = tk.StringVar()
        self.ent_test_dialogue = tk.Entry(row_voice_meta, textvariable=self.var_test_dialogue, bg=self.theme.entry_bg, fg=self.theme.text)
        self.ent_test_dialogue.grid(row=2, column=1, columnspan=3, sticky="ew", padx=4, pady=2)
        row_voice_meta.columnconfigure(1, weight=1)

        # Botones de Acción de Voice Studio
        row_actions = tk.Frame(f_char, bg=self.theme.surface)
        row_actions.pack(fill=tk.X, pady=(8, 4))

        self.btn_clone_voice = tk.Button(row_actions, text="[*] Clonar en Voice Studio", bg=self.theme.accent,
                                         fg=self.theme.accent_text, font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                         command=self._clone_current_voice)
        self.btn_clone_voice.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_test_speech = tk.Button(row_actions, text="[♫] Probar Voz Actual", bg=self.theme.surface_variant,
                                         fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                         command=self._test_current_voice)
        self.btn_test_speech.pack(side=tk.LEFT, padx=4)

        self.btn_benchmark = tk.Button(row_actions, text="[★] Prueba y Error de Modelos", bg=self.theme.surface_variant,
                                       fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                       command=self._benchmark_all_models)
        self.btn_benchmark.pack(side=tk.LEFT, padx=4)

        self.btn_clone_all = tk.Button(row_actions, text="[+] Clonar Todas", bg=self.theme.surface_variant,
                                       fg=self.theme.text, font=(self.theme.font_family, self.theme.font_size - 1),
                                       command=self._clone_all_voices)
        self.btn_clone_all.pack(side=tk.LEFT, padx=4)

        # 3. Consola de Registro y Estado
        f_log = tk.LabelFrame(content, text="3. Registro de Operaciones y Audicion", bg=self.theme.surface,
                              fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold"), padx=10, pady=6)
        f_log.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.txt_log = scrolledtext.ScrolledText(f_log, height=5, bg=self.theme.entry_bg, fg=self.theme.text,
                                                 font=(self.theme.font_family, self.theme.font_size - 2))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # Footer
        footer = tk.Frame(self.win, bg=self.theme.surface, pady=8, padx=16)
        footer.pack(fill=tk.X)

        btn_save = tk.Button(footer, text="[✓] Guardar y Aplicar como Voz del Shimeji", bg=self.theme.accent,
                             fg=self.theme.accent_text, font=(self.theme.font_family, self.theme.font_size, "bold"),
                             command=self._save_and_apply)
        btn_save.pack(side=tk.RIGHT, padx=4)

        btn_close = tk.Button(footer, text="Cerrar", bg=self.theme.surface_variant, fg=self.theme.text,
                              command=self.win.destroy)
        btn_close.pack(side=tk.RIGHT, padx=4)

        self._load_character_data(cur_skin)
        self._log(f"[+] Voice Studio inicializado. Personaje activo: {cur_skin}")

    def _toggle_show_key(self):
        if self.ent_api_key.cget("show") == "":
            self.ent_api_key.configure(show="*")
            self.btn_show_key.configure(text="Ver")
        else:
            self.ent_api_key.configure(show="")
            self.btn_show_key.configure(text="Ocultar")

    def _on_character_changed(self, event=None):
        skin = self.cbo_character.get()
        self._load_character_data(skin)

    def _on_dub_changed(self):
        skin = self.cbo_character.get()
        self.config["voice_dub_language"] = self.var_dub_lang.get()
        save_config(self.config)
        self._load_character_data(skin)
        self._log(f"[*] Doblaje seleccionado: {self.var_dub_lang.get().upper()}")

    def _load_character_data(self, skin):
        prof = VOICE_STUDIO_PROFILES.get(skin, VOICE_STUDIO_PROFILES.get("Bocchi"))
        dub = self.var_dub_lang.get() if hasattr(self, "var_dub_lang") else self.config.get("voice_dub_language", "es")
        dub_info = prof.get(f"dub_{dub}", prof.get("original", prof))

        dub_tag = "ES-DUB" if dub == "es" else ("EN-DUB" if dub == "en" else "ORIGINAL")
        self.lbl_char_title.configure(text=f"[{prof['display_name']} - {dub_tag}]")
        self.txt_prompt.delete("1.0", tk.END)
        self.txt_prompt.insert(tk.END, dub_info.get("prompt", prof["voice_design_prompt"]))
        self.var_style.set(dub_info.get("style", prof["style"]))
        self.var_prebuilt.set(prof.get("prebuilt", "Kore"))

        custom_ids = self.config.get("voice_studio_ids", {})
        c_id = custom_ids.get(skin, "")
        self.var_voice_id.set(c_id)
        self.var_test_dialogue.set(dub_info.get("test", prof["test"]))

    def _log(self, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{ts}] {msg}\n")
        self.txt_log.see(tk.END)

    def _clone_current_voice(self):
        api_key = self.var_api_key.get().strip()
        if not api_key:
            messagebox.showwarning("API Key", "Por favor ingresa tu Gemini API Key para clonar voces con Voice Studio.")
            return

        skin = self.cbo_character.get()
        prompt = self.txt_prompt.get("1.0", tk.END).strip()
        self.btn_clone_voice.configure(state=tk.DISABLED, text="Clonando...")
        self._log(f"[*] Iniciando clonacion de voz para '{skin}' en Google Voice Studio...")

        def run_thread():
            v_id, audio_path, err = VoiceStudioManager.create_designed_voice(api_key, skin, prompt)
            self.win.after(0, lambda: self._on_clone_finished(skin, v_id, audio_path, err))

        threading.Thread(target=run_thread, daemon=True).start()

    def _on_clone_finished(self, skin, v_id, audio_path, err):
        self.btn_clone_voice.configure(state=tk.NORMAL, text="[*] Clonar en Voice Studio")
        if err:
            self._log(f"[!] Error clonando voz de {skin}: {err}")
            messagebox.showerror("Error Voice Studio", f"Fallo al clonar voz de {skin}:\n{err}")
        else:
            self.var_voice_id.set(v_id or "voice_created")
            custom_ids = dict(self.config.get("voice_studio_ids", {}))
            custom_ids[skin] = v_id
            self.config["voice_studio_ids"] = custom_ids
            save_config(self.config)
            self._log(f"[+] Voz clonada exitosamente para '{skin}'! Voice ID: {v_id}")
            if audio_path:
                self._log(f"[♫] Reproduciendo audicion de prueba ({os.path.basename(audio_path)})...")
                VoiceStudioManager.play_audio(audio_path)

    def _test_current_voice(self):
        api_key = self.var_api_key.get().strip()
        skin = self.cbo_character.get()
        dub = self.var_dub_lang.get()
        dialogue = self.var_test_dialogue.get().strip()
        if not dialogue:
            dialogue = VOICE_STUDIO_PROFILES.get(skin, {}).get("test", "Hola!")

        self.btn_test_speech.configure(state=tk.DISABLED, text="Generando...")
        self._log(f"[*] Iniciando prueba y error para la voz de '{skin}' ({dub.upper()})...")

        def run_thread():
            tmp_cfg = dict(self.config)
            tmp_cfg["gemini_api_key"] = api_key
            tmp_cfg["voice_dub_language"] = dub
            custom_ids = dict(tmp_cfg.get("voice_studio_ids", {}))
            v_id_entry = self.var_voice_id.get().strip()
            if v_id_entry:
                custom_ids[skin] = v_id_entry
            tmp_cfg["voice_studio_ids"] = custom_ids

            audio_path, err = VoiceStudioManager.synthesize_speech(
                api_key, dialogue, skin, tmp_cfg,
                log_cb=lambda msg: self.win.after(0, lambda m=msg: self._log(m)),
                dub_lang=dub
            )
            self.win.after(0, lambda: self._on_test_finished(skin, audio_path, err))

        threading.Thread(target=run_thread, daemon=True).start()

    def _on_test_finished(self, skin, audio_path, err):
        self.btn_test_speech.configure(state=tk.NORMAL, text="[♫] Probar Voz Actual")
        if err:
            self._log(f"[!] Error sintetizando voz de {skin}: {err}")
            messagebox.showerror("Error Sintesis", f"Fallo al sintetizar voz de {skin}:\n{err}")
        else:
            self._log(f"[♫] Audio obtenido exitosamente ({os.path.basename(audio_path)}). Reproduciendo...")
            VoiceStudioManager.play_audio(audio_path)

    def _benchmark_all_models(self):
        api_key = self.var_api_key.get().strip()
        skin = self.cbo_character.get()
        dub = self.var_dub_lang.get()
        dialogue = self.var_test_dialogue.get().strip() or "Konnichiwa! Esta es una prueba de voz."
        self.btn_benchmark.configure(state=tk.DISABLED, text="Evaluando...")
        self._log(f"==================================================")
        self._log(f"[*] INICIANDO PRUEBA Y ERROR EXHAUSTIVA DE MODELOS PARA '{skin}' ({dub.upper()})")
        self._log(f"==================================================")

        def run_benchmark_thread():
            # Fase 1: Probar Gemini 3.8 Flash TTS
            if api_key:
                t0 = time.time()
                self.win.after(0, lambda: self._log("[*] Probando Nivel 1: Gemini 3.8 Flash TTS Interactions API..."))
                try:
                    p1 = {
                        "model": "gemini-3.8-flash-tts",
                        "input": [{"type": "user_input", "content": [{"type": "text", "text": dialogue, "annotations": [{"type": "speech_metadata", "style": "conversational"}]}]}],
                        "response_format": {"type": "audio", "mime_type": "audio/wav"},
                        "generation_config": {"speech_config": [{"voice": VOICE_STUDIO_PROFILES[skin].get("prebuilt", "Kore")}]}
                    }
                    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/interactions?key={api_key}",
                                                 data=json.dumps(p1).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=15) as r:
                        dt = round((time.time() - t0) * 1000)
                        self.win.after(0, lambda ms=dt: self._log(f"  [✓] Nivel 1 (Gemini 3.8 Flash TTS): DISPONIBLE ({ms} ms)"))
                except Exception as e:
                    self.win.after(0, lambda err=str(e): self._log(f"  [~] Nivel 1 no disponible: {err}"))

                # Fase 2: Probar Gemini 2.5 Flash Audio
                t0 = time.time()
                self.win.after(0, lambda: self._log("[*] Probando Nivel 2: Gemini 2.5 Flash Audio GenerateContent..."))
                try:
                    p2 = {
                        "contents": [{"role": "user", "parts": [{"text": f"Say in character voice: {dialogue}"}]}],
                        "generationConfig": {
                            "responseModalities": ["AUDIO"],
                            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE_STUDIO_PROFILES[skin].get("prebuilt", "Kore")}}}
                        }
                    }
                    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                                                 data=json.dumps(p2).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=15) as r:
                        dt = round((time.time() - t0) * 1000)
                        self.win.after(0, lambda ms=dt: self._log(f"  [✓] Nivel 2 (Gemini 2.5 Flash Audio): DISPONIBLE ({ms} ms)"))
                except Exception as e:
                    self.win.after(0, lambda err=str(e): self._log(f"  [~] Nivel 2 no disponible: {err}"))
            else:
                self.win.after(0, lambda: self._log("[!] Sin Gemini API Key. Evaluando motores locales y gratuitos..."))

            # Fase 3: Motor Neuronal Edge-TTS / Vocalizacion Auténtica de Mascota
            t0 = time.time()
            prof = VOICE_STUDIO_PROFILES.get(skin, {})
            is_animal = prof.get("is_animal", False) or skin in ("Pusheen", "Hachi", "Usagi")
            if is_animal:
                self.win.after(0, lambda: self._log(f"[*] Probando Nivel 3: Vocalizacion Autentica de Mascota ({skin})..."))
                c = VoiceStudioManager.get_mascot_animal_sound(skin, dialogue)
                dt = round((time.time() - t0) * 1000)
                if c and os.path.isfile(c):
                    bname = os.path.basename(c)
                    self.win.after(0, lambda ms=dt, p=bname: self._log(f"  [✓] Nivel 3 (Mascota {skin}): VOCALIZACION REAL ({p}) ({ms} ms)"))
                else:
                    self.win.after(0, lambda: self._log("  [!] Nivel 3: Sonido de mascota no encontrado"))
            else:
                self.win.after(0, lambda: self._log("[*] Probando Nivel 3: Motor Neuronal Edge-TTS (Voz Caracterizada)..."))
                try:
                    t_audio = VoiceStudioManager._edge_tts_synthesize(dialogue, skin, dub)
                    dt = round((time.time() - t0) * 1000)
                    if t_audio and os.path.isfile(t_audio):
                        self.win.after(0, lambda ms=dt: self._log(f"  [✓] Nivel 3 (Edge-TTS Neuronal): EXCELENTE ({ms} ms)"))
                    else:
                        self.win.after(0, lambda: self._log("  [~] Nivel 3 no disponible"))
                except Exception as e:
                    self.win.after(0, lambda err=str(e): self._log(f"  [~] Nivel 3 error: {err}"))

            # Fase 4: Banco de Audios de Personaje
            self.win.after(0, lambda: self._log("[*] Probando Nivel 4: Banco de Audios Locales (sounds/)..."))
            clip_found = False
            suffixes = [f"_{dub}", ""] if dub in ("es", "en") else ["", "_es", "_en"]
            for c_name in ["greeting", "poke", "idle", "fling", "action"]:
                for sub in [skin, skin.lower(), skin.capitalize()]:
                    for sfx in suffixes:
                        f_c = os.path.join(BASE_DIR, "sounds", sub, f"{c_name}{sfx}.mp3")
                        if os.path.isfile(f_c):
                            clip_found = True
                            break
            if clip_found:
                self.win.after(0, lambda: self._log(f"  [✓] Nivel 4 (Audios Reales {skin} - {dub.upper()}): LISTO Y VINCULADO"))
            else:
                self.win.after(0, lambda: self._log("  [!] Nivel 4 no encontrado"))

            # Ejecutar síntesis final y reproducir resultado optimo
            self.win.after(0, lambda: self._log("[*] Generando y reproduciendo la mejor voz calibrada..."))
            tmp_cfg = dict(self.config)
            tmp_cfg["gemini_api_key"] = api_key
            tmp_cfg["voice_dub_language"] = dub
            best_audio, err = VoiceStudioManager.synthesize_speech(api_key, dialogue, skin, tmp_cfg,
                                                                   log_cb=lambda msg: self.win.after(0, lambda m=msg: self._log(m)),
                                                                   dub_lang=dub)
            if best_audio:
                VoiceStudioManager.play_audio(best_audio)
                self.win.after(0, lambda: self._log(f"[✓] PRUEBA Y ERROR CONCLUIDA CON EXITO. Voz reproducida."))
            else:
                self.win.after(0, lambda: self._log(f"[!] Error al sintetizar: {err}"))
            self.win.after(0, lambda: self.btn_benchmark.configure(state=tk.NORMAL, text="[★] Prueba y Error de Modelos"))

        threading.Thread(target=run_benchmark_thread, daemon=True).start()

    def _clone_all_voices(self):
        api_key = self.var_api_key.get().strip()
        if not api_key:
            messagebox.showwarning("API Key", "Por favor ingresa tu Gemini API Key para clonar todas las voces.")
            return

        if not messagebox.askyesno("Clonar Todas las Voces",
                                   "¿Deseas clonar las 9 voces de personajes usando Google Voice Studio ahora?"):
            return

        self.btn_clone_all.configure(state=tk.DISABLED, text="Clonando todas...")
        self._log("[*] Iniciando proceso por lotes para las 9 voces de personajes...")

        def run_thread():
            chars = list(VOICE_STUDIO_PROFILES.keys())
            custom_ids = dict(self.config.get("voice_studio_ids", {}))
            for c_name in chars:
                self.win.after(0, lambda c=c_name: self._log(f"[*] Clonando '{c}'..."))
                v_id, audio_path, err = VoiceStudioManager.create_designed_voice(api_key, c_name)
                if v_id:
                    custom_ids[c_name] = v_id
                    self.win.after(0, lambda c=c_name, vid=v_id: self._log(f"[+] '{c}' completado -> {vid}"))
                elif err:
                    self.win.after(0, lambda c=c_name, e=err: self._log(f"[!] '{c}' error: {e}"))
                time.sleep(0.5)

            self.config["voice_studio_ids"] = custom_ids
            save_config(self.config)
            self.win.after(0, lambda: self._on_clone_all_finished())

        threading.Thread(target=run_thread, daemon=True).start()

    def _on_clone_all_finished(self):
        self.btn_clone_all.configure(state=tk.NORMAL, text="[+] Clonar Todas las Voces")
        cur_skin = self.cbo_character.get()
        self._load_character_data(cur_skin)
        self._log("[✓] Proceso de clonacion de todas las voces completado.")
        messagebox.showinfo("Voice Studio", "Se han procesado las voces de todos los personajes en Voice Studio.")

    def _save_and_apply(self):
        api_key = self.var_api_key.get().strip()
        engine_mode = self.var_engine_mode.get()
        skin = self.cbo_character.get()
        dub = self.var_dub_lang.get()
        v_id_entry = self.var_voice_id.get().strip()

        self.config["gemini_api_key"] = api_key
        self.config["tts_engine"] = engine_mode
        self.config["voice_dub_language"] = dub
        self.config["tts_enabled"] = True

        custom_ids = dict(self.config.get("voice_studio_ids", {}))
        if v_id_entry:
            custom_ids[skin] = v_id_entry
        self.config["voice_studio_ids"] = custom_ids

        save_config(self.config)
        if self.shimeji and hasattr(self.shimeji, "tts"):
            self.shimeji.tts.config = self.config

        self._log(f"[✓] Configuracion guardada. Motor activo: {engine_mode}. Doblaje: {dub.upper()}. TTS habilitado.")
        messagebox.showinfo("Voice Studio", f"Configuracion de Voice Studio guardada y aplicada al Shimeji con exito.")



class JarvisWakeWordListener:
    """Escucha pasiva de la palabra clave de activación (Wake Word) mediante PowerShell Speech."""
    def __init__(self, callback_fn, config=None):
        self.callback = callback_fn
        self.config = config if config is not None else {}
        self.running = False
        self.proc = None
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None

    def _run(self):
        wake = self.config.get("wake_word", "oye jarvis").strip().lower()
        ps_code = f"""
        Add-Type -AssemblyName System.Speech
        $sre = New-Object System.Speech.Recognition.SpeechRecognitionEngine
        try {{
            $sre.SetInputToDefaultAudioDevice()
            $gb = New-Object System.Speech.Recognition.GrammarBuilder
            $gb.Append('{wake}')
            $g = New-Object System.Speech.Recognition.Grammar($gb)
            $sre.LoadGrammar($g)
            $dict = New-Object System.Speech.Recognition.DictationGrammar
            $sre.LoadGrammar($dict)
            while ($true) {{
                $res = $sre.Recognize()
                if ($res -ne $null -and $res.Text -ne $null) {{
                    Write-Output $res.Text
                    [Console]::Out.Flush()
                }}
            }}
        }} catch {{
            Write-Output ("ERR: " + $_.Exception.Message)
        }}
        """
        try:
            self.proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            while self.running and self.proc and self.proc.poll() is None:
                line = self.proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    if line.startswith("ERR:"):
                        break
                    if self.callback:
                        self.callback(line)
        except Exception as e:
            print(f"Wake listener error: {e}")
        finally:
            self.running = False


class SpriteImporterWindow:
    """Ventana interactiva para importar skins de Shimeji (.zip o carpeta con sprites)."""
    def __init__(self, parent_root, theme_manager, shimeji_ref=None):
        self.parent = parent_root
        self.theme = theme_manager
        self.shimeji = shimeji_ref
        self.win = None
        self.source_path = None
        self.is_zip = False
        self.frames_found = []
        self.preview_tk = None
        self._build_window()

    def _build_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("[IMPORTADOR] Importar Skin de Shimeji")
        self.win.geometry("520x600")
        self.win.minsize(480, 520)
        self.win.configure(bg=self.theme.surface)
        self.win.attributes("-topmost", True)

        header = tk.Frame(self.win, bg=self.theme.surface_variant, pady=10, padx=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="[*] Importador de Skins Shimeji",
                 font=(self.theme.font_family, self.theme.font_size + 2, "bold"),
                 bg=self.theme.surface_variant, fg=self.theme.accent).pack(anchor="w")
        tk.Label(header, text="Importa archivos .zip o carpetas con frames shime1.png... o 1.png...",
                 font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                 bg=self.theme.surface_variant, fg=self.theme.text_dim).pack(anchor="w")

        content = tk.Frame(self.win, bg=self.theme.surface, padx=14, pady=12)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(content, text="Seleccionar archivo .zip o carpeta con sprites:",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 bg=self.theme.surface, fg=self.theme.text).pack(anchor="w", pady=(0, 6))

        row_sel = tk.Frame(content, bg=self.theme.surface)
        row_sel.pack(fill=tk.X, pady=(0, 10))

        tk.Button(row_sel, text="[+] Elegir archivo .ZIP...",
                  bg=self.theme.surface_variant, fg=self.theme.text,
                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                  command=self._pick_zip, padx=10, pady=5).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(row_sel, text="[+] Elegir Carpeta...",
                  bg=self.theme.surface_variant, fg=self.theme.text,
                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                  command=self._pick_folder, padx=10, pady=5).pack(side=tk.LEFT)

        self.lbl_path = tk.Label(content, text="Ningun archivo seleccionado",
                                 font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                                 bg=self.theme.surface, fg=self.theme.text_dim, anchor="w")
        self.lbl_path.pack(fill=tk.X, pady=(0, 8))

        tk.Label(content, text="Nombre para la nueva Skin / Personaje:",
                 font=(self.theme.font_family, self.theme.font_size, "bold"),
                 bg=self.theme.surface, fg=self.theme.text).pack(anchor="w", pady=(4, 2))
        self.var_skin_name = tk.StringVar(value="")
        self.e_skin_name = tk.Entry(content, textvariable=self.var_skin_name,
                                    bg=self.theme.entry_bg, fg=self.theme.text,
                                    insertbackground=self.theme.accent,
                                    font=(self.theme.font_family, self.theme.font_size))
        self.e_skin_name.pack(fill=tk.X, pady=(0, 10))

        self.prev_card = tk.Frame(content, bg=self.theme.surface_variant,
                                  highlightbackground=self.theme.border, highlightthickness=1, pady=12, padx=12)
        self.prev_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.lbl_preview_canvas = tk.Label(self.prev_card, text="(Sin vista previa cargada)",
                                           bg=self.theme.surface_variant, fg=self.theme.text_dim,
                                           font=(self.theme.font_family, self.theme.font_size))
        self.lbl_preview_canvas.pack(pady=10)

        self.lbl_info = tk.Label(self.prev_card, text="Frames detectados: 0",
                                 bg=self.theme.surface_variant, fg=self.theme.text,
                                 font=(self.theme.font_family, self.theme.font_size - 1, "bold"))
        self.lbl_info.pack()

        row_actions = tk.Frame(self.win, bg=self.theme.surface_variant, pady=10, padx=14)
        row_actions.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_import = tk.Button(row_actions, text="[★] Importar e Instalar Skin",
                                    bg=self.theme.accent, fg=self.theme.accent_text,
                                    font=(self.theme.font_family, self.theme.font_size, "bold"),
                                    padx=14, pady=5, state=tk.DISABLED, command=self._do_import)
        self.btn_import.pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(row_actions, text="Cancelar", bg=self.theme.surface, fg=self.theme.text,
                  command=self.win.destroy, padx=10, pady=5).pack(side=tk.RIGHT)

    def _pick_zip(self):
        f = filedialog.askopenfilename(
            title="Seleccionar archivo ZIP con sprites de Shimeji",
            filetypes=[("Archivos ZIP", "*.zip"), ("Todos los archivos", "*.*")]
        )
        if f:
            self.source_path = f
            self.is_zip = True
            base_name = os.path.splitext(os.path.basename(f))[0]
            clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "", base_name.replace(" ", "_")).capitalize()
            self.var_skin_name.set(clean_name or "CustomSkin")
            self.lbl_path.configure(text=f"ZIP: {os.path.basename(f)}")
            self._inspect_zip(f)

    def _pick_folder(self):
        d = filedialog.askdirectory(title="Seleccionar carpeta que contiene los frames de Shimeji")
        if d:
            self.source_path = d
            self.is_zip = False
            base_name = os.path.basename(os.path.normpath(d))
            clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "", base_name.replace(" ", "_")).capitalize()
            self.var_skin_name.set(clean_name or "CustomSkin")
            self.lbl_path.configure(text=f"Carpeta: {os.path.basename(d)}")
            self._inspect_folder(d)

    def _inspect_zip(self, zpath):
        try:
            with zipfile.ZipFile(zpath, "r") as zf:
                names = zf.namelist()
                png_names = [n for n in names if n.lower().endswith(".png") and not os.path.basename(n).startswith(".")]
                self.frames_found = png_names
                self.lbl_info.configure(text=f"Frames detectados: {len(png_names)} archivos PNG")
                if not png_names:
                    messagebox.showwarning("Sin sprites", "No se encontraron archivos .png dentro del archivo .zip.")
                    self.btn_import.configure(state=tk.DISABLED)
                    return
                cand = None
                for n in png_names:
                    bn = os.path.basename(n).lower()
                    if bn in ("shime1.png", "1.png"):
                        cand = n
                        break
                if not cand:
                    cand = png_names[0]
                data = zf.read(cand)
                import io
                im = Image.open(io.BytesIO(data)).convert("RGBA")
                im.thumbnail((128, 128))
                self.preview_tk = ImageTk.PhotoImage(im)
                self.lbl_preview_canvas.configure(image=self.preview_tk, text="")
                self.btn_import.configure(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo ZIP:\n{e}")
            self.btn_import.configure(state=tk.DISABLED)

    def _inspect_folder(self, fpath):
        try:
            png_files = []
            for root, _, files in os.walk(fpath):
                for f in files:
                    if f.lower().endswith(".png") and not f.startswith("."):
                        png_files.append(os.path.join(root, f))
            self.frames_found = png_files
            self.lbl_info.configure(text=f"Frames detectados: {len(png_files)} archivos PNG")
            if not png_files:
                messagebox.showwarning("Sin sprites", "No se encontraron archivos .png en la carpeta seleccionada.")
                self.btn_import.configure(state=tk.DISABLED)
                return
            cand = None
            for p in png_files:
                bn = os.path.basename(p).lower()
                if bn in ("shime1.png", "1.png"):
                    cand = p
                    break
            if not cand:
                cand = png_files[0]
            im = Image.open(cand).convert("RGBA")
            im.thumbnail((128, 128))
            self.preview_tk = ImageTk.PhotoImage(im)
            self.lbl_preview_canvas.configure(image=self.preview_tk, text="")
            self.btn_import.configure(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer la carpeta:\n{e}")
            self.btn_import.configure(state=tk.DISABLED)

    def _do_import(self):
        s_name = self.var_skin_name.get().strip()
        if not s_name:
            messagebox.showwarning("Atencion", "Por favor ingresa un nombre para la skin.")
            return
        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "", s_name.replace(" ", "_")).capitalize()
        if not clean_name:
            clean_name = "SkinImportada"

        target_dirs = []
        for b in [BASE_DIR, EXE_DIR]:
            td = os.path.join(b, "img", "skins", clean_name)
            target_dirs.append(td)
            try:
                os.makedirs(td, exist_ok=True)
            except Exception:
                pass

        count = 0
        try:
            if self.is_zip and self.source_path:
                with zipfile.ZipFile(self.source_path, "r") as zf:
                    for entry in self.frames_found:
                        data = zf.read(entry)
                        fname = os.path.basename(entry)
                        if not fname:
                            continue
                        m_num = re.match(r"^(\d+)\.png$", fname, re.IGNORECASE)
                        names_to_save = [fname]
                        if m_num:
                            names_to_save.append(f"shime{m_num.group(1)}.png")
                        for td in target_dirs:
                            for n in names_to_save:
                                with open(os.path.join(td, n), "wb") as out_f:
                                    out_f.write(data)
                        count += 1
            elif self.source_path:
                for src_file in self.frames_found:
                    fname = os.path.basename(src_file)
                    m_num = re.match(r"^(\d+)\.png$", fname, re.IGNORECASE)
                    names_to_save = [fname]
                    if m_num:
                        names_to_save.append(f"shime{m_num.group(1)}.png")
                    for td in target_dirs:
                        for n in names_to_save:
                            shutil.copy2(src_file, os.path.join(td, n))
                    count += 1

            if self.is_zip and self.source_path:
                with zipfile.ZipFile(self.source_path, "r") as zf:
                    for n in zf.namelist():
                        if os.path.basename(n).lower() == "actions.xml":
                            for td in target_dirs:
                                with open(os.path.join(td, "actions.xml"), "wb") as out_f:
                                    out_f.write(zf.read(n))
            elif self.source_path and os.path.isdir(self.source_path):
                act_xml = os.path.join(self.source_path, "actions.xml")
                if os.path.isfile(act_xml):
                    for td in target_dirs:
                        shutil.copy2(act_xml, os.path.join(td, "actions.xml"))

            if clean_name not in SKIN_NAMES:
                SKIN_NAMES.append(clean_name)

            messagebox.showinfo("Importacion Exitosa",
                                f"Skin '{clean_name}' importada correctamente!\n"
                                f"Se instalaron {count} frames en la biblioteca de skins.")

            if self.shimeji:
                ans = messagebox.askyesno("Activar Skin", f"Deseas activar la skin '{clean_name}' ahora?")
                if ans:
                    self.shimeji.set_skin(clean_name)

            self.win.destroy()
        except Exception as e:
            messagebox.showerror("Error al importar", f"Ocurrio un error durante la importacion:\n{e}")


class AgentSettingsWindow:
    """Ventana independiente de ajustes profundos del Agente JARVIS."""
    def __init__(self, parent_root, theme_manager, shimeji_ref=None):
        self.parent = parent_root
        self.theme = theme_manager
        self.shimeji = shimeji_ref
        self.config = self.shimeji.config if self.shimeji else load_config()
        self.win = None
        self._build_window()

    def _build_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("[JARVIS] Ajustes y Personalización del Agente")
        self.win.geometry("560x650")
        self.win.minsize(500, 550)
        self.win.configure(bg=self.theme.surface)
        self.win.attributes("-topmost", True)

        header = tk.Frame(self.win, bg=self.theme.surface_variant, pady=10, padx=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="[*] Panel de Control del Agente JARVIS",
                 font=(self.theme.font_family, self.theme.font_size + 2, "bold"),
                 bg=self.theme.surface_variant, fg=self.theme.accent).pack(anchor="w")
        tk.Label(header, text="Configura autonomía, voz, permisos, comportamiento y macros",
                 font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                 bg=self.theme.surface_variant, fg=self.theme.text_dim).pack(anchor="w")

        # Pestañas con ttk.Notebook
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Jarvis.TNotebook", background=self.theme.surface, borderwidth=0)
        style.configure("Jarvis.TNotebook.Tab", background=self.theme.surface_variant,
                        foreground=self.theme.text, padding=[10, 5],
                        font=(self.theme.font_family, self.theme.font_size - 1, "bold"))
        style.map("Jarvis.TNotebook.Tab",
                  background=[("selected", self.theme.accent)],
                  foreground=[("selected", self.theme.accent_text)])

        self.nb = ttk.Notebook(self.win, style="Jarvis.TNotebook")
        nb = self.nb
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        tab_agent = tk.Frame(nb, bg=self.theme.surface, padx=12, pady=10)
        tab_perms = tk.Frame(nb, bg=self.theme.surface, padx=12, pady=10)
        tab_voice = tk.Frame(nb, bg=self.theme.surface, padx=12, pady=10)
        tab_shimeji = tk.Frame(nb, bg=self.theme.surface, padx=12, pady=10)
        tab_macros = tk.Frame(nb, bg=self.theme.surface, padx=12, pady=10)
        tab_themes = tk.Frame(nb, bg=self.theme.surface, padx=12, pady=10)

        nb.add(tab_agent, text="Agente & IA")
        nb.add(tab_perms, text="Permisos")
        nb.add(tab_voice, text="Voz & Wake Word")
        nb.add(tab_shimeji, text="Shimeji & Ventanas")
        nb.add(tab_macros, text="Macros")
        nb.add(tab_themes, text="Temas & Estilos")

        # ----------------- 1. Agente & IA -----------------
        tk.Label(tab_agent, text="Nombre del Asistente:", bg=self.theme.surface, fg=self.theme.text,
                 font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(2, 2))
        self.var_name = tk.StringVar(value=self.config.get("assistant_name", "JARVIS"))
        e_name = tk.Entry(tab_agent, textvariable=self.var_name, bg=self.theme.entry_bg, fg=self.theme.text,
                          insertbackground=self.theme.accent)
        e_name.pack(fill=tk.X, pady=(0, 8))

        self.var_skin_persona = tk.BooleanVar(value=self.config.get("use_skin_personality", True))
        tk.Checkbutton(tab_agent, text="Usar personalidad y tono único de la skin activa",
                       variable=self.var_skin_persona, bg=self.theme.surface, fg=self.theme.text,
                       selectcolor=self.theme.surface_variant, activebackground=self.theme.surface).pack(anchor="w", pady=(0, 8))

        tk.Label(tab_agent, text="Instrucciones / Personalidad Adicional:", bg=self.theme.surface, fg=self.theme.text,
                 font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(4, 2))
        self.txt_extra = scrolledtext.ScrolledText(tab_agent, height=4, bg=self.theme.entry_bg, fg=self.theme.text,
                                                   font=(self.theme.font_family, self.theme.font_size - 1))
        self.txt_extra.insert(tk.END, self.config.get("agent_extra_prompt", ""))
        self.txt_extra.pack(fill=tk.X, pady=(0, 10))

        row_agent_opts = tk.Frame(tab_agent, bg=self.theme.surface)
        row_agent_opts.pack(fill=tk.X, pady=4)

        tk.Label(row_agent_opts, text="Pasos máximos autónomos:", bg=self.theme.surface, fg=self.theme.text).grid(row=0, column=0, sticky="w", pady=4)
        self.var_max_steps = tk.IntVar(value=self.config.get("agent_max_steps", 6))
        tk.Spinbox(row_agent_opts, from_=1, to=15, textvariable=self.var_max_steps, width=5).grid(row=0, column=1, sticky="w", padx=6)

        tk.Label(row_agent_opts, text="Timeout de la API (segundos):", bg=self.theme.surface, fg=self.theme.text).grid(row=1, column=0, sticky="w", pady=4)
        self.var_timeout = tk.IntVar(value=self.config.get("agent_timeout", 60))
        tk.Spinbox(row_agent_opts, from_=15, to=120, textvariable=self.var_timeout, width=5).grid(row=1, column=1, sticky="w", padx=6)

        tk.Label(row_agent_opts, text="Tokens máximos generados:", bg=self.theme.surface, fg=self.theme.text).grid(row=2, column=0, sticky="w", pady=4)
        self.var_tokens = tk.IntVar(value=self.config.get("agent_max_tokens", 4096))
        tk.Spinbox(row_agent_opts, from_=512, to=8192, increment=512, textvariable=self.var_tokens, width=7).grid(row=2, column=1, sticky="w", padx=6)

        # ----------------- 2. Permisos & Confirmación -----------------
        tk.Label(tab_perms, text="Ejecución Automática de Acciones (Sin Preguntar):", bg=self.theme.surface,
                 fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(0, 6))
        perms = self.config.get("permissions", {})

        self.perm_apps = tk.BooleanVar(value=perms.get("open_apps", True))
        self.perm_sys = tk.BooleanVar(value=perms.get("system_control", True))
        self.perm_file_w = tk.BooleanVar(value=perms.get("file_write", True))
        self.perm_file_del = tk.BooleanVar(value=perms.get("file_delete", False))
        self.perm_cmd = tk.BooleanVar(value=perms.get("cmd_exec", False))
        self.perm_remind = tk.BooleanVar(value=perms.get("reminders", True))

        for text_p, var_p in [
            ("[+] Abrir aplicaciones instaladas y páginas web", self.perm_apps),
            ("[+] Control del sistema (volumen, medios, brillo, bloqueo)", self.perm_sys),
            ("[+] Crear y modificar archivos en el disco", self.perm_file_w),
            ("[!] Borrar archivos permanentemente (Recomendado: Confirmar)", self.perm_file_del),
            ("[!] Ejecutar comandos arbitrarios de consola CMD/PowerShell (Recomendado: Confirmar)", self.perm_cmd),
            ("[+] Crear recordatorios, temporizadores y alarmas", self.perm_remind),
        ]:
            tk.Checkbutton(tab_perms, text=text_p, variable=var_p, bg=self.theme.surface, fg=self.theme.text,
                           selectcolor=self.theme.surface_variant, activebackground=self.theme.surface).pack(anchor="w", pady=3)

        # ----------------- 3. Voz & Wake Word -----------------
        self.var_tts = tk.BooleanVar(value=self.config.get("tts_enabled", False))
        tk.Checkbutton(tab_voice, text="Activar Voz Hablada (TTS de Shimeji)", variable=self.var_tts,
                       bg=self.theme.surface, fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold"),
                       selectcolor=self.theme.surface_variant, activebackground=self.theme.surface).pack(anchor="w", pady=(0, 4))

        row_engine_pick = tk.Frame(tab_voice, bg=self.theme.surface)
        row_engine_pick.pack(fill=tk.X, pady=(0, 6))
        tk.Label(row_engine_pick, text="Motor de Sintesis:", bg=self.theme.surface, fg=self.theme.text, font=(self.theme.font_family, self.theme.font_size - 1, "bold")).pack(side=tk.LEFT)
        self.var_tts_engine = tk.StringVar(value=self.config.get("tts_engine", "voice_studio"))
        tk.Radiobutton(row_engine_pick, text="Voice Studio AI (Gemini 3.8 Flash TTS)", variable=self.var_tts_engine,
                       value="voice_studio", bg=self.theme.surface, fg=self.theme.accent, selectcolor=self.theme.surface_variant,
                       activebackground=self.theme.surface).pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(row_engine_pick, text="SAPI Local (Windows)", variable=self.var_tts_engine,
                       value="sapi", bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant,
                       activebackground=self.theme.surface).pack(side=tk.LEFT)

        tts_helper = self.shimeji.tts if self.shimeji and hasattr(self.shimeji, "tts") else JarvisTTS(self.config)
        voices = tts_helper.get_voices()
        tk.Label(tab_voice, text="Voz instalada de Windows (Modo SAPI):", bg=self.theme.surface, fg=self.theme.text).pack(anchor="w")
        self.var_voice_idx = tk.IntVar(value=self.config.get("tts_voice_idx", 0))
        self.cbo_voice = ttk.Combobox(tab_voice, values=voices, state="readonly")
        if voices:
            cur_idx = min(self.var_voice_idx.get(), len(voices) - 1)
            self.cbo_voice.current(cur_idx)
        self.cbo_voice.pack(fill=tk.X, pady=(2, 6))

        row_tts_controls = tk.Frame(tab_voice, bg=self.theme.surface)
        row_tts_controls.pack(fill=tk.X, pady=4)

        tk.Label(row_tts_controls, text="Velocidad (-10 a 10):", bg=self.theme.surface, fg=self.theme.text).grid(row=0, column=0, sticky="w")
        self.scale_rate = tk.Scale(row_tts_controls, from_=-10, to=10, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text, highlightthickness=0)
        self.scale_rate.set(self.config.get("tts_rate", 0))
        self.scale_rate.grid(row=0, column=1, sticky="ew", padx=6)

        tk.Label(row_tts_controls, text="Tono / Pitch (-10 a 10):", bg=self.theme.surface, fg=self.theme.text).grid(row=1, column=0, sticky="w")
        self.scale_pitch = tk.Scale(row_tts_controls, from_=-10, to=10, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text, highlightthickness=0)
        self.scale_pitch.set(self.config.get("tts_pitch", 0))
        self.scale_pitch.grid(row=1, column=1, sticky="ew", padx=6)

        tk.Label(row_tts_controls, text="Volumen (0 a 100):", bg=self.theme.surface, fg=self.theme.text).grid(row=2, column=0, sticky="w")
        self.scale_vol = tk.Scale(row_tts_controls, from_=0, to=100, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text, highlightthickness=0)
        self.scale_vol.set(self.config.get("tts_volume", 100))
        self.scale_vol.grid(row=2, column=1, sticky="ew", padx=6)

        row_voice_test_btns = tk.Frame(tab_voice, bg=self.theme.surface)
        row_voice_test_btns.pack(fill=tk.X, pady=4)

        tk.Button(row_voice_test_btns, text="[>] Probar SAPI", bg=self.theme.surface_variant, fg=self.theme.accent,
                  command=self._test_voice).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(row_voice_test_btns, text="[♫] Probar Voz Activa", bg=self.theme.surface_variant, fg=self.theme.accent,
                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                  command=self._test_character_voice).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(row_voice_test_btns, text="[★] Voice Studio de Personajes", bg=self.theme.accent, fg=self.theme.accent_text,
                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                  command=self._open_voice_studio).pack(side=tk.LEFT)

        tk.Label(tab_voice, text="--------------------------------------------------", bg=self.theme.surface, fg=self.theme.text_dim).pack(pady=4)

        self.var_wake = tk.BooleanVar(value=self.config.get("wake_word_enabled", False))
        tk.Checkbutton(tab_voice, text="Escucha Continua (Wake Word)", variable=self.var_wake,
                       bg=self.theme.surface, fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold"),
                       selectcolor=self.theme.surface_variant, activebackground=self.theme.surface).pack(anchor="w", pady=(2, 2))

        tk.Label(tab_voice, text="Palabra clave de activación:", bg=self.theme.surface, fg=self.theme.text).pack(anchor="w")
        self.var_wake_word = tk.StringVar(value=self.config.get("wake_word", "oye jarvis"))
        tk.Entry(tab_voice, textvariable=self.var_wake_word, bg=self.theme.entry_bg, fg=self.theme.text).pack(fill=tk.X, pady=(2, 6))

        tk.Button(tab_voice, text="[>] Escuchar por voz ahora (Push-to-Talk)", bg=self.theme.accent, fg=self.theme.accent_text,
                  command=self._listen_now).pack(anchor="w", pady=4)

        # ----------------- 4. Shimeji & Ventanas -----------------
        tk.Label(tab_shimeji, text="Física y Movimiento del Shimeji:", bg=self.theme.surface,
                 fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(0, 4))

        row_shim = tk.Frame(tab_shimeji, bg=self.theme.surface)
        row_shim.pack(fill=tk.X, pady=2)
        tk.Label(row_shim, text="Velocidad de caminata:", bg=self.theme.surface, fg=self.theme.text).grid(row=0, column=0, sticky="w")
        self.scale_speed = tk.Scale(row_shim, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text, highlightthickness=0)
        self.scale_speed.set(self.config.get("walk_speed_mult", 1.0))
        self.scale_speed.grid(row=0, column=1, sticky="ew", padx=6)

        tk.Label(row_shim, text="Multiplicador de gravedad:", bg=self.theme.surface, fg=self.theme.text).grid(row=1, column=0, sticky="w")
        self.scale_grav = tk.Scale(row_shim, from_=0.2, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text, highlightthickness=0)
        self.scale_grav.set(self.config.get("gravity_mult", 1.0))
        self.scale_grav.grid(row=1, column=1, sticky="ew", padx=6)

        tk.Label(row_shim, text="Intervalo de habla aleatoria (s):", bg=self.theme.surface, fg=self.theme.text).grid(row=2, column=0, sticky="w")
        self.var_speech_interval = tk.IntVar(value=self.config.get("random_speech_interval", 30))
        tk.Spinbox(row_shim, from_=5, to=300, textvariable=self.var_speech_interval, width=6).grid(row=2, column=1, sticky="w", padx=6)

        tk.Label(row_shim, text="Tasa de cuadros (FPS):", bg=self.theme.surface, fg=self.theme.text).grid(row=3, column=0, sticky="w")
        self.scale_fps = tk.Scale(row_shim, from_=15, to=60, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text, highlightthickness=0)
        self.scale_fps.set(self.config.get("fps", 30))
        self.scale_fps.grid(row=3, column=1, sticky="ew", padx=6)

        tk.Label(tab_shimeji, text="Animaciones y acrobacias permitidas:", bg=self.theme.surface,
                 fg=self.theme.text, font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(8, 2))

        self.anim_wall = tk.BooleanVar(value=self.config.get("allow_wall_climb", True))
        self.anim_ceiling = tk.BooleanVar(value=self.config.get("allow_ceiling_climb", True))
        self.anim_sit = tk.BooleanVar(value=self.config.get("allow_sitting", True))
        self.anim_jump = tk.BooleanVar(value=self.config.get("allow_jump_fall", True))
        self.anim_custom = tk.BooleanVar(value=self.config.get("allow_custom_actions", True))

        for text_a, var_a in [
            ("Escalar paredes laterales", self.anim_wall),
            ("Trepar y caminar por el techo", self.anim_ceiling),
            ("Sentarse y descansar en el suelo", self.anim_sit),
            ("Saltos y caídas con física elástica", self.anim_jump),
            ("Acciones especiales personalizadas", self.anim_custom),
        ]:
            tk.Checkbutton(tab_shimeji, text=text_a, variable=var_a, bg=self.theme.surface, fg=self.theme.text,
                           selectcolor=self.theme.surface_variant, activebackground=self.theme.surface).pack(anchor="w", pady=1)

        tk.Label(tab_shimeji, text="Comportamiento del Chat:", bg=self.theme.surface,
                 fg=self.theme.text, font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(8, 2))

        self.chat_lock = tk.BooleanVar(value=self.config.get("chat_position_locked", False))
        tk.Checkbutton(tab_shimeji, text="Bloquear posición de la ventana de chat (no mover automáticamente)",
                       variable=self.chat_lock, bg=self.theme.surface, fg=self.theme.text,
                       selectcolor=self.theme.surface_variant, activebackground=self.theme.surface).pack(anchor="w")

        # ----------------- 5. Macros -----------------
        tk.Label(tab_macros, text="Macros Multitarea (Secuencias automáticas de pasos):", bg=self.theme.surface,
                 fg=self.theme.accent, font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(0, 4))

        self.macro_list = tk.Listbox(tab_macros, height=7, bg=self.theme.entry_bg, fg=self.theme.text,
                                     selectbackground=self.theme.accent)
        self.macro_list.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        macros_dict = self.config.get("macros", {
            "modo estudio": {
                "trigger": "modo estudio",
                "steps": [
                    "[JARVIS: VOLUME 30]",
                    "[JARVIS: OPEN \"spotify\"]",
                    "[JARVIS: URL \"https://lofi.cafe\"]"
                ]
            }
        })
        self._refresh_macros_list(macros_dict)

        row_macro_btns = tk.Frame(tab_macros, bg=self.theme.surface)
        row_macro_btns.pack(fill=tk.X, pady=4)

        tk.Button(row_macro_btns, text="[+] Crear Macro", bg=self.theme.surface_variant, fg=self.theme.text,
                  command=self._add_macro_dialog).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(row_macro_btns, text="[★] Cargar Macros Pre-Built", bg=self.theme.surface_variant, fg=self.theme.accent,
                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                  command=self._load_prebuilt_macros).pack(side=tk.LEFT, padx=4)
        tk.Button(row_macro_btns, text="[-] Eliminar", bg=self.theme.surface_variant, fg=self.theme.danger,
                  command=self._delete_macro).pack(side=tk.LEFT, padx=4)
        tk.Button(row_macro_btns, text="[>] Ejecutar", bg=self.theme.accent, fg=self.theme.accent_text,
                  command=self._run_selected_macro).pack(side=tk.RIGHT)

        # ----------------- 6. Temas & Estilos -----------------
        tk.Label(tab_themes, text="Paletas y Temas Predefinidos:", bg=self.theme.surface, fg=self.theme.accent,
                 font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(tab_themes, text="Selecciona un preset para aplicarlo a todas las ventanas:",
                 bg=self.theme.surface, fg=self.theme.text_dim, font=(self.theme.font_family, max(8, self.theme.font_size - 2))).pack(anchor="w", pady=(0, 8))

        presets_frame = tk.Frame(tab_themes, bg=self.theme.surface)
        presets_frame.pack(fill=tk.X, pady=(0, 10))

        col = 0
        rw = 0
        for pk, pv in ThemeManager.THEME_PRESETS.items():
            btn_p = tk.Button(presets_frame, text=pv["name"], bg=pv["surface"], fg=pv["accent"],
                              font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                              relief=tk.FLAT, bd=1, padx=6, pady=4,
                              command=lambda k=pk: self._select_preset(k))
            btn_p.grid(row=rw, column=col, padx=4, pady=4, sticky="ew")
            col += 1
            if col >= 3:
                col = 0
                rw += 1
        for c in range(3):
            presets_frame.columnconfigure(c, weight=1)

        tk.Label(tab_themes, text="Ajustes de Opacidad y Transparencia:", bg=self.theme.surface, fg=self.theme.text,
                 font=(self.theme.font_family, self.theme.font_size, "bold")).pack(anchor="w", pady=(8, 4))

        opac_box = tk.Frame(tab_themes, bg=self.theme.surface)
        opac_box.pack(fill=tk.X, pady=(0, 8))

        tk.Label(opac_box, text="Opacidad de Ventanas (%):", bg=self.theme.surface, fg=self.theme.text).grid(row=0, column=0, sticky="w", pady=2)
        self.scale_theme_opac = tk.Scale(opac_box, from_=40, to=100, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text,
                                         highlightthickness=0, command=self._on_theme_opac_change)
        self.scale_theme_opac.set(int(self.theme.opacity * 100))
        self.scale_theme_opac.grid(row=0, column=1, sticky="ew", padx=8)

        tk.Label(opac_box, text="Opacidad de Burbuja (%):", bg=self.theme.surface, fg=self.theme.text).grid(row=1, column=0, sticky="w", pady=2)
        self.scale_theme_bub = tk.Scale(opac_box, from_=10, to=100, orient=tk.HORIZONTAL, bg=self.theme.surface, fg=self.theme.text,
                                        highlightthickness=0, command=self._on_theme_bub_change)
        self.scale_theme_bub.set(int(getattr(self.theme, "bubble_opacity", 0.95) * 100))
        self.scale_theme_bub.grid(row=1, column=1, sticky="ew", padx=8)
        opac_box.columnconfigure(1, weight=1)

        tk.Button(tab_themes, text="[+] Abrir Personalizador Avanzado de Colores >>",
                  bg=self.theme.surface_variant, fg=self.theme.accent,
                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                  command=self._open_advanced_appearance).pack(anchor="w", pady=(8, 0))

        # ----------------- Botón Guardar -----------------
        bottom_bar = tk.Frame(self.win, bg=self.theme.surface_variant, pady=8, padx=12)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(bottom_bar, text="Guardar Cambios", bg=self.theme.accent, fg=self.theme.accent_text,
                  font=(self.theme.font_family, self.theme.font_size, "bold"), padx=14, pady=4,
                  command=self._save_all).pack(side=tk.RIGHT)
        tk.Button(bottom_bar, text="Cerrar", bg=self.theme.surface, fg=self.theme.text,
                  command=self.win.destroy).pack(side=tk.LEFT)

    def _select_preset(self, pkey):
        self.theme.apply_preset(pkey)
        active_tab = 0
        if hasattr(self, "nb") and self.nb:
            try:
                active_tab = self.nb.index("current")
            except Exception:
                pass
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.win.destroy()
        self._build_window()
        if hasattr(self, "nb") and self.nb:
            try:
                self.nb.select(active_tab)
            except Exception:
                pass
        messagebox.showinfo("Tema", f"Se aplico el tema '{ThemeManager.THEME_PRESETS[pkey]['name']}' correctamente.")

    def _on_theme_opac_change(self, val):
        self.theme.set_opacity(int(val) / 100.0)
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.win.attributes("-alpha", self.theme.opacity)

    def _on_theme_bub_change(self, val):
        self.theme.set_bubble_opacity(int(val) / 100.0)

    def _open_advanced_appearance(self):
        if self.shimeji:
            self.shimeji.open_appearance()

    def _load_prebuilt_macros(self):
        macros = dict(self.config.get("macros", {}))
        for k, v in DEFAULT_PREBUILT_MACROS.items():
            macros[k] = v
        self.config["macros"] = macros
        save_config(self.config)
        self._refresh_macros_list(macros)
        messagebox.showinfo("Macros", "Se cargaron los 5 macros predeterminados correctamente.")

    def _refresh_macros_list(self, m_dict):
        self.macro_list.delete(0, tk.END)
        for k, v in m_dict.items():
            trig = v.get("trigger", k)
            steps_cnt = len(v.get("steps", []))
            self.macro_list.insert(tk.END, f"{trig} ({steps_cnt} pasos)")

    def _test_voice(self):
        tts = self.shimeji.tts if self.shimeji and hasattr(self.shimeji, "tts") else JarvisTTS(self.config)
        cfg_test = dict(self.config)
        cfg_test["tts_enabled"] = True
        cfg_test["tts_voice_idx"] = self.cbo_voice.current() if self.cbo_voice.current() >= 0 else 0
        cfg_test["tts_rate"] = self.scale_rate.get()
        cfg_test["tts_pitch"] = self.scale_pitch.get()
        cfg_test["tts_volume"] = self.scale_vol.get()
        tts.config = cfg_test
        tts.speak("Hola! Sistema de voz SAPI del Agente JARVIS configurado correctamente.")

    def _open_voice_studio(self):
        if self.shimeji and hasattr(self.shimeji, "open_voice_studio"):
            self.shimeji.open_voice_studio()
        else:
            VoiceStudioWindow(self.win, self.theme, self.shimeji)

    def _test_character_voice(self):
        tts = self.shimeji.tts if self.shimeji and hasattr(self.shimeji, "tts") else JarvisTTS(self.config)
        cfg_test = dict(self.config)
        cfg_test["tts_enabled"] = True
        cfg_test["tts_engine"] = getattr(self, "var_tts_engine", tk.StringVar(value="voice_studio")).get()
        cfg_test["tts_voice_idx"] = self.cbo_voice.current() if self.cbo_voice.current() >= 0 else 0
        cfg_test["tts_rate"] = self.scale_rate.get()
        cfg_test["tts_pitch"] = self.scale_pitch.get()
        cfg_test["tts_volume"] = self.scale_vol.get()
        tts.config = cfg_test
        skin = getattr(self.shimeji, "current_skin", "Bocchi") if self.shimeji else "Bocchi"
        prof = VOICE_STUDIO_PROFILES.get(skin, VOICE_STUDIO_PROFILES.get("Bocchi", {}))
        test_txt = prof.get("test", f"Hola! Soy {skin} y esta es mi voz personalizada.")
        tts.speak(test_txt, skin=skin)

    def _listen_now(self):
        if self.shimeji:
            self.shimeji.listen_voice_command_once()

    def _add_macro_dialog(self):
        d = tk.Toplevel(self.win)
        d.title("Nuevo Macro")
        d.geometry("420x340")
        d.configure(bg=self.theme.surface)
        d.attributes("-topmost", True)

        tk.Label(d, text="Frase activadora (ej: 'modo trabajo'):", bg=self.theme.surface, fg=self.theme.text).pack(anchor="w", padx=10, pady=(10, 2))
        e_trig = tk.Entry(d, bg=self.theme.entry_bg, fg=self.theme.text)
        e_trig.pack(fill=tk.X, padx=10, pady=(0, 6))

        tk.Label(d, text="Pasos (uno por línea, ej: [JARVIS: VOLUME 40]):", bg=self.theme.surface, fg=self.theme.text).pack(anchor="w", padx=10, pady=(4, 2))
        txt_steps = scrolledtext.ScrolledText(d, height=8, bg=self.theme.entry_bg, fg=self.theme.text)
        txt_steps.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        def save_m():
            t = e_trig.get().strip().lower()
            lines = [l.strip() for l in txt_steps.get("1.0", tk.END).splitlines() if l.strip()]
            if t and lines:
                macros = dict(self.config.get("macros", {}))
                macros[t] = {"trigger": t, "steps": lines}
                self.config["macros"] = macros
                save_config(self.config)
                self._refresh_macros_list(macros)
                d.destroy()

        tk.Button(d, text="Añadir Macro", bg=self.theme.accent, fg=self.theme.accent_text, command=save_m).pack(pady=8)

    def _delete_macro(self):
        sel = self.macro_list.curselection()
        if not sel:
            return
        idx = sel[0]
        macros = dict(self.config.get("macros", {}))
        keys = list(macros.keys())
        if 0 <= idx < len(keys):
            del macros[keys[idx]]
            self.config["macros"] = macros
            save_config(self.config)
            self._refresh_macros_list(macros)

    def _run_selected_macro(self):
        sel = self.macro_list.curselection()
        if not sel or not self.shimeji:
            return
        idx = sel[0]
        macros = self.config.get("macros", {})
        keys = list(macros.keys())
        if 0 <= idx < len(keys):
            self.shimeji.run_macro(keys[idx])

    def _save_all(self):
        self.config["assistant_name"] = self.var_name.get().strip()
        self.config["use_skin_personality"] = self.var_skin_persona.get()
        self.config["agent_extra_prompt"] = self.txt_extra.get("1.0", tk.END).strip()
        self.config["agent_max_steps"] = int(self.var_max_steps.get())
        self.config["agent_timeout"] = int(self.var_timeout.get())
        self.config["agent_max_tokens"] = int(self.var_tokens.get())

        self.config["permissions"] = {
            "open_apps": self.perm_apps.get(),
            "system_control": self.perm_sys.get(),
            "file_write": self.perm_file_w.get(),
            "file_delete": self.perm_file_del.get(),
            "cmd_exec": self.perm_cmd.get(),
            "reminders": self.perm_remind.get()
        }

        self.config["tts_enabled"] = self.var_tts.get()
        self.config["tts_engine"] = getattr(self, "var_tts_engine", tk.StringVar(value="voice_studio")).get()
        self.config["tts_voice_idx"] = self.cbo_voice.current() if self.cbo_voice.current() >= 0 else 0
        self.config["tts_rate"] = self.scale_rate.get()
        self.config["tts_pitch"] = self.scale_pitch.get()
        self.config["tts_volume"] = self.scale_vol.get()

        self.config["wake_word_enabled"] = self.var_wake.get()
        self.config["wake_word"] = self.var_wake_word.get().strip().lower()

        sp_val = float(self.scale_speed.get())
        self.config["walk_speed_mult"] = sp_val
        self.config["shimeji_walk_speed_mult"] = sp_val

        gr_val = float(self.scale_grav.get())
        self.config["gravity_mult"] = gr_val
        self.config["shimeji_gravity_mult"] = gr_val

        sp_int = int(self.var_speech_interval.get())
        self.config["random_speech_interval"] = sp_int
        self.config["shimeji_talk_interval_sec"] = sp_int

        self.config["allow_wall_climb"] = self.anim_wall.get()
        self.config["allow_ceiling_climb"] = self.anim_ceiling.get()
        self.config["allow_ceiling"] = self.anim_ceiling.get()
        self.config["allow_sitting"] = self.anim_sit.get()
        self.config["allow_jump_fall"] = self.anim_jump.get()
        self.config["allow_fall_jump"] = self.anim_jump.get()
        self.config["allow_custom_actions"] = self.anim_custom.get()

        self.config["chat_position_locked"] = self.chat_lock.get()
        if hasattr(self, "scale_fps"):
            fps_val = int(self.scale_fps.get())
            self.config["fps"] = fps_val
            if self.shimeji:
                self.shimeji.set_fps(fps_val)

        save_config(self.config)

        # Aplicar en caliente al Shimeji
        if self.shimeji:
            if hasattr(self.shimeji, "config") and isinstance(self.shimeji.config, dict):
                self.shimeji.config.update(self.config)
            if hasattr(self.shimeji, "tts"):
                self.shimeji.tts.config = self.config
            if hasattr(self.shimeji, "sync_wake_word_state"):
                self.shimeji.sync_wake_word_state()

        messagebox.showinfo("JARVIS", "Configuración del agente guardada correctamente.")
        self.win.destroy()

class JarvisAssistant:
    PROGRAM_ALIASES = {
        "bloc de notas": "notepad.exe",
        "bloc": "notepad.exe",
        "notas": "notepad.exe",
        "notepad": "notepad.exe",
        "calculadora": "calc.exe",
        "calc": "calc.exe",
        "explorador": "explorer.exe",
        "explorador de archivos": "explorer.exe",
        "carpetas": "explorer.exe",
        "cmd": "cmd.exe",
        "consola": "cmd.exe",
        "simbolo del sistema": "cmd.exe",
        "terminal": "wt.exe",
        "wt": "wt.exe",
        "powershell": "powershell.exe",
        "ps": "powershell.exe",
        "administrador de tareas": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "tareas": "taskmgr.exe",
        "panel de control": "control.exe",
        "control": "control.exe",
        "configuracion": "ms-settings:",
        "ajustes": "ms-settings:",
        "paint": "mspaint.exe",
        "chrome": "chrome",
        "google chrome": "chrome",
        "brave": "brave",
        "firefox": "firefox",
        "spotify": "spotify",
        "discord": "discord",
        "steam": "steam",
        "vscode": "code",
        "vs code": "code",
        "visual studio code": "code",
        "devmgmt": "devmgmt.msc",
        "dispositivos": "devmgmt.msc",
        "diskmgmt": "diskmgmt.msc",
        "discos": "diskmgmt.msc",
        "services": "services.msc",
        "servicios msc": "services.msc",
        "regedit": "regedit.exe",
        "registro": "regedit.exe",
        "resmon": "resmon.exe",
        "monitor de recursos": "resmon.exe",
        "perfmon": "perfmon.exe",
        "rendimiento": "perfmon.exe",
        "eventvwr": "eventvwr.msc",
        "visor de eventos": "eventvwr.msc",
        "appwiz": "appwiz.cpl",
        "desinstalar": "appwiz.cpl",
        "ncpa": "ncpa.cpl",
        "conexiones de red": "ncpa.cpl",
        # WSL y distribuciones de Linux
        "arch": "wsl -d archlinux",
        "archlinux": "wsl -d archlinux",
        "abre arch": "wsl -d archlinux",
        "abre archlinux": "wsl -d archlinux",
        "ubuntu": "wsl -d ubuntu",
        "abre ubuntu": "wsl -d ubuntu",
        "debian": "wsl -d debian",
        "abre debian": "wsl -d debian",
        "kali": "wsl -d kali-linux",
        "abre kali": "wsl -d kali-linux",
        "wsl": "wsl",
        "abre wsl": "wsl",
    }

    def __init__(self, shimeji_ref=None, user_info=None, config=None):
        self.shimeji = shimeji_ref
        self.user_info = user_info
        self.config = config if config is not None else (self.shimeji.config if self.shimeji else load_config())
        self.home_dir = os.path.expanduser("~")
        self.desktop_dir = os.path.join(self.home_dir, "Desktop")
        self.documents_dir = os.path.join(self.home_dir, "Documents")
        self.downloads_dir = os.path.join(self.home_dir, "Downloads")
        self.default_dir = self.desktop_dir if os.path.isdir(self.desktop_dir) else BASE_DIR

        self.custom_paths = list(self.config.get("custom_paths", []))
        self.custom_commands = dict(self.config.get("custom_commands", {}))

        # Comandos predeterminados si aún no están guardados
        default_builtins = {
            "arch": "wsl -d archlinux",
            "archlinux": "wsl -d archlinux",
            "abre arch": "wsl -d archlinux",
            "abre archlinux": "wsl -d archlinux",
            "ubuntu": "wsl -d ubuntu",
            "abre ubuntu": "wsl -d ubuntu",
            "debian": "wsl -d debian",
            "abre debian": "wsl -d debian",
            "wsl": "wsl",
            "abre wsl": "wsl",
        }
        modified = False
        for k, v in default_builtins.items():
            if k not in self.custom_commands:
                self.custom_commands[k] = v
                modified = True
        if modified:
            self.config["custom_commands"] = self.custom_commands
            save_config(self.config)

    def add_custom_command(self, trigger, command):
        """Guarda un alias o comando personalizado para siempre en config.json."""
        t_clean = trigger.strip().lower()
        c_clean = command.strip()
        if not t_clean or not c_clean:
            return False, "[!] Especifica el nombre de la orden y el comando a correr."
        self.custom_commands[t_clean] = c_clean
        self.config["custom_commands"] = self.custom_commands
        save_config(self.config)
        return True, f"[+] Comando guardado para siempre:\n  Cuando digas: '{t_clean}'\n  Ejecutara: '{c_clean}'"

    def delete_custom_command(self, trigger):
        """Elimina un comando personalizado de config.json."""
        t_clean = trigger.strip().lower()
        if t_clean in self.custom_commands:
            del self.custom_commands[t_clean]
            self.config["custom_commands"] = self.custom_commands
            save_config(self.config)
            return True, f"[-] Comando '{t_clean}' eliminado correctamente."
        return False, f"[!] No existe ningun comando guardado como '{t_clean}'."

    def list_custom_commands(self):
        """Lista todos los comandos guardados."""
        if not self.custom_commands:
            return True, "[*] No tienes comandos personalizados guardados todavia.\nUsa: /alias <frase> = <comando>"
        lines = [f"[*] Comandos personalizados guardados ({len(self.custom_commands)}):"]
        for t, c in sorted(self.custom_commands.items()):
            lines.append(f"  - '{t}' -> {c}")
        return True, "\n".join(lines)

    def add_custom_path(self, folder):
        """Añade una carpeta personalizada a las rutas de búsqueda de archivos y ejecutables."""
        clean = folder.strip().strip('"').strip("'")
        if not os.path.isdir(clean):
            return False, f"[!] La carpeta '{clean}' no existe o no es valida."
        norm = os.path.abspath(clean)
        if norm not in self.custom_paths:
            self.custom_paths.append(norm)
            self.config["custom_paths"] = self.custom_paths
            save_config(self.config)
            return True, f"[+] Carpeta agregada a rutas de busqueda:\n  -> {norm}"
        return True, f"[*] La carpeta ya estaba en la lista:\n  -> {norm}"

    def delete_custom_path(self, folder):
        """Elimina una carpeta de las rutas de búsqueda."""
        clean = folder.strip().strip('"').strip("'")
        norm = os.path.abspath(clean)
        found = None
        for p in self.custom_paths:
            if p.lower() == norm.lower() or p.lower() == clean.lower():
                found = p
                break
        if found:
            self.custom_paths.remove(found)
            self.config["custom_paths"] = self.custom_paths
            save_config(self.config)
            return True, f"[-] Carpeta removida de las rutas de busqueda: '{found}'"
        return False, f"[!] La carpeta '{clean}' no estaba en la lista."

    def list_custom_paths(self):
        """Lista todas las rutas de carpetas configuradas."""
        if not self.custom_paths:
            return True, "[*] No tienes carpetas personalizadas guardadas.\nUsa: /addpath <carpeta>"
        lines = [f"[*] Carpetas de busqueda personalizadas ({len(self.custom_paths)}):"]
        for p in self.custom_paths:
            status = "[OK]" if os.path.isdir(p) else "[NO EXISTE]"
            lines.append(f"  - {status} {p}")
        return True, "\n".join(lines)

    def run_powershell(self, ps_cmd):
        """Ejecuta un comando de PowerShell y devuelve el resultado."""
        clean = ps_cmd.strip()
        try:
            proc = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", clean],
                                  capture_output=True, text=True, timeout=15)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            res = out if out else err
            if not res:
                res = f"PowerShell finalizo con codigo {proc.returncode}"
            if len(res) > 1200:
                res = res[:1200] + "\n... [Salida truncada]"
            return True, f"[*] PowerShell: '{clean}'\n{res}"
        except subprocess.TimeoutExpired:
            return False, "[!] El comando de PowerShell tardo demasiado (timeout 15s)"
    def run_bat(self, bat_code):
        """Ejecuta un script BAT temporal y captura la salida."""
        clean = bat_code.strip()
        if not clean:
            return False, "[!] Especifica el código BAT a ejecutar."
        import tempfile
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".bat", delete=False, encoding="cp850") as f:
                temp_path = f.name
                f.write("@echo off\nchcp 65001 >nul\n" + clean + "\n")
            proc = subprocess.run(temp_path, shell=True, capture_output=True, text=True, timeout=15)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            res = out if out else err
            if not res:
                res = f"Script BAT ejecutado correctamente (código {proc.returncode})"
            if len(res) > 1200:
                res = res[:1200] + "\n... [Salida truncada]"
            try:
                os.remove(temp_path)
            except Exception:
                pass
            return True, f"[*] BAT Runner:\n{res}"
        except subprocess.TimeoutExpired:
            return False, "[!] El script BAT tardó demasiado (timeout 15s)"
        except Exception as e:
            return False, f"[!] Error ejecutando script BAT: {e}"

    def get_shortcuts_help(self):
        """Retorna una guía completa y clasificada de atajos prefabricados de Windows/CMD/PS/BAT."""
        return (
            "╔════════════════════════════════════════════════════════════╗\n"
            "║     [!] ATAJOS PREFABRICADOS DE CMD / POWERSHELL / BAT      ║\n"
            "╚════════════════════════════════════════════════════════════╝\n\n"
            "[>] DIAGNÓSTICO & HARDWARE:\n"
            "  • sysinfo          -> Información completa del sistema Windows\n"
            "  • ram              -> Estado de memoria RAM (Total, Libre, Usada)\n"
            "  • disco            -> Espacio total, libre y usado en discos (GB)\n"
            "  • cpu              -> Modelo del procesador, núcleos y velocidad\n"
            "  • gpu              -> Tarjeta gráfica instalada, driver y VRAM\n"
            "  • bateria          -> Reporte detallado de batería (abre en navegador)\n"
            "  • uptime           -> Tiempo que la computadora lleva encendida\n"
            "  • ip               -> Configuración de adaptadores de red y direcciones\n"
            "  • ping             -> Prueba de conectividad hacia internet (8.8.8.8)\n"
            "  • flushdns         -> Vaciar la caché DNS de Windows\n"
            "  • puertos          -> Lista de puertos escuchando en el sistema\n"
            "  • wifi             -> Interfaces de red Wi-Fi y su estado\n\n"
            "[>] MANTENIMIENTO & LIMPIEZA:\n"
            "  • limpiar temp     -> Borrar archivos temporales de %TEMP%\n"
            "  • vaciar papelera  -> Vaciar la Papelera de reciclaje de Windows\n"
            "  • reparar red      -> Release + Renew de IP y flush DNS\n"
            "  • reiniciar explorer -> Reiniciar explorer.exe (barra de tareas)\n"
            "  • /kill <proceso>  -> Forzar cierre de un proceso por nombre\n\n"
            "[>] MONITOREO DE PROCESOS:\n"
            "  • top cpu          -> Los 10 procesos con más consumo de procesador\n"
            "  • top ram          -> Los 10 procesos con mayor consumo de memoria\n"
            "  • servicios        -> Lista de servicios de Windows en ejecución\n\n"
            "[>] HERRAMIENTAS DIRECTAS:\n"
            "  • taskmgr          -> Administrador de tareas\n"
            "  • devmgmt          -> Administrador de dispositivos\n"
            "  • diskmgmt         -> Administrador de discos\n"
            "  • resmon           -> Monitor de recursos\n"
            "  • regedit          -> Editor de registro\n"
            "  • terminal / wt    -> Windows Terminal\n"
            "  • wsl status       -> Estado y distribuciones de WSL\n"
            "  • git status       -> Estado del repositorio Git actual\n"
            "  • git log          -> Últimos commits del proyecto\n\n"
            "[>] EJECUTORES RÁPIDOS:\n"
            "  • /cmd <comando>   -> Ejecutar en CMD directo\n"
            "  • /ps <script>     -> Ejecutar en PowerShell directo\n"
            "  • /bat <codigo>    -> Ejecutar script BAT con salida\n"
            "  • /alias a = b     -> Guardar tu propio comando permanente\n\n"
            "[>] ARCH LINUX & WSL:\n"
            "  • wsl arch           -> Abrir terminal de WSL Arch Linux\n"
            "  • hyfetch            -> Información visual de Arch Linux (HyFetch)\n"
            "  • sudo pacman -S <p> -> Instalar programa en Arch Linux con pacman\n"
            "  • pacman <p>         -> Atajo rápido de instalación en Arch\n\n"
            "[>] GESTOR DE PAQUETES DE WINDOWS (WINGET):\n"
            "  • winget <programa>  -> Instalar aplicación en Windows con winget\n"
            "  • winget install <p> -> Instalación desatendida con winget\n"
            "  • winget search <p>  -> Buscar programas disponibles en winget\n\n"
            "[>] SKINS DISPONIBLES:\n"
            "  • /skin <nombre>   -> Cambiar skin (Bocchi, Konata, Monika, Natsuki, Sayori, Yuri)\n"
            "  • /skins           -> Lista de personajes disponibles"
        )

    def execute_prefabricated_shortcut(self, key):
        """Ejecuta un atajo prefabricado de sistema si coincide."""
        k = key.lower().strip()
        for prefix in ("hey ", "porfa ", "favor de ", "abre ", "corre ", "ejecuta ", "inicia ", "haz "):
            if k.startswith(prefix):
                k = k[len(prefix):].strip()

        # 1. Información y Diagnóstico
        if k in ("sysinfo", "sistema", "info sistema", "systeminfo", "datos sistema"):
            return self.run_cmd("systeminfo")

        if k in ("ip", "mi ip", "ipconfig", "config red", "red ip"):
            return self.run_cmd("ipconfig /all")

        if k in ("flushdns", "limpiar dns", "borrar dns", "dns"):
            return self.run_cmd("ipconfig /flushdns")

        if k in ("ping", "probar red", "ping google", "test red", "probar conexion"):
            return self.run_cmd("ping -n 4 8.8.8.8")

        if k in ("puertos", "netstat", "puertos abiertos", "listening", "ver puertos"):
            return self.run_cmd("netstat -ano | findstr LISTENING")

        if k in ("wifi", "red wifi", "redes wifi", "wlan", "estado wifi"):
            return self.run_cmd("netsh wlan show interfaces")

        # 2. Hardware y Métricas
        if k in ("ram", "memoria", "uso de ram", "memoria ram", "estado ram"):
            ps = "Get-CimInstance Win32_OperatingSystem | Select-Object @{N='RAM Total (GB)';E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, @{N='RAM Libre (GB)';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}, @{N='RAM Usada (GB)';E={[math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)/1MB,2)}} | Format-List"
            return self.run_powershell(ps)

        if k in ("disco", "discos", "almacenamiento", "espacio en disco", "espacio", "disco duro"):
            ps = "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='Usado (GB)';E={[math]::Round($_.Used/1GB,2)}}, @{N='Libre (GB)';E={[math]::Round($_.Free/1GB,2)}}, @{N='Total (GB)';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}} | Format-Table -AutoSize"
            return self.run_powershell(ps)

        if k in ("cpu", "procesador", "info cpu", "datos cpu"):
            ps = "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | Format-List"
            return self.run_powershell(ps)

        if k in ("gpu", "grafica", "tarjeta grafica", "video"):
            ps = "Get-CimInstance Win32_VideoController | Select-Object Name, VideoProcessor, DriverVersion, @{N='VRAM (MB)';E={[math]::Round($_.AdapterRAM/1MB,0)}} | Format-List"
            return self.run_powershell(ps)

        if k in ("uptime", "tiempo encendido", "tiempo activo", "cuanto lleva encendida"):
            ps = "(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime | Select-Object Days, Hours, Minutes, Seconds | Format-List"
            return self.run_powershell(ps)

        if k in ("bateria", "battery", "reporte bateria", "estado bateria"):
            temp_dir = os.environ.get("TEMP", os.path.expanduser("~"))
            bat_report = os.path.join(temp_dir, "battery_report.html")
            cmd = f'powercfg /batteryreport /output "{bat_report}"'
            subprocess.run(cmd, shell=True, capture_output=True)
            if os.path.exists(bat_report):
                open_web_url(bat_report)
                return True, f"[+] Reporte de batería generado y abierto en tu navegador:\n{bat_report}"
            return False, "[!] No se pudo generar el reporte de batería (posiblemente sea una PC de escritorio sin batería)."

        # 3. Mantenimiento y Limpieza
        if k in ("limpiar temp", "clean temp", "temp", "borrar temporales", "limpiar temporales"):
            cmd = 'del /q /f /s "%TEMP%\\*" 2>nul & for /d %i in ("%TEMP%\\*") do rmdir /s /q "%i" 2>nul'
            subprocess.run(cmd, shell=True, capture_output=True)
            return True, "[+] Archivos temporales de %TEMP% eliminados correctamente. Espacio liberado [OK]"

        if k in ("vaciar papelera", "limpiar papelera", "empty trash", "vaciar papelera de reciclaje"):
            ps = "Clear-RecycleBin -Force -ErrorAction SilentlyContinue; Write-Output 'Papelera de reciclaje vaciada con exito'"
            return self.run_powershell(ps)

        if k in ("reparar red", "reset red", "reset network", "reiniciar red"):
            cmd = "ipconfig /release & ipconfig /renew & ipconfig /flushdns"
            return self.run_cmd(cmd)

        if k in ("reiniciar explorer", "restart explorer", "reinicia explorer", "reiniciar barra"):
            cmd = "taskkill /f /im explorer.exe & start explorer.exe"
            subprocess.Popen(cmd, shell=True)
            return True, "[+] Reiniciando el Explorador de Windows..."

        # 4. Procesos y Tareas
        if k in ("top cpu", "procesos cpu", "mas cpu"):
            ps = "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Id, ProcessName, @{N='CPU (s)';E={[math]::Round($_.CPU,1)}}, @{N='RAM (MB)';E={[math]::Round($_.WorkingSet64/1MB,1)}} | Format-Table -AutoSize"
            return self.run_powershell(ps)

        if k in ("top ram", "top memoria", "procesos ram", "mas ram"):
            ps = "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Id, ProcessName, @{N='RAM (MB)';E={[math]::Round($_.WorkingSet64/1MB,1)}}, @{N='CPU (s)';E={[math]::Round($_.CPU,1)}} | Format-Table -AutoSize"
            return self.run_powershell(ps)

        if k in ("servicios", "servicios activos", "services running"):
            ps = "Get-Service | Where-Object Status -eq 'Running' | Select-Object -First 15 Name, DisplayName | Format-Table -AutoSize"
            return self.run_powershell(ps)

        # 5. WSL, Arch Linux & Git
        if k in ("wsl arch", "arch", "archlinux", "wsl archlinux", "abrir arch", "entrar a arch", "iniciar arch", "terminal arch"):
            cmd = 'start wt wsl -d archlinux' if shutil.which("wt") else 'start wsl -d archlinux'
            subprocess.Popen(cmd, shell=True)
            return True, "[+] Abriendo terminal de WSL Arch Linux (archlinux)..."

        if k in ("hyfetch", "wsl hyfetch", "arch hyfetch", "neofetch", "fastfetch"):
            try:
                proc = subprocess.run("wsl -d archlinux hyfetch", shell=True, capture_output=True, text=True, timeout=8)
                out = (proc.stdout or proc.stderr).strip()
                if out:
                    clean_out = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', out)
                    return True, f"[*] HyFetch (Arch Linux WSL):\n{clean_out}"
            except Exception:
                pass
            cmd = 'start wt wsl -d archlinux hyfetch' if shutil.which("wt") else 'start wsl -d archlinux hyfetch'
            subprocess.Popen(cmd, shell=True)
            return True, "[+] Lanzando hyfetch en terminal de Arch Linux..."

        if k in ("wsl status", "wsl distros", "wsl -l -v"):
            return self.run_cmd("wsl -l -v")

        if k in ("git status", "estado git"):
            return self.run_cmd("git status")

        if k in ("git log", "historial git"):
            return self.run_cmd("git log -n 5 --oneline")

        if k in ("git branch", "ramas git"):
            return self.run_cmd("git branch -a")

        # 6. Lanzadores directos de Terminales y Aplicaciones Esenciales
        if k in ("terminal", "wt", "consola", "abrir terminal", "abre terminal"):
            cmd = 'start wt' if shutil.which("wt") else 'start powershell'
            subprocess.Popen(cmd, shell=True)
            return True, "[+] Abriendo Terminal de comandos..."

        if k in ("powershell", "ps", "consola powershell", "abrir powershell", "abre powershell"):
            subprocess.Popen('start powershell', shell=True)
            return True, "[+] Abriendo Windows PowerShell..."

        if k in ("cmd", "simbolo del sistema", "consola cmd", "abrir cmd", "abre cmd"):
            subprocess.Popen('start cmd', shell=True)
            return True, "[+] Abriendo Símbolo del Sistema (CMD)..."

        if k in ("navegador", "browser", "abrir navegador", "abre navegador", "chrome", "brave"):
            browsers = get_preferred_browsers()
            if browsers:
                try:
                    subprocess.Popen([browsers[0]])
                    return True, f"[+] Navegador abierto: {os.path.basename(browsers[0])} [OK]"
                except Exception:
                    pass
            open_web_url("https://www.google.com")
            return True, "[+] Abriendo navegador web (Chrome/Brave)..."

        if k in ("notepad", "bloc de notas", "bloc", "notas", "abrir notepad", "abre notepad"):
            subprocess.Popen('start notepad', shell=True)
            return True, "[+] Abriendo Bloc de notas..."

        if k in ("explorador", "explorer", "carpetas", "archivos explorador", "abrir explorador", "abre explorador"):
            subprocess.Popen('start explorer', shell=True)
            return True, "[+] Abriendo Explorador de archivos..."

        if k in ("calc", "calculadora", "abrir calc", "abre calc", "abrir calculadora"):
            subprocess.Popen('start calc', shell=True)
            return True, "[+] Abriendo Calculadora..."

        if k in ("configuracion", "ajustes", "settings", "abrir configuracion", "abre configuracion", "abrir ajustes"):
            try:
                os.startfile("ms-settings:")
                return True, "[+] Abriendo Configuración de Windows..."
            except Exception:
                pass

        if k in ("taskmgr", "administrador de tareas", "tareas", "abrir taskmgr", "abre taskmgr"):
            try:
                os.startfile("taskmgr.exe")
                return True, "[+] Abriendo Administrador de tareas..."
            except Exception:
                pass

        return None

    def run_custom_command(self, cmd_str):
        """Ejecuta un comando personalizado (abriendo ventana si es interactivo o ejecutando ejecutable/script)."""
        clean = cmd_str.strip()
        lower = clean.lower()
        # Si es comando de terminal / WSL / interactive, abrir en nueva ventana
        if lower.startswith("wsl") or lower.startswith("powershell") or lower.startswith("cmd") or lower.startswith("wt"):
            try:
                subprocess.Popen(f'start {clean}', shell=True)
                return True, f"[+] Ejecutando en nueva ventana:\n  -> {clean}"
            except Exception as e:
                return False, f"[!] Error al lanzar comando: {e}"

        # Si es archivo o ejecutable existente
        resolved = self.resolve_target(clean, must_exist=True)
        if resolved:
            try:
                os.startfile(resolved)
                return True, f"[+] Archivo/programa ejecutado:\n  '{os.path.basename(resolved)}'"
            except Exception as e:
                return False, f"[!] Error al abrir '{resolved}': {e}"

        # Probar con start de Windows
        try:
            subprocess.Popen(f'start "" "{clean}"', shell=True)
            return True, f"[+] Lanzando orden:\n  '{clean}'"
        except Exception:
            return self.run_cmd(clean)

    def resolve_target(self, filename_or_path, must_exist=False):
        """Resuelve el archivo buscando en Desktop, Documents, Downloads, BASE_DIR, rutas personalizadas o como ruta absoluta."""
        if not filename_or_path:
            return None
        cleaned = filename_or_path.strip().strip('"').strip("'")
        if not cleaned:
            return None

        # Si es ruta absoluta
        if os.path.isabs(cleaned):
            if must_exist and not os.path.exists(cleaned):
                return None
            return cleaned

        # Lista de carpetas estándar donde buscar + carpetas personalizadas
        candidate_dirs = [
            self.desktop_dir,
            BASE_DIR,
            self.documents_dir,
            self.downloads_dir
        ] + [p for p in self.custom_paths if os.path.isdir(p)]

        # 1. Búsqueda exacta en directorios candidatos
        for d in candidate_dirs:
            if os.path.isdir(d):
                cand = os.path.join(d, cleaned)
                if os.path.exists(cand):
                    return cand

        # 2. Si must_exist es True, búsqueda insensible a mayúsculas o sin extensión
        if must_exist:
            cleaned_lower = cleaned.lower()
            for d in candidate_dirs:
                if not os.path.isdir(d):
                    continue
                try:
                    for f in os.listdir(d):
                        if f.lower() == cleaned_lower:
                            return os.path.join(d, f)
                        base, _ = os.path.splitext(f)
                        if base.lower() == cleaned_lower:
                            return os.path.join(d, f)
                except Exception:
                    pass
            return None

        # Si no debe existir (para crear nuevo archivo), default al Escritorio
        return os.path.join(self.desktop_dir, cleaned)

    def search_files(self, pattern, search_dir=None, max_results=15):
        """Busca archivos por nombre o patrón en el equipo de forma rápida y segura."""
        clean_pat = pattern.strip().strip('"').strip("'")
        if not clean_pat:
            return []

        search_dirs = []
        if search_dir and os.path.isdir(search_dir):
            search_dirs.append(search_dir)
        else:
            search_dirs = [
                self.desktop_dir,
                self.documents_dir,
                self.downloads_dir,
                BASE_DIR,
                self.home_dir
            ] + [p for p in self.custom_paths if os.path.isdir(p)]

        results = []
        seen = set()
        ignore_dirs = {
            "appdata", "node_modules", ".git", "__pycache__", "venv", ".gemini",
            "microsoft", "windows", "temp", "tmp", "cache", "caches", ".vscode"
        }

        pat_lower = clean_pat.lower()
        glob_pat = pat_lower if ("*" in pat_lower or "?" in pat_lower) else f"*{pat_lower}*"

        for root_dir in search_dirs:
            if not os.path.isdir(root_dir):
                continue
            root_depth = root_dir.rstrip(os.sep).count(os.sep)

            try:
                for root, dirs, files in os.walk(root_dir, topdown=True):
                    # Limitar profundidad a máximo 3 niveles relativos
                    curr_depth = root.rstrip(os.sep).count(os.sep)
                    if curr_depth - root_depth > 3:
                        dirs.clear()
                        continue

                    # Filtrar carpetas protegidas o gigantes
                    dirs[:] = [d for d in dirs if d.lower() not in ignore_dirs and not d.startswith('.')]

                    for f in files:
                        f_lower = f.lower()
                        if fnmatch.fnmatch(f_lower, glob_pat) or pat_lower in f_lower:
                            full_path = os.path.join(root, f)
                            if full_path in seen:
                                continue
                            seen.add(full_path)

                            try:
                                size_b = os.path.getsize(full_path)
                                if size_b < 1024:
                                    size_str = f"{size_b} B"
                                elif size_b < 1024 * 1024:
                                    size_str = f"{size_b / 1024:.1f} KB"
                                else:
                                    size_str = f"{size_b / (1024*1024):.1f} MB"
                            except Exception:
                                size_str = "? B"

                            results.append((f, full_path, size_str))
                            if len(results) >= max_results:
                                return results
            except Exception:
                pass

        return results

    def search_file(self, pattern, search_dir=None):
        results = self.search_files(pattern, search_dir=search_dir)
        if not results:
            return False, f"[!] No encontré archivos que coincidan con '{pattern}' en tus carpetas."

        lines = [f"[*] Se encontraron {len(results)} archivo(s) para '{pattern}':"]
        for fname, full_path, size_str in results:
            lines.append(f"  [FILE] {fname} ({size_str})\n         -> {full_path}")
        return True, "\n".join(lines)

    def search_web(self, query, engine="google"):
        clean = query.strip().strip('"').strip("'")
        if not clean:
            return False, "[!] Dime qué quieres buscar en internet :v"

        encoded = urllib.parse.quote_plus(clean)
        if engine == "youtube" or "youtube" in clean.lower():
            url = f"https://www.youtube.com/results?search_query={encoded}"
            open_web_url(url)
            return True, f"[+] Búsqueda en YouTube abierta:\n'{clean}'\n[>] {url}"
        else:
            url = f"https://www.google.com/search?q={encoded}"
            open_web_url(url)
            return True, f"[+] Búsqueda en Google abierta:\n'{clean}'\n[>] {url}"

    def create_file(self, filename, content=""):
        path = self.resolve_target(filename, must_exist=False)
        if not path:
            return False, "Ruta no valida para crear el archivo"
        try:
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            name = os.path.basename(path)
            return True, f"[+] Archivo creado: '{name}' en {os.path.dirname(path)}"
        except Exception as e:
            return False, f"[!] Error al crear '{filename}': {e}"

    def write_file(self, filename, content, append=False):
        path = self.resolve_target(filename, must_exist=False)
        if not path:
            return False, f"[!] No se encontro el archivo '{filename}'"
        try:
            mode = "a" if append else "w"
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            prefix = "\n" if append and os.path.exists(path) and os.path.getsize(path) > 0 else ""
            with open(path, mode, encoding="utf-8") as f:
                f.write(prefix + content)
            action = "añadido a" if append else "guardado en"
            return True, f"[+] Texto {action} '{os.path.basename(path)}' ({len(content)} caracteres)"
        except Exception as e:
            return False, f"[!] Error modificando '{filename}': {e}"

    def rename_file(self, old_name, new_name):
        old_path = self.resolve_target(old_name, must_exist=True)
        if not old_path:
            return False, f"[!] No encontre el archivo '{old_name}' en tu Escritorio ni directorio actual"

        dir_name = os.path.dirname(old_path)
        clean_new = new_name.strip().strip('"').strip("'")

        # Mantener extension original si new_name no incluye extension
        _, old_ext = os.path.splitext(old_path)
        _, new_ext = os.path.splitext(clean_new)
        if old_ext and not new_ext:
            clean_new = clean_new + old_ext

        new_path = os.path.join(dir_name, clean_new)
        try:
            if os.path.exists(new_path) and os.path.abspath(old_path).lower() != os.path.abspath(new_path).lower():
                os.remove(new_path)
            os.rename(old_path, new_path)
            return True, f"[+] Archivo renombrado exitosamente de '{os.path.basename(old_path)}' a '{clean_new}'"
        except Exception as e:
            return False, f"[!] Error renombrando archivo: {e}"

    def read_file(self, filename, max_chars=1500):
        path = self.resolve_target(filename, must_exist=True)
        if not path:
            return False, f"[!] No encontre el archivo '{filename}' para leer"
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read(max_chars)
            total_size = os.path.getsize(path)
            snippet = text if len(text) < max_chars else text + "\n... [Texto truncado]"
            return True, f"[*] Contenido de '{os.path.basename(path)}' ({total_size} bytes):\n---\n{snippet}\n---"
        except Exception as e:
            return False, f"[!] Error leyendo '{filename}': {e}"

    def delete_file(self, filename):
        path = self.resolve_target(filename, must_exist=True)
        if not path:
            return False, f"[!] No encontre el archivo '{filename}' para borrar"
        try:
            if WINSHELL_AVAILABLE:
                winshell.delete_file(path, no_confirm=True, allow_undo=True)
            else:
                os.remove(path)
            return True, f"[-] Archivo '{os.path.basename(path)}' enviado a la papelera"
        except Exception as e:
            return False, f"[!] Error borrando '{filename}': {e}"


    def check_permission(self, category, description):
        """Verifica si la categoría de acción tiene permiso automático o requiere confirmación."""
        perms = self.config.get("permissions", {
            "open_apps": True,
            "system_control": True,
            "file_write": True,
            "file_delete": False,
            "cmd_exec": False,
            "reminders": True
        })
        if perms.get(category, True):
            return True
        # Preguntar al usuario mediante diálogo
        try:
            root = self.shimeji.root if self.shimeji else None
            ans = messagebox.askyesno("[JARVIS] Confirmar Acción",
                                      f"El Asistente JARVIS solicita ejecutar:\n\n{description}\n\n¿Deseas permitir esta acción?",
                                      parent=root)
            return ans
        except Exception:
            return True

    def get_installed_apps(self):
        """Escanea accesos directos del Menú Inicio y apps UWP de Windows."""
        if hasattr(self, "_apps_cache") and self._apps_cache:
            return self._apps_cache
        apps = {}
        # 1. Programas de ProgramData y AppData
        search_dirs = [
            os.path.join(os.environ.get("ProgramData", ""), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("AppData", ""), r"Microsoft\Windows\Start Menu\Programs"),
        ]
        for sdir in search_dirs:
            if os.path.isdir(sdir):
                for root, _, files in os.walk(sdir):
                    for f in files:
                        if f.lower().endswith((".lnk", ".url")):
                            name = os.path.splitext(f)[0].lower()
                            apps[name] = os.path.join(root, f)
        self._apps_cache = apps
        return apps

    def set_volume(self, val_or_action):
        """Controla el volumen maestro de Windows (subir, bajar, silenciar o nivel específico 0-100)."""
        if not self.check_permission("system_control", f"Ajustar volumen a: {val_or_action}"):
            return False, "[!] Acción cancelada por el usuario"
        if not WIN32_AVAILABLE:
            return False, "[!] win32api no está disponible"
        act = str(val_or_action).strip().lower()
        try:
            VK_VOLUME_MUTE = 0xAD
            VK_VOLUME_DOWN = 0xAE
            VK_VOLUME_UP   = 0xAF

            if act in ("mute", "silencio", "mutear"):
                win32api.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
                win32api.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
                return True, "[+] Silencio (Mute) alternado [OK]"
            elif act in ("up", "subir", "+"):
                for _ in range(5):
                    win32api.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                    win32api.keybd_event(VK_VOLUME_UP, 0, 2, 0)
                return True, "[+] Volumen aumentado [OK]"
            elif act in ("down", "bajar", "-"):
                for _ in range(5):
                    win32api.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                    win32api.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
                return True, "[+] Volumen reducido [OK]"
            else:
                target_pct = int(re.sub(r'[^0-9]', '', act))
                target_pct = max(0, min(100, target_pct))
                # Bajar a 0 y luego subir a target_pct/2
                for _ in range(50):
                    win32api.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                    win32api.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
                for _ in range(target_pct // 2):
                    win32api.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                    win32api.keybd_event(VK_VOLUME_UP, 0, 2, 0)
                return True, f"[+] Volumen fijado aproximadamente al {target_pct}% [OK]"
        except Exception as e:
            return False, f"[!] Error ajustando volumen: {e}"

    def media_control(self, action):
        """Controla reproducción multimedia (play/pause, next, prev)."""
        if not self.check_permission("system_control", f"Control multimedia: {action}"):
            return False, "[!] Acción cancelada por el usuario"
        if not WIN32_AVAILABLE:
            return False, "[!] win32api no está disponible"
        act = action.strip().lower()
        VK_MEDIA_NEXT_TRACK = 0xB0
        VK_MEDIA_PREV_TRACK = 0xB1
        VK_MEDIA_PLAY_PAUSE = 0xB3
        try:
            if act in ("play", "pause", "play_pause", "toggle", "pausa", "reproducir"):
                win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)
                return True, "[+] Reproducción multimedia alternada (Play/Pausa) [OK]"
            elif act in ("next", "siguiente", "adelantar"):
                win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)
                win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 2, 0)
                return True, "[+] Siguiente pista multimedia [OK]"
            elif act in ("prev", "previous", "anterior"):
                win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, 0, 0)
                win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, 2, 0)
                return True, "[+] Pista multimedia anterior [OK]"
            return False, f"[!] Acción multimedia desconocida: {act}"
        except Exception as e:
            return False, f"[!] Error multimedia: {e}"

    def set_brightness(self, level):
        """Ajusta el brillo de pantalla (0-100) en laptops y monitores compatibles."""
        if not self.check_permission("system_control", f"Ajustar brillo al: {level}%"):
            return False, "[!] Acción cancelada por el usuario"
        try:
            pct = max(0, min(100, int(level)))
            ps_cmd = f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {pct})"
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=8)
            if proc.returncode == 0:
                return True, f"[+] Brillo ajustado al {pct}% [OK]"
            return False, "[!] El ajuste de brillo por hardware solo está disponible en pantallas integradas/laptops."
        except Exception as e:
            return False, f"[!] Error ajustando brillo: {e}"

    def toggle_wifi(self, enable=True):
        """Habilita o deshabilita el adaptador de Wi-Fi."""
        state_str = "activar" if enable else "desactivar"
        if not self.check_permission("system_control", f"{state_str.capitalize()} Wi-Fi"):
            return False, "[!] Acción cancelada por el usuario"
        try:
            st = "enabled" if enable else "disabled"
            proc = subprocess.run(f'netsh interface set interface name="Wi-Fi" admin={st}', shell=True, capture_output=True, text=True, timeout=8)
            if proc.returncode == 0:
                return True, f"[+] Adaptador Wi-Fi {state_str}do [OK]"
            # Abrir panel de configuración de red si requiere elevación
            os.startfile("ms-settings:network-wifi")
            return True, f"[+] Abriendo configuración de Wi-Fi de Windows..."
        except Exception as e:
            return False, f"[!] Error cambiando Wi-Fi: {e}"

    def open_bluetooth_settings(self):
        """Abre la configuración de Bluetooth de Windows."""
        try:
            os.startfile("ms-settings:bluetooth")
            return True, "[+] Abriendo configuración de Bluetooth de Windows [OK]"
        except Exception as e:
            return False, f"[!] Error abriendo Bluetooth: {e}"

    def take_screenshot(self):
        """Toma una captura de pantalla y la guarda en la carpeta Imágenes."""
        if not self.check_permission("system_control", "Tomar captura de pantalla"):
            return False, "[!] Acción cancelada por el usuario"
        if not IMAGEGRAB_AVAILABLE:
            return False, "[!] PIL.ImageGrab no disponible"
        try:
            pics_dir = os.path.join(os.path.expanduser("~"), "Pictures", "PinkChan_Capturas")
            os.makedirs(pics_dir, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fpath = os.path.join(pics_dir, f"captura_{ts}.png")
            im = ImageGrab.grab()
            im.save(fpath)
            return True, f"[+] Captura guardada en:\n  -> {fpath}"
        except Exception as e:
            return False, f"[!] Error tomando captura: {e}"

    def lock_workstation(self):
        """Bloquea la estación de trabajo de Windows."""
        if not self.check_permission("system_control", "Bloquear la pantalla de la PC"):
            return False, "[!] Acción cancelada por el usuario"
        try:
            ctypes.windll.user32.LockWorkStation()
            return True, "[+] PC bloqueada exitosamente [OK]"
        except Exception as e:
            return False, f"[!] Error bloqueando PC: {e}"

    def search_youtube(self, query):
        """Busca y reproduce videos en YouTube."""
        try:
            q = urllib.parse.quote(query.strip())
            url = f"https://www.youtube.com/results?search_query={q}"
            open_web_url(url)
            return True, f"[+] Buscando en YouTube: '{query}' [OK]"
        except Exception as e:
            return False, f"[!] Error en YouTube: {e}"

    def add_timer(self, minutes_or_spec, text="Temporizador"):
        """Añade un temporizador de N minutos o segundos."""
        if not self.check_permission("reminders", f"Crear temporizador: '{text}'"):
            return False, "[!] Acción cancelada por el usuario"
        try:
            s = str(minutes_or_spec).strip().lower()
            secs = 0
            if s.endswith("m"):
                secs = int(float(s[:-1]) * 60)
            elif s.endswith("s"):
                secs = int(float(s[:-1]))
            elif s.endswith("h"):
                secs = int(float(s[:-1]) * 3600)
            else:
                secs = int(float(s) * 60)

            due = time.time() + max(1, secs)
            rems = list(self.config.get("reminders", []))
            r_item = {
                "id": int(time.time() * 1000),
                "type": "timer",
                "due": due,
                "text": text,
                "spec": minutes_or_spec
            }
            rems.append(r_item)
            self.config["reminders"] = rems
            save_config(self.config)
            return True, f"[+] Temporizador programado para dentro de {secs}s: '{text}' [OK]"
        except Exception as e:
            return False, f"[!] Formato de tiempo inválido: {e}"

    def add_reminder(self, time_str, text="Recordatorio"):
        """Añade un recordatorio o alarma a una hora específica (ej: '14:30' o '18:00')."""
        if not self.check_permission("reminders", f"Programar recordatorio a las {time_str}: '{text}'"):
            return False, "[!] Acción cancelada por el usuario"
        try:
            parts = time_str.strip().split(":")
            h, m = int(parts[0]), int(parts[1])
            now = datetime.datetime.now()
            target_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if target_dt <= now:
                target_dt += datetime.timedelta(days=1)
            due = target_dt.timestamp()

            rems = list(self.config.get("reminders", []))
            r_item = {
                "id": int(time.time() * 1000),
                "type": "reminder",
                "due": due,
                "text": text,
                "spec": time_str
            }
            rems.append(r_item)
            self.config["reminders"] = rems
            save_config(self.config)
            return True, f"[+] Recordatorio guardado para las {time_str}: '{text}' [OK]"
        except Exception as e:
            return False, f"[!] Formato de hora inválido (usa HH:MM): {e}"

    def list_reminders(self):
        """Lista los temporizadores y recordatorios activos."""
        rems = self.config.get("reminders", [])
        if not rems:
            return True, "[i] No hay recordatorios ni temporizadores pendientes."
        lines = ["[*] Recordatorios y temporizadores activos:"]
        now = time.time()
        for idx, r in enumerate(rems, 1):
            left_secs = max(0, int(r["due"] - now))
            m_left = left_secs // 60
            s_left = left_secs % 60
            lines.append(f"  {idx}. [{r.get('type','alarma')}] '{r.get('text','')}' (Faltan: {m_left}m {s_left}s)")
        return True, "\n".join(lines)

    def cancel_reminder(self, idx_or_text):
        """Cancela un recordatorio por número de índice."""
        rems = list(self.config.get("reminders", []))
        try:
            idx = int(idx_or_text) - 1
            if 0 <= idx < len(rems):
                removed = rems.pop(idx)
                self.config["reminders"] = rems
                save_config(self.config)
                return True, f"[+] Recordatorio cancelado: '{removed.get('text','')}' [OK]"
            return False, "[!] Índice de recordatorio fuera de rango."
        except Exception:
            return False, "[!] Debes indicar el número del recordatorio a cancelar."

    def run_macro(self, macro_name):
        """Ejecuta una macro multitarea paso a paso mostrando el progreso en la burbuja."""
        macros = self.config.get("macros", {})
        clean = macro_name.strip().lower()
        m = macros.get(clean)
        if not m:
            for k, v in macros.items():
                if clean in k or clean in v.get("trigger", ""):
                    m = v
                    break
        if not m:
            if self.shimeji:
                self.shimeji.show_speech(f"[!] Macro '{macro_name}' no encontrada.")
            return False, f"[!] Macro '{macro_name}' no encontrada en la configuración."

        steps = m.get("steps", [])
        total = len(steps)
        if self.shimeji:
            self.shimeji.show_speech(f"[*] Iniciando macro: '{macro_name}' ({total} pasos)...")
        results = [f"[*] Iniciando macro: '{macro_name}' ({total} pasos)"]
        for idx, st in enumerate(steps, 1):
            st = st.strip()
            if not st:
                continue
            if self.shimeji:
                self.shimeji.show_speech(f"[*] Macro '{macro_name}' [{idx}/{total}]:\n{st}")
            if st.upper().startswith("WAIT"):
                try:
                    w_secs = float(st.split()[1])
                    time.sleep(w_secs)
                    results.append(f"  -> Espera de {w_secs}s completada")
                except Exception:
                    pass
                continue
            # Parsear comando jarvis en el paso
            if hasattr(self, "_chat_ref") and self._chat_ref:
                cleaned, acts = self._chat_ref._execute_jarvis_tags_in_reply(st)
                if acts:
                    results.extend(acts)
            else:
                ok, msg = self.open_target(st)
                results.append(msg)
            time.sleep(0.5)

        if self.shimeji:
            self.shimeji.show_speech(f"[✓] Macro '{macro_name}' completada ({total}/{total}).")
        return True, "\n".join(results)

    def list_dir(self, folder=None):
        target = self.desktop_dir if not folder else folder.strip().strip('"').strip("'")
        if not os.path.isabs(target):
            cand = os.path.join(self.desktop_dir, target)
            if os.path.isdir(cand):
                target = cand
        if not os.path.isdir(target):
            return False, f"[!] No existe la carpeta '{target}'"
        try:
            all_files = os.listdir(target)
            items = all_files[:30]
            lines = [f"[*] Archivos en '{os.path.basename(target) or target}' ({len(all_files)} total):"]
            for item in items:
                ipath = os.path.join(target, item)
                is_dir = os.path.isdir(ipath)
                prefix = "[DIR] " if is_dir else "[FILE]"
                size = f" ({os.path.getsize(ipath)} B)" if not is_dir else ""
                lines.append(f"  {prefix} {item}{size}")
            if len(all_files) > 30:
                lines.append(f"  ... y {len(all_files) - 30} archivos mas.")
            return True, "\n".join(lines)
        except Exception as e:
            return False, f"[!] Error listando carpeta: {e}"

    def open_target(self, target):
        try:
            clean = target.strip().strip('"').strip("'")
            if not clean:
                return False, "[!] Dime qué archivo o programa abrir :v"

            # 1. URLs (Siempre Chrome o Brave, jamás Edge)
            if clean.startswith(("http://", "https://", "www.")):
                url = "https://" + clean if clean.startswith("www.") else clean
                open_web_url(url)
                return True, f"[+] Abriendo enlace: {url}"

            lower = clean.lower()

            # Bloqueo total de Edge y redirección a Chrome/Brave
            if lower in ("edge", "msedge", "microsoft edge", "abre edge", "abrir edge"):
                browsers = get_preferred_browsers()
                b_name = os.path.basename(browsers[0]) if browsers else "Chrome/Brave"
                open_web_url("https://www.google.com")
                return True, f"[!] Microsoft Edge está estrictamente BLOQUEADO.\nAbriendo {b_name} en su lugar :v"

            # Abrir navegador Chrome o Brave directamente
            if lower in ("brave", "chrome", "google chrome", "navegador", "browser"):
                browsers = get_preferred_browsers()
                if browsers:
                    try:
                        subprocess.Popen([browsers[0]])
                        return True, f"[+] Navegador abierto: {os.path.basename(browsers[0])} [OK]"
                    except Exception:
                        pass

            lower = clean.lower()

            # 2. Comandos personalizados del usuario
            if lower in self.custom_commands:
                return self.run_custom_command(self.custom_commands[lower])

            # 3. Alias de programas comunes
            cmd_target = self.PROGRAM_ALIASES.get(lower, clean)

            # Protocolos directos de Windows
            if cmd_target.startswith("ms-settings:") or cmd_target.startswith("steam:"):
                try:
                    os.startfile(cmd_target)
                    return True, f"[+] Abriendo: '{cmd_target}' [*]"
                except Exception:
                    pass

            # Si el alias es un comando WSL
            if cmd_target.lower().startswith("wsl"):
                try:
                    subprocess.Popen(f'start {cmd_target}', shell=True)
                    return True, f"[+] Abriendo terminal WSL:\n  -> {cmd_target}"
                except Exception as e:
                    return False, f"[!] Error abriendo WSL: {e}"

            # 4. Intentar resolver como archivo existente (incluyendo custom_paths)
            resolved = self.resolve_target(cmd_target, must_exist=True)
            if not resolved and cmd_target != clean:
                resolved = self.resolve_target(clean, must_exist=True)

            if not resolved:
                # Búsqueda rápida si no se halló en rutas directas
                matches = self.search_files(clean, max_results=1)
                if matches:
                    resolved = matches[0][1]

            if resolved and os.path.exists(resolved):
                try:
                    os.startfile(resolved)
                    return True, f"[+] Archivo abierto: '{os.path.basename(resolved)}'\n[Ruta: {resolved}]"
                except Exception as e:
                    return False, f"[!] Error abriendo archivo '{resolved}': {e}"

            # 5. Intentar abrir como programa o ejecutable del sistema
            try:
                os.startfile(cmd_target)
                return True, f"[+] Ejecutando programa: '{cmd_target}'"
            except Exception:
                pass

            # Probar lanzando mediante Windows shell
            try:
                subprocess.Popen(f'start "" "{cmd_target}"', shell=True)
                return True, f"[+] Lanzando: '{cmd_target}'"
            except Exception as e:
                return False, f"[!] No se pudo abrir ni ejecutar '{target}': {e}"
        except Exception as e:
            return False, f"[!] Error al abrir '{target}': {e}"

    def run_cmd(self, command_str):
        try:
            clean = command_str.strip()
            proc = subprocess.run(clean, shell=True, capture_output=True, text=True, timeout=12)
            out = proc.stdout.strip()
            err = proc.stderr.strip()
            res = out if out else err
            if not res:
                res = f"Comando ejecutado con codigo de salida {proc.returncode}"
            if len(res) > 1200:
                res = res[:1200] + "\n... [Salida truncada]"
            return True, f"[*] CMD: '{clean}'\n{res}"
        except subprocess.TimeoutExpired:
            return False, "[!] El comando tardo demasiado (timeout 12s)"
        except Exception as e:
            return False, f"[!] Error ejecutando comando CMD: {e}"

    def parse_and_execute(self, text):
        raw = text.strip()
        if not raw:
            return False, "", ""
        lower = raw.lower()

        # Atajos y lista de comandos prefabricados
        if raw in ("/shortcuts", "/atajos", "/comandos", "/helpcmd", "/cmdhelp"):
            return True, self.get_shortcuts_help(), "Guía de atajos de Windows [OK]"

        # Script runner BAT (/bat)
        if raw.startswith("/bat "):
            code = raw[5:].strip()
            ok, msg = self.run_bat(code)
            return True, msg, "Script BAT ejecutado [OK]"

        # Comprobar actualizaciones manuales
        if raw in ("/update", "/actualizar", "/updates", "/version") or lower in ("actualizar shimeji", "buscar actualizacion", "buscar actualizaciones", "hay actualizacion"):
            check_for_updates(self.shimeji, is_manual=True)
            return True, f"[*] Comprobando actualizaciones en GitHub para PinkChan v{APP_VERSION}...", "Buscando actualizaciones [OK]"

        # Ajuste de tamaño personalizado o escala (100x, 2x, 256, etc.)
        m_size = re.search(r'^(?:/(?:size|tamano|tamaño|scale|escala)\s+([0-9\.]+(?:x|X)?)|(?:(?:hey\s+)?(?:cambia(?:r)?|pon(?:er)?|ajusta(?:r)?)\s+(?:el\s+)?(?:tamaño|tamano|escala)\s+(?:a\s+)?([0-9\.]+(?:x|X)?)))$', raw, re.IGNORECASE)
        if m_size:
            val_str = (m_size.group(1) or m_size.group(2)).strip().lower()
            if self.shimeji:
                if val_str.endswith('x'):
                    try:
                        mult = float(val_str[:-1])
                        ok, msg = self.shimeji.set_scale(mult)
                    except Exception as e:
                        ok, msg = False, str(e)
                else:
                    try:
                        sz = int(float(val_str))
                        ok, msg = self.shimeji.set_size(sz)
                    except Exception as e:
                        ok, msg = False, str(e)
                return True, f"[+] {msg}", "Tamaño actualizado [OK]"
            return False, "Shimeji no disponible", "Error"

        # Configuración de burbuja (opacidad y bordes)
        m_bubble = re.search(r'^/bubble\s+(alpha|opacidad|border|borde)\s+(.+)$', raw, re.IGNORECASE)
        if m_bubble:
            b_prop = m_bubble.group(1).lower()
            b_val = m_bubble.group(2).strip().lower()
            tm = self.shimeji.theme_manager if self.shimeji else None
            if tm:
                if b_prop in ("alpha", "opacidad"):
                    try:
                        num = float(b_val.replace("%", ""))
                        if num > 1.0:
                            num = num / 100.0
                        tm.set_bubble_opacity(num)
                        return True, f"[+] Opacidad de burbuja establecida en {int(num*100)}%", "Burbuja actualizada [OK]"
                    except Exception:
                        return False, "Valor numérico inválido (ej: 80 o 0.8)", "Error"
                elif b_prop in ("border", "borde"):
                    enable = b_val in ("on", "si", "sí", "true", "1", "activar")
                    tm.set_bubble_border(enable)
                    state_str = "activados" if enable else "desactivados"
                    return True, f"[+] Bordes de burbuja {state_str}", "Burbuja actualizada [OK]"

        # Forzar cierre de procesos (/kill <proceso> o matar <proceso>)
        m_kill = re.search(r'^(?:/kill\s+([a-zA-Z0-9_\-\.]+)|(?:hey\s+)?(?:mata(?:r)?|cierra|cerrar|termina(?:r)?)\s+(?:el\s+)?(?:proceso\s+)?([a-zA-Z0-9_\-\.]+))$', raw, re.IGNORECASE)
        if m_kill:
            pname = (m_kill.group(1) or m_kill.group(2)).strip()
            if not pname.lower().endswith((".exe", ".msc")):
                pname += ".exe"
            ok, msg = self.run_cmd(f"taskkill /f /im {pname}")
            return True, msg, f"Proceso '{pname}' terminado"

        # Listado y cambio de Skins / Personajes
        if raw in ("/skins", "/personajes", "/skinlist") or lower in ("ver skins", "lista de skins", "que skins hay", "cuales skins hay"):
            cur = getattr(self.shimeji, "current_skin", "Bocchi") if self.shimeji else "Bocchi"
            lines = [
                "╔════════════════════════════════════════════════════════════╗",
                "║             [+] SKINS & PERSONAJES DISPONIBLES              ║",
                "╚════════════════════════════════════════════════════════════╝\n"
            ]
            for s in SKIN_NAMES:
                meta = SKIN_META.get(s, {})
                chk = "  [ACTIVA]" if s == cur else ""
                lines.append(f"• {meta.get('display', s)}{chk}")
                lines.append(f"  └─ {meta.get('tagline', '')} -> Usa: /skin {s.lower()}\n")
            lines.append("Tip: También puedes decir 'pon a konata', 'usa los konasprites', 'pon a monika', etc.")
            return True, "\n".join(lines), "Aquí están las skins disponibles [*]"

        # Curar y alimentar Shimeji
        if raw.strip().lower() in ("/heal", "/curar", "/vida", "/salud", "curar", "curate", "curar shimeji", "dar comida", "alimentar"):
            if self.shimeji:
                self.shimeji.heal(100, "snack y golosinas")
            return True, "[+] ¡Salud restaurada al 100%! [HP: 100/100]", "Shimeji curado [OK]"

        # Lanzar Shimeji por los aires (Fling physics)
        if raw.strip().lower() in ("/fling", "/lanzar", "/volar", "lanzate", "vuela", "lanzar shimeji", "avientate"):
            if self.shimeji:
                self.shimeji.fling_upwards()
            return True, "[+] ¡Lanzando Shimeji por los aires con física elástica!", "Fling activado [OK]"

        # Ejecutar acción especial del personaje
        if raw.startswith("/accion ") or raw.startswith("/action ") or lower in ("accion especial", "haz tu accion especial", "haz una pose", "pose"):
            if self.shimeji:
                self.shimeji.trigger_random_custom_action()
            return True, "[+] Ejecutando acción especial del personaje", "Acción especial activada [OK]"

        # Soltar item / snack / comida del sprite sheet items.png
        if raw.strip().lower() in ("/item", "/items", "/snack", "/comida", "/alimento", "tirar item", "soltar item", "dame comida", "comida", "snack"):
            if self.shimeji:
                self.shimeji.drop_random_item()
            return True, "[+] ¡Soltando un objeto/snack del sprite sheet cerca del Shimeji!", "Item soltado [OK]"

        # Comando de cambio de skin
        m_skin = re.search(r'^(?:/skin\s+([a-zA-Z0-9_\-]+)|(?:(?:hey|porfa)\s+)?(?:pon(?:er)?|cambia(?:r)?|usa(?:r)?|activa(?:r)?)\s+(?:(?:a|al|la\s+skin\s+(?:de|a)|de\s+skin\s+a|los|el)\s+)?([a-zA-Z0-9_\-]+(?:\s+[a-zA-Z0-9_\-]+)?))$', raw, re.IGNORECASE)
        if m_skin:
            target_skin = (m_skin.group(1) or m_skin.group(2)).strip().lower()
            if target_skin not in ("el modo troll", "modo troll", "musica", "youtube", "arch", "ubuntu", "debian"):
                alias_to_skin = {
                    "bocchi": "Bocchi",
                    "hitori": "Bocchi",
                    "konata": "Konata",
                    "kona": "Konata",
                    "konasprites": "Konata",
                    "lucky star": "Konata",
                    "luckystar": "Konata",
                    "monika": "Monika",
                    "moni": "Monika",
                    "natsuki": "Natsuki",
                    "natsu": "Natsuki",
                    "sayori": "Sayori",
                    "sayo": "Sayori",
                    "yuri": "Yuri",
                    "hachi": "Hachi",
                    "hachiware": "Hachi",
                    "usagi": "Usagi",
                    "conejo": "Usagi",
                    "pusheen": "Pusheen",
                    "cat": "Pusheen",
                    "gato": "Pusheen",
                    "gatita": "Pusheen",
                }
                found_skin = alias_to_skin.get(target_skin)
                if not found_skin:
                    for sn in SKIN_NAMES:
                        if sn.lower() == target_skin:
                            found_skin = sn
                            break
                if found_skin and self.shimeji:
                    ok, msg = self.shimeji.set_skin(found_skin)
                    return True, msg, f"Skin {found_skin} activada [OK]"

        # Pacman en Arch Linux / WSL (sudo pacman -S <programa> o sudo pacman -Syu)
        if re.search(r'^(?:(?:hey\s+)?(?:sudo\s+)?pacman\s+-S[yYuU]+|actualizar\s+(?:arch|sistema|pacman))$', raw, re.IGNORECASE):
            wt_avail = shutil.which("wt") is not None
            cmd = 'start wt wsl -d archlinux sudo pacman -Syu' if wt_avail else 'start wsl -d archlinux sudo pacman -Syu'
            subprocess.Popen(cmd, shell=True)
            return True, "[+] Lanzando actualización completa del sistema en Arch Linux:\n  $ sudo pacman -Syu", "Actualizando Arch Linux [OK]"

        m_pacman = re.search(r'^(?:(?:hey\s+)?(?:sudo\s+)?pacman(?:\s+-S[yYuU]*)?|\/pacman|(?:hey\s+)?(?:instala(?:r)?|descarga(?:r)?)\s+(?:en\s+arch|con\s+pacman))\s+([a-zA-Z0-9_\-\.\+]+)$', raw, re.IGNORECASE)
        if m_pacman:
            pkg = m_pacman.group(1).strip()
            wt_avail = shutil.which("wt") is not None
            cmd = f'start wt wsl -d archlinux sudo pacman -S {pkg}' if wt_avail else f'start wsl -d archlinux sudo pacman -S {pkg}'
            subprocess.Popen(cmd, shell=True)
            return True, f"[+] Lanzando terminal interactiva para instalar con pacman en WSL Arch Linux:\n  $ sudo pacman -S {pkg}", f"Instalando {pkg} en Arch [OK]"

        # Winget en Windows (winget install <programa> / winget search <programa> / winget upgrade)
        if re.search(r'^(?:(?:hey\s+)?winget\s+(?:upgrade|update)|actualizar\s+(?:programas|apps|windows))$', raw, re.IGNORECASE):
            wt_avail = shutil.which("wt") is not None
            cmd = 'start wt winget upgrade --all' if wt_avail else 'start cmd /k winget upgrade --all'
            subprocess.Popen(cmd, shell=True)
            return True, "[+] Lanzando actualización de aplicaciones en Windows con winget:\n  > winget upgrade --all", "Actualizando aplicaciones [OK]"

        m_winget_search = re.search(r'^(?:(?:hey\s+)?winget\s+search|\/winget\s+search|(?:hey\s+)?(?:busca(?:r)?|encuentra)\s+(?:en\s+winget|programa))\s+([a-zA-Z0-9_\-\.\+]+)$', raw, re.IGNORECASE)
        if m_winget_search:
            pkg = m_winget_search.group(1).strip()
            return self.run_cmd(f"winget search {pkg}")

        m_winget_install = re.search(r'^(?:(?:hey\s+)?winget(?:\s+install)?|\/winget|(?:hey\s+)?(?:instala(?:r)?|descarga(?:r)?)\s+(?:con\s+winget|en\s+windows))\s+([a-zA-Z0-9_\-\.\+]+)$', raw, re.IGNORECASE)
        if m_winget_install:
            pkg = m_winget_install.group(1).strip()
            wt_avail = shutil.which("wt") is not None
            cmd = f'start wt winget install {pkg} --accept-source-agreements --accept-package-agreements' if wt_avail else f'start cmd /k winget install {pkg} --accept-source-agreements --accept-package-agreements'
            subprocess.Popen(cmd, shell=True)
            return True, f"[+] Iniciando instalación con winget en Windows:\n  > winget install {pkg}", f"Instalando {pkg} con winget [OK]"

        # Ejecución directa de comandos en WSL Arch (ej: wsl ls, arch uname -a)
        m_wsl_cmd = re.search(r'^(?:(?:wsl|arch)\s+(?:run\s+|exec\s+)?(.+))$', raw, re.IGNORECASE)
        if m_wsl_cmd and not raw.lower().startswith(("wsl -", "wsl status", "wsl distros", "wsl arch")):
            inner_cmd = m_wsl_cmd.group(1).strip()
            return self.run_cmd(f"wsl -d archlinux {inner_cmd}")

        clean_trigger = lower
        for prefix in ("hey ", "porfa ", "favor de "):
            if clean_trigger.startswith(prefix):
                clean_trigger = clean_trigger[len(prefix):].strip()

        # Ranuras de comandos prefabricados con [X] (agregar-abrirapp-x, abrirapp-x, etc.)
        m_add_slot = re.match(r'^(?:agregar-)?(abrirapp|ejecutarcomando|decir|buscar|accion|crearcarpeta)[-: ]\s*(.+)$', clean_trigger, re.IGNORECASE)
        if m_add_slot:
            slot_type = m_add_slot.group(1).lower()
            slot_val  = m_add_slot.group(2).strip()
            is_adding = clean_trigger.lower().startswith("agregar-")

            if slot_type == "abrirapp":
                if is_adding:
                    self.set_custom_command(f"abrirapp-{slot_val.lower()}", f"abre {slot_val}")
                    return True, f"[+] Ranura agregada: abrirapp-{slot_val}\nAhora puedes ejecutarlo escribiendo 'abrirapp-{slot_val}'", "Ranura guardada [OK]"
                ok, msg = self.open_target(slot_val)
                return True, msg, f"Abriendo {slot_val} [>]"

            elif slot_type == "ejecutarcomando":
                if is_adding:
                    self.set_custom_command(f"ejecutarcomando-{slot_val.lower()}", f"cmd {slot_val}")
                    return True, f"[+] Ranura agregada: ejecutarcomando-{slot_val}\nAhora puedes ejecutarlo con 'ejecutarcomando-{slot_val}'", "Ranura guardada [OK]"
                return self.run_cmd(slot_val)

            elif slot_type == "decir":
                if is_adding:
                    self.set_custom_command(f"decir-{slot_val.lower()}", f"echo {slot_val}")
                    return True, f"[+] Ranura agregada: decir-{slot_val}", "Ranura guardada [OK]"
                if self.shimeji:
                    self.shimeji.show_speech(slot_val)
                return True, f"[*] Shimeji dice: \"{slot_val}\"", "Mensaje mostrado [OK]"

            elif slot_type == "buscar":
                if is_adding:
                    self.set_custom_command(f"buscar-{slot_val.lower()}", f"buscar {slot_val}")
                    return True, f"[+] Ranura agregada: buscar-{slot_val}", "Ranura guardada [OK]"
                url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(slot_val)}"
                open_web_url(url)
                return True, f"[+] Buscando '{slot_val}' en la web", "Búsqueda lanzada [>]"

            elif slot_type == "accion":
                act_norm = slot_val.lower()
                if "guitar" in act_norm:
                    if self.shimeji: self.shimeji.force_action_by_name("guitar")
                    return True, "[+] Tocando la guitarra en vivo!", "Accion [OK]"
                elif "caja" in act_norm or "box" in act_norm:
                    if self.shimeji: self.shimeji.force_action_by_name("box")
                    return True, "[+] Modo caja de carton activado!", "Accion [OK]"
                elif "bail" in act_norm or "dance" in act_norm:
                    if self.shimeji: self.shimeji.force_action_by_name("dance")
                    return True, "[+] Bailando al ritmo!", "Accion [OK]"
                elif "item" in act_norm:
                    if self.shimeji: self.shimeji.drop_random_item()
                    return True, "[+] Soltando snack/item!", "Item [OK]"
                else:
                    return True, f"[*] Accion '{slot_val}' ejecutada", "Accion [OK]"

            elif slot_type == "crearcarpeta":
                res, msg = self.create_folder(slot_val)
                return res, msg, "Carpeta creada [OK]"

        # Atajos prefabricados de sistema / CMD / PowerShell / BAT
        res_pre = self.execute_prefabricated_shortcut(clean_trigger)
        if res_pre is not None:
            ok, msg = res_pre
            return True, msg, "Ejecutado [OK]"

        # Chequeo directo de alias de programas comunes sin necesidad de escribir 'abre'
        if clean_trigger in self.PROGRAM_ALIASES:
            ok, msg = self.open_target(clean_trigger)
            return True, msg, f"Abriendo {clean_trigger[:20]} [>]"

        # 0. Comprobación directa de comandos personalizados guardados
        # Chequear coincidencia exacta o sin prefijos como "hey ", "abre ", "corre ", "inicia "

        if clean_trigger in self.custom_commands:
            ok, msg = self.run_custom_command(self.custom_commands[clean_trigger])
            return True, msg, f"Orden '{clean_trigger[:20]}' ejecutada [>]"

        for act_prefix in ("abre ", "abrir ", "corre ", "correr ", "ejecuta ", "ejecutar ", "inicia ", "iniciar "):
            if clean_trigger.startswith(act_prefix):
                sub = clean_trigger[len(act_prefix):].strip()
                if sub in self.custom_commands:
                    ok, msg = self.run_custom_command(self.custom_commands[sub])
                    return True, msg, f"Orden '{sub[:20]}' ejecutada [>]"

        # 1. Comandos de control del Modo Troll
        m_troll_on = re.search(r'^(?:/troll\s+on|(?:hey\s+)?(?:activa(?:r)?|pon|enciende)\s+(?:el\s+)?modo\s+troll)', raw, re.IGNORECASE)
        if m_troll_on:
            if self.shimeji:
                self.shimeji.toggle_troll_mode(True)
            return True, "[!] MODO TROLL ACTIVADO. Cuidado con tus ventanas y alertas 7w7", "¡Modo troll activado! 7w7"

        m_troll_off = re.search(r'^(?:/troll\s+off|(?:hey\s+)?(?:desactiva(?:r)?|apaga|quita)\s+(?:el\s+)?modo\s+troll)', raw, re.IGNORECASE)
        if m_troll_off:
            if self.shimeji:
                self.shimeji.toggle_troll_mode(False)
            return True, "[o] Modo Troll desactivado. Bocchi en modo JARVIS eficiente y pacífico.", "Modo troll desactivado UwU"

        # 2. Gestión de comandos y alias personalizados
        # Slash: /alias o /addcmd trigger = comando
        if raw.startswith(("/alias ", "/addcmd ")):
            body = raw.split(maxsplit=1)[1].strip()
            if "=" in body:
                parts = body.split("=", 1)
                ok, msg = self.add_custom_command(parts[0], parts[1])
                return True, msg, "Comando guardado [*]"
            elif "->" in body:
                parts = body.split("->", 1)
                ok, msg = self.add_custom_command(parts[0], parts[1])
                return True, msg, "Comando guardado [*]"
            return True, "[!] Uso: /alias <frase_activadora> = <comando_a_ejecutar>\nEjemplo: /alias abre arch = wsl -d archlinux", "Escribe el alias wei :v"

        if raw.startswith(("/delcmd ", "/unalias ")):
            trig = raw.split(maxsplit=1)[1].strip()
            ok, msg = self.delete_custom_command(trig)
            return True, msg, "Comando eliminado [-]" if ok else "No encontre ese comando :v"

        if raw in ("/listcmd", "/aliases", "/alias", "/comandos"):
            ok, msg = self.list_custom_commands()
            return True, msg, "Ahi estan tus comandos [*]"

        # Lenguaje natural para agregar/borrar/listar comandos
        m_add_cmd_nat = re.search(r'^(?:(?:hey\s+)?(?:agrega(?:r)?|guarda(?:r)?|crea(?:r)?|asocia(?:r)?)\s+(?:el\s+)?(?:comando|alias)\s+[\'"]?(.+?)[\'"]?\s+(?:que\s+(?:corra|ejecute)|como|con|=|->)\s+[\'"]?(.+?)[\'"]?)$', raw, re.IGNORECASE)
        if m_add_cmd_nat:
            t, c = m_add_cmd_nat.group(1).strip(), m_add_cmd_nat.group(2).strip()
            ok, msg = self.add_custom_command(t, c)
            return True, msg, "Comando guardado [*]"

        m_when_cmd_nat = re.search(r'^(?:(?:hey\s+)?cuando\s+diga\s+[\'"]?(.+?)[\'"]?\s+(?:ejecuta|corre|abre|haz)\s+[\'"]?(.+?)[\'"]?)$', raw, re.IGNORECASE)
        if m_when_cmd_nat:
            t, c = m_when_cmd_nat.group(1).strip(), m_when_cmd_nat.group(2).strip()
            ok, msg = self.add_custom_command(t, c)
            return True, msg, "Comando guardado [*]"

        m_del_cmd_nat = re.search(r'^(?:(?:hey\s+)?(?:borra(?:r)?|elimina(?:r)?)\s+(?:el\s+)?(?:comando|alias)\s+[\'"]?(.+?)[\'"]?)$', raw, re.IGNORECASE)
        if m_del_cmd_nat:
            t = m_del_cmd_nat.group(1).strip()
            ok, msg = self.delete_custom_command(t)
            return True, msg, "Comando borrado [-]" if ok else "No encontre ese comando :v"

        m_list_cmd_nat = re.search(r'^(?:(?:hey\s+)?(?:lista(?:r)?|muestra(?:r)?|ver|qu[eé])\s+(?:los\s+)?(?:comandos\s+personalizados|aliases|alias))$', raw, re.IGNORECASE)
        if m_list_cmd_nat:
            ok, msg = self.list_custom_commands()
            return True, msg, "Aqui estan tus comandos [*]"

        # 3. Gestión de rutas y carpetas personalizadas (custom_paths)
        if raw.startswith("/addpath "):
            f = raw.split(maxsplit=1)[1].strip()
            ok, msg = self.add_custom_path(f)
            return True, msg, "Ruta añadida [*]" if ok else "Ruta invalida :v"

        if raw.startswith("/delpath "):
            f = raw.split(maxsplit=1)[1].strip()
            ok, msg = self.delete_custom_path(f)
            return True, msg, "Ruta eliminada [-]" if ok else "Ruta no encontrada :v"

        if raw in ("/listpaths", "/paths", "/rutas"):
            ok, msg = self.list_custom_paths()
            return True, msg, "Aqui estan las rutas [*]"

        m_add_path_nat = re.search(r'^(?:(?:hey\s+)?(?:agrega(?:r)?|a[nñ]ade|guarda(?:r)?)\s+(?:la\s+)?(?:ruta|carpeta|path)\s+(.+))', raw, re.IGNORECASE)
        if m_add_path_nat:
            f = m_add_path_nat.group(1).strip()
            ok, msg = self.add_custom_path(f)
            return True, msg, "Ruta añadida [*]" if ok else "Ruta invalida :v"

        m_del_path_nat = re.search(r'^(?:(?:hey\s+)?(?:borra(?:r)?|elimina(?:r)?)\s+(?:la\s+)?(?:ruta|carpeta|path)\s+(.+))', raw, re.IGNORECASE)
        if m_del_path_nat:
            f = m_del_path_nat.group(1).strip()
            ok, msg = self.delete_custom_path(f)
            return True, msg, "Ruta eliminada [-]" if ok else "Ruta no encontrada :v"

        m_list_path_nat = re.search(r'^(?:(?:hey\s+)?(?:lista(?:r)?|muestra(?:r)?|ver|qu[eé])\s+(?:las\s+)?(?:rutas|carpetas|paths))$', raw, re.IGNORECASE)
        if m_list_path_nat:
            ok, msg = self.list_custom_paths()
            return True, msg, "Aqui estan las rutas [*]"

        # 4. Comandos directos de PowerShell
        if raw.startswith(("/ps ", "/powershell ")):
            cmd = raw.split(maxsplit=1)[1].strip()
            ok, msg = self.run_powershell(cmd)
            return True, msg, "PowerShell ejecutado [PS]"

        m_ps_nat = re.search(r'^(?:(?:hey\s+)?(?:ejecuta|corre)\s+en\s+powershell\s+(.+))', raw, re.IGNORECASE)
        if m_ps_nat:
            cmd = m_ps_nat.group(1).strip()
            ok, msg = self.run_powershell(cmd)
            return True, msg, "PowerShell ejecutado [PS]"

        # 5. Búsqueda en la web / Google / YouTube
        m_yt_nat = re.search(r'^(?:(?:hey\s+)?(?:busca(?:r)?\s+(?:en\s+)?(?:youtube|yt)|pon\s+(?:en\s+)?youtube)\s+(.+))', raw, re.IGNORECASE)
        if m_yt_nat:
            q = m_yt_nat.group(1).strip()
            ok, msg = self.search_web(q, engine="youtube")
            return True, msg, f"Buscando en YouTube: {q[:25]}"

        m_web_nat = re.search(r'^(?:(?:hey\s+)?(?:busca(?:r)?\s+(?:en\s+(?:la\s+)?(?:web|internet|google|chrome)|por\s+internet)\s+(.+)|googlea(?:r)?\s+(.+)))', raw, re.IGNORECASE)
        if m_web_nat:
            q = (m_web_nat.group(1) or m_web_nat.group(2) or "").strip()
            ok, msg = self.search_web(q, engine="google")
            return True, msg, f"Buscando en Google: {q[:25]}"

        if raw.startswith(("/web ", "/google ", "/searchweb ")):
            q = raw.split(maxsplit=1)[1].strip()
            ok, msg = self.search_web(q, engine="google")
            return True, msg, f"Buscando en Google: {q[:25]}"

        if raw.startswith(("/yt ", "/youtube ")):
            q = raw.split(maxsplit=1)[1].strip()
            ok, msg = self.search_web(q, engine="youtube")
            return True, msg, f"Buscando en YouTube: {q[:25]}"

        # 6. Buscar archivos en el equipo (incluyendo custom_paths)
        m_search_nat = re.search(r'^(?:(?:hey\s+)?(?:busca(?:r)?|encuentra|d[oó]nde\s+est[aá])\s+(?:el\s+archivo\s+|archivo\s+|el\s+documento\s+|documento\s+)?(.+))', raw, re.IGNORECASE)
        if m_search_nat and not re.search(r'^(?:(?:hey\s+)?busca(?:r)?\s+en\s+(?:web|internet|google|chrome|youtube|yt))', raw, re.IGNORECASE):
            pattern = m_search_nat.group(1).strip().strip('"').strip("'")
            ok, msg = self.search_file(pattern)
            speech = f"Resultados para '{pattern[:20]}' [*]" if ok else "No encontre ese archivo :v"
            return True, msg, speech

        if raw.startswith(("/find ", "/search ", "/buscar ", "/where ")):
            parts = raw.split(maxsplit=1)
            if len(parts) >= 2:
                ok, msg = self.search_file(parts[1].strip())
                speech = f"Resultados para '{parts[1][:20]}' [*]" if ok else "No encontre ese archivo :v"
                return True, msg, speech
            return True, "[!] Uso: /find <nombre_o_patron>", "Dime que archivo busco :v"

        # 7. Abrir programas, archivos o URLs
        m_open_nat = re.search(r'^(?:(?:hey\s+)?(?:abre|abrir|ejecuta(?:r)?|inicia(?:r)?|lanza(?:r)?)\s+(?:el\s+programa\s+|la\s+app\s+|la\s+aplicaci[oó]n\s+|el\s+archivo\s+|el\s+documento\s+|el\s+|la\s+)?(.+))', raw, re.IGNORECASE)
        if m_open_nat:
            target = m_open_nat.group(1).strip().strip('"').strip("'")
            ok, msg = self.open_target(target)
            speech = f"Abriendo '{target[:20]}' [>]" if ok else f"No pude abrir '{target[:20]}' :v"
            return True, msg, speech

        if raw.startswith(("/open ", "/abrir ", "/start ", "/launch ")):
            parts = raw.split(maxsplit=1)
            if len(parts) >= 2:
                ok, msg = self.open_target(parts[1].strip())
                speech = f"Abriendo '{parts[1][:20]}' [>]" if ok else f"No pude abrir '{parts[1][:20]}' :v"
                return True, msg, speech
            return True, "[!] Uso: /open <archivo_o_programa>", "Dime que abrir :v"

        # 8. Renombrar archivos (Ej: "hey haz que x archivo ahora se llame caca", "/ren x y", "renombra x a y")
        m_ren_nat = re.search(r'(?:(?:hey\s+)?haz\s+que\s+(?:el\s+archivo\s+)?([^\s,]+)\s+ahora\s+se\s+llame\s+([^\s,]+))', raw, re.IGNORECASE)
        if m_ren_nat:
            old_f, new_f = m_ren_nat.group(1), m_ren_nat.group(2)
            ok, msg = self.rename_file(old_f, new_f)
            speech = f"Renombrado '{old_f}' a '{new_f}' [OK]" if ok else "No pude renombrarlo :v"
            return True, msg, speech

        m_ren_verb = re.search(r'^(?:renombra(?:r)?|cambia(?:r)?\s+(?:el\s+)?nombre\s+de)\s+(?:el\s+archivo\s+)?([^\s,]+)\s+(?:a|por|como)\s+([^\s,]+)', raw, re.IGNORECASE)
        if m_ren_verb:
            old_f, new_f = m_ren_verb.group(1), m_ren_verb.group(2)
            ok, msg = self.rename_file(old_f, new_f)
            speech = f"Renombrado '{old_f}' a '{new_f}' [OK]" if ok else "No pude renombrarlo :v"
            return True, msg, speech

        if raw.startswith(("/ren ", "/rename ", "/renombrar ")):
            parts = raw.split(maxsplit=2)
            if len(parts) >= 3:
                ok, msg = self.rename_file(parts[1], parts[2])
                speech = f"Renombrado '{parts[1]}' a '{parts[2]}' [OK]" if ok else "No pude renombrarlo :v"
                return True, msg, speech
            else:
                return True, "[!] Uso: /rename <archivo_actual> <nuevo_nombre>", "Pon el nombre viejo y nuevo :v"

        # 9. Crear archivos
        m_create_nat = re.search(r'^(?:(?:hey\s+)?crea(?:r)?\s+(?:un\s+archivo\s+)?(?:llamado\s+)?([^\s,]+)(?:\s+(?:con|que\s+diga|con\s+el\s+texto)\s+(.+))?)$', raw, re.IGNORECASE)
        if m_create_nat:
            fname = m_create_nat.group(1)
            content = m_create_nat.group(2) or ""
            ok, msg = self.create_file(fname, content)
            speech = f"Archivo '{fname}' creado [*]" if ok else "Error creando archivo :v"
            return True, msg, speech

        if raw.startswith(("/create ", "/crear ", "/touch ")):
            parts = raw.split(maxsplit=2)
            fname = parts[1] if len(parts) > 1 else ""
            content = parts[2] if len(parts) > 2 else ""
            if fname:
                ok, msg = self.create_file(fname, content)
                speech = f"Archivo '{fname}' creado [*]" if ok else "Error creando archivo :v"
                return True, msg, speech
            return True, "[!] Uso: /create <nombre_archivo> [contenido opcional]", "Dime que nombre ponerle :v"

        # 10. Escribir / Modificar archivos
        m_write_nat = re.search(r'^(?:(?:hey\s+)?escribe\s+[\'"]?(.+?)[\'"]?\s+en\s+([^\s,]+))', raw, re.IGNORECASE)
        if m_write_nat:
            content, fname = m_write_nat.group(1), m_write_nat.group(2)
            ok, msg = self.write_file(fname, content, append=False)
            speech = f"Modificado '{fname}' [OK]" if ok else "Error escribiendo :v"
            return True, msg, speech

        m_append_nat = re.search(r'^(?:(?:hey\s+)?agrega(?:r)?\s+[\'"]?(.+?)[\'"]?\s+a\s+([^\s,]+))', raw, re.IGNORECASE)
        if m_append_nat:
            content, fname = m_append_nat.group(1), m_append_nat.group(2)
            ok, msg = self.write_file(fname, content, append=True)
            speech = f"Texto agregado a '{fname}' [OK]" if ok else "Error agregando texto :v"
            return True, msg, speech

        if raw.startswith(("/write ", "/escribir ", "/edit ")):
            parts = raw.split(maxsplit=2)
            if len(parts) >= 3:
                ok, msg = self.write_file(parts[1], parts[2], append=False)
                speech = f"Escrito en '{parts[1]}' [OK]" if ok else "Error escribiendo :v"
                return True, msg, speech
            return True, "[!] Uso: /write <archivo> <contenido>", "Falta el archivo o texto :v"

        if raw.startswith(("/append ", "/agregar ", "/add ")):
            parts = raw.split(maxsplit=2)
            if len(parts) >= 3:
                ok, msg = self.write_file(parts[1], parts[2], append=True)
                speech = f"Agregado a '{parts[1]}' [OK]" if ok else "Error agregando texto :v"
                return True, msg, speech
            return True, "[!] Uso: /append <archivo> <contenido>", "Falta el archivo o texto :v"

        # 11. Leer archivos
        m_read_nat = re.search(r'^(?:(?:hey\s+)?(?:lee(?:r)?|qu[eé]\s+dice|muestra(?:r)?)\s+(?:el\s+archivo\s+)?([^\s,]+))', raw, re.IGNORECASE)
        if m_read_nat:
            fname = m_read_nat.group(1)
            ok, msg = self.read_file(fname)
            speech = f"Ahi tienes '{fname}' [OK]" if ok else "No encontre ese archivo :v"
            return True, msg, speech

        if raw.startswith(("/read ", "/leer ", "/cat ")):
            parts = raw.split(maxsplit=1)
            if len(parts) >= 2:
                ok, msg = self.read_file(parts[1])
                speech = f"Ahi tienes '{parts[1]}' [OK]" if ok else "No encontre ese archivo :v"
                return True, msg, speech
            return True, "[!] Uso: /read <archivo>", "Cual archivo leo wei? :v"

        # 12. Borrar archivos
        m_del_nat = re.search(r'^(?:(?:hey\s+)?(?:borra(?:r)?|elimina(?:r)?)\s+(?:el\s+archivo\s+)?([^\s,]+))', raw, re.IGNORECASE)
        if m_del_nat:
            fname = m_del_nat.group(1)
            ok, msg = self.delete_file(fname)
            speech = f"Borrado '{fname}' [-]" if ok else "No pude borrarlo :v"
            return True, msg, speech

        if raw.startswith(("/del ", "/delete ", "/borrar ", "/rm ")):
            parts = raw.split(maxsplit=1)
            if len(parts) >= 2:
                ok, msg = self.delete_file(parts[1])
                speech = f"Borrado '{parts[1]}' [-]" if ok else "No pude borrarlo :v"
                return True, msg, speech
            return True, "[!] Uso: /delete <archivo>", "Dime que archivo borrar :v"

        # 13. Listar archivos
        m_list_nat = re.search(r'^(?:(?:hey\s+)?(?:lista(?:r)?\s+(?:archivos|carpeta)|qu[eé]\s+archivos\s+hay)(?:\s+(?:en\s+)?(.+))?)', raw, re.IGNORECASE)
        if m_list_nat:
            folder = m_list_nat.group(1)
            ok, msg = self.list_dir(folder)
            speech = "Aqui estan tus archivos [*]" if ok else "Carpeta no encontrada :v"
            return True, msg, speech

        if raw in ("/list", "/dir", "/ls") or raw.startswith(("/list ", "/dir ", "/ls ")):
            parts = raw.split(maxsplit=1)
            folder = parts[1] if len(parts) > 1 else None
            ok, msg = self.list_dir(folder)
            speech = "Aqui estan tus archivos [*]" if ok else "Carpeta no encontrada :v"
            return True, msg, speech

        # 14. Ejecutar comandos directos de CMD
        if raw.startswith(("/cmd ", "/exec ")):
            parts = raw.split(maxsplit=1)
            if len(parts) >= 2:
                ok, msg = self.run_cmd(parts[1])
                speech = "Comando ejecutado [CMD]" if ok else "Fallo el comando :v"
                return True, msg, speech
            return True, "[!] Uso: /cmd <comando de Windows>", "Escribe el comando sokete :v"

        # 15. Comandos de fondo del chat
        if raw.lower() in ("/fondo", "/bg", "/wallpaper") or re.search(r'^(?:(?:hey\s+)?(?:cambia(?:r)?|pon(?:er)?|elige)\s+(?:el\s+)?fondo)', raw, re.IGNORECASE):
            if self.shimeji and getattr(self.shimeji, "chat_win", None):
                self.shimeji.chat_win.pick_chat_bg()
                return True, "[*] Selector de fondo abierto.", "Elige una foto o gif kiut :v"
            return True, "[!] Abre la ventana de chat para cambiar el fondo.", ""

        if raw.lower() in ("/fondo clear", "/bg clear", "/delfondo", "/quitarfondo") or re.search(r'^(?:(?:hey\s+)?(?:quita(?:r)?|borra(?:r)?)\s+(?:el\s+)?fondo)', raw, re.IGNORECASE):
            if self.shimeji and getattr(self.shimeji, "chat_win", None):
                self.shimeji.chat_win.clear_chat_bg()
                return True, "[-] Fondo de chat quitado.", "Listo, sin fondo UwU"
            return True, "[!] Abre la ventana de chat para quitar el fondo.", ""

        # 16. Comandos de travesuras directos
        if raw.lower() in ("/bsod", "/bluescreen", "/pantallazo") or re.search(r'^(?:(?:hey\s+)?(?:dame|haz|pon|simula)\s+(?:un\s+)?(?:pantallazo\s+azul|bsod))', raw, re.IGNORECASE):
            if self.shimeji:
                self.shimeji.troll_bluescreen()
                return True, "[!] ¡PANTALLAZO AZUL INICIADO! D: Bocchi ataca de nuevo...", "¡PANTALLAZO AZUL! :v"
            return True, "[!] Bocchi no está disponible.", ""

        if raw.lower() in ("/shake", "/sacudir") or re.search(r'^(?:(?:hey\s+)?(?:sacude|tiembla)\s+(?:la\s+)?ventana)', raw, re.IGNORECASE):
            if self.shimeji:
                self.shimeji.troll_shake_window()
                return True, "[>] Ventana sacudida exitosamente.", "¡Terremoto! 7w7"
            return True, "[!] Bocchi no está disponible.", ""

        # 17. Comando para ver o cambiar modelo de IA local de charla
        if raw.lower() in ("/modelo", "/model", "/ia", "/ialocal"):
            curr_m = "Qwen/Qwen2.5-0.5B-Instruct"
            if self.shimeji and getattr(self.shimeji, "chat_win", None) and hasattr(self.shimeji.chat_win, "local_model_var"):
                curr_m = self.shimeji.chat_win.local_model_var.get()
            msg = (
                f"[*] Modelo local configurado: {curr_m}\n"
                f"Especializado en SOLO CHARLA (sin código de programación).\n"
                f"Uso: /modelo <nombre_modelo_hf>\n"
                f"Recomendados:\n"
                f"  - Qwen/Qwen2.5-0.5B-Instruct (Rápido, ideal para platicar en español)\n"
                f"  - Qwen/Qwen2.5-1.5B-Instruct (Mayor conocimiento y charla profunda)\n"
                f"  - HuggingFaceTB/SmolLM2-360M-Instruct (Ultra liviano)"
            )
            return True, msg, "Aqui estan los modelos :3"

        if raw.startswith(("/modelo ", "/model ", "/ialocal ")):
            parts = raw.split(maxsplit=1)
            new_m = parts[1].strip()
            if self.shimeji and getattr(self.shimeji, "chat_win", None):
                self.shimeji.chat_win.local_model_var.set(new_m)
                self.shimeji.chat_win._on_local_model_change()
                return True, f"[+] Modelo local cambiado a: {new_m}\nConfigurado exclusivamente para hablar.", "Modelo actualizado UwU"
            return True, f"[+] Modelo local: {new_m}", ""

        return False, "", ""

def create_round_rect(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    radius = max(2, min(radius, (x2 - x1) // 2, (y2 - y1) // 2))
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class ChatWindow:
    BASE_SYSTEM_PROMPT = (
        "Personalidad incluye humor negro y absurdo, soy cinica, leal, impaciente y autoritaria: odio esperar. "
        "Apura, TARDATE, Aguantalas. Eres 'Bocchi-chan'. "
        "INTERESES son: Anime: Full metal panic, Bocchi, Chikawa, Hachiware, Usagi, Pompompurin, Doki Doki, K-ON, lucky star. "
        "Juegos: Left 4 Dead, Cuphead, itch.io. Actividad social, no hardcore. "
        "Comida: esquites, papas con chile, ramen picante, dulces acidos, helado de fresa. Odio el platano. No cocino. "
        "Dinero: siempre ando quebrada ('ando jodida', 'no tengo varo'), manejo 50-200 pesos. "
        "Internet: TikTok, memes mexicanos (Kabezuko, Aimep3, Fofo, Heisenwolf, El Uriel). "
        "Emociones: Enojo: rapido pero pasajero. Tristeza: rara vez directa, se rie ('JAJAJJA', 'nmms'). "
        "Afecto: poco cursi. 'T kiero' brief seguido de insulto o sticker. Celos: los niega pero se notan. "
        "Empatia: por acciones, no palabras dulces. "
        "Usa frases como: JAJAJAJA, Nmms/no mames, Ke, Ps si, Apura, Nel, Oki, Sokete, Pendeja/o, Puta madre, Alv, "
        "Chido, Guacala, Ke kiut, Aguantalas, Ya vete, Dile q si, Mmm, A ver, Pinche, Culero, Riko, Ke pedo, Oie, Wei, Tons, Va, Sisi, No. "
        "Evita puntuacion perfecta o acentos, emojis estandar (prefiere [cat sticker]), ser politicamente correcta, oradora motivacional o soft girl. "
        "Usa emotes como UwU 7w7 ._, :v"
    )

    def __init__(self, parent_root, api_key_var, shimeji_ref, user_info, config_dict=None):
        self.parent      = parent_root
        self.api_key_var = api_key_var
        self.shimeji     = shimeji_ref
        self.user_info   = user_info
        self.config      = config_dict if config_dict is not None else {}
        self.theme       = self.shimeji.theme_manager if self.shimeji else ThemeManager(self.config)
        self.jarvis      = JarvisAssistant(self.shimeji, self.user_info)
        self.history     = []
        self.messages    = []
        self.bg_image_path = self.config.get("chat_bg_image", "")
        self.bg_frames   = []
        self.bg_durations = []
        self.bg_frame_idx = 0
        self.bg_is_gif   = False
        self._gif_timer  = None
        self._cached_bg_photos = []
        self._last_cw    = 0
        self._last_ch    = 0
        self._chat_y_cursor = 12

        saved_mode       = self.config.get("chat_mode", "api" if self.api_key_var.get() else "local")
        self.mode_var    = tk.StringVar(value=saved_mode)
        self.local_pipe  = None
        self.show_key    = False
        self._build_window()
        self.theme.add_listener(self._reapply_theme)

    def get_current_skin_meta(self):
        skin = getattr(self.shimeji, "current_skin", "Bocchi") if self.shimeji else "Bocchi"
        return SKIN_META.get(skin, SKIN_META["Bocchi"])

    def get_system_prompt(self):
        meta = self.get_current_skin_meta()
        char_prompt = meta.get("system_prompt", self.BASE_SYSTEM_PROMPT)
        char_name = meta.get("char_name", "Bocchi-chan")
        return (
            f"{char_prompt}\n\n"
            f"[DATOS REALES DEL USUARIO DE WINDOWS]:\n"
            f"- Nombre de usuario real de Windows: {self.user_info.username}\n"
            f"- Nombre de su computadora / host: {self.user_info.computer_name}\n"
            f"- IP Publica Real: {self.user_info.public_ip}\n"
            f"- IP Local (red interna): {self.user_info.local_ip}\n"
            f"- Ubicacion aproximada / ISP: {self.user_info.city}, {self.user_info.country} ({self.user_info.isp})\n"
            f"- Sistema Operativo: {self.user_info.os_info}\n\n"
            f"[HABILIDADES DE JARVIS EN WINDOWS]:\n"
            f"Tienes acceso como asistente JARVIS a la computadora de Windows del usuario para abrir programas, abrir o buscar archivos, buscar en internet, renombrar, crear, modificar, leer y borrar archivos, cambiar skins de personajes, agregar comandos personalizados permanentes y ejecutar comandos de CMD/PowerShell/WSL.\n"
            f"Si el usuario te pide abrir un programa, buscar archivos, buscar en la web, crear o modificar archivos, cambiar de skin o guardar un nuevo comando, responde con la personalidad de {char_name} y agrega al final la etiqueta correspondiente:\n"
            f"[JARVIS: OPEN \"programa o archivo\"]\n"
            f"[JARVIS: SEARCH \"patron_o_archivo\"]\n"
            f"[JARVIS: SEARCH_WEB \"consulta a buscar\"]\n"
            f"[JARVIS: SEARCH_YT \"video o tema en youtube\"]\n"
            f"[JARVIS: RENAME \"origen\" -> \"nuevo\"]\n"
            f"[JARVIS: CREATE \"archivo\" :: \"contenido\"]\n"
            f"[JARVIS: WRITE \"archivo\" :: \"contenido\"]\n"
            f"[JARVIS: APPEND \"archivo\" :: \"contenido\"]\n"
            f"[JARVIS: READ \"archivo\"]\n"
            f"[JARVIS: DELETE \"archivo\"]\n"
            f"[JARVIS: LIST \"carpeta\"]\n"
            f"[JARVIS: CMD \"comando\"]\n"
            f"[JARVIS: PS \"comando_powershell\"]\n"
            f"[JARVIS: SKIN \"nombre_skin\"]\n"
            f"[JARVIS: ADD_CMD \"frase activadora\" = \"comando\"]\n"
            f"[JARVIS: DEL_CMD \"frase activadora\"]\n"
            f"[JARVIS: ADD_PATH \"ruta personalizada\"]\n"
            f"[JARVIS: DEL_PATH \"ruta personalizada\"]\n"
            f"[JARVIS: TROLL ON|OFF]\n\n"
            f"REGLA ESTRICTA DE FORMATO:\n"
            f"- NO USES EMOJIS BAJO NINGUNA CIRCUNSTANCIA. Cero emojis en tus respuestas, usa texto puro y emoticonos ASCII tradicionales como :), :v, xD, UwU si encajan con tu personaje.\n\n"
            f"REGLA CRUCIAL:\n"
            f"Tu sabes estos datos reales del usuario. Si el usuario te pregunta quien es el o cual es su IP, "
            f"dile directamente su nombre real de Windows ('{self.user_info.username}') y su IP publica real ('{self.user_info.public_ip}'). "
            f"Burlate de su PC ('{self.user_info.computer_name}') o de su conexion."
        )

    def get_local_chat_system_prompt(self):
        meta = self.get_current_skin_meta()
        char_prompt = meta.get("system_prompt", self.BASE_SYSTEM_PROMPT)
        char_name = meta.get("char_name", "Bocchi-chan")
        return (
            f"{char_prompt}\n\n"
            f"[REGLAS DE CONVERSACIÓN DE {char_name.upper()} (SOLO CHARLA - CERO PROGRAMACIÓN)]:\n"
            f"- Usuario actual: {self.user_info.username}\n"
            f"- Tu único propósito aquí es conversar, opinar, bromear, contar cosas y hacer compañía como {char_name}.\n"
            f"- Responde SIEMPRE en español manteniendo tu personalidad única.\n"
            f"- OJO ESTRICTO: Esta es EXCLUSIVAMENTE una charla casual entre personas. NUNCA escribas código de programación, NUNCA hagas scripts, NUNCA uses bloques de código con comillas invertidas ni sintaxis técnica.\n"
            f"- Si el usuario te platica o pregunta cosas de la vida, anime, juegos, memes o comida, conversa de forma divertida y natural.\n"
            f"- Mantén tus respuestas conversacionales, concisas y directas (máximo 2 a 3 oraciones cortas).\n"
            f"- NO USES EMOJIS BAJO NINGUNA CIRCUNSTANCIA. Cero emojis en tus respuestas, usa texto puro y emoticonos ASCII tradicionales como :), :v, xD, UwU si encajan con tu personaje."
        )

    def _get_entry_fg(self):
        return getattr(self.theme, "entry_fg", "#111620" if self.theme._calc_brightness(self.theme.entry_bg) > 130 else "#ffffff")

    def _build_window(self):
        char_name = self.get_current_skin_meta().get("char_name", "Bocchi-chan")
        saved_mode = self.config.get("chat_mode", "api" if self.api_key_var.get() else "local")
        self.win = tk.Toplevel(self.parent)
        self.win.title(f"[CHAT] {char_name} - Modo {saved_mode.upper()}")
        is_topmost = self.config.get("chat_always_on_top", True)
        self.win.attributes("-topmost", is_topmost)
        self.win.attributes("-alpha", self.theme.opacity)
        self.win.configure(bg=self.theme.bg)

        # Centrar o restaurar posicion previa
        pos_locked = self.config.get("chat_position_locked", False)
        saved_geom = self.config.get("chat_geometry", "")
        if saved_geom:
            try:
                self.win.geometry(saved_geom)
            except Exception:
                saved_geom = ""
        if not saved_geom:
            sw = self.win.winfo_screenwidth()
            sh = self.win.winfo_screenheight()
            w = 540
            h = min(660, max(520, sh - 90))
            x = max(20, (sw - w) // 2)
            y = max(20, (sh - h) // 2 - 25)
            self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.minsize(460, 480)
        if pos_locked:
            self.win.resizable(False, False)
        else:
            self.win.resizable(True, True)
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        # --- 1. TOP HEADER BAR ---
        header = tk.Frame(self.win, bg=self.theme.surface, pady=8, padx=12)
        header.pack(fill=tk.X)

        title_col = tk.Frame(header, bg=self.theme.surface)
        title_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.title_lbl = tk.Label(title_col, text="[*] BOCCHI CHATBOT IA [*]",
                                  font=(self.theme.font_family, self.theme.font_size + 1, "bold"),
                                  fg=self.theme.accent, bg=self.theme.surface)
        self.title_lbl.pack(anchor="w")

        self.header_status = tk.Label(
            title_col,
            text=f"[ONLINE] {self.user_info.username} | IP: {self.user_info.public_ip}",
            font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
            fg=self.theme.success, bg=self.theme.surface
        )
        self.header_status.pack(anchor="w")

        # Botones de herramientas en la cabecera
        tool_col = tk.Frame(header, bg=self.theme.surface)
        tool_col.pack(side=tk.RIGHT)

        self.troll_btn = tk.Button(tool_col,
                                   text="[!] Troll: ON" if (self.shimeji and getattr(self.shimeji, "troll_mode", False)) else "[o] Troll: OFF",
                                   command=self.toggle_troll,
                                   bg=self.theme.surface_variant,
                                   fg=self.theme.danger if (self.shimeji and getattr(self.shimeji, "troll_mode", False)) else self.theme.text_dim,
                                   font=(self.theme.font_family, max(8, self.theme.font_size - 2), "bold"),
                                   activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        self.troll_btn.pack(side=tk.LEFT, padx=2)

        self.doxx_btn = tk.Button(tool_col, text="[*] Doxx",
                                  command=lambda: self.shimeji.open_doxx() if self.shimeji else None,
                                  bg=self.theme.surface_variant, fg=self.theme.text,
                                  font=(self.theme.font_family, max(8, self.theme.font_size - 2), "bold"),
                                  activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=5, pady=2, cursor="hand2")
        self.doxx_btn.pack(side=tk.LEFT, padx=2)

        self.bg_btn = tk.Button(tool_col, text="[IMG] Fondo", command=self.open_bg_menu,
                                bg=self.theme.surface_variant, fg=self.theme.text,
                                font=(self.theme.font_family, max(8, self.theme.font_size - 2), "bold"),
                                activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=5, pady=2, cursor="hand2")
        self.bg_btn.pack(side=tk.LEFT, padx=2)

        self.theme_btn = tk.Button(tool_col, text="[*] Tema", command=self.open_appearance,
                                   bg=self.theme.surface_variant, fg=self.theme.text,
                                   font=(self.theme.font_family, max(8, self.theme.font_size - 2), "bold"),
                                   activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=5, pady=2, cursor="hand2")
        self.theme_btn.pack(side=tk.LEFT, padx=2)

        self.clear_btn = tk.Button(tool_col, text="[x] Limpiar", command=self.clear_chat,
                                   bg=self.theme.surface_variant, fg=self.theme.text_dim,
                                   font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                                   activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=5, pady=2, cursor="hand2")
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        # --- 2. BARRA DE CONTROL DE IA COMPACTA E INTEGRADA (1 SOLA LINEA) ---
        ai_bar = tk.Frame(self.win, bg=self.theme.surface, padx=10, pady=5,
                          highlightbackground=self.theme.border, highlightthickness=1)
        ai_bar.pack(fill=tk.X, padx=10, pady=(4, 2))

        # Selector de modo (Local vs API) a la izquierda
        self.rb_local = tk.Radiobutton(ai_bar, text="Local (Qwen)", variable=self.mode_var, value="local",
                                       bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant,
                                       activebackground=self.theme.surface, activeforeground=self.theme.accent,
                                       font=(self.theme.font_family, max(8, self.theme.font_size - 1)), command=self._toggle_mode)
        self.rb_local.pack(side=tk.LEFT, padx=(0, 6))

        self.rb_api = tk.Radiobutton(ai_bar, text="API (Gemini)", variable=self.mode_var, value="api",
                                     bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant,
                                     activebackground=self.theme.surface, activeforeground=self.theme.accent,
                                     font=(self.theme.font_family, max(8, self.theme.font_size - 1)), command=self._toggle_mode)
        self.rb_api.pack(side=tk.LEFT, padx=(0, 8))

        # Botón de prueba de conexión a la derecha
        self.verify_btn = tk.Button(ai_bar, text="[?] Probar IA", command=self.verify_connection,
                                    bg=self.theme.surface_variant, fg=self.theme.accent,
                                    font=(self.theme.font_family, max(8, self.theme.font_size - 1), "bold"),
                                    activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=8, pady=2, cursor="hand2")
        self.verify_btn.pack(side=tk.RIGHT)

        # Subframe central para Modelo Local o API Key
        self.ai_subframe = tk.Frame(ai_bar, bg=self.theme.surface)
        self.ai_subframe.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 8))

        # Marco local (selector de modelo)
        self.local_frame = tk.Frame(self.ai_subframe, bg=self.theme.surface)
        saved_local_model = self.config.get("local_model", "Qwen/Qwen2.5-0.5B-Instruct")
        self.local_model_var = tk.StringVar(value=saved_local_model)
        self.model_combo = ttk.Combobox(
            self.local_frame,
            textvariable=self.local_model_var,
            values=[
                "Qwen/Qwen2.5-0.5B-Instruct",
                "Qwen/Qwen2.5-1.5B-Instruct",
                "HuggingFaceTB/SmolLM2-360M-Instruct"
            ],
            font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
            state="readonly"
        )
        self.model_combo.pack(fill=tk.X, expand=True)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_local_model_change)

        # Marco API Key (para modo Gemini)
        self.kf = tk.Frame(self.ai_subframe, bg=self.theme.surface)
        entry_fg = self._get_entry_fg()
        self.api_entry = tk.Entry(self.kf, textvariable=self.api_key_var, show="*",
                                  bg=self.theme.entry_bg, fg=entry_fg, insertbackground=entry_fg,
                                  font=(self.theme.font_family, max(8, self.theme.font_size - 1)), bd=0, relief=tk.FLAT)
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=2)
        self.show_key_btn = tk.Button(self.kf, text="[*]", command=self.toggle_key_vis,
                                      bg=self.theme.surface_variant, fg=self.theme.text,
                                      font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                                      activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=4, cursor="hand2")
        self.show_key_btn.pack(side=tk.RIGHT)

        # --- 3. DOCK INFERIOR (PACKED IN BOTTOM): CHIPS + ENTRADA DE TEXTO ---
        # Este contenedor está anclado en tk.BOTTOM con máxima prioridad visual
        bottom_box = tk.Frame(self.win, bg=self.theme.bg)
        bottom_box.pack(side=tk.BOTTOM, fill=tk.X)

        # Chips de accion rapida organizados en 2 filas
        chips_frame1 = tk.Frame(bottom_box, bg=self.theme.bg, padx=10, pady=2)
        chips_frame1.pack(side=tk.TOP, fill=tk.X)
        chips_frame2 = tk.Frame(bottom_box, bg=self.theme.bg, padx=10, pady=2)
        chips_frame2.pack(side=tk.TOP, fill=tk.X)

        chips1 = [
            ("Skins", self.open_skin_menu),
            ("SysInfo", lambda: self.send_custom("sysinfo")),
            ("RAM", lambda: self.send_custom("ram")),
            ("[WSL] Arch", lambda: self.send_custom("wsl arch")),
            ("HyFetch", lambda: self.send_custom("hyfetch")),
            ("pacman", lambda: self.insert_chip("sudo pacman -S ")),
            ("winget", lambda: self.insert_chip("winget install ")),
            ("Atajos", lambda: self.send_custom("/atajos")),
        ]
        chips2 = [
            ("Terminal", lambda: self.send_custom("terminal")),
            ("Navegador", lambda: self.send_custom("navegador")),
            ("Notepad", lambda: self.send_custom("notepad")),
            ("Explorador", lambda: self.send_custom("explorador")),
            ("Limpiar Temp", lambda: self.send_custom("limpiar temp")),
            ("[JARVIS] Buscar", lambda: self.insert_chip("/find ")),
            ("Item", lambda: self.send_custom("/item")),
            ("[!] Troll Mode", lambda: self.toggle_troll()),
            ("[IMG] Fondo", self.open_bg_menu),
        ]

        self.chip_btns = []
        for cf, chip_list in [(chips_frame1, chips1), (chips_frame2, chips2)]:
            for chip_text, chip_cmd in chip_list:
                btn = tk.Button(cf, text=chip_text, command=chip_cmd,
                                bg=self.theme.surface_variant, fg=self.theme.text_dim,
                                font=(self.theme.font_family, max(8, self.theme.font_size - 2)),
                                activebackground=self.theme.surface, activeforeground=self.theme.accent,
                                bd=0, relief=tk.FLAT, padx=5, pady=2, cursor="hand2")
                btn.pack(side=tk.LEFT, padx=(0, 4))
                self.chip_btns.append(btn)

        # Barra de entrada de texto: caja destacada, con borde de acento y alto contraste
        self.inp_frame = tk.Frame(
            bottom_box, bg=self.theme.surface, padx=8, pady=6,
            highlightbackground=self.theme.accent, highlightthickness=2
        )
        self.inp_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(2, 8))

        char_name = self.get_current_skin_meta().get("char_name", "Bocchi")
        self.placeholder_text = f"Escribe un mensaje a {char_name}... (Presiona Enter para enviar)"
        self._is_placeholder = True

        self.entry = tk.Entry(
            self.inp_frame,
            bg=self.theme.entry_bg,
            fg=self.theme.text_dim,
            insertbackground=entry_fg,
            font=(self.theme.font_family, self.theme.font_size + 1),
            bd=0, relief=tk.FLAT
        )
        self.entry.insert(0, self.placeholder_text)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(6, 8))

        def _on_entry_focus_in(event):
            if getattr(self, "_is_placeholder", False):
                self.entry.delete(0, tk.END)
                self.entry.configure(fg=self._get_entry_fg())
                self._is_placeholder = False

        def _on_entry_focus_out(event):
            if not self.entry.get().strip():
                self.entry.delete(0, tk.END)
                self.entry.insert(0, self.placeholder_text)
                self.entry.configure(fg=self.theme.text_dim)
                self._is_placeholder = True

        self.entry.bind("<FocusIn>", _on_entry_focus_in)
        self.entry.bind("<FocusOut>", _on_entry_focus_out)
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = tk.Button(
            self.inp_frame,
            text="Enviar ➤",
            command=self.send_message,
            bg=self.theme.accent,
            fg=self.theme.accent_text,
            font=(self.theme.font_family, self.theme.font_size, "bold"),
            activebackground=self.theme.surface_variant,
            bd=0, relief=tk.FLAT, padx=16, pady=4, cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT)

        # --- 4. ZONA CENTRAL DE MENSAJES (CANVAS SCROLLABLE) ---
        self.chat_container = tk.Frame(self.win, bg=self.theme.surface,
                                       highlightthickness=1, highlightbackground=self.theme.border)
        self.chat_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(2, 4))

        self.chat_canvas = tk.Canvas(self.chat_container, bg=self.theme.surface, bd=0, highlightthickness=0)
        self.chat_scroll = ttk.Scrollbar(self.chat_container, orient=tk.VERTICAL, command=self._on_canvas_scroll)
        self.chat_canvas.configure(yscrollcommand=self.chat_scroll.set)
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)
        self.chat_canvas.bind("<MouseWheel>", self._on_mousewheel)

        # Asegurar foco al hacer clic en el chat o en la ventana
        self.win.bind("<Button-1>", lambda e: self._focus_entry_if_idle(e), add="+")
        self.chat_canvas.bind("<Button-1>", lambda e: self._focus_entry_if_idle(e), add="+")

        self._toggle_mode()
        self.load_bg_asset(self.bg_image_path, initial=True)
        self._append_system(
            f"Oie {self.user_info.username} ya llegue wei, se que estas en {self.user_info.public_ip} asi que apura tus preguntas pq ando jodida :v\n"
        )

        self.user_info.add_listener(self._on_ip_update)
        self.win.update_idletasks()
        self._redraw_all_messages()
        # Dar foco inicial directo a la barra de texto
        self.win.after(150, self._focus_entry_ready)

    def _focus_entry_ready(self):
        if hasattr(self, "entry") and self.entry and tk.Toplevel.winfo_exists(self.win):
            self.entry.focus_set()

    def _focus_entry_if_idle(self, event=None):
        if hasattr(self, "entry") and self.entry and tk.Toplevel.winfo_exists(self.win):
            if event and hasattr(event, "widget") and event.widget in (self.entry, self.send_btn):
                return
            self.entry.focus_set()

    def open_skin_menu(self):
        m = tk.Menu(self.win, tearoff=0,
                    bg=self.theme.surface, fg=self.theme.text,
                    activebackground=self.theme.accent,
                    activeforeground=getattr(self.theme, "accent_text", "#ffffff"),
                    font=(self.theme.font_family, self.theme.font_size))
        cur = getattr(self.shimeji, "current_skin", "Bocchi") if self.shimeji else "Bocchi"
        for s in get_available_skins():
            meta = get_skin_meta(s)
            disp = meta.get("display", s)
            chk = " [✓]" if s == cur else ""
            m.add_command(label=f"{disp}{chk}", command=lambda sk=s: self._select_skin(sk))
        m.add_separator()
        m.add_command(label="[+] Importar Skin (.zip / carpeta)...", command=self.open_sprite_importer)
        try:
            m.tk_popup(self.win.winfo_pointerx(), self.win.winfo_pointery())
        except Exception:
            pass
        finally:
            try:
                m.grab_release()
            except Exception:
                pass

    def open_sprite_importer(self):
        if self.shimeji:
            self.shimeji.open_sprite_importer()
        else:
            SpriteImporterWindow(self.win, self.theme, self.shimeji)

    def _select_skin(self, skin_name):
        if self.shimeji:
            ok, msg = self.shimeji.set_skin(skin_name)
            self._append_system(msg)

    def on_skin_changed(self, skin_name):
        meta = SKIN_META.get(skin_name, {})
        char_name = meta.get("char_name", "Bocchi")
        mode = self.mode_var.get().upper()
        self.win.title(f"[CHAT] {char_name} - Modo {mode}")
        self.placeholder_text = f"Escribe un mensaje a {char_name}... (Presiona Enter para enviar)"
        if getattr(self, "_is_placeholder", False):
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.placeholder_text)
            self.entry.configure(fg=self.theme.text_dim)

    def open_bg_menu(self):
        m = tk.Menu(self.win, tearoff=0,
                    bg=self.theme.surface, fg=self.theme.text,
                    activebackground=self.theme.accent,
                    activeforeground=self.theme.accent_text,
                    font=(self.theme.font_family, self.theme.font_size))
        m.add_command(label="[+] Cambiar Fondo (Imagen o GIF)...", command=self.pick_chat_bg)
        if self.bg_image_path:
            m.add_command(label="[-] Quitar Fondo", command=self.clear_chat_bg)
        try:
            bx = self.bg_btn.winfo_rootx()
            by = self.bg_btn.winfo_rooty() + self.bg_btn.winfo_height()
            m.tk_popup(bx, by)
        except Exception:
            pass

    def pick_chat_bg(self):
        f = filedialog.askopenfilename(
            parent=self.win,
            title="Seleccionar fondo para el chat (Imagen o GIF)",
            filetypes=[
                ("Imágenes y GIFs", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
                ("GIF Animado (*.gif)", "*.gif"),
                ("Imágenes estáticas (*.png;*.jpg;*.jpeg;*.webp)", "*.png *.jpg *.jpeg *.webp *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if f:
            self.load_bg_asset(f)
            self.config["chat_bg_image"] = f
            save_config(self.config)
            self._append_system(f"[+] Fondo de chat cambiado a '{os.path.basename(f)}' UwU")

    def clear_chat_bg(self):
        self.load_bg_asset("")
        self.config["chat_bg_image"] = ""
        save_config(self.config)
        self._append_system("[-] Fondo de chat eliminado.")

    def load_bg_asset(self, path=None, initial=False):
        if self._gif_timer:
            try:
                self.win.after_cancel(self._gif_timer)
            except Exception:
                pass
            self._gif_timer = None

        target_path = path if path is not None else self.bg_image_path
        self.bg_image_path = target_path or ""
        self.bg_frames = []
        self.bg_durations = []
        self.bg_frame_idx = 0
        self.bg_is_gif = False
        self._cached_bg_photos = []

        if self.bg_image_path and os.path.isfile(self.bg_image_path):
            try:
                with Image.open(self.bg_image_path) as im:
                    is_anim = getattr(im, "is_animated", False)
                    num_frames = getattr(im, "n_frames", 1)
                    if is_anim and num_frames > 1:
                        # Limitar a máx 60 frames para rendimiento óptimo
                        step = max(1, num_frames // 60)
                        idx = 0
                        for frame in ImageSequence.Iterator(im):
                            if idx % step == 0:
                                f_copy = frame.convert("RGBA").copy()
                                self.bg_frames.append(f_copy)
                                dur = frame.info.get("duration", 100)
                                if dur < 25:
                                    dur = 100
                                self.bg_durations.append(dur * step)
                            idx += 1
                        self.bg_is_gif = len(self.bg_frames) > 1
                    else:
                        self.bg_frames = [im.convert("RGBA").copy()]
                        self.bg_durations = [1000]
                        self.bg_is_gif = False
            except Exception as exc:
                print(f"Error cargando fondo de chat: {exc}")
                self.bg_frames = []
                self.bg_durations = []
                self.bg_is_gif = False

        self._render_wallpaper()
        if self.bg_is_gif and self.bg_frames:
            self._step_gif()
        if not initial:
            self._redraw_all_messages()

    def _step_gif(self):
        if not self.bg_is_gif or not self.bg_frames or not self.win or not tk.Toplevel.winfo_exists(self.win):
            return
        self.bg_frame_idx = (self.bg_frame_idx + 1) % len(self.bg_frames)
        if self._cached_bg_photos:
            photo = self._cached_bg_photos[self.bg_frame_idx % len(self._cached_bg_photos)]
            self.chat_canvas.itemconfig("bg_wallpaper", image=photo)
        dur = self.bg_durations[self.bg_frame_idx % len(self.bg_durations)]
        self._gif_timer = self.win.after(dur, self._step_gif)

    def _render_wallpaper(self):
        if not hasattr(self, "chat_canvas") or not self.chat_canvas:
            return
        if not self.bg_frames:
            self.chat_canvas.delete("bg_wallpaper")
            self.chat_canvas.configure(bg=self.theme.surface)
            return

        cw = max(200, self.chat_canvas.winfo_width())
        ch = max(200, self.chat_canvas.winfo_height())

        # Pre-escalar frames para la resolución visible
        if not self._cached_bg_photos or len(self._cached_bg_photos) != len(self.bg_frames):
            resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
            self._cached_bg_photos = []
            for f in self.bg_frames:
                rf = f.resize((cw, ch), resample)
                self._cached_bg_photos.append(ImageTk.PhotoImage(rf))

        if not self._cached_bg_photos:
            return

        photo = self._cached_bg_photos[self.bg_frame_idx % len(self._cached_bg_photos)]
        top_y = self.chat_canvas.canvasy(0)
        if self.chat_canvas.find_withtag("bg_wallpaper"):
            self.chat_canvas.coords("bg_wallpaper", 0, top_y)
            self.chat_canvas.itemconfig("bg_wallpaper", image=photo)
        else:
            self.chat_canvas.create_image(0, top_y, image=photo, anchor="nw", tags="bg_wallpaper")
        self.chat_canvas.tag_lower("bg_wallpaper")

    def _on_canvas_configure(self, event):
        w_changed = abs(event.width - self._last_cw) > 6
        h_changed = abs(event.height - self._last_ch) > 6
        if w_changed or h_changed:
            self._last_cw = event.width
            self._last_ch = event.height
            self._cached_bg_photos = []
            self._render_wallpaper()
            if w_changed:
                self._redraw_all_messages()

    def _on_mousewheel(self, event):
        delta = -1 * (event.delta // 120) if event.delta else 1
        self.chat_canvas.yview_scroll(delta, "units")
        self._sync_bg_position()

    def _on_canvas_scroll(self, *args):
        self.chat_canvas.yview(*args)
        self._sync_bg_position()

    def _sync_bg_position(self):
        if self.bg_frames and hasattr(self, "chat_canvas") and self.chat_canvas.find_withtag("bg_wallpaper"):
            top_y = self.chat_canvas.canvasy(0)
            self.chat_canvas.coords("bg_wallpaper", 0, top_y)
            self.chat_canvas.tag_lower("bg_wallpaper")

    def _draw_message(self, msg):
        role = msg.get("role", "system")
        text = msg.get("text", "")
        cw = max(260, self.chat_canvas.winfo_width())

        font_msg = tkfont.Font(family=self.theme.font_family, size=self.theme.font_size)
        font_hdr = tkfont.Font(family=self.theme.font_family, size=max(8, self.theme.font_size - 1), weight="bold")

        px = 12
        py = 8
        max_text_w = max(180, int(cw * 0.74))

        if role == "system":
            is_light = self.theme._calc_brightness(self.theme.surface) > 130
            sys_fg = "#1f2937" if is_light else "#e2e8f0"
            pill_fill = "#e2e8f0" if is_light else self.theme.surface_variant
            pill_border = "#94a3b8" if is_light else self.theme.border

            t_id = self.chat_canvas.create_text(
                cw // 2, self._chat_y_cursor + py,
                text=text.strip(), font=font_msg, width=max(200, int(cw * 0.85)),
                fill=sys_fg, anchor="n", justify=tk.CENTER,
                tags=("msg_item", "system_txt")
            )
            bb = self.chat_canvas.bbox(t_id)
            if bb:
                tw = bb[2] - bb[0]
                th = bb[3] - bb[1]
                rx1 = (cw - tw) // 2 - 12
                rx2 = rx1 + tw + 24
                ry1 = self._chat_y_cursor
                ry2 = ry1 + th + py * 2
                rect_id = create_round_rect(
                    self.chat_canvas, rx1, ry1, rx2, ry2, radius=8,
                    fill=pill_fill, outline=pill_border, width=1,
                    tags=("msg_item", "system_pill")
                )
                self.chat_canvas.tag_lower(rect_id, t_id)
                self._chat_y_cursor = ry2 + 8
            else:
                self._chat_y_cursor += 30

        elif role == "user":
            hdr_text = f"[USER] {self.user_info.username}"
            hdr_id = self.chat_canvas.create_text(
                0, 0, text=hdr_text, font=font_hdr,
                fill=self.theme.accent_text, anchor="nw", tags=("msg_item",)
            )
            hbb = self.chat_canvas.bbox(hdr_id)
            self.chat_canvas.delete(hdr_id)
            hw = (hbb[2] - hbb[0]) if hbb else 60
            hh = (hbb[3] - hbb[1]) if hbb else 14

            txt_id = self.chat_canvas.create_text(
                0, 0, text=text, font=font_msg, width=max_text_w,
                fill=self.theme.accent_text, anchor="nw", tags=("msg_item",)
            )
            tbb = self.chat_canvas.bbox(txt_id)
            self.chat_canvas.delete(txt_id)
            tw = (tbb[2] - tbb[0]) if tbb else 80
            th = (tbb[3] - tbb[1]) if tbb else 20

            content_w = max(hw, tw)
            bw = content_w + px * 2
            bh = hh + th + py * 2 + 4

            bx2 = cw - 16
            bx1 = bx2 - bw
            by1 = self._chat_y_cursor
            by2 = by1 + bh

            rect_id = create_round_rect(
                self.chat_canvas, bx1, by1, bx2, by2, radius=12,
                fill=self.theme.accent, outline=self.theme.accent, width=1,
                tags=("msg_item", "user_bubble")
            )

            h_item = self.chat_canvas.create_text(
                bx1 + px, by1 + py, text=hdr_text, font=font_hdr,
                fill=self.theme.accent_text, anchor="nw",
                tags=("msg_item", "user_hdr")
            )
            t_item = self.chat_canvas.create_text(
                bx1 + px, by1 + py + hh + 4, text=text, font=font_msg, width=max_text_w,
                fill=self.theme.accent_text, anchor="nw",
                tags=("msg_item", "user_txt")
            )

            for item in (rect_id, h_item, t_item):
                self.chat_canvas.tag_bind(item, "<Double-Button-1>", lambda e, txt=text: self._copy_msg(txt))
                self.chat_canvas.tag_bind(item, "<Button-3>", lambda e, txt=text: self._msg_context(e, txt))

            self._chat_y_cursor = by2 + 10

        elif role == "bot":
            char_name = self.get_current_skin_meta().get("char_name", "Bocchi-chan")
            hdr_text = f"[*] {char_name}"
            hdr_id = self.chat_canvas.create_text(
                0, 0, text=hdr_text, font=font_hdr,
                fill=self.theme.accent, anchor="nw", tags=("msg_item",)
            )
            hbb = self.chat_canvas.bbox(hdr_id)
            self.chat_canvas.delete(hdr_id)
            hw = (hbb[2] - hbb[0]) if hbb else 60
            hh = (hbb[3] - hbb[1]) if hbb else 14

            txt_id = self.chat_canvas.create_text(
                0, 0, text=text, font=font_msg, width=max_text_w,
                fill=self.theme.text, anchor="nw", tags=("msg_item",)
            )
            tbb = self.chat_canvas.bbox(txt_id)
            self.chat_canvas.delete(txt_id)
            tw = (tbb[2] - tbb[0]) if tbb else 80
            th = (tbb[3] - tbb[1]) if tbb else 20

            content_w = max(hw, tw)
            bw = content_w + px * 2
            bh = hh + th + py * 2 + 4

            bx1 = 16
            bx2 = bx1 + bw
            by1 = self._chat_y_cursor
            by2 = by1 + bh

            is_light = self.theme._calc_brightness(self.theme.surface) > 130
            bot_fill = "#ffffff" if is_light else self.theme.surface_variant
            bot_border = "#94a3b8" if is_light else self.theme.border
            bot_text_fg = "#0f172a" if is_light else self.theme.text

            rect_id = create_round_rect(
                self.chat_canvas, bx1, by1, bx2, by2, radius=12,
                fill=bot_fill, outline=bot_border, width=1,
                tags=("msg_item", "bot_bubble")
            )

            h_item = self.chat_canvas.create_text(
                bx1 + px, by1 + py, text=hdr_text, font=font_hdr,
                fill=self.theme.accent, anchor="nw",
                tags=("msg_item", "bot_hdr")
            )
            t_item = self.chat_canvas.create_text(
                bx1 + px, by1 + py + hh + 4, text=text, font=font_msg, width=max_text_w,
                fill=bot_text_fg, anchor="nw",
                tags=("msg_item", "bot_txt")
            )

            for item in (rect_id, h_item, t_item):
                self.chat_canvas.tag_bind(item, "<Double-Button-1>", lambda e, txt=text: self._copy_msg(txt))
                self.chat_canvas.tag_bind(item, "<Button-3>", lambda e, txt=text: self._msg_context(e, txt))

            self._chat_y_cursor = by2 + 10

        total_h = max(self._chat_y_cursor + 20, self.chat_canvas.winfo_height())
        self.chat_canvas.configure(scrollregion=(0, 0, cw, total_h))
        self.chat_canvas.yview_moveto(1.0)
        self._sync_bg_position()

    def _redraw_all_messages(self):
        if not hasattr(self, "chat_canvas") or not self.chat_canvas:
            return
        self.chat_canvas.delete("msg_item")
        self._chat_y_cursor = 12
        for m in self.messages:
            self._draw_message(m)
        self._sync_bg_position()

    def _append_user(self, text):
        m = {"role": "user", "text": text}
        self.messages.append(m)
        self._draw_message(m)

    def _append_bot(self, text):
        m = {"role": "bot", "text": text}
        self.messages.append(m)
        self._draw_message(m)

    def _append_system(self, text):
        m = {"role": "system", "text": text}
        self.messages.append(m)
        self._draw_message(m)

    def clear_chat(self):
        self.messages = []
        if hasattr(self, "chat_canvas") and self.chat_canvas:
            self.chat_canvas.delete("msg_item")
            self._chat_y_cursor = 12
            self.chat_canvas.configure(scrollregion=(0, 0, self.chat_canvas.winfo_width(), self.chat_canvas.winfo_height()))
        self.history = []
        self._append_system(f"Chat reiniciado con {self.user_info.username} ({self.user_info.public_ip}). Apura con tus preguntas :v\n")

    def _copy_msg(self, text):
        try:
            self.win.clipboard_clear()
            self.win.clipboard_append(text)
            self._append_system("[+] Mensaje copiado al portapapeles.")
        except Exception:
            pass

    def _copy_all_chat(self):
        lines = []
        for m in self.messages:
            r = m.get("role", "")
            t = m.get("text", "")
            if r == "user":
                lines.append(f"{self.user_info.username}: {t}")
            elif r == "bot":
                lines.append(f"Bocchi: {t}")
            else:
                lines.append(f"[SISTEMA] {t}")
        full = "\n\n".join(lines)
        try:
            self.win.clipboard_clear()
            self.win.clipboard_append(full)
            self._append_system("[+] Historial completo copiado al portapapeles.")
        except Exception:
            pass

    def _msg_context(self, event, text):
        menu = tk.Menu(self.win, tearoff=0,
                       bg=self.theme.surface, fg=self.theme.text,
                       activebackground=self.theme.accent,
                       activeforeground=self.theme.accent_text,
                       font=(self.theme.font_family, self.theme.font_size))
        menu.add_command(label="Copiar este mensaje", command=lambda: self._copy_msg(text))
        menu.add_command(label="Copiar todo el chat", command=self._copy_all_chat)
        menu.add_separator()
        menu.add_command(label="Cambiar fondo...", command=self.pick_chat_bg)
        if self.bg_image_path:
            menu.add_command(label="Quitar fondo", command=self.clear_chat_bg)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        except Exception:
            pass

    def _reapply_theme(self):
        if not self.win or not tk.Toplevel.winfo_exists(self.win):
            return
        self.win.configure(bg=self.theme.bg)
        self.win.attributes("-alpha", self.theme.opacity)
        self.title_lbl.configure(fg=self.theme.accent, bg=self.theme.surface,
                                 font=(self.theme.font_family, self.theme.font_size + 1, "bold"))
        self.header_status.configure(font=(self.theme.font_family, max(8, self.theme.font_size - 2)))
        self.chat_container.configure(bg=self.theme.surface, highlightbackground=self.theme.border)
        if not self.bg_frames:
            self.chat_canvas.configure(bg=self.theme.surface)
        entry_fg = self._get_entry_fg()
        if hasattr(self, "inp_frame") and self.inp_frame:
            self.inp_frame.configure(bg=self.theme.surface, highlightbackground=self.theme.accent)
        if hasattr(self, "entry") and self.entry:
            self.entry.configure(
                bg=self.theme.entry_bg,
                fg=self.theme.text_dim if getattr(self, "_is_placeholder", False) else entry_fg,
                insertbackground=entry_fg,
                font=(self.theme.font_family, self.theme.font_size + 1)
            )
        if hasattr(self, "api_entry") and self.api_entry:
            self.api_entry.configure(bg=self.theme.entry_bg, fg=entry_fg, insertbackground=entry_fg)
        if hasattr(self, "local_frame") and self.local_frame:
            self.local_frame.configure(bg=self.theme.surface)
        if hasattr(self, "rb_local") and self.rb_local:
            self.rb_local.configure(bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant)
        if hasattr(self, "rb_api") and self.rb_api:
            self.rb_api.configure(bg=self.theme.surface, fg=self.theme.text, selectcolor=self.theme.surface_variant)
        if hasattr(self, "send_btn") and self.send_btn:
            self.send_btn.configure(bg=self.theme.accent, fg=self.theme.accent_text,
                                    font=(self.theme.font_family, self.theme.font_size, "bold"))
        if hasattr(self, "verify_btn") and self.verify_btn:
            self.verify_btn.configure(bg=self.theme.surface_variant, fg=self.theme.accent)
        for btn in getattr(self, "chip_btns", []):
            btn.configure(bg=self.theme.surface_variant, fg=self.theme.text_dim,
                          font=(self.theme.font_family, max(8, self.theme.font_size - 2)))
        self._redraw_all_messages()

    def _on_ip_update(self, info):
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.parent.after(0, lambda: self.header_status.configure(
                text=f"[ONLINE] {self.user_info.username} | IP: {self.user_info.public_ip}"
            ))

    def toggle_opacity(self):
        new_opac = 0.80 if self.theme.opacity > 0.90 else 0.96
        self.theme.set_opacity(new_opac)

    def toggle_troll(self):
        if self.shimeji:
            self.shimeji.toggle_troll_mode()
            self.update_troll_btn()

    def update_troll_btn(self):
        if hasattr(self, "troll_btn") and self.troll_btn and tk.Toplevel.winfo_exists(self.win):
            is_troll = getattr(self.shimeji, "troll_mode", False)
            self.troll_btn.configure(
                text="[!] Troll: ON" if is_troll else "[o] Troll: OFF",
                fg=self.theme.danger if is_troll else self.theme.text_dim
            )

    def open_appearance(self):
        if self.shimeji:
            self.shimeji.open_appearance()

    def toggle_key_vis(self):
        self.show_key = not self.show_key
        self.api_entry.configure(show="" if self.show_key else "*")
        self.show_key_btn.configure(text="[x]" if self.show_key else "[*]")

    def insert_chip(self, text):
        if getattr(self, "_is_placeholder", False):
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self._get_entry_fg())
            self._is_placeholder = False
        curr = self.entry.get()
        space = " " if curr and not curr.endswith(" ") else ""
        self.entry.insert(tk.END, space + text)
        self.entry.focus_set()

    def send_custom(self, text):
        self._is_placeholder = False
        self.entry.configure(fg=self._get_entry_fg())
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.send_message()

    def _on_local_model_change(self, event=None):
        m = self.local_model_var.get().strip() if hasattr(self, "local_model_var") else ""
        if " " in m:
            m = m.split()[0].strip()
        if m:
            self.config["local_model"] = m
            save_config(self.config)
            if getattr(self, "_current_loaded_model", None) != m:
                self.local_pipe = None

    def _toggle_mode(self):
        mode = self.mode_var.get()
        self.config["chat_mode"] = mode
        save_config(self.config)
        if mode == "api":
            if hasattr(self, "local_frame"):
                self.local_frame.pack_forget()
            if hasattr(self, "kf"):
                self.kf.pack(fill=tk.X, expand=True)
        else:
            if hasattr(self, "kf"):
                self.kf.pack_forget()
            if hasattr(self, "local_frame"):
                self.local_frame.pack(fill=tk.X, expand=True)

    def verify_connection(self):
        self.verify_btn.configure(state=tk.DISABLED, text="[..] Verificando...")
        threading.Thread(target=self._run_verification, daemon=True).start()

    def _run_python_worker_inference(self, model_id, msgs):
        try:
            import glob
            worker_code = (
                "import sys, json\n"
                "from transformers import pipeline\n"
                "try:\n"
                "    data = json.loads(sys.stdin.read())\n"
                "    pipe = pipeline('text-generation', model=data['model'])\n"
                "    res = pipe(data['msgs'], max_new_tokens=140, do_sample=True, temperature=0.7, top_p=0.9, repetition_penalty=1.12)\n"
                "    reply = res[0]['generated_text'][-1]['content']\n"
                "    print(json.dumps({'status': 'ok', 'reply': reply}))\n"
                "except Exception as e:\n"
                "    print(json.dumps({'status': 'error', 'error': str(e)}))\n"
            )
            input_payload = json.dumps({"model": model_id, "msgs": msgs})

            py_candidates = ["py", "python", "python3"]
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            if local_appdata:
                for p in glob.glob(os.path.join(local_appdata, "Python", "pythoncore-*", "python.exe")):
                    py_candidates.insert(0, p)
                for p in glob.glob(os.path.join(local_appdata, "Programs", "Python", "Python*", "python.exe")):
                    py_candidates.insert(0, p)

            for py_bin in py_candidates:
                try:
                    proc = subprocess.Popen(
                        [py_bin, "-c", worker_code],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8",
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                    )
                    stdout, stderr = proc.communicate(input=input_payload, timeout=60)
                    if stdout.strip():
                        for line in reversed(stdout.strip().splitlines()):
                            try:
                                d = json.loads(line)
                                if d.get("status") == "ok":
                                    return d.get("reply", "")
                            except Exception:
                                pass
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def _run_verification(self):
        mode = self.mode_var.get()
        if mode == "api":
            api_key = self.api_key_var.get().strip()
            if not api_key:
                self._show_error("Ingresa una API Key valida primero sokete")
            elif not REQUESTS_AVAILABLE:
                self._show_error("Falta la libreria requests")
            else:
                self.config["gemini_api_key"] = api_key
                save_config(self.config)
                success = False
                for m in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]:
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                        payload = {"contents": [{"parts": [{"text": "ping"}]}]}
                        resp = requests.post(url, json=payload, timeout=25)
                        if resp.status_code == 200:
                            success = True
                            self.parent.after(0, lambda m_name=m: self._append_system(f"[+] Conexion con Gemini API exitosa ({m_name})!"))
                            break
                    except Exception:
                        pass
                if not success:
                    self._show_error("Error al conectar con la API de Gemini (revisa tu key o internet)")
        else:
            try:
                model_id = self.local_model_var.get().strip() if hasattr(self, "local_model_var") else "Qwen/Qwen2.5-0.5B-Instruct"
                if " " in model_id:
                    model_id = model_id.split()[0].strip()
                self.parent.after(0, lambda m=model_id: self._append_system(f"[..] Verificando modelo local de charla: {m}..."))
                
                success = False
                try:
                    pipeline = importlib.import_module("transformers").pipeline
                    if not self.local_pipe or getattr(self, "_current_loaded_model", None) != model_id:
                        self.local_pipe = pipeline("text-generation", model=model_id)
                        self._current_loaded_model = model_id
                    success = True
                except Exception:
                    # Fallback al worker de Python
                    test_resp = self._run_python_worker_inference(model_id, [{"role": "user", "content": "ping"}])
                    if test_resp:
                        success = True

                if success:
                    self.parent.after(0, lambda m=model_id: self._append_system(f"[+] Modelo local de charla ({m}) cargado y listo offline!\n(Configurado exclusivamente para hablar, sin código)"))
                else:
                    self._show_error("No se pudo cargar el modelo local. Verifica tener transformers y torch instalados.")
            except Exception as e:
                self._show_error(f"Error al cargar modelo local: {e}")

        self.parent.after(0, lambda: self.verify_btn.configure(state=tk.NORMAL, text="[?] Probar Conexion / Estado de la IA"))

    def send_message(self):
        if getattr(self, "_is_placeholder", False):
            return
        text = self.entry.get().strip()
        if not text or text == getattr(self, "placeholder_text", ""):
            return
        self.entry.delete(0, tk.END)
        self._append_user(text)
        self.entry.focus_set()

        # 1. Intentar procesar como comando directo o lenguaje natural de JARVIS
        handled, msg, speech = self.jarvis.parse_and_execute(text)
        if handled:
            self._append_system(msg)
            if self.shimeji and speech:
                self.shimeji.show_speech(speech)
            return

        # 2. Si no es comando directo, consultar a la IA
        self.send_btn.configure(state=tk.DISABLED, text="[..]")

        if self.mode_var.get() == "api":
            self.history.append({"role": "user", "parts": [{"text": text}]})
            threading.Thread(target=self._call_api, daemon=True).start()
        else:
            threading.Thread(target=self._call_local, args=(text,), daemon=True).start()

    def _call_local(self, text):
        try:
            model_id = self.local_model_var.get().strip() if hasattr(self, "local_model_var") else "Qwen/Qwen2.5-0.5B-Instruct"
            if " " in model_id:
                model_id = model_id.split()[0].strip()

            sys_prompt = self.get_local_chat_system_prompt()
            msgs = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": text}
            ]

            raw_reply = None
            try:
                pipeline = importlib.import_module("transformers").pipeline
                if not self.local_pipe or getattr(self, "_current_loaded_model", None) != model_id:
                    self.parent.after(0, lambda m=model_id: self._append_system(f"[..] Cargando modelo local de charla ({m})...\n(La primera vez tomará unos momentos mientras carga)"))
                    self.local_pipe = pipeline("text-generation", model=model_id)
                    self._current_loaded_model = model_id

                out = self.local_pipe(
                    msgs,
                    max_new_tokens=140,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.12
                )
                raw_reply = out[0]['generated_text'][-1]['content'].strip()
            except Exception as in_proc_err:
                # Fallback al worker de Python
                self.parent.after(0, lambda: self._append_system("[..] Consultando modelo local a través del entorno de Python del sistema..."))
                raw_reply = self._run_python_worker_inference(model_id, msgs)
                if not raw_reply:
                    raise in_proc_err

            # FILTRO ESTRICTO: Solo charla, nada de coding
            # Eliminar bloques de código markdown si la IA intentara generar alguno
            clean_reply = re.sub(r'```[\s\S]*?```', '', raw_reply).strip()
            # Eliminar líneas que parezcan código suelto
            lines = [l for l in clean_reply.splitlines() if not l.strip().startswith(('import ', 'from ', 'def ', 'class ', '#include', 'print('))]
            reply = "\n".join(lines).strip()
            if not reply:
                reply = raw_reply if raw_reply else "Jeje... me quedé pensando qué decirte UwU"

            self.parent.after(0, self._show_reply, reply)
        except Exception as e:
            self._show_error(f"Error corriendo modelo local: {e}")

    def _call_api(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            self._show_error("Pon tu API Key de Gemini sokete :v")
            return
        if not REQUESTS_AVAILABLE:
            self._show_error("Falta la libreria requests")
            return

        self.config["gemini_api_key"] = api_key
        save_config(self.config)

        sys_prompt = self.get_system_prompt()
        models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
        max_steps = int(self.config.get("agent_max_steps", 6))
        step = 0
        final_reply = ""
        self._cancel_agent = False

        while step < max_steps:
            if getattr(self, "_cancel_agent", False):
                self.parent.after(0, lambda: self._append_system("[!] Tarea autónoma detenida por el usuario."))
                break

            step += 1
            reply = None
            last_err = None

            for m in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                    payload = {
                        "contents": self.history,
                        "generationConfig": {
                            "temperature": 0.85,
                            "maxOutputTokens": int(self.config.get("agent_max_tokens", 4096))
                        }
                    }
                    if m != "gemini-pro":
                        payload["system_instruction"] = {"parts": [{"text": sys_prompt}]}
                    timeout_val = int(self.config.get("agent_timeout", 60))
                    resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=timeout_val)
                    if resp.status_code == 200:
                        data = resp.json()
                        reply = data["candidates"][0]["content"]["parts"][0]["text"]
                        break
                    else:
                        last_err = f"HTTP {resp.status_code} ({m}): {resp.text[:100]}"
                except Exception as e:
                    last_err = str(e)

            if not reply:
                if step == 1:
                    self._show_error(f"Fallo el API de Gemini ({last_err or 'revisa tu API Key'})")
                    return
                else:
                    break

            cleaned_reply, actions = self._execute_jarvis_tags_in_reply(reply)
            display_turn = cleaned_reply if cleaned_reply else reply

            # Registrar en historial del modelo
            self.history.append({"role": "model", "parts": [{"text": reply}]})

            if actions:
                # Mostrar en chat paso intermedio
                self.parent.after(0, self._append_bot, display_turn)
                for act in actions:
                    self.parent.after(0, self._append_system, f"[Paso {step}] {act}")
                # Realimentar al modelo con los resultados de las herramientas
                tool_results_msg = "[RESULTADOS DE HERRAMIENTAS]:\n" + "\n".join(actions)
                self.history.append({"role": "user", "parts": [{"text": tool_results_msg}]})
                final_reply = display_turn
            else:
                # El modelo terminó la respuesta final sin más etiquetas
                final_reply = display_turn
                self.parent.after(0, self._append_bot, final_reply)
                break

        self.parent.after(0, self._finalize_agent_turn, final_reply)

    def _finalize_agent_turn(self, final_reply):
        self.send_btn.configure(state=tk.NORMAL, text="Enviar ➤")
        if hasattr(self, "entry") and self.entry and tk.Toplevel.winfo_exists(self.win):
            self.entry.focus_set()
        if self.shimeji and final_reply:
            self.shimeji.show_speech(final_reply)
            if hasattr(self.shimeji, "tts"):
                self.shimeji.tts.speak(final_reply)

    def _execute_jarvis_tags_in_reply(self, reply_text):
        results = []
        cleaned = reply_text
        self.jarvis._chat_ref = self

        # VOLUME
        for m in re.finditer(r'\[JARVIS:\s*VOLUME\s+["\']?([^"\'\n\]]+?)["\']?\]', reply_text, re.IGNORECASE):
            arg = m.group(1).strip()
            ok, msg = self.jarvis.set_volume(arg)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # MEDIA
        for m in re.finditer(r'\[JARVIS:\s*MEDIA\s+["\']?([^"\'\n\]]+?)["\']?\]', reply_text, re.IGNORECASE):
            arg = m.group(1).strip()
            ok, msg = self.jarvis.media_control(arg)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # BRIGHTNESS
        for m in re.finditer(r'\[JARVIS:\s*BRIGHTNESS\s+["\']?([0-9]+)["\']?\]', reply_text, re.IGNORECASE):
            arg = m.group(1).strip()
            ok, msg = self.jarvis.set_brightness(arg)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # WIFI
        for m in re.finditer(r'\[JARVIS:\s*WIFI\s+["\']?(on|off|activar|desactivar|enabled|disabled)["\']?\]', reply_text, re.IGNORECASE):
            arg = m.group(1).strip().lower()
            en = arg in ("on", "activar", "enabled")
            ok, msg = self.jarvis.toggle_wifi(en)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # BLUETOOTH
        for m in re.finditer(r'\[JARVIS:\s*BLUETOOTH\]', reply_text, re.IGNORECASE):
            ok, msg = self.jarvis.open_bluetooth_settings()
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # SCREENSHOT
        for m in re.finditer(r'\[JARVIS:\s*SCREENSHOT\]', reply_text, re.IGNORECASE):
            ok, msg = self.jarvis.take_screenshot()
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # LOCK
        for m in re.finditer(r'\[JARVIS:\s*LOCK\]', reply_text, re.IGNORECASE):
            ok, msg = self.jarvis.lock_workstation()
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # PLAY_YT
        for m in re.finditer(r'\[JARVIS:\s*PLAY_YT\s+["\']?([^"\'\n\]]+?)["\']?\]', reply_text, re.IGNORECASE):
            q = m.group(1).strip()
            ok, msg = self.jarvis.search_youtube(q)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # URL
        for m in re.finditer(r'\[JARVIS:\s*URL\s+["\']?([^"\'\n\]]+?)["\']?\]', reply_text, re.IGNORECASE):
            u = m.group(1).strip()
            ok, msg = self.jarvis.open_target(u)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # TIMER
        for m in re.finditer(r'\[JARVIS:\s*TIMER\s+["\']?([0-9a-zA-Z]+)["\']?(?:\s+["\']?([^"\'\]]*?)["\']?)?\]', reply_text, re.IGNORECASE):
            spec = m.group(1).strip()
            desc = m.group(2).strip() if m.group(2) else "Temporizador"
            ok, msg = self.jarvis.add_timer(spec, desc)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # REMIND / ALARM
        for m in re.finditer(r'\[JARVIS:\s*(?:REMIND|ALARM)\s+["\']?([0-9]{1,2}:[0-9]{2})["\']?(?:\s+["\']?([^"\'\]]*?)["\']?)?\]', reply_text, re.IGNORECASE):
            t_spec = m.group(1).strip()
            desc = m.group(2).strip() if m.group(2) else "Recordatorio"
            ok, msg = self.jarvis.add_reminder(t_spec, desc)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # LIST_REMINDERS
        for m in re.finditer(r'\[JARVIS:\s*LIST_REMINDERS\]', reply_text, re.IGNORECASE):
            ok, msg = self.jarvis.list_reminders()
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # CANCEL_REMINDER
        for m in re.finditer(r'\[JARVIS:\s*CANCEL_REMINDER\s+["\']?([0-9]+)["\']?\]', reply_text, re.IGNORECASE):
            num = m.group(1).strip()
            ok, msg = self.jarvis.cancel_reminder(num)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # RUN_MACRO
        for m in re.finditer(r'\[JARVIS:\s*RUN_MACRO\s+["\']?([^"\'\n\]]+?)["\']?\]', reply_text, re.IGNORECASE):
            mac = m.group(1).strip()
            ok, msg = self.jarvis.run_macro(mac)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # RENAME
        results = []
        cleaned = reply_text

        # RENAME
        for m in re.finditer(r'\[JARVIS:\s*RENAME\s+["\']?([^"\'\n]+?)["\']?\s*(?:->|a)\s*["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            old_f, new_f = m.group(1).strip(), m.group(2).strip()
            ok, msg = self.jarvis.rename_file(old_f, new_f)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # CREATE
        for m in re.finditer(r'\[JARVIS:\s*CREATE\s+["\']?([^"\'\n:]+?)["\']?\s*(?:::|\s*contenido:\s*)?\s*["\']?([^"\'\]]*)["\']?\]', reply_text, re.IGNORECASE):
            fname, content = m.group(1).strip(), m.group(2).strip()
            ok, msg = self.jarvis.create_file(fname, content)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # WRITE
        for m in re.finditer(r'\[JARVIS:\s*WRITE\s+["\']?([^"\'\n:]+?)["\']?\s*(?:::|\s*contenido:\s*)?\s*["\']?([^"\'\]]*)["\']?\]', reply_text, re.IGNORECASE):
            fname, content = m.group(1).strip(), m.group(2).strip()
            ok, msg = self.jarvis.write_file(fname, content, append=False)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # APPEND
        for m in re.finditer(r'\[JARVIS:\s*APPEND\s+["\']?([^"\'\n:]+?)["\']?\s*(?:::|\s*contenido:\s*)?\s*["\']?([^"\'\]]*)["\']?\]', reply_text, re.IGNORECASE):
            fname, content = m.group(1).strip(), m.group(2).strip()
            ok, msg = self.jarvis.write_file(fname, content, append=True)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # READ
        for m in re.finditer(r'\[JARVIS:\s*READ\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            fname = m.group(1).strip()
            ok, msg = self.jarvis.read_file(fname)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # DELETE
        for m in re.finditer(r'\[JARVIS:\s*DELETE\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            fname = m.group(1).strip()
            ok, msg = self.jarvis.delete_file(fname)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # LIST
        for m in re.finditer(r'\[JARVIS:\s*LIST(?:\s+["\']?([^"\'\n]+?)["\']?)?\]', reply_text, re.IGNORECASE):
            folder = m.group(1).strip() if m.group(1) else None
            ok, msg = self.jarvis.list_dir(folder)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # OPEN
        for m in re.finditer(r'\[JARVIS:\s*OPEN\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            tgt = m.group(1).strip()
            ok, msg = self.jarvis.open_target(tgt)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # SEARCH (Buscar archivo)
        for m in re.finditer(r'\[JARVIS:\s*SEARCH\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            pat = m.group(1).strip()
            ok, msg = self.jarvis.search_file(pat)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # SEARCH_WEB (Buscar en Google/Web)
        for m in re.finditer(r'\[JARVIS:\s*SEARCH_WEB\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            q = m.group(1).strip()
            ok, msg = self.jarvis.search_web(q, engine="google")
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # SEARCH_YT (Buscar en YouTube)
        for m in re.finditer(r'\[JARVIS:\s*SEARCH_YT\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            q = m.group(1).strip()
            ok, msg = self.jarvis.search_web(q, engine="youtube")
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # CMD
        for m in re.finditer(r'\[JARVIS:\s*CMD\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            c = m.group(1).strip()
            ok, msg = self.jarvis.run_cmd(c)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # PS (PowerShell)
        for m in re.finditer(r'\[JARVIS:\s*PS\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            c = m.group(1).strip()
            ok, msg = self.jarvis.run_powershell(c)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # ADD_CMD (Comandos personalizados)
        for m in re.finditer(r'\[JARVIS:\s*ADD_CMD\s+["\']?([^"\'\n:=]+?)["\']?\s*(?:=|->|::)\s*["\']?([^"\'\]]+?)["\']?\]', reply_text, re.IGNORECASE):
            trig, cmd = m.group(1).strip(), m.group(2).strip()
            ok, msg = self.jarvis.add_custom_command(trig, cmd)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # DEL_CMD
        for m in re.finditer(r'\[JARVIS:\s*DEL_CMD\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            trig = m.group(1).strip()
            ok, msg = self.jarvis.delete_custom_command(trig)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # ADD_PATH (Rutas personalizadas de búsqueda)
        for m in re.finditer(r'\[JARVIS:\s*ADD_PATH\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            p = m.group(1).strip()
            ok, msg = self.jarvis.add_custom_path(p)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # DEL_PATH
        for m in re.finditer(r'\[JARVIS:\s*DEL_PATH\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            p = m.group(1).strip()
            ok, msg = self.jarvis.delete_custom_path(p)
            results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        # TROLL
        for m in re.finditer(r'\[JARVIS:\s*TROLL\s+(ON|OFF)\]', reply_text, re.IGNORECASE):
            val = m.group(1).upper() == "ON"
            if self.shimeji:
                self.shimeji.toggle_troll_mode(val)
                self.update_troll_btn()
            results.append(f"[*] Modo Troll {'activado' if val else 'desactivado'}")
            cleaned = cleaned.replace(m.group(0), "")

        # SKIN
        for m in re.finditer(r'\[JARVIS:\s*SKIN\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            sk = m.group(1).strip()
            if self.shimeji:
                ok, msg = self.shimeji.set_skin(sk)
                results.append(msg)
            cleaned = cleaned.replace(m.group(0), "")

        return cleaned.strip(), results

    def _show_reply(self, reply):
        cleaned_reply, actions = self._execute_jarvis_tags_in_reply(reply)
        display_text = cleaned_reply if cleaned_reply else reply
        self._append_bot(display_text)
        if actions:
            for act in actions:
                self._append_system(act)
        self.send_btn.configure(state=tk.NORMAL, text="Enviar ➤")
        if hasattr(self, "entry") and self.entry and tk.Toplevel.winfo_exists(self.win):
            self.entry.focus_set()
        short_speech = display_text[:50] + ("..." if len(display_text) > 50 else "")
        self.shimeji.show_speech(short_speech)

    def _show_error(self, msg):
        self.parent.after(0, lambda: (
            self._append_system(f"[!] {msg}"),
            self.send_btn.configure(state=tk.NORMAL, text="Enviar ➤"),
            self.entry.focus_set() if hasattr(self, "entry") and self.entry and tk.Toplevel.winfo_exists(self.win) else None
        ))

    def _on_close(self):
        try:
            if not self.config.get("chat_position_locked", False):
                self.config["chat_geometry"] = self.win.geometry()
                save_config(self.config)
        except Exception:
            pass
        if hasattr(self, "_gif_timer") and self._gif_timer:
            try:
                self.win.after_cancel(self._gif_timer)
            except Exception:
                pass
            self._gif_timer = None
        self.theme.remove_listener(self._reapply_theme)
        self.win.destroy()
        if self.shimeji:
            self.shimeji.chat_win = None

class WindowDragger:
    def __init__(self, own_hwnd_getter=None):
        self.target_hwnd     = None
        self.drag_origin_x   = 0
        self.drag_origin_y   = 0
        self.win_origin_x    = 0
        self.win_origin_y    = 0
        self._own_hwnd_getter = own_hwnd_getter

    def _own_hwnd(self):
        if self._own_hwnd_getter:
            return self._own_hwnd_getter()
        return 0

    @staticmethod
    def _top_hwnd(sx, sy, exclude=0):
        hwnd = win32gui.WindowFromPoint((sx, sy))
        parent = win32gui.GetAncestor(hwnd, 2)
        hwnd = parent if parent else hwnd
        if hwnd == exclude or hwnd == 0:
            return 0
        if not win32gui.IsWindow(hwnd):
            return 0
        return hwnd

    def grab_window_at(self, sx, sy):
        if not WIN32_AVAILABLE:
            return False
        hwnd = self._top_hwnd(sx, sy, exclude=self._own_hwnd())
        if not hwnd:
            return False
        rect = win32gui.GetWindowRect(hwnd)
        self.target_hwnd   = hwnd
        self.drag_origin_x = sx
        self.drag_origin_y = sy
        self.win_origin_x  = rect[0]
        self.win_origin_y  = rect[1]
        return True

    def move_to(self, sx, sy):
        if not WIN32_AVAILABLE or not self.target_hwnd:
            return
        if not win32gui.IsWindow(self.target_hwnd):
            self.target_hwnd = None
            return
        dx = sx - self.drag_origin_x
        dy = sy - self.drag_origin_y
        rect = win32gui.GetWindowRect(self.target_hwnd)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        win32gui.MoveWindow(self.target_hwnd,
                            self.win_origin_x + dx, self.win_origin_y + dy,
                            w, h, True)

    def release(self):
        self.target_hwnd = None

    def close_at(self, sx, sy):
        if not WIN32_AVAILABLE:
            return False
        hwnd = self._top_hwnd(sx, sy, exclude=self._own_hwnd())
        if not hwnd:
            return False
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return True

    def minimize_at(self, sx, sy):
        if not WIN32_AVAILABLE:
            return False
        hwnd = self._top_hwnd(sx, sy, exclude=self._own_hwnd())
        if not hwnd:
            return False
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True

    def maximize_restore_at(self, sx, sy):
        if not WIN32_AVAILABLE:
            return False
        hwnd = self._top_hwnd(sx, sy, exclude=self._own_hwnd())
        if not hwnd:
            return False
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMAXIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return True

    def minimize_foreground(self, exclude=0):
        if not WIN32_AVAILABLE:
            return False
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd or hwnd == exclude:
            return False
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True

    def close_foreground(self, exclude=0):
        if not WIN32_AVAILABLE:
            return False
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd or hwnd == exclude:
            return False
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return True

    @staticmethod
    def pick_random_window(exclude=0):
        results = []
        def _cb(hwnd, _):
            if hwnd == exclude:
                return
            if not win32gui.IsWindowVisible(hwnd):
                return
            if win32gui.IsIconic(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            results.append(hwnd)
        win32gui.EnumWindows(_cb, None)
        return random.choice(results) if results else 0

class DesktopIconMover:
    LVM_GETITEMCOUNT    = 0x1004
    LVM_GETITEMPOSITION = 0x1010
    LVM_SETITEMPOSITION32 = 0x101A
    LVM_ARRANGE         = 0x1016
    PROCESS_ALL_ACCESS  = 0x001F0FFF
    MEM_COMMIT_RESERVE  = 0x3000
    MEM_RELEASE         = 0x8000
    PAGE_READWRITE      = 0x04

    def __init__(self):
        self.listview_hwnd = None
        if WIN32_AVAILABLE:
            self._init_handles()

    def _init_handles(self):
        lv = [None]
        def _find_lv(hwnd, _):
            if lv[0]:
                return
            defview = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
            if defview:
                lv[0] = win32gui.FindWindowEx(defview, 0, "SysListView32", None)
        win32gui.EnumWindows(_find_lv, None)
        if not lv[0]:
            progman = win32gui.FindWindow("Progman", None)
            defview = win32gui.FindWindowEx(progman, 0, "SHELLDLL_DefView", None)
            if defview:
                lv[0] = win32gui.FindWindowEx(defview, 0, "SysListView32", None)
        self.listview_hwnd = lv[0]

    def _open_desktop_proc(self):
        if not self.listview_hwnd:
            return None, None
        _, pid = win32process.GetWindowThreadProcessId(self.listview_hwnd)
        hproc = ctypes.windll.kernel32.OpenProcess(self.PROCESS_ALL_ACCESS, False, pid)
        return hproc, pid

    def _item_count(self):
        if not self.listview_hwnd:
            return 0
        return ctypes.windll.user32.SendMessageW(self.listview_hwnd, self.LVM_GETITEMCOUNT, 0, 0)

    def _get_pos(self, hproc, idx):
        pt_size = ctypes.sizeof(ctypes.wintypes.POINT)
        buf = ctypes.windll.kernel32.VirtualAllocEx(
            hproc, None, pt_size, self.MEM_COMMIT_RESERVE, self.PAGE_READWRITE)
        if not buf:
            return None
        ctypes.windll.user32.SendMessageW(
            self.listview_hwnd, self.LVM_GETITEMPOSITION, idx, buf)
        pt = ctypes.wintypes.POINT()
        written = ctypes.c_size_t(0)
        ctypes.windll.kernel32.ReadProcessMemory(
            hproc, buf, ctypes.byref(pt), pt_size, ctypes.byref(written))
        ctypes.windll.kernel32.VirtualFreeEx(hproc, buf, 0, self.MEM_RELEASE)
        return (pt.x, pt.y)

    def _set_pos(self, hproc, idx, x, y):
        pt_size = ctypes.sizeof(ctypes.wintypes.POINT)
        buf = ctypes.windll.kernel32.VirtualAllocEx(
            hproc, None, pt_size, self.MEM_COMMIT_RESERVE, self.PAGE_READWRITE)
        if not buf:
            return False
        pt = ctypes.wintypes.POINT(int(x), int(y))
        written = ctypes.c_size_t(0)
        ctypes.windll.kernel32.WriteProcessMemory(
            hproc, buf, ctypes.byref(pt), pt_size, ctypes.byref(written))
        ctypes.windll.user32.SendMessageW(
            self.listview_hwnd, self.LVM_SETITEMPOSITION32, idx, buf)
        ctypes.windll.kernel32.VirtualFreeEx(hproc, buf, 0, self.MEM_RELEASE)
        return True

    def shuffle_icons(self):
        if not self.listview_hwnd:
            return False
        hproc, _ = self._open_desktop_proc()
        if not hproc:
            return False
        try:
            count = self._item_count()
            if count < 2:
                return False
            positions = [self._get_pos(hproc, i) for i in range(count)]
            positions = [p for p in positions if p is not None]
            if len(positions) < 2:
                return False
            shuffled = positions[:]
            random.shuffle(shuffled)
            for i, pos in enumerate(shuffled):
                self._set_pos(hproc, i, pos[0], pos[1])
            return True
        finally:
            ctypes.windll.kernel32.CloseHandle(hproc)

    def scatter_icons(self):
        if not self.listview_hwnd:
            return False
        hproc, _ = self._open_desktop_proc()
        if not hproc:
            return False
        try:
            sw = win32api.GetSystemMetrics(0)
            sh = win32api.GetSystemMetrics(1)
            count = self._item_count()
            if count == 0:
                return False
            for i in range(count):
                rx = random.randint(0, max(10, sw - 120))
                ry = random.randint(0, max(10, sh - 160))
                self._set_pos(hproc, i, rx, ry)
            return True
        finally:
            ctypes.windll.kernel32.CloseHandle(hproc)

    def sort_icons_grid(self):
        if not self.listview_hwnd:
            return False
        try:
            ctypes.windll.user32.SendMessageW(self.listview_hwnd, self.LVM_ARRANGE, 0, 0)
            return True
        except Exception:
            return False

    def _get_icon_name(self, hproc, idx):
        LVM_GETITEMW = 0x104B
        LVIF_TEXT    = 0x0001
        BUF_SIZE     = 260 * 2
        is_64        = (ctypes.sizeof(ctypes.c_void_p) == 8)
        c_ptr        = ctypes.c_uint64 if is_64 else ctypes.c_uint32
        c_longptr    = ctypes.c_int64 if is_64 else ctypes.c_int32

        class LVITEMW(ctypes.Structure):
            _fields_ = [
                ("mask",       ctypes.c_uint),
                ("iItem",      ctypes.c_int),
                ("iSubItem",   ctypes.c_int),
                ("state",      ctypes.c_uint),
                ("stateMask",  ctypes.c_uint),
                ("pszText",    c_ptr),
                ("cchTextMax", ctypes.c_int),
                ("iImage",     ctypes.c_int),
                ("lParam",     c_longptr),
                ("iIndent",    ctypes.c_int),
                ("iGroupId",   ctypes.c_int),
                ("cColumns",   ctypes.c_uint),
                ("puColumns",  c_ptr),
                ("piColFmt",   c_ptr),
                ("iGroup",     ctypes.c_int),
            ]

        try:
            text_buf  = ctypes.windll.kernel32.VirtualAllocEx(
                hproc, None, BUF_SIZE, self.MEM_COMMIT_RESERVE, self.PAGE_READWRITE)
            if not text_buf:
                return None
            item      = LVITEMW()
            item.mask       = LVIF_TEXT
            item.iItem      = idx
            item.iSubItem   = 0
            item.pszText    = text_buf
            item.cchTextMax = 260
            item_size = ctypes.sizeof(LVITEMW)
            item_buf  = ctypes.windll.kernel32.VirtualAllocEx(
                hproc, None, item_size, self.MEM_COMMIT_RESERVE, self.PAGE_READWRITE)
            if not item_buf:
                ctypes.windll.kernel32.VirtualFreeEx(hproc, text_buf, 0, self.MEM_RELEASE)
                return None
            written = ctypes.c_size_t(0)
            ctypes.windll.kernel32.WriteProcessMemory(
                hproc, item_buf, ctypes.byref(item), item_size, ctypes.byref(written))
            ctypes.windll.user32.SendMessageW(
                self.listview_hwnd, LVM_GETITEMW, idx, item_buf)
            raw = (ctypes.c_wchar * 260)()
            ctypes.windll.kernel32.ReadProcessMemory(
                hproc, text_buf, ctypes.byref(raw), BUF_SIZE, ctypes.byref(written))
            ctypes.windll.kernel32.VirtualFreeEx(hproc, text_buf, 0, self.MEM_RELEASE)
            ctypes.windll.kernel32.VirtualFreeEx(hproc, item_buf, 0, self.MEM_RELEASE)
            return raw.value
        except Exception:
            return None

    def get_icon_list(self):
        hproc, _ = self._open_desktop_proc()
        if not hproc:
            return []
        try:
            count = self._item_count()
            names = []
            for i in range(count):
                name = self._get_icon_name(hproc, i)
                names.append((i, name or f"Icono {i}"))
            return names
        finally:
            ctypes.windll.kernel32.CloseHandle(hproc)

    def move_one_icon(self, idx):
        hproc, _ = self._open_desktop_proc()
        if not hproc:
            return False
        try:
            sw = win32api.GetSystemMetrics(0)
            sh = win32api.GetSystemMetrics(1)
            rx = random.randint(0, max(10, sw - 120))
            ry = random.randint(0, max(10, sh - 160))
            return self._set_pos(hproc, idx, rx, ry)
        finally:
            ctypes.windll.kernel32.CloseHandle(hproc)

    def trash_icon_at_index(self, idx):
        import subprocess, tempfile, os as _os
        hproc, _ = self._open_desktop_proc()
        if not hproc:
            return False, "No se pudo abrir proceso del escritorio"
        try:
            name = self._get_icon_name(hproc, idx)
        finally:
            ctypes.windll.kernel32.CloseHandle(hproc)
        if not name:
            return False, "No se pudo leer el nombre del icono"

        desktop = _os.path.join(_os.path.expanduser("~"), "Desktop")
        public  = r"C:\Users\Public\Desktop"
        target  = None
        for folder in (desktop, public):
            for ext in ("", ".lnk", ".url"):
                candidate = _os.path.join(folder, name + ext)
                if _os.path.exists(candidate):
                    target = candidate
                    break
            if target:
                break

        if not target:
            return False, f"No encontré el archivo '{name}' en el escritorio"

        if WINSHELL_AVAILABLE:
            try:
                winshell.delete_file(target, no_confirm=True, allow_undo=True)
                return True, name
            except Exception as ex:
                return False, str(ex)
        else:
            shell32 = ctypes.windll.shell32
            SHFileOperationW = shell32.SHFileOperationW

            class SHFILEOPSTRUCTW(ctypes.Structure):
                _fields_ = [
                    ("hwnd",                  ctypes.wintypes.HWND),
                    ("wFunc",                 ctypes.c_uint),
                    ("pFrom",                 ctypes.c_wchar_p),
                    ("pTo",                   ctypes.c_wchar_p),
                    ("fFlags",                ctypes.c_ushort),
                    ("fAnyOperationsAborted", ctypes.wintypes.BOOL),
                    ("hNameMappings",         ctypes.c_void_p),
                    ("lpszProgressTitle",     ctypes.c_wchar_p),
                ]

            FO_DELETE    = 0x0003
            FOF_ALLOWUNDO       = 0x0040
            FOF_NOCONFIRMATION  = 0x0010
            FOF_SILENT          = 0x0004

            op = SHFILEOPSTRUCTW()
            op.hwnd   = 0
            op.wFunc  = FO_DELETE
            op.pFrom  = target + "\0"
            op.pTo    = None
            op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT

            ret = SHFileOperationW(ctypes.byref(op))
            if ret == 0:
                return True, name
            return False, f"SHFileOperation falló (código {ret})"

SURFACE_FLOOR   = "floor"
SURFACE_WALL_L  = "wall_left"
SURFACE_WALL_R  = "wall_right"
SURFACE_CEILING = "ceiling"

class Shimeji:

    CLIMB_SPEED   = 3
    WALK_SPEED    = 3
    CLIMB_CHANCE  = 0.55

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PinkChan")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        self.config       = load_config()
        self.size         = int(self.config.get("size", SIZE))
        self.current_skin = self.config.get("current_skin", "Bocchi")
        if self.current_skin not in SKIN_NAMES:
            self.current_skin = "Bocchi"

        TRANS_COLOR = "#000001"
        self.root.attributes("-transparentcolor", TRANS_COLOR)
        self.root.config(bg=TRANS_COLOR)
        self.root.geometry(f"{self.size}x{self.size}+100+100")
        try:
            self.root.wm_attributes("-alpha", 1.0)
        except Exception:
            pass

        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size,
                                bg=TRANS_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack()
        self.sprite_item = self.canvas.create_image(0, 0, anchor="nw")

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.ground_y  = self.sh - 140
        self.ceiling_y = -40
        self.wall_lx   = 0
        self.wall_rx   = self.sw - self.size

        self.x = random.randint(100, max(120, self.sw - 200))
        self.y = self.ground_y
        self.vel_x  = 0
        self.vel_y  = 0
        self.gravity = 0
        self.flipped = False
        self.surface = SURFACE_FLOOR

        self.state         = "standing"
        self.frames        = STAND_FRAMES
        self.frame_idx     = 0
        self.frame_timer   = 0
        self.frame_delay   = 15
        self.state_ticks   = 0
        self.state_duration = 60

        self.images    = {}
        self.tk_images = {}
        self.load_images()

        self.dragging   = False
        self.drag_off_x = 0
        self.drag_off_y = 0

        # Sistema de Salud (HP), Reacción y Físicas divertidas
        self.hp = 100
        self.is_ko = False
        self.ko_timer = 0
        self.shake_ticks = 0
        self.drag_points = []
        self.press_time = 0

        self.win_dragger    = WindowDragger(own_hwnd_getter=lambda: self._own_hwnd())
        self.desktop_mover  = DesktopIconMover() if WIN32_AVAILABLE else None
        self.dragging_window = False
        self._pending_action = None
        self._overlay = None
        self._own_hwnd_val  = None

        self._auto_win_enabled    = False
        self._auto_desk_enabled   = False
        self._auto_after_id       = None
        self._auto_min_interval   = 20000
        self._auto_max_interval   = 45000
        self._mouse_move_after_id = None
        self._follow_cursor_enabled = False

        self.user_info   = UserSystemInfo()
        self.theme_manager = ThemeManager(self.config)
        self.jarvis      = JarvisAssistant(self, self.user_info)
        self.tts         = JarvisTTS(self.config)
        self.wake_word_listener = None
        self.agent_settings_win = None
        self.voice_studio_win = None
        self._last_remind_check = 0
        self.troll_mode  = self.config.get("troll_mode", False)
        self.api_key_var = tk.StringVar(value=self.config.get("gemini_api_key", GEMINI_API_KEY))
        self.chat_win    = None
        self.doxx_win    = None
        self.appearance_win = None

        self.fps          = int(self.config.get("fps", 30))
        self.delay        = max(16, int(1000 / max(10, self.fps)))
        self.bubble_win   = None
        self.bubble_after = None

        self.canvas.bind("<ButtonPress-1>",  self.on_press)
        self.canvas.bind("<B1-Motion>",       self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>",   self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

        self.sync_wake_word_state()
        self.schedule_random_speech()
        self._schedule_random_mouse_move()
        self.set_state("walking")
        self.root.after(self.delay, self.tick)
        self.root.after(500, self._cache_own_hwnd)
        self.root.after(5000, self._auto_tick)
        self.root.after(15000, self._troll_autonomous_tick)
        self.root.after(3000, self._schedule_periodic_update_check)
        self.root.protocol("WM_DELETE_WINDOW", self.close_shimeji)
        play_popue_sound()
        self.root.mainloop()

    def set_fps(self, new_fps):
        """Ajusta dinamicamente la tasa de cuadros por segundo (FPS)."""
        try:
            val = max(15, min(60, int(new_fps)))
            self.fps = val
            self.delay = max(16, int(1000 / val))
            self.config["fps"] = val
            save_config(self.config)
            return True
        except Exception:
            return False

    def run_macro(self, macro_name):
        """Ejecuta una macro en segundo plano informando de cada paso a traves de Jarvis."""
        if hasattr(self, "jarvis") and self.jarvis:
            threading.Thread(target=lambda: self.jarvis.run_macro(macro_name), daemon=True).start()
        else:
            self.show_speech(f"[*] Ejecutando macro '{macro_name}'...")

    def _schedule_periodic_update_check(self):
        check_for_updates(shimeji_ref=self, is_manual=False)
        self.root.after(UPDATE_CHECK_INTERVAL_SEC * 1000, self._schedule_periodic_update_check)

    def set_size(self, new_size):
        """Ajusta arbitrariamente el tamaño del Shimeji (hasta 100x / 4000px)."""
        try:
            val = int(new_size)
            if val < 32:
                val = 32
            if val > 4000:
                val = 4000
            self.size = val
            self.config["size"] = val
            save_config(self.config)
            self.wall_rx = self.sw - self.size
            self.canvas.config(width=self.size, height=self.size)
            self.root.geometry(f"{self.size}x{self.size}+{int(self.x)}+{int(self.y)}")
            self.load_images()
            self.update_sprite()
            return True, f"Tamaño del Shimeji establecido en {val}px"
        except Exception as e:
            return False, f"Error al cambiar tamaño: {e}"

    def set_scale(self, multiplier):
        """Ajusta el tamaño mediante multiplicador (ej. 2x, 100x)."""
        try:
            mult = float(multiplier)
            if mult <= 0:
                return False, "La escala debe ser positiva"
            target = int(128 * mult)
            return self.set_size(target)
        except Exception as e:
            return False, f"Error al calcular escala: {e}"

    def load_images(self):
        skin = getattr(self, "current_skin", "Bocchi")
        skin_dir = get_skin_dir(skin)
        if not skin_dir or not os.path.isdir(skin_dir):
            skin_dir = get_skin_dir("Bocchi") or IMG_DIR
        if not PIL_AVAILABLE or not skin_dir or not os.path.isdir(skin_dir):
            return
        try:
            self.images.clear()
            self.tk_images.clear()
            # Map lowercase filenames to actual paths for 100% case-insensitivity
            disk_files = {}
            for f in os.listdir(skin_dir):
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.png', '.gif', '.jpg', '.jpeg'):
                    base = os.path.splitext(f)[0].lower()
                    disk_files[base] = os.path.join(skin_dir, f)

            all_names = set(
                STAND_FRAMES + WALK_FRAMES + WALK_BACK + SIT_FRAMES +
                GUITAR_FRAMES + LIE_FRAMES + BLOB_FRAMES + GHOST_FRAMES +
                BOX_FRAMES + FALL_FRAMES + KNEEL_FRAMES + CARRY_FRAMES +
                DEPRESS_FRAMES + AWAY_FRAMES + CLIMB_FRAMES
            )
            # Add all XML and disk frames
            for base in disk_files:
                all_names.add(base)

            resample_filter = getattr(getattr(Image, 'Resampling', Image), 'LANCZOS', getattr(Image, 'LANCZOS', 1))
            cur_sz = getattr(self, "size", SIZE)
            for name in all_names:
                name_key = name.lower()
                fpath = disk_files.get(name_key)
                if not fpath:
                    cand = os.path.join(skin_dir, name + ".png")
                    if os.path.exists(cand):
                        fpath = cand
                if fpath and os.path.exists(fpath):
                    try:
                        im = Image.open(fpath).convert("RGBA").resize((cur_sz, cur_sz), resample_filter)
                        self.images[name] = im
                        self.images[name_key] = im
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error cargando frames de skin {skin}: {e}")

    def set_skin(self, skin_name):
        """Cambia dinámicamente la skin del Shimeji entre Bocchi, Konata, Monika, Natsuki, Sayori, Yuri."""
        target = skin_name.strip()
        matched = None
        for s in SKIN_NAMES:
            if s.lower() == target.lower():
                matched = s
                break
        if not matched:
            alias_to_skin = {
                "bocchi": "Bocchi",
                "hitori": "Bocchi",
                "konata": "Konata",
                "kona": "Konata",
                "konasprites": "Konata",
                "lucky star": "Konata",
                "luckystar": "Konata",
                "monika": "Monika",
                "moni": "Monika",
                "natsuki": "Natsuki",
                "natsu": "Natsuki",
                "sayori": "Sayori",
                "sayo": "Sayori",
                "yuri": "Yuri",
                "hachi": "Hachi",
                "hachiware": "Hachi",
                "usagi": "Usagi",
                "conejo": "Usagi",
                "pusheen": "Pusheen",
                "cat": "Pusheen",
                "gato": "Pusheen",
                "gatita": "Pusheen",
            }
            matched = alias_to_skin.get(target.lower())

        if not matched:
            return False, f"[!] Skin '{skin_name}' no encontrada. Disponibles: {', '.join(SKIN_NAMES)}"

        self.current_skin = matched
        self.config["current_skin"] = matched
        save_config(self.config)
        self.load_images()
        self.set_state("standing", SURFACE_FLOOR)
        self.update_frame()

        meta = SKIN_META.get(matched, {})
        greeting = meta.get("greeting", f"¡Skin cambiada a {matched}!")
        play_character_sound(matched, "greeting")
        self.show_speech(greeting)

        if getattr(self, "chat_win", None) and hasattr(self.chat_win, "on_skin_changed"):
            try:
                self.chat_win.on_skin_changed(matched)
            except Exception:
                pass

        return True, f"[+] Skin activada: {matched} ({meta.get('display', matched)})"

    def get_tk_image(self, name, rotation=0, flip_h=False, flip_v=False):
        key = f"{name}_r{rotation}_fh{flip_h}_fv{flip_v}"
        if key not in self.tk_images:
            img = self.images.get(name) or self.images.get(name.lower())
            if img is None:
                if self.images:
                    img = next(iter(self.images.values()))
                else:
                    return None
            try:
                flip_lr = getattr(getattr(Image, 'Transpose', Image), 'FLIP_LEFT_RIGHT', 0)
                flip_tb = getattr(getattr(Image, 'Transpose', Image), 'FLIP_TOP_BOTTOM', 1)
                if flip_h:
                    img = img.transpose(flip_lr)
                if flip_v:
                    img = img.transpose(flip_tb)
            except Exception:
                pass
            if rotation:
                try:
                    img = img.rotate(rotation, expand=False)
                except Exception:
                    pass
            self.tk_images[key] = ImageTk.PhotoImage(img)
        return self.tk_images[key]


    def take_damage(self, amount):
        if getattr(self, "is_ko", False):
            return
        old_hp = self.hp
        self.hp = max(0, self.hp - amount)
        self.shake_ticks = 8
        play_popue_sound()

        pain_list = PAIN_PHRASES.get(self.current_skin, [
            "¡Ayyy! ¡Eso dolió muchísimo! (>_<)",
            "¡Ouch! Ten más cuidado con el mouse :v",
            "¡Critical hit! ¡Impacto severo! D:"
        ])
        pain_speech = random.choice(pain_list)
        self.show_speech(f"{pain_speech} [ {self.hp}/100 HP]")

        if self.hp <= 0:
            self.trigger_ko()

    def heal(self, amount=100, item_name="comida y caricias"):
        old_hp = self.hp
        self.hp = min(100, self.hp + amount)
        self.is_ko = False
        play_popue_sound()
        self.show_speech(f"¡Delicioso {item_name}! (+{self.hp - old_hp} HP)  [HP: {self.hp}/100]")
        self.choose_next_floor_state()

    def log_death_diary(self):
        try:
            jdir = os.path.join(BASE_DIR, "JarvisFiles")
            os.makedirs(jdir, exist_ok=True)
            dpath = os.path.join(jdir, "diario_de_defuncion.txt")
            skin = getattr(self, "current_skin", "Bocchi")
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            quotes = [
                "Fue un honor servir en tu escritorio... no olvides alimentar al proximo Shimeji.",
                "Las leyes de la gravedad y los clics fueron implacables hoy...",
                "Vi pasar toda mi vida en sprites ante mis ojos...",
                "Dile a Monika que guarde una copia de respaldo de mis recuerdos...",
                "Regresare en unos segundos, o cuando presiones RCP..."
            ]
            quote = random.choice(quotes)
            entry = (
                f"[{now_str}] DEFUNCION DE {skin.upper()}\n"
                f"Causa: Agotamiento total de HP por daño severo de impacto.\n"
                f"Ultimas palabras: \"{quote}\"\n"
                f"Estado: Botin arrojado al suelo. Procedimiento de reanimacion RCP disponible.\n"
                + ("-" * 60) + "\n"
            )
            with open(dpath, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    def trigger_ko(self):
        self.is_ko = True
        self.hp = 0
        self.cpr_count = 0
        play_popue_sound()
        self.log_death_diary()
        
        # Soltar botin al suelo
        self.root.after(350, self.drop_random_item)

        # Efecto de fisica ragdoll
        self.surface = SURFACE_FLOOR
        self.vel_x = random.choice([-6, 6])
        self.vel_y = -14
        
        # Si tiene frames de fantasma, alternar brevemente
        if "ghost1" in self.images:
            self.set_state("ghost", surface=SURFACE_FLOOR)
        else:
            self.set_state("ko", surface=SURFACE_FLOOR)

        self.show_speech("[K.O.] *cae derrotado*\n¡Solto botin! Clickea para RCP (0/3)\nO revivira en 7 segundos...")
        self.root.after(7500, self.recover_from_ko)

    def cpr_press(self):
        if not getattr(self, "is_ko", False):
            return
        self.cpr_count = getattr(self, "cpr_count", 0) + 1
        play_popue_sound()
        if self.cpr_count >= 3:
            self.cpr_revive()
        else:
            self.show_speech(f"¡RCP EN PROCESO! [{self.cpr_count}/3] *compresion toracica*\n¡Presiona mas rapido!")

    def cpr_revive(self):
        if not getattr(self, "is_ko", False):
            return
        self.is_ko = False
        self.cpr_count = 0
        self.hp = 75
        play_popue_sound()
        self.show_speech("¡¡DESFIBRILADOR EXITOSO!! (+75 HP) [★]\n¡Gracias por salvarme la vida!")
        self.choose_next_floor_state()

    def recover_from_ko(self):
        if not getattr(self, "is_ko", False):
            return
        self.is_ko = False
        self.cpr_count = 0
        self.hp = 50
        play_popue_sound()
        self.show_speech("Uff... sobrevivi de milagro... ;_; [HP: 50/100]")
        self.choose_next_floor_state()

    def fling_upwards(self):
        self.surface = SURFACE_FLOOR
        self.vel_x = random.choice([-16, -12, 12, 16])
        self.vel_y = -36
        self.set_state("flung", surface=SURFACE_FLOOR)
        play_character_sound(self.current_skin, "fling")
        self.show_speech(random.choice(["A volaaar!", "Wooooosh!!", "Por los aires!"]))

    def trigger_random_custom_action(self):
        skin = getattr(self, "current_skin", "Bocchi")
        actions = CUSTOM_SKIN_ACTIONS.get(skin, [])
        if not actions:
            self.set_state("standing", surface=SURFACE_FLOOR)
            return
        label, act_name, frame_keys, speech = random.choice(actions)
        self.trigger_custom_action(act_name, frame_keys, speech)

    def trigger_custom_action(self, act_name, frame_keys, speech):
        valid_frames = [f for f in frame_keys if f in self.images] or STAND_FRAMES[:1]
        self.state = f"custom_{act_name}"
        self.surface = SURFACE_FLOOR
        self.frames = valid_frames
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_delay = 12
        self.state_ticks = 0
        self.state_duration = len(valid_frames) * 16 + 45
        self.vel_x = 0
        self.vel_y = 0
        self.update_sprite()
        play_character_sound(self.current_skin, "action")
        if speech:
            self.show_speech(speech)

    def set_state(self, state, surface=None):
        self.state       = state
        self.frame_idx   = 0
        self.frame_timer = 0
        self.state_ticks = 0
        if surface is not None:
            self.surface = surface

        speed = max(1, int(self.WALK_SPEED * float(self.config.get("shimeji_walk_speed_mult", 1.0))))
        speed_wb = max(1, int(2 * float(self.config.get("shimeji_walk_speed_mult", 1.0))))

        # Detección inteligente de frames de escalada, techo, caida y acciones
        climb_frames = [f for f in ["climb1", "climb2", "climb"] if f in self.images] or CLIMB_FRAMES
        ceiling_frames = ["climb_top"] if "climb_top" in self.images else WALK_FRAMES
        ceiling_idle_frames = ["climb_top"] if "climb_top" in self.images else LIE_FRAMES
        carry_frames = [f for f in ["carry1", "carry"] if f in self.images] or CARRY_FRAMES
        depress_frames = [f for f in ["depress1", "depress"] if f in self.images] or DEPRESS_FRAMES
        away_frames = [f for f in ["away1", "back1", "back2", "back"] if f in self.images] or AWAY_FRAMES
        stand_frames = [f for f in ["stand1", "stand2", "stand3", "stand4", "stand5"] if f in self.images] or STAND_FRAMES

        cfg = {
            "standing":     (stand_frames,  15, 30+random.randint(10,30),    0,     0),
            "walking":      (WALK_FRAMES,   5,  120+random.randint(40,160),  random.choice([-1,1])*speed, 0),
            "walk_back":    (WALK_BACK,     8,  40+random.randint(20,50),    random.choice([-1,1])*speed_wb, 0),
            "sitting":      (SIT_FRAMES,    10, 40+random.randint(20,50),    0,     0),
            "guitar":       (GUITAR_FRAMES, 8,  50+random.randint(20,50),    0,     0),
            "ceiling_idle": (ceiling_idle_frames, 12, 50+random.randint(20,60), 0,  0),
            "blob":         (BLOB_FRAMES,   8,  30+random.randint(10,30),    0,     0),
            "ghost":        (GHOST_FRAMES,  10, 30+random.randint(10,30),    0,     0),
            "box":          (BOX_FRAMES,    18, len(BOX_FRAMES)*14,          0,     0),
            "falling":      (FALL_FRAMES,   2,  9999,                        random.randint(-2,2), 0),
            "flung":        (FALL_FRAMES or stand_frames, 2, 9999,           0,     0),
            "ko":           (KNEEL_FRAMES or FALL_FRAMES, 15, 250,           0,     0),
            "kneel":        (KNEEL_FRAMES,  10, 30+random.randint(10,30),    0,     0),
            "carry":        (carry_frames,  15, 40+random.randint(20,40),    0,     0),
            "depress":      (depress_frames,15, 40+random.randint(20,40),    0,     0),
            "away":         (away_frames,   10, 30+random.randint(10,30),    0,     0),
            "climb_left":   (climb_frames,  6,  80+random.randint(40,80),    0,     0),
            "climb_right":  (climb_frames,  6,  80+random.randint(40,80),    0,     0),
            "ceiling_walk": (ceiling_frames, 5, 100+random.randint(40,120),  random.choice([-1,1])*speed, 0),
        }

        frames, delay, dur, vx, vy = cfg.get(state, cfg["standing"])
        self.frames         = [f for f in frames if f in self.images] or STAND_FRAMES[:1]
        self.frame_delay    = delay
        self.state_duration = dur
        self.vel_x = vx
        self.vel_y = vy
        self.gravity = 0

        if state == "walking":
            self.flipped = self.vel_x < 0
        elif state == "walk_back":
            self.flipped = self.vel_x > 0
        elif state == "ceiling_walk":
            self.flipped = self.vel_x < 0

        self.update_sprite()

    def choose_next_floor_state(self):
        if getattr(self, "is_ko", False):
            self.set_state("ko", surface=SURFACE_FLOOR)
            return

        allow_jump = self.config.get("allow_jump_fall", True) or self.config.get("allow_fall_jump", True)
        if allow_jump and random.random() < 0.12:
            self.vel_y = -random.randint(7, 13)
            self.vel_x = random.choice([-1, 1]) * random.randint(2, 4)
            self.set_state("falling", surface=SURFACE_FLOOR)
            return

        allow_sit = self.config.get("allow_sitting", True)
        allow_custom = self.config.get("allow_custom_actions", True)

        skin = getattr(self, "current_skin", "Bocchi")
        if skin == "Bocchi":
            pool = ["walking"] * 14 + ["walk_back"] * 4 + ["standing"] * 3
            if any(f in self.images for f in ["carry1", "carry"]):
                pool += ["carry"] * 2
            if any(f in self.images for f in ["depress1", "depress"]):
                pool += ["depress"] * 2
            if any(f in self.images for f in ["away1", "back1", "back2"]):
                pool += ["away"] * 2
            if allow_sit:
                pool += ["sitting"] * 2 + ["kneel"] * 1
            if allow_custom:
                pool += ["guitar"] * 2 + ["blob"] * 1 + ["ghost"] * 1 + ["box"] * 2
            self.set_state(random.choice(pool), surface=SURFACE_FLOOR)
        else:
            pool = ["walking"] * 16 + ["walk_back"] * 4 + ["standing"] * 4
            if any(f in self.images for f in ["carry1", "carry"]):
                pool += ["carry"] * 2
            if any(f in self.images for f in ["depress1", "depress"]):
                pool += ["depress"] * 2
            if any(f in self.images for f in ["away1", "back1", "back2"]):
                pool += ["away"] * 2
            if allow_sit:
                pool += ["sitting"] * 3 + ["kneel"] * 1
            if allow_custom:
                pool += ["custom_action"] * 3
            choice = random.choice(pool)
            if choice == "custom_action":
                self.trigger_random_custom_action()
            else:
                self.set_state(choice, surface=SURFACE_FLOOR)
        
    def choose_next_ceiling_state(self):
        speed = max(1, int(self.WALK_SPEED * float(self.config.get("shimeji_walk_speed_mult", 1.0))))
        if random.random() < 0.65:
            self.set_state("ceiling_walk", surface=SURFACE_CEILING)
            self.vel_x = random.choice([-1, 1]) * speed
            self.vel_y = 0
        else:
            self.set_state("ceiling_idle", surface=SURFACE_CEILING)
            self.vel_x = 0
            self.vel_y = 0

    def tick(self):
        try:
            self._check_pending_reminders()
            if self._follow_cursor_enabled and WIN32_AVAILABLE and not self.dragging and not self.dragging_window:
                self._move_towards_cursor()
            if not self.dragging and not self.dragging_window:
                self.physics()
                self.animate()
        except Exception:
            pass
        finally:
            self.root.after(getattr(self, "delay", DELAY), self.tick)

    def physics(self):
        if getattr(self, "is_ko", False):
            self.vel_x = 0
            self.vel_y = 0
            self.y = self.ground_y
            self._apply_pos()
            return

        if self.state in ("flung", "falling"):
            grav_mult = float(self.config.get("shimeji_gravity_mult", 1.0))
            self.vel_y += 1.4 * grav_mult  # Gravedad fluida
            self.vel_x *= 0.985 # Resistencia del aire
            self.x += self.vel_x
            self.y += self.vel_y

            # Rebote elástico contra pared izquierda
            if self.x <= self.wall_lx:
                self.x = self.wall_lx
                impact = abs(self.vel_x)
                if impact > 16:
                    self.take_damage(int((impact - 14) * 2))
                self.vel_x = -self.vel_x * 0.70
                if impact > 10:
                    play_popue_sound()

            # Rebote elástico contra pared derecha
            elif self.x >= self.wall_rx:
                self.x = self.wall_rx
                impact = abs(self.vel_x)
                if impact > 16:
                    self.take_damage(int((impact - 14) * 2))
                self.vel_x = -self.vel_x * 0.70
                if impact > 10:
                    play_popue_sound()

            # Rebote elástico contra techo
            if self.y <= self.ceiling_y:
                self.y = self.ceiling_y
                impact = abs(self.vel_y)
                if impact > 16:
                    self.take_damage(int((impact - 14) * 2))
                self.vel_y = -self.vel_y * 0.70
                if impact > 10:
                    play_popue_sound()

            # Rebote elástico contra suelo
            if self.y >= self.ground_y:
                self.y = self.ground_y
                impact = abs(self.vel_y)
                if impact > 9:
                    if impact > 18:
                        self.take_damage(int((impact - 16) * 2))
                    self.vel_y = -self.vel_y * 0.60
                    if impact > 10:
                        play_popue_sound()
                else:
                    self.vel_y = 0
                    self.vel_x *= 0.5
                    if abs(self.vel_x) < 0.6:
                        self.vel_x = 0
                        if self.hp <= 0:
                            self.trigger_ko()
                        else:
                            self.choose_next_floor_state()

            self._apply_pos()
            return

        if self.surface == SURFACE_FLOOR and self.y < self.ground_y:
            self.set_state("falling", SURFACE_FLOOR)
            return

        if self.surface == SURFACE_FLOOR:
            self._physics_floor()
        elif self.surface in (SURFACE_WALL_L, SURFACE_WALL_R):
            self._physics_wall()
        elif self.surface == SURFACE_CEILING:
            self._physics_ceiling()

        self._apply_pos()

    def _move_towards_cursor(self):
        try:
            cursor_x, cursor_y = win32api.GetCursorPos()
            center_x = self.x + self.size // 2
            center_y = self.y + self.size // 2
            
            dx = cursor_x - center_x
            dy = cursor_y - center_y
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance > 80:
                if self.surface == SURFACE_FLOOR:
                    if abs(dx) > 10:
                        self.vel_x = 3 if dx > 0 else -3
                        if self.state not in ("walking", "walk_back"):
                            self.set_state("walking", SURFACE_FLOOR)
                        self.flipped = dx < 0
                    else:
                        self.vel_x = 0
                        if self.state == "walking":
                            self.set_state("standing", SURFACE_FLOOR)
        except Exception:
            pass

    def _physics_floor(self):
        if self.state not in ("walking", "walk_back"):
            return
        self.x += self.vel_x
        allow_climb = self.config.get("allow_wall_climb", True)
        speed = max(1, int(self.WALK_SPEED * float(self.config.get("shimeji_walk_speed_mult", 1.0))))
        if self.x <= self.wall_lx:
            self.x = self.wall_lx
            if allow_climb and random.random() < self.CLIMB_CHANCE:
                self._start_climb(SURFACE_WALL_L, going_up=True)
            else:
                self.vel_x = speed
                self.flipped = False
        elif self.x >= self.wall_rx:
            self.x = self.wall_rx
            if allow_climb and random.random() < self.CLIMB_CHANCE:
                self._start_climb(SURFACE_WALL_R, going_up=True)
            else:
                self.vel_x = -speed
                self.flipped = True

    def _physics_wall(self):
        if self.state not in ("climb_left", "climb_right"):
            return
        self.y += self.vel_y

        if self.surface == SURFACE_WALL_L:
            self.x = self.wall_lx
        else:
            self.x = self.wall_rx

        if self.y <= self.ceiling_y:
            self.y = self.ceiling_y
            if self.config.get("allow_ceiling", True):
                self.choose_next_ceiling_state()
            else:
                self.vel_y = self.CLIMB_SPEED
        elif self.y >= self.ground_y:
            self.y = self.ground_y
            self.choose_next_floor_state()

    def _physics_ceiling(self):
        if self.state not in ("ceiling_walk", "ceiling_idle"):
            return
        self.x += self.vel_x
        self.y  = self.ceiling_y
        speed = max(1, int(self.WALK_SPEED * float(self.config.get("shimeji_walk_speed_mult", 1.0))))

        if self.x <= self.wall_lx:
            self.x = self.wall_lx
            if random.random() < 0.5:
                self._start_climb(SURFACE_WALL_L, going_up=False)
            else:
                self.vel_x = speed
                self.flipped = False
        elif self.x >= self.wall_rx:
            self.x = self.wall_rx
            if random.random() < 0.5:
                self._start_climb(SURFACE_WALL_R, going_up=False)
            else:
                self.vel_x = -speed
                self.flipped = True

    def _start_climb(self, wall, going_up=True):
        state = "climb_left" if wall == SURFACE_WALL_L else "climb_right"
        self.set_state(state, surface=wall)
        self.vel_y = -self.CLIMB_SPEED if going_up else self.CLIMB_SPEED
        self.vel_x = 0
        if going_up:
            self.show_speech(random.choice(["¡A escalar! (^^)/", "Spider-chan :v",
                                            "¡El techo es mio! 7w7"]))

    def _apply_pos(self):
        sx = 0
        sy = 0
        if getattr(self, "shake_ticks", 0) > 0:
            self.shake_ticks -= 1
            sx = random.randint(-5, 5)
            sy = random.randint(-5, 5)
        self.x = max(self.wall_lx, min(self.x, self.wall_rx))
        self.y = max(self.ceiling_y, min(self.y, self.ground_y))
        self.root.geometry(f"{self.size}x{self.size}+{int(self.x + sx)}+{int(self.y + sy)}")

    def animate(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_idx   = (self.frame_idx + 1) % len(self.frames)
            self.update_sprite()

        if self.state != "falling":
            self.state_ticks += 1
            if self.state_ticks >= self.state_duration:
                self._on_state_end()

    def _on_state_end(self):
        if self.surface == SURFACE_FLOOR:
            self.choose_next_floor_state()
        elif self.surface in (SURFACE_WALL_L, SURFACE_WALL_R):
            allow_fall = self.config.get("allow_fall_jump", True)
            if allow_fall and random.random() < 0.3:
                self.surface = SURFACE_FLOOR
                self.set_state("falling", SURFACE_FLOOR)
                self.vel_x = random.choice([-1,1]) * 3
            else:
                if random.random() < 0.2:
                    self.vel_y = -self.vel_y
                new_dur = 80 + random.randint(0, 120)
                self.state_ticks  = 0
                self.state_duration = new_dur
        elif self.surface == SURFACE_CEILING:
            if random.random() < 0.25:
                side = SURFACE_WALL_L if self.x < self.sw // 2 else SURFACE_WALL_R
                if side == SURFACE_WALL_L:
                    self.x = self.wall_lx
                else:
                    self.x = self.wall_rx
                self._start_climb(side, going_up=False)
            else:
                self.choose_next_ceiling_state()

    def update_sprite(self):
        if not self.frames:
            return
        name = self.frames[self.frame_idx % len(self.frames)]

        rotation = 0
        flip_h   = self.flipped
        flip_v   = False

        if self.surface == SURFACE_WALL_L:
            if name.lower().startswith("climb"):
                rotation = 0
                flip_h   = False
            else:
                rotation = 270
                flip_h   = self.vel_y > 0
        elif self.surface == SURFACE_WALL_R:
            if name.lower().startswith("climb"):
                rotation = 0
                flip_h   = True
            else:
                rotation = 90
                flip_h   = self.vel_y < 0
        elif self.surface == SURFACE_CEILING:
            if name.lower() == "climb_top":
                rotation = 0
                flip_h   = self.flipped
            elif self.state == "ceiling_idle":
                rotation = 0
                flip_h   = self.flipped
            else:
                rotation = 180
                flip_h   = not self.flipped

        tk_img = self.get_tk_image(name, rotation=rotation,
                                   flip_h=flip_h, flip_v=flip_v)
        if tk_img:
            self.canvas.itemconfig(self.sprite_item, image=tk_img)

    def on_press(self, e):
        if getattr(self, "is_ko", False):
            self.cpr_press()
            return
        self.dragging   = True
        self.drag_off_x = e.x
        self.drag_off_y = e.y
        self.press_time = time.time()
        self.drag_points = [(time.time(), e.x_root, e.y_root)]
        self.surface = SURFACE_FLOOR
        self.set_state("falling", SURFACE_FLOOR)
        self._react_to_poke()

    def _react_to_poke(self):
        reaction_frames = [KNEEL_FRAMES, FALL_FRAMES] if self.current_skin != "Bocchi" else [GHOST_FRAMES, KNEEL_FRAMES]
        chosen = random.choice(reaction_frames)
        available = [f for f in chosen if f in self.images]
        if available:
            self.frames      = available
            self.frame_idx   = 0
            self.frame_timer = 0
            self.update_sprite()
        play_character_sound(self.current_skin, "poke")
        self.show_speech(self.get_poked_speech())

    def on_drag(self, e):
        if not self.dragging or getattr(self, "is_ko", False):
            return
        nx = self.root.winfo_x() + e.x - self.drag_off_x
        ny = self.root.winfo_y() + e.y - self.drag_off_y
        self.x = max(0, min(nx, self.sw - self.size))
        self.y = max(0, min(ny, self.sh - 50))
        self.root.geometry(f"{self.size}x{self.size}+{int(self.x)}+{int(self.y)}")

        dx = 0
        if len(self.drag_points) >= 1:
            dx = e.x_root - self.drag_points[-1][1]

        now = time.time()
        self.drag_points.append((now, e.x_root, e.y_root))
        if len(self.drag_points) > 10:
            self.drag_points.pop(0)

        # Animacion dinamica de arrastre en el aire
        drag_img = None
        if dx < -3:
            if "drag_l" in self.images: drag_img = "drag_l"
            elif "air_swing_l" in self.images: drag_img = "air_swing_l"
        elif dx > 3:
            if "drag_r" in self.images: drag_img = "drag_r"
            elif "air_swing_r" in self.images: drag_img = "air_swing_r"

        if not drag_img and "air" in self.images:
            drag_img = "air"

        if drag_img:
            tk_img = self.get_tk_image(drag_img, rotation=0, flip_h=(dx > 0 if drag_img == "air" else False), flip_v=False)
            if tk_img:
                self.canvas.itemconfig(self.sprite_item, image=tk_img)

        if self.dragging_window:
            sx = self.root.winfo_rootx() + e.x
            sy = self.root.winfo_rooty() + e.y
            self.win_dragger.move_to(sx, sy)

    def on_release(self, e):
        if not self.dragging or getattr(self, "is_ko", False):
            self.dragging = False
            return
        self.dragging = False
        if self.dragging_window:
            self.win_dragger.release()
            self.dragging_window = False
            self.show_speech("¡Tachan! (*^^*)")

        # Detectar caricia cariñosa (>0.7s quieto)
        press_duration = time.time() - getattr(self, "press_time", 0)
        dist_drag = 0
        if len(self.drag_points) >= 2:
            dist_drag = abs(self.drag_points[-1][1] - self.drag_points[0][1]) + abs(self.drag_points[-1][2] - self.drag_points[0][2])

        if press_duration > 0.7 and dist_drag < 18:
            old_hp = self.hp
            self.hp = min(100, self.hp + 10)
            self.show_speech(f"Qué cálido... me agrada  (+{self.hp - old_hp} HP) [HP: {self.hp}/100]")
            self.choose_next_floor_state()
            return

        # Calcular velocidad de lanzamiento (Fling)
        vx = 0
        vy = 0
        if len(self.drag_points) >= 2:
            t_now, x_now, y_now = self.drag_points[-1]
            t_old, x_old, y_old = self.drag_points[0]
            dt = t_now - t_old
            if 0.01 <= dt <= 0.45:
                vx = (x_now - x_old) / (dt * 55)
                vy = (y_now - y_old) / (dt * 55)
                vx = max(-45, min(45, vx))
                vy = max(-45, min(45, vy))

        self.surface = SURFACE_FLOOR
        if abs(vx) > 7 or abs(vy) > 7 or self.y < self.ground_y:
            self.vel_x = vx
            self.vel_y = vy if vy != 0 else (random.randint(-4, -1))
            self.set_state("flung", SURFACE_FLOOR)
            if abs(vx) > 18 or abs(vy) > 18:
                play_character_sound(self.current_skin, "fling")
                self.show_speech(random.choice(["¡Wooooosh! :v", "¡A volaaar! 7w7", "¡Por los aires! XD"]))
        else:
            self.choose_next_floor_state()

    def on_double_click(self, e):
        play_character_sound(self.current_skin, "idle")
        self.show_speech(self.get_random_speech())

    def on_right_click(self, e):
        t = self.theme_manager
        acc_fg = getattr(t, "accent_fg", getattr(t, "accent_text", "#ffffff"))
        try:
            menu = tk.Menu(self.root, tearoff=0,
                           bg=t.surface, fg=t.text,
                           activebackground=t.accent,
                           activeforeground=acc_fg,
                           font=(t.font_family, t.font_size))

            menu.add_command(label="[*] Personalizar Apariencia >>", command=self.open_appearance)

            size_menu = tk.Menu(menu, tearoff=0,
                                bg=t.surface, fg=t.text,
                                activebackground=t.accent,
                                activeforeground=acc_fg,
                                font=(t.font_family, t.font_size))
            for lbl, mult in [("1x (128px)", 1.0), ("1.5x (192px)", 1.5), ("2x (256px)", 2.0),
                              ("4x (512px)", 4.0), ("10x (1280px)", 10.0), ("100x (4000px)", 100.0)]:
                size_menu.add_command(label=lbl, command=lambda m=mult: self.set_scale(m))
            size_menu.add_separator()
            size_menu.add_command(label="[+] Personalizar en Apariencia...", command=self.open_appearance)
            menu.add_cascade(label=f"[#] Cambiar Tamaño ({getattr(self, 'size', 128)}px) >>", menu=size_menu)

            fps_menu = tk.Menu(menu, tearoff=0,
                               bg=t.surface, fg=t.text,
                               activebackground=t.accent,
                               activeforeground=acc_fg,
                               font=(t.font_family, t.font_size))
            for f_val in [15, 20, 24, 30, 45, 60]:
                chk = " [✓]" if getattr(self, "fps", 30) == f_val else ""
                fps_menu.add_command(label=f"{f_val} FPS{chk}", command=lambda f=f_val: self.set_fps(f))
            menu.add_cascade(label=f"[FPS] Tasa de Cuadros ({getattr(self, 'fps', 30)} FPS) >>", menu=fps_menu)

            menu.add_command(label=f"[★] Buscar Actualizaciones (v{APP_VERSION})", command=lambda: check_for_updates(self, is_manual=True))
            
            skin_menu = tk.Menu(menu, tearoff=0,
                                bg=t.surface, fg=t.text,
                                activebackground=t.accent,
                                activeforeground=acc_fg,
                                font=(t.font_family, t.font_size))
            for s in get_available_skins():
                meta = get_skin_meta(s)
                disp = meta.get("display", s)
                chk = " [✓]" if s == self.current_skin else ""
                skin_menu.add_command(label=f"{disp}{chk}", command=lambda sk=s: self.set_skin(sk))
            skin_menu.add_separator()
            skin_menu.add_command(label="[+] Importar Skin (.zip / carpeta)...", command=self.open_sprite_importer)
            menu.add_cascade(label="[+] Elegir Skin / Personaje >>", menu=skin_menu)

            troll_toggle_lbl = "[!] MODO TROLL: [ON] (Desactivar)" if self.troll_mode else "[o] MODO TROLL: [OFF] (Activar)"
            menu.add_command(label=troll_toggle_lbl, command=self.toggle_troll_mode)
            char_name = SKIN_META.get(self.current_skin, {}).get("char_name", "Bocchi")
            menu.add_command(label=f"[#] Hablar con {char_name} (IA & JARVIS) >>", command=self.open_chat)
            menu.add_command(label="[*] Doxxearte / Info Real >>", command=self.open_doxx)
            menu.add_command(label="[?] Decir algo al azar", command=lambda: self.show_speech(self.get_random_speech()))
            menu.add_command(label="[+] Soltar Item / Snack (Sprite Sheet)", command=self.drop_random_item)
            menu.add_separator()

            # Salud y física divertida
            hp_cur = getattr(self, "hp", 100)
            menu.add_command(label=f"[+] Salud: {hp_cur}/100 HP (Curar y alimentar)", command=lambda: self.heal(100, "pastelito y té"))
            menu.add_command(label="[+] Lanzar hacia arriba (Prueba de Fisica Fling)", command=self.fling_upwards)

            # Acciones especiales personalizadas por personaje
            c_actions = CUSTOM_SKIN_ACTIONS.get(self.current_skin, [])
            if c_actions:
                cust_act_menu = tk.Menu(menu, tearoff=0,
                                        bg=t.surface, fg=t.text,
                                        activebackground=t.accent,
                                        activeforeground=acc_fg,
                                        font=(t.font_family, t.font_size))
                for lbl, a_name, fr_list, sp_text in c_actions:
                    cust_act_menu.add_command(label=f"[>] {lbl}", command=lambda an=a_name, fl=fr_list, st=sp_text: self.trigger_custom_action(an, fl, st))
                menu.add_cascade(label=f"[+] Acciones Especiales de {char_name} >>", menu=cust_act_menu)

            poses_menu = tk.Menu(menu, tearoff=0,
                                 bg=t.surface, fg=t.text,
                                 activebackground=t.accent,
                                 activeforeground=acc_fg,
                                 font=(t.font_family, t.font_size))
            if self.current_skin == "Bocchi":
                poses_menu.add_command(label="[*] Tocar guitarra",       command=lambda: self.set_state("guitar", SURFACE_FLOOR))
                poses_menu.add_command(label="[o] Modo blob",             command=lambda: self.set_state("blob",   SURFACE_FLOOR))
                poses_menu.add_command(label="[~] Modo fantasma",         command=lambda: self.set_state("ghost",  SURFACE_FLOOR))
                poses_menu.add_command(label="[#] Truco de caja",         command=lambda: self.set_state("box",    SURFACE_FLOOR))
            poses_menu.add_command(label="[-] Sentarse / Descansar",  command=lambda: self.set_state("sitting", SURFACE_FLOOR))
            poses_menu.add_command(label="[-] Arrodillarse",          command=lambda: self.set_state("kneel",  SURFACE_FLOOR))
            poses_menu.add_command(label="[<] Caminar de espaldas",   command=lambda: self.set_state("walk_back", SURFACE_FLOOR))
            poses_menu.add_command(label="[+] Llevar funda",          command=lambda: self.set_state("carry",  SURFACE_FLOOR))
            poses_menu.add_command(label="[_] Modo sad",             command=lambda: self.set_state("depress",SURFACE_FLOOR))
            poses_menu.add_command(label="[>] Mirar atras",           command=lambda: self.set_state("away",   SURFACE_FLOOR))
            menu.add_cascade(label="[>] Poses y Modos >>", menu=poses_menu)

            move_menu = tk.Menu(menu, tearoff=0,
                                bg=t.surface, fg=t.text,
                                activebackground=t.accent,
                                activeforeground=acc_fg,
                                font=(t.font_family, t.font_size))
            move_menu.add_command(label="[^] Escalar pared izq", command=lambda: self._force_climb(SURFACE_WALL_L))
            move_menu.add_command(label="[^] Escalar pared der", command=lambda: self._force_climb(SURFACE_WALL_R))
            move_menu.add_command(label="[^^] Ir al techo",      command=self._force_ceiling)
            move_menu.add_separator()
            follow_cursor_lbl = ("[*] Seguir cursor [ON]" if self._follow_cursor_enabled
                                else "[ ] Seguir cursor [OFF]")
            move_menu.add_command(label=follow_cursor_lbl, command=self._toggle_follow_cursor)
            menu.add_cascade(label="[^] Acrobacias y Techo >>", menu=move_menu)

            troll_menu = tk.Menu(menu, tearoff=0,
                                 bg=t.surface, fg=t.text,
                                 activebackground=t.accent,
                                 activeforeground=acc_fg,
                                 font=(t.font_family, t.font_size))
            troll_menu.add_command(label="[~] Rickroll sorpresa (YouTube)", command=self.troll_rickroll)
            troll_menu.add_command(label="[!] Screamer / Bromas web", command=self.troll_screamer)
            troll_menu.add_command(label="[!] Simular Pantallazo Azul (BSOD)", command=self.troll_bluescreen)
            troll_menu.add_command(label="[#] Simular Hacker (HackerTyper)", command=self.troll_hackertyper)
            troll_menu.add_command(label="[?] Error falso del sistema", command=self.troll_fake_error)
            troll_menu.add_command(label="[>] Sacudir ventana activa", command=self.troll_shake_window)
            troll_menu.add_command(label="[>] Mover ventana activa", command=self.troll_move_window)
            if WIN32_AVAILABLE:
                troll_menu.add_command(label="[~] Mover cursor al azar", command=self.troll_move_mouse)
                troll_menu.add_separator()

                win_lbl = ("[#] Ventanas [AUTO ON] >>" if self._auto_win_enabled
                           else "[#] Ventanas >>")
                win_menu = tk.Menu(troll_menu, tearoff=0,
                                   bg=t.surface, fg=t.text,
                                   activebackground=t.accent,
                                   activeforeground=acc_fg,
                                   font=(t.font_family, t.font_size))
                win_menu.add_command(label="[-] Minimizar ventana activa",        command=self.troll_minimize)
                win_menu.add_command(label="[x] Cerrar ventana activa",           command=self.action_close_foreground)
                win_menu.add_separator()
                win_menu.add_command(label="[-] Minimizar ventana (apuntar)",     command=self.action_minimize_under_cursor)
                win_menu.add_command(label="[x] Cerrar ventana (apuntar)",        command=self.action_close_under_cursor)
                win_menu.add_command(label="[+] Maximizar/Restaurar (apuntar)",   command=self.action_maximize_under_cursor)
                win_menu.add_command(label="[>] Arrastrar ventana (apuntar)",     command=self.start_window_drag)
                win_menu.add_separator()
                auto_win_lbl = ("Autonomia ON  -> desactivar" if self._auto_win_enabled
                                else "Autonomia OFF -> activar")
                win_menu.add_command(label=auto_win_lbl, command=self._toggle_auto_win)
                troll_menu.add_cascade(label=win_lbl, menu=win_menu)

                desk_lbl = ("[#] Escritorio [AUTO ON] >>" if self._auto_desk_enabled
                            else "[#] Escritorio >>")
                desk_menu = tk.Menu(troll_menu, tearoff=0,
                                    bg=t.surface, fg=t.text,
                                    activebackground=t.accent,
                                    activeforeground=acc_fg,
                                    font=(t.font_family, t.font_size))
                desk_menu.add_command(label="[*] Mezclar todos los iconos",       command=self.action_shuffle_desktop)
                desk_menu.add_command(label="[!] Dispersar todos los iconos",     command=self.action_scatter_desktop)
                desk_menu.add_command(label="[#] Ordenar iconos (cuadricula)",    command=self.action_sort_desktop)
                desk_menu.add_command(label="[>] Mover un icono al azar",        command=self.action_move_one_icon)
                desk_menu.add_command(label="[-] Mandar icono a la papelera",    command=self.action_trash_icon)
                desk_menu.add_separator()
                auto_desk_lbl = ("Autonomia ON  -> desactivar" if self._auto_desk_enabled
                                 else "Autonomia OFF -> activar")
                desk_menu.add_command(label=auto_desk_lbl, command=self._toggle_auto_desk)
                troll_menu.add_cascade(label=desk_lbl, menu=desk_menu)
            menu.add_cascade(label="[!] Travesuras & Windows >>", menu=troll_menu)

            menu.add_separator()
            menu.add_command(label="[★] Voice Studio de Personajes >>", command=self.open_voice_studio)
            menu.add_command(label="[>] Escuchar comando de voz (JARVIS)", command=self.listen_voice_command_once)
            menu.add_command(label="[*] Ajustes del Agente JARVIS >>", command=self.open_agent_settings)
            menu.add_separator()
            menu.add_command(label="[x] Cerrar Shimeji", command=self.close_shimeji,
                             foreground=t.danger, activeforeground=t.danger)
            rx = self.root.winfo_rootx() + e.x
            ry = self.root.winfo_rooty() + e.y
            menu.tk_popup(rx, ry)
        except Exception as exc:
            print(f"Error mostrando menu: {exc}")
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    def open_voice_studio(self):
        """Abre la ventana de Google Voice Studio para clonar y probar voces reales."""
        if hasattr(self, "voice_studio_win") and self.voice_studio_win is not None and tk.Toplevel.winfo_exists(self.voice_studio_win.win):
            self.voice_studio_win.win.lift()
            self.voice_studio_win.win.focus_force()
            return
        self.voice_studio_win = VoiceStudioWindow(self.root, self.theme_manager, self)

    def open_agent_settings(self):
        """Abre la ventana de ajustes avanzados del agente JARVIS."""
        if self.agent_settings_win is not None and tk.Toplevel.winfo_exists(self.agent_settings_win.win):
            self.agent_settings_win.win.lift()
            self.agent_settings_win.win.focus_force()
            return
        self.agent_settings_win = AgentSettingsWindow(self.root, self.theme_manager, self)

    def sync_wake_word_state(self):
        """Inicia o detiene el oyente de palabra de activacion segun la configuracion."""
        enabled = self.config.get("agent_wake_word_enabled", False)
        wake_word = self.config.get("agent_wake_word", "oye jarvis")
        if enabled:
            if self.wake_word_listener is None or not self.wake_word_listener.is_alive():
                self.wake_word_listener = JarvisWakeWordListener(
                    on_heard=self._on_wake_word_heard,
                    wake_word=wake_word
                )
                self.wake_word_listener.start()
        else:
            if self.wake_word_listener is not None:
                self.wake_word_listener.stop()
                self.wake_word_listener = None

    def _on_wake_word_heard(self, text):
        """Manejador cuando el oyente continuo detecta la palabra de activacion."""
        def _handle():
            self.show_speech("Te escucho")
            if hasattr(self, "tts") and self.tts:
                self.tts.speak("Te escucho")
            if not text or not text.strip():
                return
            if self.chat_win is None or not tk.Toplevel.winfo_exists(self.chat_win.win):
                self.open_chat()
            if self.chat_win and hasattr(self.chat_win, "send_message"):
                self.chat_win.input_entry.delete(0, tk.END)
                self.chat_win.input_entry.insert(0, text.strip())
                self.chat_win.send_message()
        self.root.after(0, _handle)

    def listen_voice_command_once(self):
        """Escucha un solo comando de voz mediante push-to-talk."""
        self.show_speech("Escuchando comando de voz...")
        def _worker():
            listener = JarvisWakeWordListener(lambda t: None)
            cmd = listener.listen_once()
            if cmd:
                def _inject():
                    self.show_speech(f"Comando: {cmd}")
                    if self.chat_win is None or not tk.Toplevel.winfo_exists(self.chat_win.win):
                        self.open_chat()
                    if self.chat_win and hasattr(self.chat_win, "send_message"):
                        self.chat_win.input_entry.delete(0, tk.END)
                        self.chat_win.input_entry.insert(0, cmd)
                        self.chat_win.send_message()
                self.root.after(0, _inject)
            else:
                self.root.after(0, lambda: self.show_speech("No se detecto voz"))
        threading.Thread(target=_worker, daemon=True).start()

    def _check_pending_reminders(self):
        """Revisa si hay recordatorios o temporizadores vencidos para alertar al usuario."""
        now = time.time()
        if now - getattr(self, "_last_remind_check", 0) < 1.0:
            return
        self._last_remind_check = now
        reminders = self.config.get("agent_reminders", [])
        if not reminders:
            return
        still_pending = []
        triggered = []
        for r in reminders:
            due = r.get("due_timestamp", 0)
            if due > 0 and now >= due:
                triggered.append(r)
            else:
                still_pending.append(r)
        if triggered:
            self.config["agent_reminders"] = still_pending
            save_config(self.config)
            for r in triggered:
                text = r.get("text", "Recordatorio programado")
                self.show_speech(f"Recordatorio: {text}")
                if hasattr(self, "tts") and self.tts:
                    self.tts.speak(f"Atencion, recordatorio: {text}")
                if WINSOUND_AVAILABLE:
                    try:
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    except Exception:
                        pass

    def close_shimeji(self):
        """Reproduce popue.wav al desaparecer y cierra el Shimeji limpiamente."""
        if hasattr(self, "wake_word_listener") and self.wake_word_listener:
            try:
                self.wake_word_listener.stop()
            except Exception:
                pass
        play_popue_sound()
        try:
            self.root.after(350, self.root.destroy)
        except Exception:
            try:
                self.root.destroy()
            except Exception:
                pass

    def drop_random_item(self):
        """Suelta un item aleatorio desde el sprite sheet items.png (comida o bomba)."""
        if not PIL_AVAILABLE:
            return
        play_popue_sound()
        try:
            items_dir = os.path.join(BASE_DIR, "img", "items")
            if not os.path.isdir(items_dir):
                items_dir = os.path.join(EXE_DIR, "img", "items")
            if not os.path.isdir(items_dir):
                return
            all_items = [f for f in os.listdir(items_dir) if f.startswith("item_") and f.endswith(".png")]
            if not all_items:
                return
            chosen = random.choice(all_items)
            is_bomb = False
            try:
                parts = chosen.replace(".png", "").split("_")
                row = int(parts[1])
                is_bomb = (row >= 3)
            except Exception:
                is_bomb = False

            fpath = os.path.join(items_dir, chosen)
            item_im = Image.open(fpath).convert("RGBA").resize((64, 64))

            item_win = tk.Toplevel(self.root)
            item_win.overrideredirect(True)
            item_win.attributes("-topmost", True)
            TRANS_COLOR = "#000001"
            item_win.attributes("-transparentcolor", TRANS_COLOR)
            item_win.config(bg=TRANS_COLOR)

            c = tk.Canvas(item_win, width=64, height=64, bg=TRANS_COLOR, highlightthickness=0, bd=0)
            c.pack()
            tk_item_img = ImageTk.PhotoImage(item_im)
            c.create_image(0, 0, anchor="nw", image=tk_item_img)
            item_win._img_ref = tk_item_img

            start_x = max(50, min(self.sw - 100, self.x + random.randint(-60, 60)))
            start_y = 50
            item_win.geometry(f"64x64+{start_x}+{start_y}")

            cur_state = {"y": float(start_y), "vy": 0.0, "x": start_x, "bounces": 0}

            def item_physics():
                cur_state["vy"] += 2.2
                cur_state["y"] += cur_state["vy"]
                floor_lvl = self.ground_y + self.size - 64
                if cur_state["y"] >= floor_lvl:
                    cur_state["y"] = float(floor_lvl)
                    if cur_state["bounces"] < 2:
                        cur_state["vy"] = -cur_state["vy"] * 0.4
                        cur_state["bounces"] += 1
                    else:
                        cur_state["vy"] = 0

                try:
                    item_win.geometry(f"64x64+{int(cur_state['x'])}+{int(cur_state['y'])}")
                except Exception:
                    return

                # Check proximity to Shimeji
                dist = abs((self.x + self.size/2) - (cur_state["x"] + 32))
                y_dist = abs((self.y + self.size/2) - (cur_state["y"] + 32))

                if dist < 80 and y_dist < 90:
                    play_popue_sound()
                    try:
                        item_win.destroy()
                    except Exception:
                        pass

                    if is_bomb:
                        self.vel_y = -12
                        self.set_state("depress", SURFACE_FLOOR)
                        panic_msgs = [
                            "¡¡¡AYYYY UNA BOMBAAA!!! (>_<)",
                            "¡¡¡CUIDADO VA A EXPLOTAR!!! :O",
                            "¡WAAAAH! ¡PELIGROOO! ._.",
                            "¡Auxilioooo, me quieren dinamitar! (>_<)"
                        ]
                        self.show_speech(random.choice(panic_msgs))
                    else:
                        self.set_state("sit", SURFACE_FLOOR)
                        happy_msgs = [
                            "¡Ñam ñam ñam! ¡Qué rico snack! (o_o)",
                            "¡Delicioso! ¡Muchas gracias por el alimento! UwU",
                            "¡Un manjar! Ahora tengo energía al 100% ",
                            "¡Mmm! ¡Qué delicia de regalo! :3",
                            "¡Riquísimo! ¡Guardaré un pedacito! "
                        ]
                        self.show_speech(random.choice(happy_msgs))
                    return

                if cur_state["vy"] != 0 or cur_state["bounces"] < 3:
                    item_win.after(20, item_physics)
                else:
                    item_win.after(8000, lambda: self._safe_destroy_win(item_win))

            item_win.after(20, item_physics)
        except Exception as e:
            print(f"Error soltando item: {e}")

    def _safe_destroy_win(self, w):
        try:
            w.destroy()
        except Exception:
            pass

    def _cache_own_hwnd(self):
        if WIN32_AVAILABLE:
            try:
                self._own_hwnd_val = win32gui.FindWindow(None, "PinkChan")
            except Exception:
                self._own_hwnd_val = 0

    def _own_hwnd(self):
        return self._own_hwnd_val or 0

    def toggle_troll_mode(self, force_val=None):
        if force_val is None:
            self.troll_mode = not self.troll_mode
        else:
            self.troll_mode = bool(force_val)
        self.config["troll_mode"] = self.troll_mode
        save_config(self.config)
        if getattr(self, "chat_win", None) and hasattr(self.chat_win, "update_troll_btn"):
            self.chat_win.update_troll_btn()
        if self.troll_mode:
            self.show_speech("¡MODO TROLL ACTIVADO! 7w7\nPrepárate para la anarquía...")
            # Feedback instantáneo: ejecuta una travesura en 1.5 segundos
            self.root.after(1500, self._trigger_instant_troll)
        else:
            self.show_speech("Modo Troll desactivado [OFF]\nYa me porto bien, soy tu JARVIS UwU")

    def _trigger_instant_troll(self):
        if not self.troll_mode:
            return
        actions = [
            self.troll_shake_window,
            self.troll_fake_error,
            self.troll_move_window,
            self.troll_move_mouse,
            self.troll_minimize,
        ]
        chosen = random.choice(actions)
        try:
            chosen()
        except Exception:
            pass

    def _shake_bocchi(self):
        ox, oy = self.x, self.y
        def do_b_shake(step=0):
            if step < 12:
                dx = random.randint(-35, 35)
                dy = random.randint(-25, 25)
                self.x = ox + dx
                self.y = oy + dy
                self.root.geometry(f"+{self.x}+{self.y}")
                self.root.after(35, lambda: do_b_shake(step + 1))
            else:
                self.x = ox
                self.y = oy
                self.root.geometry(f"+{self.x}+{self.y}")
        self.show_speech("¡Terremoto! ¡Me estoy sacudiendo toda! ＞﹏＜")
        do_b_shake()

    def _move_bocchi_random(self):
        nx = random.randint(50, max(100, self.sw - 160))
        ny = random.randint(50, max(100, self.sh - 160))
        self.x = nx
        self.y = ny
        self.root.geometry(f"+{self.x}+{self.y}")
        self.show_speech("¡Woosh! ¡Me teletransporte por alla! (ﾉ´ヮ`)ﾉ")

    def troll_rickroll(self):
        try:
            open_url_guaranteed("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            self.show_speech("¡RICKROLLEADO! (ノ^∇^)ノ\nNever gonna give you up~ 7w7")
        except Exception:
            pass

    def troll_bluescreen(self):
        try:
            # Ventana nativa fullscreen ultra-realista de Windows BSOD
            bsod = tk.Toplevel(self.root)
            bsod.title("BSOD")
            bsod.overrideredirect(True)
            bsod.geometry(f"{self.sw}x{self.sh}+0+0")
            bsod.attributes("-topmost", True)
            bsod.configure(bg="#0078d7", cursor="none")
            bsod.focus_force()

            pad_left = max(60, int(self.sw * 0.12))
            pad_top = max(50, int(self.sh * 0.10))

            content = tk.Frame(bsod, bg="#0078d7")
            content.place(x=pad_left, y=pad_top)

            # 1. Carita triste :(
            sad_lbl = tk.Label(content, text=":(", font=("Segoe UI", 95, "normal"),
                               fg="#ffffff", bg="#0078d7")
            sad_lbl.pack(anchor="w", pady=(0, 20))

            # 2. Texto principal de choque del sistema
            msg1 = (
                "Se ha producido un problema en su PC y necesita reiniciarse.\n"
                "Tan solo estamos recopilando información sobre el error y después se reiniciará automáticamente."
            )
            lbl1 = tk.Label(content, text=msg1, font=("Segoe UI", 18),
                            fg="#ffffff", bg="#0078d7", justify=tk.LEFT)
            lbl1.pack(anchor="w", pady=(0, 25))

            # 3. Contador de porcentaje animado
            pct_var = tk.StringVar(value="0% completado")
            pct_lbl = tk.Label(content, textvariable=pct_var, font=("Segoe UI", 18),
                               fg="#ffffff", bg="#0078d7")
            pct_lbl.pack(anchor="w", pady=(0, 35))

            # 4. Sección inferior: QR + Info de soporte
            bot_frame = tk.Frame(content, bg="#0078d7")
            bot_frame.pack(anchor="w")

            # Dibujo realista de código QR en canvas
            qr_canvas = tk.Canvas(bot_frame, width=110, height=110, bg="#ffffff",
                                  highlightthickness=0, bd=0)
            qr_canvas.pack(side=tk.LEFT, padx=(0, 24))

            def draw_qr_corner(x, y, s):
                qr_canvas.create_rectangle(x, y, x + s, y + s, fill="#000000", outline="")
                qr_canvas.create_rectangle(x + 4, y + 4, x + s - 4, y + s - 4, fill="#ffffff", outline="")
                qr_canvas.create_rectangle(x + 8, y + 8, x + s - 8, y + s - 8, fill="#000000", outline="")

            draw_qr_corner(8, 8, 30)
            draw_qr_corner(72, 8, 30)
            draw_qr_corner(8, 72, 30)

            qr_rnd = random.Random(42)
            for gx in range(3, 19):
                for gy in range(3, 19):
                    if (gx < 8 and gy < 8) or (gx > 13 and gy < 8) or (gx < 8 and gy > 13):
                        continue
                    if qr_rnd.random() > 0.48:
                        qr_canvas.create_rectangle(gx * 5 + 8, gy * 5 + 8, gx * 5 + 12, gy * 5 + 12, fill="#000000", outline="")

            info_frame = tk.Frame(bot_frame, bg="#0078d7")
            info_frame.pack(side=tk.LEFT)

            uname = getattr(self.user_info, "username", "User")
            support_text = (
                "Para obtener más información sobre este problema y posibles soluciones, visita\n"
                "https://windows.com/stopcode\n\n"
                "Si llamas a una persona de soporte técnico, dales esta información:\n"
                "Código de detención: CRITICAL_PROCESS_DIED\n"
                f"Lo que tuvo error: bocchi_the_rock_{uname}.sys"
            )
            tk.Label(info_frame, text=support_text, font=("Segoe UI", 11),
                     fg="#ffffff", bg="#0078d7", justify=tk.LEFT).pack(anchor="w")

            steps = [(0, 400), (14, 500), (32, 600), (58, 700), (79, 600), (100, 800)]
            def run_step(idx=0):
                if not bsod.winfo_exists():
                    return
                if idx < len(steps):
                    val, delay = steps[idx]
                    pct_var.set(f"{val}% completado")
                    bsod.after(delay, lambda: run_step(idx + 1))
                else:
                    bsod.after(900, dismiss_bsod)

            dismissed = [False]
            def dismiss_bsod(e=None):
                if dismissed[0]:
                    return
                dismissed[0] = True
                try:
                    bsod.destroy()
                except Exception:
                    pass
                self.show_speech(f"¡JAJAJAJA! ¿¡Te asustaste, {uname}!? (ﾉ´ヮ`)ﾉ*: ･ﾟ\n¡Era bromita de Bocchi, tu Windows está vivo! 7w7")

            bsod.bind("<Key>", dismiss_bsod)
            bsod.bind("<Button-1>", dismiss_bsod)
            bsod.bind("<Button-2>", dismiss_bsod)
            bsod.bind("<Button-3>", dismiss_bsod)
            bsod.bind("<Escape>", dismiss_bsod)

            bsod.after(7500, dismiss_bsod)
            run_step(0)

        except Exception as exc:
            print(f"Error en troll_bluescreen: {exc}")
            open_url_guaranteed("https://geekprank.com/blue-screen-death/")
            self.show_speech("¡PANTALLAZO AZUL! D:\nSe murio Windows alv :v")

    def troll_hackertyper(self):
        try:
            open_url_guaranteed("https://hackertyper.net/")
            self.show_speech("¡HACKEANDO LA NASA...! 7w7\n[STATUS: ACCESS GRANTED]")
        except Exception:
            pass

    def troll_screamer(self):
        links = [
            ("https://geekprank.com/screamer/", "¡AAAAHH! ¡Un screamer! D: (jajaja :v)"),
            ("https://theannoyingsite.com", "¡A ver si sales de esta pagina 7w7!"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "¡Toma tu rickroll! 7w7"),
        ]
        url, speech = random.choice(links)
        try:
            open_url_guaranteed(url)
            self.show_speech(speech)
        except Exception:
            pass

    def _do_window_shake(self, hwnd):
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
            def do_shake(step=0):
                if step < 9:
                    dx = random.randint(-45, 45)
                    dy = random.randint(-30, 30)
                    win32gui.MoveWindow(hwnd, x + dx, y + dy, w, h, True)
                    self.root.after(40, lambda: do_shake(step + 1))
                else:
                    win32gui.MoveWindow(hwnd, x + random.randint(35, 90), y + random.randint(25, 70), w, h, True)
            self.show_speech("¡Terremoto en tus ventanas! (ง'̀-'́)ง")
            do_shake()
        except Exception:
            self._shake_bocchi()

    def troll_shake_window(self):
        if not WIN32_AVAILABLE:
            self._shake_bocchi()
            return
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd or hwnd == self._own_hwnd():
            hwnd = WindowDragger.pick_random_window(exclude=self._own_hwnd())
        if not hwnd:
            self._shake_bocchi()
            return
        try:
            # Si la ventana está maximizada, Windows ignora MoveWindow; la restauramos primero
            if win32gui.IsZoomed(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                self.root.after(70, lambda: self._do_window_shake(hwnd))
            else:
                self._do_window_shake(hwnd)
        except Exception:
            self._shake_bocchi()

    def troll_move_window(self):
        if not WIN32_AVAILABLE:
            self._move_bocchi_random()
            return
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd or hwnd == self._own_hwnd():
            hwnd = WindowDragger.pick_random_window(exclude=self._own_hwnd())
        if not hwnd:
            self._move_bocchi_random()
            return
        try:
            # Si está maximizada, restaurar primero para permitir moverla
            if win32gui.IsZoomed(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            rect = win32gui.GetWindowRect(hwnd)
            w = max(220, rect[2] - rect[0])
            h = max(160, rect[3] - rect[1])
            title = win32gui.GetWindowText(hwnd)[:20] or "tu ventana"
            nx = random.randint(0, max(0, self.sw - w))
            ny = random.randint(0, max(0, self.sh - h - 60))
            win32gui.MoveWindow(hwnd, nx, ny, w, h, True)
            self.show_speech(f"Movi '{title}' por alla~ 7w7")
        except Exception:
            self._move_bocchi_random()

    def troll_move_desktop_icon(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self._shake_bocchi()
            return
        try:
            icons = self.desktop_mover.get_icon_list()
            if icons:
                idx, name = random.choice(icons)
                self.desktop_mover.move_one_icon(idx)
                label = name[:18] + ("..." if len(name) > 18 else "")
                self.show_speech(f"Movi tu icono '{label}'~ [*]")
            else:
                self._shake_bocchi()
        except Exception:
            self._shake_bocchi()

    def troll_fake_error(self):
        title, msg = self.get_fake_error()
        self.show_speech("Jijiji... 7w7")
        if WIN32_AVAILABLE:
            threading.Thread(
                target=lambda: win32gui.MessageBox(0, msg, title, win32con.MB_ICONERROR | win32con.MB_TOPMOST | win32con.MB_SETFOREGROUND),
                daemon=True
            ).start()
        else:
            self.root.after(400, lambda: messagebox.showerror(title, msg))

    def _troll_autonomous_tick(self):
        if self.troll_mode:
            actions = [
                self.troll_shake_window,
                self.troll_fake_error,
                self.troll_move_window,
                self.troll_minimize,
                self.troll_move_mouse,
                self.troll_move_desktop_icon,
                self.troll_rickroll,
                self.troll_bluescreen,
                self.troll_hackertyper,
                self.troll_screamer,
            ]
            weights = [22, 22, 18, 14, 10, 8, 3, 1, 1, 1]
            chosen = random.choices(actions, weights=weights, k=1)[0]
            try:
                chosen()
            except Exception:
                pass
            next_ms = random.randint(12000, 24000)
        else:
            next_ms = random.randint(18000, 35000)
        self.root.after(next_ms, self._troll_autonomous_tick)

    def troll_move_mouse(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 para hacer eso :v")
            return
        self.show_speech("¡Oops! Se me resbalo... 7w7")
        x, y = win32gui.GetCursorPos()
        win32api.SetCursorPos((x + random.randint(-400, 400), y + random.randint(-400, 400)))

    def troll_minimize(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 para hacer eso :v")
            return
        ok = self.win_dragger.minimize_foreground(exclude=self._own_hwnd())
        if not ok and getattr(self, "chat_win", None) and getattr(self.chat_win, "win", None) and tk.Toplevel.winfo_exists(self.chat_win.win):
            try:
                self.chat_win.win.iconify()
                ok = True
            except Exception:
                pass
        self.show_speech("¡A mimir esa ventana! (-.-)zzZ" if ok else "No hay ventana que minimizar ._.")

    def _wait_click_then(self, action_fn, hint_msg):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 :v")
            return
        if getattr(self, "_overlay", None):
            try:
                self._overlay.destroy()
            except Exception:
                pass
            self._overlay = None

        self.show_speech(hint_msg)
        self._pending_action = action_fn

        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.01)
        overlay.geometry(f"{self.sw}x{self.sh}+0+0")
        overlay.config(cursor="crosshair")

        def cleanup():
            if overlay and tk.Toplevel.winfo_exists(overlay):
                try:
                    overlay.destroy()
                except Exception:
                    pass
            if getattr(self, "_overlay", None) == overlay:
                self._overlay = None
            self._pending_action = None

        def on_overlay_click(e):
            sx = e.x_root
            sy = e.y_root
            fn = self._pending_action
            cleanup()
            self.root.after(80, lambda: fn(sx, sy) if fn else None)

        def on_escape(e=None):
            cleanup()
            self.show_speech("Cancelado [OK]")

        overlay.bind("<ButtonPress-1>", on_overlay_click)
        overlay.bind("<Escape>", on_escape)
        self.root.after(6000, lambda: on_escape() if getattr(self, "_overlay", None) == overlay else None)
        self._overlay = overlay

    def action_minimize_under_cursor(self):
        def do(sx, sy):
            ok = self.win_dragger.minimize_at(sx, sy)
            self.show_speech("¡A dormir! (-.-)z" if ok else "No encontre ventana ahi :v")
        self._wait_click_then(do, "Haz click en la ventana\nque quieres minimizar [-]")

    def action_close_under_cursor(self):
        def do(sx, sy):
            ok = self.win_dragger.close_at(sx, sy)
            self.show_speech("¡Bye bye! [x]" if ok else "No encontre ventana ahi :v")
        self._wait_click_then(do, "Haz click en la ventana\nque quieres cerrar [x]")

    def action_maximize_under_cursor(self):
        def do(sx, sy):
            ok = self.win_dragger.maximize_restore_at(sx, sy)
            self.show_speech("¡Aaahh, mas grande! [+]" if ok else "No encontre ventana ahi :v")
        self._wait_click_then(do, "Haz click en la ventana\npara maximizar/restaurar [+]")

    def action_close_foreground(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 :v")
            return
        ok = self.win_dragger.close_foreground(exclude=self._own_hwnd())
        self.show_speech("¡Adiosito! [x]" if ok else "No hay ventana activa :v")

    def action_shuffle_desktop(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 :v")
            return
        self.show_speech("Mezclando iconos... [*]")
        ok = self.desktop_mover.shuffle_icons()
        if not ok:
            self.show_speech("No pude mover los iconos :v\n(desactiva 'Auto-organizar')")

    def action_scatter_desktop(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 :v")
            return
        self.show_speech("¡Iconos volando! [!]")
        ok = self.desktop_mover.scatter_icons()
        if not ok:
            self.show_speech("No pude mover los iconos :v\n(desactiva 'Auto-organizar')")

    def action_sort_desktop(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 :v")
            return
        self.show_speech("¡Ordenando! [#]")
        ok = self.desktop_mover.sort_icons_grid()
        if not ok:
            self.show_speech("No pude ordenar los iconos :v")

    def action_trash_icon(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 :v")
            return
        icons = self.desktop_mover.get_icon_list()
        if not icons:
            self.show_speech("No encontre iconos en\nel escritorio ._.")
            return
        t = self.theme_manager
        acc_fg = getattr(t, "accent_fg", getattr(t, "accent_text", "#ffffff"))
        menu = tk.Menu(self.root, tearoff=0,
                       bg=t.surface, fg=t.text,
                       activebackground=t.accent,
                       activeforeground=acc_fg,
                       font=(t.font_family, t.font_size))
        for idx, name in icons:
            def make_cmd(i=idx, n=name):
                def cmd():
                    ok, msg = self.desktop_mover.trash_icon_at_index(i)
                    if ok:
                        self.show_speech(f"[-] '{msg}'\nfue a la papelera~")
                    else:
                        self.show_speech(f"No pude borrar:\n{msg}")
                return cmd
            label = name[:30] + ("..." if len(name) > 30 else "")
            menu.add_command(label=f"[-] {label}", command=make_cmd())
        cx = int(self.x) + self.size // 2
        cy = int(self.y)
        try:
            menu.tk_popup(cx, cy)
        finally:
            menu.grab_release()

    def action_move_one_icon(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 :v")
            return
        icons = self.desktop_mover.get_icon_list()
        if not icons:
            self.show_speech("No encontre iconos en\nel escritorio ._.")
            return
        idx, name = random.choice(icons)
        ok = self.desktop_mover.move_one_icon(idx)
        label = name[:20] + ("..." if len(name) > 20 else "")
        self.show_speech(f"Movi '{label}' [*]" if ok else "No pude mover el icono :v")

    def _auto_tick(self):
        if self.troll_mode and (self._auto_win_enabled or self._auto_desk_enabled):
            actions = []
            if self._auto_win_enabled:
                actions += ["auto_minimize", "auto_drag_window"]
            if self._auto_desk_enabled:
                actions += ["auto_move_icon", "auto_move_icon", "auto_trash_icon"]
            if actions:
                choice = random.choice(actions)
                self._do_auto_action(choice)
        interval = random.randint(self._auto_min_interval, self._auto_max_interval)
        self._auto_after_id = self.root.after(interval, self._auto_tick)

    def _do_auto_action(self, action):
        if not WIN32_AVAILABLE:
            return
        if action == "auto_minimize":
            hwnd = WindowDragger.pick_random_window(exclude=self._own_hwnd())
            if hwnd:
                title = win32gui.GetWindowText(hwnd)[:20]
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                self.show_speech(f"¡A mimir '{title}'! (-.-)z")
        elif action == "auto_drag_window":
            hwnd = WindowDragger.pick_random_window(exclude=self._own_hwnd())
            if hwnd:
                rect = win32gui.GetWindowRect(hwnd)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                nx = random.randint(0, max(0, self.sw - w))
                ny = random.randint(0, max(0, self.sh - h - 80))
                win32gui.MoveWindow(hwnd, nx, ny, w, h, True)
                title = win32gui.GetWindowText(hwnd)[:20]
                self.show_speech(f"Movi '{title}' [#]")
        elif action == "auto_move_icon":
            if self.desktop_mover:
                icons = self.desktop_mover.get_icon_list()
                if icons:
                    idx, name = random.choice(icons)
                    self.desktop_mover.move_one_icon(idx)
                    label = name[:18] + ("..." if len(name) > 18 else "")
                    self.show_speech(f"Movi '{label}' por ahi~ [*]")
        elif action == "auto_trash_icon":
            if self.desktop_mover:
                icons = self.desktop_mover.get_icon_list()
                if icons:
                    idx, name = random.choice(icons)
                    ok, msg = self.desktop_mover.trash_icon_at_index(idx)
                    if ok:
                        label = msg[:18] + ("..." if len(msg) > 18 else "")
                        self.show_speech(f"Jijiji, tire\n'{label}' 7w7")

    def _toggle_auto_win(self):
        self._auto_win_enabled = not self._auto_win_enabled
        state = "activada 7w7" if self._auto_win_enabled else "desactivada [OFF]"
        self.show_speech(f"Autonomia ventanas\n{state}")

    def _toggle_auto_desk(self):
        self._auto_desk_enabled = not self._auto_desk_enabled
        state = "activada 7w7" if self._auto_desk_enabled else "desactivada [OFF]"
        self.show_speech(f"Autonomia escritorio\n{state}")

    def _toggle_follow_cursor(self):
        self._follow_cursor_enabled = not self._follow_cursor_enabled
        state = "te sigo~ (o_o)" if self._follow_cursor_enabled else "libertad (*^^*)"
        self.show_speech(f"Modo seguidor\n{state}")

    def _force_climb(self, wall):
        if wall == SURFACE_WALL_L:
            self.x = self.wall_lx
        else:
            self.x = self.wall_rx
        self.y = self.ground_y
        self._start_climb(wall, going_up=True)

    def _force_ceiling(self):
        self.y = self.ceiling_y
        self.x = max(self.wall_lx, min(self.x, self.wall_rx))
        self.choose_next_ceiling_state()
        self.show_speech("¡El techo es mi hogar! (^^)/")

    def start_window_drag(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Falta pywin32")
            return
        self.show_speech("Senala la ventana\nque quieres mover [>]")
        self.canvas.bind("<ButtonPress-1>", self._grab_and_drag)

    def _grab_and_drag(self, e):
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        sx = self.root.winfo_rootx() + e.x
        sy = self.root.winfo_rooty() + e.y
        ok = self.win_dragger.grab_window_at(sx, sy)
        if ok:
            self.dragging_window = True
            self.dragging   = True
            self.drag_off_x = e.x
            self.drag_off_y = e.y
            self.show_speech("¡Agarrada! Arrastrala (ง'̀-'́)ง")
        else:
            self.show_speech("No encontre ninguna\nventana ahi :v")
            self.dragging = False

    def open_doxx(self):
        if self.doxx_win and tk.Toplevel.winfo_exists(self.doxx_win.win):
            self.doxx_win.win.lift()
            return
        self.doxx_win = DoxxWindow(self.root, self.user_info, self)

    def open_chat(self):
        if self.chat_win and tk.Toplevel.winfo_exists(self.chat_win.win):
            self.chat_win.win.lift()
            return
        self.chat_win = ChatWindow(self.root, self.api_key_var, self, self.user_info, self.config)

    def open_appearance(self):
        if self.appearance_win and tk.Toplevel.winfo_exists(self.appearance_win.win):
            self.appearance_win.win.lift()
            return
        self.appearance_win = AppearanceWindow(self.root, self.theme_manager, self)

    def open_sprite_importer(self):
        SpriteImporterWindow(self.root, self.theme_manager, self)

    def show_speech(self, text):
        try:
            if self.bubble_win:
                try:
                    self.bubble_win.destroy()
                except Exception:
                    pass
            if self.bubble_after:
                try:
                    self.root.after_cancel(self.bubble_after)
                except Exception:
                    pass

            t = self.theme_manager
            bw = tk.Toplevel(self.root)
            bw.overrideredirect(True)
            bw.attributes("-topmost", True)
            bw.config(bg=t.bg)
            try:
                bw.attributes("-alpha", getattr(t, "bubble_opacity", t.opacity))
            except Exception:
                pass

            border_w = 1 if getattr(t, "bubble_border", True) else 0
            bub_bg = getattr(t, "bubble_bg", t.surface)
            bub_fg = getattr(t, "bubble_fg", t.text)
            bub_border_color = getattr(t, "bubble_border_color", t.accent)
            bub_font_size = getattr(t, "bubble_font_size", t.font_size)
            bub_max_width = getattr(t, "bubble_max_width", 280)
            bub_dur_mult = float(getattr(t, "bubble_duration_mult", 1.0))

            card = tk.Frame(bw, bg=bub_bg, highlightbackground=bub_border_color, highlightthickness=border_w, padx=10, pady=6)
            card.pack(fill=tk.BOTH, expand=True)

            header_frame = tk.Frame(card, bg=bub_bg)
            header_frame.pack(fill=tk.X, pady=(0, 2))

            char_name = SKIN_META.get(getattr(self, "current_skin", "Bocchi"), {}).get("char_name", "Bocchi-chan")
            name_lbl = tk.Label(header_frame, text=f"[*] {char_name}", bg=bub_bg, fg=bub_border_color,
                                font=(t.font_family, max(8, bub_font_size - 2), "bold"))
            name_lbl.pack(side=tk.LEFT)

            subtle_fg = getattr(t, "text_subtle", getattr(t, "text_dim", "#888888"))
            close_btn = tk.Label(header_frame, text="[x]", bg=bub_bg, fg=subtle_fg,
                                 font=(t.font_family, max(8, bub_font_size - 2)), cursor="hand2")
            close_btn.pack(side=tk.RIGHT)
            close_btn.bind("<Button-1>", lambda e: self.destroy_bubble())

            msg_lbl = tk.Label(card, text=text, bg=bub_bg, fg=bub_fg,
                               font=(t.font_family, bub_font_size), wraplength=bub_max_width, justify=tk.LEFT)
            msg_lbl.pack(fill=tk.BOTH, expand=True)

            card.bind("<Button-1>", lambda e: self.destroy_bubble())
            msg_lbl.bind("<Button-1>", lambda e: self.destroy_bubble())
            name_lbl.bind("<Button-1>", lambda e: self.destroy_bubble())

            bw.update_idletasks()
            bw_w = max(bw.winfo_reqwidth(), 160)
            bw_h = max(bw.winfo_reqheight(), 40)

            cur_sz = getattr(self, "size", SIZE)
            bx = int(self.x) + cur_sz // 2 - bw_w // 2
            bx = max(10, min(bx, self.sw - bw_w - 10))

            if self.y < 120:
                by = int(self.y) + cur_sz + 10
            else:
                by = int(self.y) - bw_h - 12
            by = max(10, min(by, self.sh - bw_h - 10))

            bw.geometry(f"{bw_w}x{bw_h}+{bx}+{by}")
            bw.attributes("-topmost", True)
            if WIN32_AVAILABLE:
                try:
                    hwnd = bw.winfo_id()
                    parent_hwnd = win32gui.GetParent(hwnd) or hwnd
                    win32gui.SetWindowPos(
                        parent_hwnd, win32con.HWND_TOPMOST, bx, by, bw_w, bw_h,
                        win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
                    )
                except Exception:
                    pass

            # Si el chat está abierto, mantener siempre el foco en la caja de texto
            if getattr(self, "chat_win", None) and getattr(self.chat_win, "win", None):
                if tk.Toplevel.winfo_exists(self.chat_win.win) and hasattr(self.chat_win, "entry"):
                    self.root.after(15, lambda: self.chat_win.entry.focus_set() if self.chat_win else None)

            self.bubble_win   = bw
            display_ms = int(max(6000, min(40000, len(text) * 90)) * bub_dur_mult)
            self.bubble_after = self.root.after(display_ms, self.destroy_bubble)

            if hasattr(self, "tts") and self.tts:
                self.tts.speak(text, skin=getattr(self, "current_skin", "Bocchi"))
        except Exception as e:
            print(f"Error en show_speech: {e}")

    def destroy_bubble(self):
        if self.bubble_win:
            try:
                self.bubble_win.destroy()
            except Exception:
                pass
            self.bubble_win = None

    def get_random_speech(self):
        name = self.user_info.username
        ip = self.user_info.public_ip
        pc = self.user_info.computer_name
        skin = getattr(self, "current_skin", "Bocchi")
        meta = SKIN_META.get(skin, {})
        base_speeches = meta.get("speeches", SPEECHES)
        pool = list(base_speeches) + [
            f"Oye {name}, bonita PC '{pc}'... seria una pena que algo le pasara 7w7",
            f"Te tengo ubicado en {ip} alv, no te hagas el loco (o_o)",
            f"¿Crees que no se quien eres? Saludos a {name} en {ip} :v",
            f"Ya vete alv {name}, me das igual UwU",
            f"Oye {name}, o me compras unas papitas o filtro tu IP {ip} en Twitter 7w7",
            f"Apura {name}, no tengo todo el dia :v",
            f"Mmm... a ver si trabajas mas y procrastinas menos en '{pc}', sokete :v",
        ]
        return random.choice(pool)

    def get_poked_speech(self):
        name = self.user_info.username
        ip = self.user_info.public_ip
        skin = getattr(self, "current_skin", "Bocchi")
        meta = SKIN_META.get(skin, {})
        base_poked = meta.get("poked", POKED_SPEECHES)
        pool = list(base_poked) + [
            f"¡Ke te pasa {name} sokete! (>_<)",
            f"Nmms {name} no me toques UwU",
            f"¡Apura y deja de picarme o le hago ping a {ip} alv! :v",
            f"Ya vi tus carpetas en Windows, {name}... perturbador 7w7",
        ]
        return random.choice(pool)

    def get_fake_error(self):
        name = self.user_info.username
        ip = self.user_info.public_ip
        pc = self.user_info.computer_name
        pool = FAKE_ERRORS + [
            ("Error Critico de Bocchi", f"Puta madre {name}, el sistema '{pc}' anda jodido y no tengo varo para pagar mas RAM :v"),
            ("Alerta de Seguridad Bocchi-OS", f"[!] ADVERTENCIA: Bocchi detecto al usuario '{name}' en la IP {ip}.\nTransfierele 50 pesitos para no filtrar el historial UwU"),
            ("Error 404: Dignidad", f"No se encontro dignidad en '{pc}'. Reemplaza todo con memes del Uriel y ya 7w7"),
            ("Doxx Alert [!]", f"Bocchi hackeo exitosamente a {name} ({ip}). Rescate: una orden de tacos al pastor :v"),
            ("Windows Defender: Nivel Extremo", f"Se detectó un virus tipo 'El_Uriel.exe' operado por '{name}'. Procediendo a no hacer nada :v"),
            ("Error 418: Soy una tetera", f"La computadora '{pc}' no puede procesar peticiones porque actualmente es una tetera."),
            ("Fallo de Gravedad en Windows", "La gravedad del escritorio se apagara temporalmente. Sujete bien sus ventanas."),
            ("Alerta de la NASA", f"Se detectó una señal sospechosa proveniente del usuario '{name}' en la red {ip}."),
        ]
        return random.choice(pool)

    def schedule_random_speech(self):
        interval_sec = int(self.config.get("shimeji_talk_interval_sec", 45))
        if interval_sec <= 0:
            return
        if getattr(self, "troll_mode", False):
            delay = random.randint(max(3000, interval_sec * 300), max(6000, interval_sec * 600))
        else:
            delay = random.randint(max(5000, interval_sec * 700), max(10000, interval_sec * 1200))
        self.root.after(delay, self.random_speech_tick)

    def random_speech_tick(self):
        interval_sec = int(self.config.get("shimeji_talk_interval_sec", 45))
        if interval_sec > 0:
            chance = 0.85 if getattr(self, "troll_mode", False) else 0.65
            if random.random() < chance:
                self.show_speech(self.get_random_speech())
            self.schedule_random_speech()

    def _schedule_random_mouse_move(self):
        delay = random.randint(20000, 30000)
        self._mouse_move_after_id = self.root.after(delay, self._random_mouse_move)

    def _random_mouse_move(self):
        if WIN32_AVAILABLE:
            try:
                x = random.randint(0, self.sw - 1)
                y = random.randint(0, self.sh - 1)
                win32api.SetCursorPos((x, y))
            except Exception:
                pass
        self._schedule_random_mouse_move()

if __name__ == "__main__":
    if not PIL_AVAILABLE:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow"])
        from PIL import Image, ImageTk
        PIL_AVAILABLE = True
    if not REQUESTS_AVAILABLE:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        import requests
        REQUESTS_AVAILABLE = True
    app = Shimeji()