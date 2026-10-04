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
import fnmatch
import urllib.parse
import importlib

try:
    import winreg
except Exception:
    winreg = None

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

IMG_DIR      = os.path.join(BASE_DIR, "img", "Shimeji")
ACTIONS_FILE = os.path.join(BASE_DIR, "Actions.xml")

def open_url_guaranteed(url):
    try:
        if sys.platform == "win32":
            os.startfile(url)
            return True
    except Exception:
        pass
    try:
        webbrowser.open_new_tab(url)
        return True
    except Exception:
        try:
            subprocess.Popen(f'start "" "{url}"', shell=True)
            return True
        except Exception:
            return False

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
CARRY_FRAMES   = STAND_FRAMES
DEPRESS_FRAMES = STAND_FRAMES
AWAY_FRAMES    = STAND_FRAMES
CLIMB_FRAMES   = WALK_FRAMES

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

    def __init__(self, config_dict=None):
        self.config = config_dict if config_dict is not None else {}
        self.listeners = []
        self.reload()

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
        self.config[f"custom_{key}"] = color
        self.reload()
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

        # Extra custom color buttons (visible when mode == custom)
        self.custom_colors_frame = tk.Frame(self.sec2, bg=self.theme.surface)
        if self.theme.theme_mode == "custom":
            self.custom_colors_frame.pack(fill=tk.X, pady=(8, 0))

        btn_bg = tk.Button(self.custom_colors_frame, text="Fondo...", command=lambda: self._pick_custom("bg"),
                           bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                           bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        btn_bg.pack(side=tk.LEFT, padx=(0, 4))

        btn_surf = tk.Button(self.custom_colors_frame, text="Superficie...", command=lambda: self._pick_custom("surface"),
                             bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                             bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        btn_surf.pack(side=tk.LEFT, padx=4)

        btn_txt = tk.Button(self.custom_colors_frame, text="Texto...", command=lambda: self._pick_custom("text"),
                            bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                            bd=0, relief=tk.FLAT, padx=4)
        btn_txt.pack(side=tk.LEFT, padx=4)

        btn_entry = tk.Button(self.custom_colors_frame, text="Caja texto...", command=lambda: self._pick_custom("entry_bg"),
                              bg=self.theme.surface_variant, fg=self.theme.text, font=(self.theme.font_family, 8),
                              bd=0, relief=tk.FLAT, padx=4, cursor="hand2")
        btn_entry.pack(side=tk.LEFT, padx=4)

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

    def _on_theme_update(self):
        if not self.win or not tk.Toplevel.winfo_exists(self.win):
            return
        self.win.configure(bg=self.theme.bg)
        self.win.attributes("-alpha", self.theme.opacity)
        self.accent_swatch.configure(bg=self.theme.accent)
        self.accent_hex_lbl.configure(text=self.theme.accent.upper(), fg=self.theme.text, bg=self.theme.surface)
        self.opac_scale.configure(bg=self.theme.surface, fg=self.theme.text,
                                  troughcolor=self.theme.surface_variant,
                                  activebackground=self.theme.accent)
        self.preview_card.configure(bg=self.theme.surface, highlightbackground=self.theme.border)
        self.prev_title.configure(fg=self.theme.accent, bg=self.theme.surface,
                                  font=(self.theme.font_family, self.theme.font_size, "bold"))
        self.prev_sample.configure(fg=self.theme.text, bg=self.theme.surface,
                                   font=(self.theme.font_family, self.theme.font_size))
        self.prev_badge.configure(bg=self.theme.surface_variant, font=(self.theme.font_family, self.theme.font_size - 1, "bold"))
        self.prev_btn.configure(bg=self.theme.accent, fg=self.theme.accent_text,
                                font=(self.theme.font_family, self.theme.font_size - 1, "bold"))
        if hasattr(self, "sec_bg") and self.sec_bg:
            self.sec_bg.configure(bg=self.theme.surface, highlightbackground=self.theme.border)
        if hasattr(self, "lbl_bg_status") and self.lbl_bg_status:
            self.lbl_bg_status.configure(fg=self.theme.text_dim, bg=self.theme.surface)

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
        "edge": "msedge",
        "microsoft edge": "msedge",
        "firefox": "firefox",
        "brave": "brave",
        "spotify": "spotify",
        "discord": "discord",
        "steam": "steam",
        "vscode": "code",
        "vs code": "code",
        "visual studio code": "code",
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
        except Exception as e:
            return False, f"[!] Error ejecutando PowerShell: {e}"

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
            webbrowser.open(url)
            return True, f"[+] Búsqueda en YouTube abierta:\n'{clean}'\n[>] {url}"
        else:
            url = f"https://www.google.com/search?q={encoded}"
            webbrowser.open(url)
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

            # 1. URLs
            if clean.startswith(("http://", "https://", "www.")):
                url = "https://" + clean if clean.startswith("www.") else clean
                webbrowser.open(url)
                return True, f"[+] Abriendo enlace: {url}"

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

        # 0. Comprobación directa de comandos personalizados guardados
        # Chequear coincidencia exacta o sin prefijos como "hey ", "abre ", "corre ", "inicia "
        clean_trigger = lower
        for prefix in ("hey ", "porfa ", "favor de "):
            if clean_trigger.startswith(prefix):
                clean_trigger = clean_trigger[len(prefix):].strip()

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

    def get_system_prompt(self):
        return (
            f"{self.BASE_SYSTEM_PROMPT}\n\n"
            f"[DATOS REALES DEL USUARIO DE WINDOWS]:\n"
            f"- Nombre de usuario real de Windows: {self.user_info.username}\n"
            f"- Nombre de su computadora / host: {self.user_info.computer_name}\n"
            f"- IP Publica Real: {self.user_info.public_ip}\n"
            f"- IP Local (red interna): {self.user_info.local_ip}\n"
            f"- Ubicacion aproximada / ISP: {self.user_info.city}, {self.user_info.country} ({self.user_info.isp})\n"
            f"- Sistema Operativo: {self.user_info.os_info}\n\n"
            f"[HABILIDADES DE JARVIS EN WINDOWS]:\n"
            f"Tienes acceso como asistente JARVIS a la computadora de Windows del usuario para abrir programas, abrir o buscar archivos, buscar en internet, renombrar, crear, modificar, leer y borrar archivos, agregar comandos personalizados permanentes y ejecutar comandos de CMD/PowerShell/WSL.\n"
            f"Si el usuario te pide abrir un programa, buscar archivos, buscar en la web, crear o modificar archivos, o guardar un nuevo comando, responde con tu humor de Bocchi y agrega al final la etiqueta correspondiente:\n"
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
            f"[JARVIS: ADD_CMD \"frase activadora\" = \"comando\"]\n"
            f"[JARVIS: DEL_CMD \"frase activadora\"]\n"
            f"[JARVIS: ADD_PATH \"ruta personalizada\"]\n"
            f"[JARVIS: DEL_PATH \"ruta personalizada\"]\n"
            f"[JARVIS: TROLL ON|OFF]\n\n"
            f"REGLA CRUCIAL:\n"
            f"Tu sabes estos datos reales del usuario. Si el usuario te pregunta quien es el o cual es su IP, "
            f"dile directamente su nombre real de Windows ('{self.user_info.username}') y su IP publica real ('{self.user_info.public_ip}'). "
            f"Burlate de su PC ('{self.user_info.computer_name}') o de su conexion. "
            f"Si no te pregunta directamente, tambien puedes soltar comentarios casuales usando su nombre o amenazando con doxxearlo en broma, "
            f"exigiendole 50 pesos para esquites."
        )

    def get_local_chat_system_prompt(self):
        return (
            f"{self.BASE_SYSTEM_PROMPT}\n\n"
            f"[REGLAS DE CONVERSACIÓN DE BOCCHI (SOLO CHARLA - CERO PROGRAMACIÓN)]:\n"
            f"- Usuario actual: {self.user_info.username}\n"
            f"- Tu único propósito aquí es conversar, opinar, bromear, contar cosas y hacer compañía como una buena amiga.\n"
            f"- Responde SIEMPRE en español manteniendo tu personalidad única (tímida, algo dramática o cínica, pero leal y chistosa).\n"
            f"- OJO ESTRICTO: Esta es EXCLUSIVAMENTE una charla casual entre personas. NUNCA escribas código de programación, NUNCA hagas scripts, NUNCA uses bloques de código con comillas invertidas ni sintaxis técnica.\n"
            f"- Si el usuario te platica o pregunta cosas de la vida, anime, juegos, memes o comida, conversa de forma divertida y natural.\n"
            f"- Mantén tus respuestas conversacionales, concisas y directas (máximo 2 a 3 oraciones cortas)."
        )

    def _build_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("[CHAT] Bocchi Chatbot IA")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", self.theme.opacity)
        self.win.configure(bg=self.theme.bg)
        self.win.geometry("520x640")
        self.win.minsize(440, 480)
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        # Top Header Bar
        header = tk.Frame(self.win, bg=self.theme.surface, pady=8, padx=14)
        header.pack(fill=tk.X)

        title_col = tk.Frame(header, bg=self.theme.surface)
        title_col.pack(side=tk.LEFT)

        self.title_lbl = tk.Label(title_col, text="[*] BOCCHI CHATBOT IA [*]",
                                  font=(self.theme.font_family, self.theme.font_size + 2, "bold"),
                                  fg=self.theme.accent, bg=self.theme.surface)
        self.title_lbl.pack(anchor="w")

        self.header_status = tk.Label(
            title_col,
            text=f"[ONLINE] Conectado con: {self.user_info.username} | IP: {self.user_info.public_ip}",
            font=(self.theme.font_family, self.theme.font_size - 1),
            fg=self.theme.success, bg=self.theme.surface
        )
        self.header_status.pack(anchor="w")

        # Right header toolbar buttons
        tool_col = tk.Frame(header, bg=self.theme.surface)
        tool_col.pack(side=tk.RIGHT)

        self.troll_btn = tk.Button(tool_col,
                                   text="[!] Troll: ON" if (self.shimeji and getattr(self.shimeji, "troll_mode", False)) else "[o] Troll: OFF",
                                   command=self.toggle_troll,
                                   bg=self.theme.surface_variant,
                                   fg=self.theme.danger if (self.shimeji and getattr(self.shimeji, "troll_mode", False)) else self.theme.text_dim,
                                   font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                   activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        self.troll_btn.pack(side=tk.LEFT, padx=2)

        self.doxx_btn = tk.Button(tool_col, text="[*] Doxx",
                                  command=lambda: self.shimeji.open_doxx() if self.shimeji else None,
                                  bg=self.theme.surface_variant, fg=self.theme.text,
                                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                  activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        self.doxx_btn.pack(side=tk.LEFT, padx=2)

        self.bg_btn = tk.Button(tool_col, text="[IMG] Fondo", command=self.open_bg_menu,
                                bg=self.theme.surface_variant, fg=self.theme.text,
                                font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        self.bg_btn.pack(side=tk.LEFT, padx=2)

        self.theme_btn = tk.Button(tool_col, text="[*] Apariencia", command=self.open_appearance,
                                   bg=self.theme.surface_variant, fg=self.theme.text,
                                   font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                   activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        self.theme_btn.pack(side=tk.LEFT, padx=2)

        self.opacity_btn = tk.Button(tool_col, text="[o] Opacidad", command=self.toggle_opacity,
                                     bg=self.theme.surface_variant, fg=self.theme.text,
                                     font=(self.theme.font_family, self.theme.font_size - 1),
                                     activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        self.opacity_btn.pack(side=tk.LEFT, padx=2)

        self.clear_btn = tk.Button(tool_col, text="[x] Limpiar", command=self.clear_chat,
                                   bg=self.theme.surface_variant, fg=self.theme.text_dim,
                                   font=(self.theme.font_family, self.theme.font_size - 1),
                                   activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        # Mode Selection Bar
        mode_frame = tk.Frame(self.win, bg=self.theme.bg, pady=4, padx=12)
        mode_frame.pack(fill=tk.X)

        self.rb_local = tk.Radiobutton(mode_frame, text="[-] Local (Qwen Charla)", variable=self.mode_var, value="local",
                                       bg=self.theme.bg, fg=self.theme.text, selectcolor=self.theme.surface,
                                       activebackground=self.theme.bg, activeforeground=self.theme.accent,
                                       font=(self.theme.font_family, self.theme.font_size), command=self._toggle_mode)
        self.rb_local.pack(side=tk.LEFT, padx=(0, 14))

        self.rb_api = tk.Radiobutton(mode_frame, text="[*] API (Gemini)", variable=self.mode_var, value="api",
                                     bg=self.theme.bg, fg=self.theme.text, selectcolor=self.theme.surface,
                                     activebackground=self.theme.bg, activeforeground=self.theme.accent,
                                     font=(self.theme.font_family, self.theme.font_size), command=self._toggle_mode)
        self.rb_api.pack(side=tk.LEFT)

        # API Key Row (para modo API)
        self.kf = tk.Frame(self.win, bg=self.theme.surface, padx=10, pady=5,
                           highlightbackground=self.theme.border, highlightthickness=1)

        self.api_lbl = tk.Label(self.kf, text="[KEY] API Key:", bg=self.theme.surface, fg=self.theme.text_dim,
                                font=(self.theme.font_family, self.theme.font_size))
        self.api_lbl.pack(side=tk.LEFT)

        entry_fg = getattr(self.theme, "entry_fg", "#ffffff" if self.theme._calc_brightness(self.theme.entry_bg) < 130 else "#111620")
        self.api_entry = tk.Entry(self.kf, textvariable=self.api_key_var, show="*",
                                  bg=self.theme.entry_bg, fg=entry_fg, insertbackground=entry_fg,
                                  font=(self.theme.font_family, self.theme.font_size), bd=0, relief=tk.FLAT)
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=3)

        self.show_key_btn = tk.Button(self.kf, text="[*]", command=self.toggle_key_vis,
                                      bg=self.theme.surface_variant, fg=self.theme.text,
                                      font=(self.theme.font_family, self.theme.font_size - 1),
                                      activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, cursor="hand2")
        self.show_key_btn.pack(side=tk.LEFT, padx=(0, 4))

        # Local Model Row (para modo local sin API)
        self.local_frame = tk.Frame(self.win, bg=self.theme.surface, padx=10, pady=5,
                                    highlightbackground=self.theme.border, highlightthickness=1)
        self.local_lbl = tk.Label(self.local_frame, text="[IA] Modelo:", bg=self.theme.surface, fg=self.theme.text_dim,
                                  font=(self.theme.font_family, self.theme.font_size))
        self.local_lbl.pack(side=tk.LEFT)

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
            font=(self.theme.font_family, self.theme.font_size - 1)
        )
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_local_model_change)
        self.model_combo.bind("<Return>", self._on_local_model_change)

        # Test IA Button
        self.verify_btn = tk.Button(self.win, text="[?] Probar Conexion / Estado de la IA", command=self.verify_connection,
                                    bg=self.theme.surface, fg=self.theme.accent,
                                    font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                    activebackground=self.theme.surface_variant, bd=0, relief=tk.FLAT, pady=4, cursor="hand2",
                                    highlightbackground=self.theme.border, highlightthickness=1)
        self.verify_btn.pack(fill=tk.X, padx=12, pady=(2, 4))

        # Empaquetar la fila correspondiente al modo actual
        if saved_mode == "api":
            self.kf.pack(fill=tk.X, padx=12, pady=(0, 4), before=self.verify_btn)
        else:
            self.local_frame.pack(fill=tk.X, padx=12, pady=(0, 4), before=self.verify_btn)

        # 1. Input Area - Empaquetado en BOTTOM para garantizar visibilidad al 100%
        inp = tk.Frame(self.win, bg=self.theme.bg, padx=12, pady=6)
        inp.pack(side=tk.BOTTOM, fill=tk.X)

        entry_fg = getattr(self.theme, "entry_fg", "#ffffff" if self.theme._calc_brightness(self.theme.entry_bg) < 130 else "#111620")
        self.entry = tk.Entry(inp, bg=self.theme.entry_bg, fg=entry_fg,
                              insertbackground=entry_fg,
                              font=(self.theme.font_family, self.theme.font_size + 1),
                              bd=0, relief=tk.FLAT, highlightbackground=self.theme.border, highlightthickness=1)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.focus_set()

        self.send_btn = tk.Button(inp, text="Enviar >>", command=self.send_message,
                                  bg=self.theme.accent, fg=self.theme.accent_text,
                                  font=(self.theme.font_family, self.theme.font_size, "bold"),
                                  activebackground=self.theme.surface_variant,
                                  bd=0, relief=tk.FLAT, padx=14, cursor="hand2")
        self.send_btn.pack(side=tk.RIGHT)

        # 2. Quick action chips - Empaquetado en BOTTOM justo encima del cuadro de entrada
        chips_frame = tk.Frame(self.win, bg=self.theme.bg, padx=12, pady=2)
        chips_frame.pack(side=tk.BOTTOM, fill=tk.X)

        chips = [
            ("[JARVIS] Renombrar", lambda: self.insert_chip("/ren ")),
            ("[JARVIS] Crear", lambda: self.insert_chip("/create ")),
            ("[JARVIS] Archivos", lambda: self.send_custom("/list")),
            ("[WSL] Arch", lambda: self.send_custom("abre arch")),
            ("[*] Alias", lambda: self.insert_chip("/alias ")),
            ("[!] Troll Mode", lambda: self.toggle_troll()),
            ("[?] Quien soy?", lambda: self.send_custom("Quien soy yo y cual es mi IP real?")),
            ("[IMG] Fondo", self.open_bg_menu),
            ("[*] Consejo", lambda: self.send_custom("Bocchi dame un consejo")),
            ("UwU", lambda: self.insert_chip("UwU")),
            (":v", lambda: self.insert_chip(":v")),
        ]
        self.chip_btns = []
        for chip_text, chip_cmd in chips:
            btn = tk.Button(chips_frame, text=chip_text, command=chip_cmd,
                            bg=self.theme.surface_variant, fg=self.theme.text_dim,
                            font=(self.theme.font_family, self.theme.font_size - 1),
                            activebackground=self.theme.surface, activeforeground=self.theme.accent,
                            bd=0, relief=tk.FLAT, padx=6, pady=2, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self.chip_btns.append(btn)

        # 3. Chat display area con Canvas - Empaquetado en TOP con fill=BOTH expand=True
        # para tomar todo el espacio entre la barra superior y los controles inferiores
        self.chat_container = tk.Frame(self.win, bg=self.theme.surface,
                                       highlightthickness=1, highlightbackground=self.theme.border)
        self.chat_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=(4, 4))

        self.chat_canvas = tk.Canvas(self.chat_container, bg=self.theme.surface, bd=0, highlightthickness=0)
        self.chat_scroll = ttk.Scrollbar(self.chat_container, orient=tk.VERTICAL, command=self._on_canvas_scroll)
        self.chat_canvas.configure(yscrollcommand=self.chat_scroll.set)
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)
        self.chat_canvas.bind("<MouseWheel>", self._on_mousewheel)

        # Asegurar foco al hacer clic en el chat o en la ventana
        self.win.bind("<Button-1>", lambda e: self.entry.focus_set(), add="+")
        self.chat_canvas.bind("<Button-1>", lambda e: self.entry.focus_set(), add="+")

        self._toggle_mode()
        self.load_bg_asset(self.bg_image_path, initial=True)
        self._append_system(
            f"Oie {self.user_info.username} ya llegue wei, se que estas en {self.user_info.public_ip} asi que apura tus preguntas pq ando jodida :v\n"
        )

        self.user_info.add_listener(self._on_ip_update)
        self.win.update_idletasks()
        self._redraw_all_messages()

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
            hdr_text = "[*] Bocchi-chan"
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
                                 font=(self.theme.font_family, self.theme.font_size + 2, "bold"))
        self.header_status.configure(font=(self.theme.font_family, self.theme.font_size - 1))
        self.chat_container.configure(bg=self.theme.surface, highlightbackground=self.theme.border)
        if not self.bg_frames:
            self.chat_canvas.configure(bg=self.theme.surface)
        entry_fg = getattr(self.theme, "entry_fg", "#ffffff" if self.theme._calc_brightness(self.theme.entry_bg) < 130 else "#111620")
        self.entry.configure(bg=self.theme.entry_bg, fg=entry_fg, insertbackground=entry_fg,
                             font=(self.theme.font_family, self.theme.font_size + 1),
                             highlightbackground=self.theme.border)
        if hasattr(self, "api_entry") and self.api_entry:
            self.api_entry.configure(bg=self.theme.entry_bg, fg=entry_fg, insertbackground=entry_fg)
        if hasattr(self, "local_frame") and self.local_frame:
            self.local_frame.configure(bg=self.theme.surface, highlightbackground=self.theme.border)
        if hasattr(self, "local_lbl") and self.local_lbl:
            self.local_lbl.configure(bg=self.theme.surface, fg=self.theme.text_dim, font=(self.theme.font_family, self.theme.font_size))
        if hasattr(self, "rb_local") and self.rb_local:
            self.rb_local.configure(bg=self.theme.bg, fg=self.theme.text, selectcolor=self.theme.surface, font=(self.theme.font_family, self.theme.font_size))
        if hasattr(self, "rb_api") and self.rb_api:
            self.rb_api.configure(bg=self.theme.bg, fg=self.theme.text, selectcolor=self.theme.surface, font=(self.theme.font_family, self.theme.font_size))
        self.send_btn.configure(bg=self.theme.accent, fg=self.theme.accent_text,
                                font=(self.theme.font_family, self.theme.font_size, "bold"))
        self.verify_btn.configure(bg=self.theme.surface, fg=self.theme.accent,
                                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                  highlightbackground=self.theme.border)
        for btn in getattr(self, "chip_btns", []):
            btn.configure(bg=self.theme.surface_variant, fg=self.theme.text_dim,
                          font=(self.theme.font_family, self.theme.font_size - 1))
        self._redraw_all_messages()

    def _on_ip_update(self, info):
        if self.win and tk.Toplevel.winfo_exists(self.win):
            self.parent.after(0, lambda: self.header_status.configure(
                text=f"[ONLINE] Conectado con: {self.user_info.username} | IP: {self.user_info.public_ip}"
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
        curr = self.entry.get()
        space = " " if curr and not curr.endswith(" ") else ""
        self.entry.insert(tk.END, space + text)
        self.entry.focus()

    def send_custom(self, text):
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
            self.kf.pack(fill=tk.X, padx=12, pady=(0, 4), before=self.verify_btn)
        else:
            self.kf.pack_forget()
            if hasattr(self, "local_frame"):
                self.local_frame.pack(fill=tk.X, padx=12, pady=(0, 4), before=self.verify_btn)

    def verify_connection(self):
        self.verify_btn.configure(state=tk.DISABLED, text="[..] Verificando...")
        threading.Thread(target=self._run_verification, daemon=True).start()

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
                        resp = requests.post(url, json=payload, timeout=6)
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
                pipeline = importlib.import_module("transformers").pipeline
                model_id = self.local_model_var.get().strip() if hasattr(self, "local_model_var") else "Qwen/Qwen2.5-0.5B-Instruct"
                if " " in model_id:
                    model_id = model_id.split()[0].strip()
                self.parent.after(0, lambda m=model_id: self._append_system(f"[..] Verificando modelo local de charla: {m}..."))
                if not self.local_pipe or getattr(self, "_current_loaded_model", None) != model_id:
                    self.local_pipe = pipeline("text-generation", model=model_id, low_cpu_mem_usage=True)
                    self._current_loaded_model = model_id
                self.parent.after(0, lambda m=model_id: self._append_system(f"[+] Modelo local de charla ({m}) cargado y listo offline!\n(Configurado exclusivamente para hablar, sin código)"))
            except Exception as e:
                self._show_error(f"Error al cargar modelo local: {e}")

        self.parent.after(0, lambda: self.verify_btn.configure(state=tk.NORMAL, text="[?] Probar Conexion / Estado de la IA"))

    def send_message(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._append_user(text)

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
            pipeline = importlib.import_module("transformers").pipeline
            model_id = self.local_model_var.get().strip() if hasattr(self, "local_model_var") else "Qwen/Qwen2.5-0.5B-Instruct"
            if " " in model_id:
                model_id = model_id.split()[0].strip()

            if not self.local_pipe or getattr(self, "_current_loaded_model", None) != model_id:
                self.parent.after(0, lambda m=model_id: self._append_system(f"[..] Cargando modelo local de charla ({m})...\n(La primera vez tomará unos momentos mientras carga)"))
                self.local_pipe = pipeline("text-generation", model=model_id, low_cpu_mem_usage=True)
                self._current_loaded_model = model_id

            sys_prompt = self.get_local_chat_system_prompt()
            msgs = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": text}
            ]
            out = self.local_pipe(
                msgs,
                max_new_tokens=140,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.12,
                clean_up_tokenization_spaces=False
            )
            raw_reply = out[0]['generated_text'][-1]['content'].strip()

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
        reply = None
        last_err = None

        for m in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                payload = {
                    "system_instruction": {"parts": [{"text": sys_prompt}]},
                    "contents": self.history,
                    "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024}
                }
                resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=40)
                if resp.status_code == 200:
                    data = resp.json()
                    reply = data["candidates"][0]["content"]["parts"][0]["text"]
                    break
                elif resp.status_code != 404:
                    last_err = f"HTTP {resp.status_code}: {resp.text[:100]}"
            except Exception as e:
                last_err = str(e)

        if reply:
            self.history.append({"role": "model", "parts": [{"text": reply}]})
            self.parent.after(0, self._show_reply, reply)
        else:
            self._show_error(f"Fallo el API de Gemini ({last_err or 'revisa tu API Key'})")

    def _execute_jarvis_tags_in_reply(self, reply_text):
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

        return cleaned.strip(), results

    def _show_reply(self, reply):
        cleaned_reply, actions = self._execute_jarvis_tags_in_reply(reply)
        display_text = cleaned_reply if cleaned_reply else reply
        self._append_bot(display_text)
        if actions:
            for act in actions:
                self._append_system(act)
        self.send_btn.configure(state=tk.NORMAL, text="Enviar >>")
        short_speech = display_text[:50] + ("..." if len(display_text) > 50 else "")
        self.shimeji.show_speech(short_speech)

    def _show_error(self, msg):
        self.parent.after(0, lambda: (
            self._append_system(f"[!] {msg}"),
            self.send_btn.configure(state=tk.NORMAL, text="Enviar >>")
        ))

    def _on_close(self):
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
        
        TRANS_COLOR = "#000001"
        self.root.attributes("-transparentcolor", TRANS_COLOR)
        self.root.config(bg=TRANS_COLOR)
        self.root.geometry(f"{SIZE}x{SIZE}+100+100")
        try:
            self.root.wm_attributes("-alpha", 1.0)
        except Exception:
            pass

        self.canvas = tk.Canvas(self.root, width=SIZE, height=SIZE,
                                bg=TRANS_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack()
        self.sprite_item = self.canvas.create_image(0, 0, anchor="nw")

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.ground_y  = self.sh - 140
        self.ceiling_y = -40
        self.wall_lx   = 0
        self.wall_rx   = self.sw - SIZE

        self.x = random.randint(100, self.sw - 200)
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

        self.config      = load_config()
        self.user_info   = UserSystemInfo()
        self.theme_manager = ThemeManager(self.config)
        self.jarvis      = JarvisAssistant(self, self.user_info)
        self.troll_mode  = self.config.get("troll_mode", False)
        self.api_key_var = tk.StringVar(value=self.config.get("gemini_api_key", GEMINI_API_KEY))
        self.chat_win    = None
        self.doxx_win    = None
        self.appearance_win = None

        self.bubble_win   = None
        self.bubble_after = None

        self.canvas.bind("<ButtonPress-1>",  self.on_press)
        self.canvas.bind("<B1-Motion>",       self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>",   self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

        self.schedule_random_speech()
        self._schedule_random_mouse_move()
        self.set_state("walking")
        self.root.after(DELAY, self.tick)
        self.root.after(500, self._cache_own_hwnd)
        self.root.after(5000, self._auto_tick)
        self.root.after(15000, self._troll_autonomous_tick)
        self.root.mainloop()

    def load_images(self):
        if not PIL_AVAILABLE or not os.path.isdir(IMG_DIR):
            return
        try:
            # Map lowercase filenames to actual paths for 100% case-insensitivity
            disk_files = {}
            for f in os.listdir(IMG_DIR):
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.png', '.gif', '.jpg', '.jpeg'):
                    base = os.path.splitext(f)[0].lower()
                    disk_files[base] = os.path.join(IMG_DIR, f)

            all_names = set(
                STAND_FRAMES + WALK_FRAMES + WALK_BACK + SIT_FRAMES +
                GUITAR_FRAMES + LIE_FRAMES + BLOB_FRAMES + GHOST_FRAMES +
                BOX_FRAMES + FALL_FRAMES + KNEEL_FRAMES + CARRY_FRAMES +
                DEPRESS_FRAMES + AWAY_FRAMES + CLIMB_FRAMES
            )
            # Add all XML and disk frames
            for base in disk_files:
                all_names.add(base)

            for name in all_names:
                name_key = name.lower()
                fpath = disk_files.get(name_key)
                if not fpath:
                    # Direct check fallback
                    cand = os.path.join(IMG_DIR, name + ".png")
                    if os.path.exists(cand):
                        fpath = cand
                if fpath and os.path.exists(fpath):
                    try:
                        im = Image.open(fpath).convert("RGBA").resize((SIZE, SIZE))
                        self.images[name] = im
                        self.images[name_key] = im
                    except Exception:
                        pass
        except Exception:
            pass

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

    def set_state(self, state, surface=None):
        self.state       = state
        self.frame_idx   = 0
        self.frame_timer = 0
        self.state_ticks = 0
        if surface is not None:
            self.surface = surface

        speed = self.WALK_SPEED

        cfg = {
            "standing":     (STAND_FRAMES,  15, 30+random.randint(10,30),    0,     0),
            "walking":      (WALK_FRAMES,   5,  120+random.randint(40,160),  random.choice([-1,1])*speed, 0),
            "walk_back":    (WALK_BACK,     8,  40+random.randint(20,50),    random.choice([-1,1])*2, 0),
            "sitting":      (SIT_FRAMES,    10, 40+random.randint(20,50),    0,     0),
            "guitar":       (GUITAR_FRAMES, 8,  50+random.randint(20,50),    0,     0),
            "ceiling_idle": (LIE_FRAMES,    12, 50+random.randint(20,60),    0,     0),
            "blob":         (BLOB_FRAMES,   8,  30+random.randint(10,30),    0,     0),
            "ghost":        (GHOST_FRAMES,  10, 30+random.randint(10,30),    0,     0),
            "box":          (BOX_FRAMES,    18, len(BOX_FRAMES)*14,          0,     0),
            "falling":      (FALL_FRAMES,   2,  9999,                        random.randint(-2,2), 0),
            "kneel":        (KNEEL_FRAMES,  10, 30+random.randint(10,30),    0,     0),
            "carry":        (CARRY_FRAMES,  15, 40+random.randint(20,40),    0,     0),
            "depress":      (DEPRESS_FRAMES,15, 40+random.randint(20,40),    0,     0),
            "away":         (AWAY_FRAMES,   10, 30+random.randint(10,30),    0,     0),
            "climb_left":   (CLIMB_FRAMES,  6,  80+random.randint(40,80),    0,     0),
            "climb_right":  (CLIMB_FRAMES,  6,  80+random.randint(40,80),    0,     0),
            "ceiling_walk": (WALK_FRAMES,   5,  100+random.randint(40,120),  random.choice([-1,1])*speed, 0),
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
        pool = (
            ["walking"] * 20 +
            ["walk_back"] * 6 +
            ["standing"] * 2 +
            ["sitting"] * 1 +
            ["guitar"] * 1 +
            ["blob"] * 1 +
            ["ghost"] * 1 +
            ["box"] * 1 +
            ["kneel"] * 1 +
            ["carry"] * 1 +
            ["depress"] * 1 +
            ["away"] * 1
        )
        self.set_state(random.choice(pool), surface=SURFACE_FLOOR)
        
    def choose_next_ceiling_state(self):
        if random.random() < 0.65:
            self.set_state("ceiling_walk", surface=SURFACE_CEILING)
            self.vel_x = random.choice([-1, 1]) * self.WALK_SPEED
            self.vel_y = 0
        else:
            self.set_state("ceiling_idle", surface=SURFACE_CEILING)
            self.vel_x = 0
            self.vel_y = 0

    def tick(self):
        try:
            if self._follow_cursor_enabled and WIN32_AVAILABLE and not self.dragging and not self.dragging_window:
                self._move_towards_cursor()
            if not self.dragging and not self.dragging_window:
                self.physics()
                self.animate()
        except Exception:
            pass
        finally:
            self.root.after(DELAY, self.tick)

    def physics(self):
        if self.state == "falling":
            self.gravity = min(self.gravity + 1, 20)
            self.y      += self.gravity
            self.x      += self.vel_x
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.gravity = 0
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
            center_x = self.x + SIZE // 2
            center_y = self.y + SIZE // 2
            
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
        if self.x <= self.wall_lx:
            self.x = self.wall_lx
            if random.random() < self.CLIMB_CHANCE:
                self._start_climb(SURFACE_WALL_L, going_up=True)
            else:
                self.vel_x = self.WALK_SPEED
                self.flipped = False
        elif self.x >= self.wall_rx:
            self.x = self.wall_rx
            if random.random() < self.CLIMB_CHANCE:
                self._start_climb(SURFACE_WALL_R, going_up=True)
            else:
                self.vel_x = -self.WALK_SPEED
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
            self.choose_next_ceiling_state()
        elif self.y >= self.ground_y:
            self.y = self.ground_y
            self.choose_next_floor_state()

    def _physics_ceiling(self):
        if self.state not in ("ceiling_walk", "ceiling_idle"):
            return
        self.x += self.vel_x
        self.y  = self.ceiling_y

        if self.x <= self.wall_lx:
            self.x = self.wall_lx
            if random.random() < 0.5:
                self._start_climb(SURFACE_WALL_L, going_up=False)
            else:
                self.vel_x = self.WALK_SPEED
                self.flipped = False
        elif self.x >= self.wall_rx:
            self.x = self.wall_rx
            if random.random() < 0.5:
                self._start_climb(SURFACE_WALL_R, going_up=False)
            else:
                self.vel_x = -self.WALK_SPEED
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
        self.x = max(self.wall_lx, min(self.x, self.wall_rx))
        self.y = max(self.ceiling_y, min(self.y, self.ground_y))
        self.root.geometry(f"{SIZE}x{SIZE}+{int(self.x)}+{int(self.y)}")

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
            if random.random() < 0.3:
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
            rotation = 270
            flip_h   = self.vel_y > 0
        elif self.surface == SURFACE_WALL_R:
            rotation = 90
            flip_h   = self.vel_y < 0
        elif self.surface == SURFACE_CEILING:
            if self.state == "ceiling_idle":
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
        self._react_to_poke()
        self.dragging   = True
        self.drag_off_x = e.x
        self.drag_off_y = e.y
        self.surface = SURFACE_FLOOR
        self.set_state("falling", SURFACE_FLOOR)

    def _react_to_poke(self):
        reaction_frames = [GHOST_FRAMES, KNEEL_FRAMES]
        chosen = random.choice(reaction_frames)
        available = [f for f in chosen if f in self.images]
        if available:
            self.frames      = available
            self.frame_idx   = 0
            self.frame_timer = 0
            self.update_sprite()
        self.show_speech(self.get_poked_speech())

    def on_drag(self, e):
        if not self.dragging:
            return
        nx = self.root.winfo_x() + e.x - self.drag_off_x
        ny = self.root.winfo_y() + e.y - self.drag_off_y
        self.x = max(0, min(nx, self.sw - SIZE))
        self.y = max(0, min(ny, self.sh - 50))
        self.root.geometry(f"{SIZE}x{SIZE}+{int(self.x)}+{int(self.y)}")
        if self.dragging_window:
            sx = self.root.winfo_rootx() + e.x
            sy = self.root.winfo_rooty() + e.y
            self.win_dragger.move_to(sx, sy)

    def on_release(self, e):
        self.dragging = False
        if self.dragging_window:
            self.win_dragger.release()
            self.dragging_window = False
            self.show_speech("¡Tachan! (*^^*)")
        self.surface = SURFACE_FLOOR
        if self.y < self.ground_y:
            self.set_state("falling", SURFACE_FLOOR)
        else:
            self.choose_next_floor_state()

    def on_double_click(self, e):
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
            troll_toggle_lbl = "[!] MODO TROLL: [ON] (Desactivar)" if self.troll_mode else "[o] MODO TROLL: [OFF] (Activar)"
            menu.add_command(label=troll_toggle_lbl, command=self.toggle_troll_mode)
            menu.add_command(label="[#] Hablar con Bocchi (IA & JARVIS) >>", command=self.open_chat)
            menu.add_command(label="[*] Doxxearte / Info Real >>", command=self.open_doxx)
            menu.add_command(label="[?] Decir algo al azar", command=lambda: self.show_speech(self.get_random_speech()))
            menu.add_separator()

            poses_menu = tk.Menu(menu, tearoff=0,
                                 bg=t.surface, fg=t.text,
                                 activebackground=t.accent,
                                 activeforeground=acc_fg,
                                 font=(t.font_family, t.font_size))
            poses_menu.add_command(label="[*] Tocar guitarra",       command=lambda: self.set_state("guitar", SURFACE_FLOOR))
            poses_menu.add_command(label="[o] Modo blob",             command=lambda: self.set_state("blob",   SURFACE_FLOOR))
            poses_menu.add_command(label="[~] Modo fantasma",         command=lambda: self.set_state("ghost",  SURFACE_FLOOR))
            poses_menu.add_command(label="[#] Truco de caja",         command=lambda: self.set_state("box",    SURFACE_FLOOR))
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
            menu.add_command(label="[x] Cerrar Shimeji", command=self.root.destroy,
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
        cx = int(self.x) + SIZE // 2
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
                bw.attributes("-alpha", t.opacity)
            except Exception:
                pass

            card = tk.Frame(bw, bg=t.surface, highlightbackground=t.accent, highlightthickness=1, padx=10, pady=6)
            card.pack(fill=tk.BOTH, expand=True)

            header_frame = tk.Frame(card, bg=t.surface)
            header_frame.pack(fill=tk.X, pady=(0, 2))

            name_lbl = tk.Label(header_frame, text="[*] Bocchi-chan", bg=t.surface, fg=t.accent,
                                font=(t.font_family, max(8, t.font_size - 2), "bold"))
            name_lbl.pack(side=tk.LEFT)

            subtle_fg = getattr(t, "text_subtle", getattr(t, "text_dim", "#888888"))
            close_btn = tk.Label(header_frame, text="[x]", bg=t.surface, fg=subtle_fg,
                                 font=(t.font_family, max(8, t.font_size - 2)), cursor="hand2")
            close_btn.pack(side=tk.RIGHT)
            close_btn.bind("<Button-1>", lambda e: self.destroy_bubble())

            msg_lbl = tk.Label(card, text=text, bg=t.surface, fg=t.text,
                               font=(t.font_family, t.font_size), wraplength=280, justify=tk.LEFT)
            msg_lbl.pack(fill=tk.BOTH, expand=True)

            card.bind("<Button-1>", lambda e: self.destroy_bubble())
            msg_lbl.bind("<Button-1>", lambda e: self.destroy_bubble())
            name_lbl.bind("<Button-1>", lambda e: self.destroy_bubble())

            bw.update_idletasks()
            bw_w = max(bw.winfo_reqwidth(), 160)
            bw_h = max(bw.winfo_reqheight(), 40)

            bx = int(self.x) + SIZE // 2 - bw_w // 2
            bx = max(10, min(bx, self.sw - bw_w - 10))

            if self.y < 120:
                by = int(self.y) + SIZE + 10
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
            self.bubble_after = self.root.after(5000, self.destroy_bubble)
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
        pool = SPEECHES + [
            f"Oye {name}, bonita PC '{pc}'... seria una pena que algo le pasara 7w7",
            f"Te tengo ubicado en {ip} alv, no te hagas el loco (o_o)",
            f"¿Crees que no se quien eres? Saludos a {name} en {ip} :v",
            f"Ya vete alv {name}, me das igual UwU",
            f"Oye {name}, o me compras unos esquites o filtro tu IP {ip} en Twitter 7w7",
            f"Apura {name}, no tengo todo el dia :v",
            f"Mmm... a ver si trabajas mas y procrastinas menos en '{pc}', sokete :v",
        ]
        return random.choice(pool)

    def get_poked_speech(self):
        name = self.user_info.username
        ip = self.user_info.public_ip
        pool = POKED_SPEECHES + [
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
        if getattr(self, "troll_mode", False):
            delay = random.randint(6000, 14000)
        else:
            delay = random.randint(10000, 20000)
        self.root.after(delay, self.random_speech_tick)

    def random_speech_tick(self):
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