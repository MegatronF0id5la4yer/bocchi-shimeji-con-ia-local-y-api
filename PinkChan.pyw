#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk
from tkinter import colorchooser
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
    from PIL import Image, ImageTk
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
            self.surface_variant = self.config.get("custom_surface_var", "#212630")
            self.border = self.config.get("custom_border", "#2e3542")
            self.text = self.config.get("custom_text", "#f1f4f8")
            self.text_dim = self.config.get("custom_text_dim", "#94a0b3")
            self.entry_bg = self.config.get("custom_entry_bg", "#1e222b")
            self.accent = self.config.get("custom_accent", "#38bdf8")

        self.accent_text = "#ffffff" if self._calc_brightness(self.accent) < 150 else "#111620"
        self.danger = "#ef4444"
        self.success = "#22c55e"
        self.warning = "#f59e0b"

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
        self.win.geometry("500x670")
        self.win.resizable(False, False)
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
    def __init__(self, shimeji_ref=None, user_info=None):
        self.shimeji = shimeji_ref
        self.user_info = user_info
        self.desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.default_dir = self.desktop_dir if os.path.isdir(self.desktop_dir) else BASE_DIR

    def resolve_target(self, filename_or_path, must_exist=False):
        """Resuelve el archivo buscando en Desktop, BASE_DIR o como ruta absoluta."""
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

        # Probar en Desktop
        cand_desktop = os.path.join(self.desktop_dir, cleaned)
        if os.path.exists(cand_desktop):
            return cand_desktop

        # Probar en BASE_DIR
        cand_base = os.path.join(BASE_DIR, cleaned)
        if os.path.exists(cand_base):
            return cand_base

        # Si must_exist es True pero no se encontro por nombre exacto, buscar en Desktop case-insensitive o sin extension
        if must_exist:
            if os.path.isdir(self.desktop_dir):
                for f in os.listdir(self.desktop_dir):
                    if f.lower() == cleaned.lower():
                        return os.path.join(self.desktop_dir, f)
                    base, _ = os.path.splitext(f)
                    if base.lower() == cleaned.lower():
                        return os.path.join(self.desktop_dir, f)
            # Buscar en BASE_DIR
            if os.path.isdir(BASE_DIR):
                for f in os.listdir(BASE_DIR):
                    if f.lower() == cleaned.lower():
                        return os.path.join(BASE_DIR, f)
                    base, _ = os.path.splitext(f)
                    if base.lower() == cleaned.lower():
                        return os.path.join(BASE_DIR, f)
            return None

        # Si no debe existir (por ejemplo para crear), default a Desktop
        return cand_desktop

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
            if clean.startswith("http://") or clean.startswith("https://"):
                webbrowser.open(clean)
                return True, f"[+] Abriendo enlace: {clean}"

            resolved = self.resolve_target(clean, must_exist=True)
            if resolved:
                os.startfile(resolved)
                return True, f"[+] Archivo abierto: '{os.path.basename(resolved)}'"
            else:
                os.startfile(clean)
                return True, f"[+] Ejecutando programa: '{clean}'"
        except Exception as e:
            return False, f"[!] No se pudo abrir '{target}': {e}"

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

        # 2. Renombrar archivos (Ej: "hey haz que x archivo ahora se llame caca", "/ren x y", "renombra x a y")
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

        # Slash command /ren o /rename
        if raw.startswith(("/ren ", "/rename ", "/renombrar ")):
            parts = raw.split(maxsplit=2)
            if len(parts) >= 3:
                ok, msg = self.rename_file(parts[1], parts[2])
                speech = f"Renombrado '{parts[1]}' a '{parts[2]}' [OK]" if ok else "No pude renombrarlo :v"
                return True, msg, speech
            else:
                return True, "[!] Uso: /rename <archivo_actual> <nuevo_nombre>", "Pon el nombre viejo y nuevo :v"

        # 3. Crear archivos (Ej: "crea un archivo llamado notas con hola", "/create notas.txt hola")
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

        # 4. Escribir / Modificar archivos (Ej: "escribe esto en notas.txt", "/write notas.txt texto")
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

        # 5. Leer archivos (Ej: "que dice notas.txt", "lee notas.txt", "/read notas.txt")
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

        # 6. Borrar archivos (Ej: "borra notas.txt", "/del notas.txt")
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

        # 7. Listar archivos (Ej: "lista los archivos", "/dir", "/ls")
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

        # 8. Abrir programas o URLs (Ej: "abre calc", "abre chrome", "/open calc")
        m_open_nat = re.search(r'^(?:(?:hey\s+)?(?:abre|abrir|ejecuta(?:r)?)\s+([^\s,]+))', raw, re.IGNORECASE)
        if m_open_nat:
            target = m_open_nat.group(1)
            ok, msg = self.open_target(target)
            speech = f"Abriendo '{target}' [>]" if ok else f"No pude abrir '{target}' :v"
            return True, msg, speech

        if raw.startswith(("/open ", "/abrir ", "/start ")):
            parts = raw.split(maxsplit=1)
            if len(parts) >= 2:
                ok, msg = self.open_target(parts[1])
                speech = f"Abriendo '{parts[1]}' [>]" if ok else f"No pude abrir '{parts[1]}' :v"
                return True, msg, speech
            return True, "[!] Uso: /open <archivo_o_programa>", "Dime que abrir :v"

        # 9. Ejecutar comandos directos de CMD (/cmd o /exec)
        if raw.startswith(("/cmd ", "/exec ")):
            parts = raw.split(maxsplit=1)
            if len(parts) >= 2:
                ok, msg = self.run_cmd(parts[1])
                speech = "Comando ejecutado [CMD]" if ok else "Fallo el comando :v"
                return True, msg, speech
            return True, "[!] Uso: /cmd <comando de Windows>", "Escribe el comando sokete :v"

        return False, "", ""

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
            f"Tienes acceso como asistente JARVIS a la computadora de Windows del usuario para crear, modificar, renombrar, leer y borrar archivos en su Escritorio o sistema, y ejecutar comandos.\n"
            f"Si el usuario te pide crear o modificar archivos, o hacer tareas de archivos o troll, puedes responderle en tu tono de Bocchi y agregar al final la instruccion correspondiente:\n"
            f"[JARVIS: RENAME \"origen\" -> \"nuevo\"]\n"
            f"[JARVIS: CREATE \"archivo\" :: \"contenido\"]\n"
            f"[JARVIS: WRITE \"archivo\" :: \"contenido\"]\n"
            f"[JARVIS: APPEND \"archivo\" :: \"contenido\"]\n"
            f"[JARVIS: READ \"archivo\"]\n"
            f"[JARVIS: DELETE \"archivo\"]\n"
            f"[JARVIS: LIST \"carpeta\"]\n"
            f"[JARVIS: OPEN \"programa\"]\n"
            f"[JARVIS: CMD \"comando\"]\n"
            f"[JARVIS: TROLL ON|OFF]\n\n"
            f"REGLA CRUCIAL:\n"
            f"Tu sabes estos datos reales del usuario. Si el usuario te pregunta quien es el o cual es su IP, "
            f"dile directamente su nombre real de Windows ('{self.user_info.username}') y su IP publica real ('{self.user_info.public_ip}'). "
            f"Burlate de su PC ('{self.user_info.computer_name}') o de su conexion. "
            f"Si no te pregunta directamente, tambien puedes soltar comentarios casuales usando su nombre o amenazando con doxxearlo en broma, "
            f"exigiendole 50 pesos para esquites."
        )

    def _build_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("[CHAT] Bocchi Chatbot IA")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", self.theme.opacity)
        self.win.configure(bg=self.theme.bg)
        self.win.geometry("490x650")
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

        self.rb_local = tk.Radiobutton(mode_frame, text="[-] Local (SmolLM)", variable=self.mode_var, value="local",
                                       bg=self.theme.bg, fg=self.theme.text, selectcolor=self.theme.surface,
                                       activebackground=self.theme.bg, activeforeground=self.theme.accent,
                                       font=(self.theme.font_family, self.theme.font_size), command=self._toggle_mode)
        self.rb_local.pack(side=tk.LEFT, padx=(0, 14))

        self.rb_api = tk.Radiobutton(mode_frame, text="[*] API (Gemini)", variable=self.mode_var, value="api",
                                     bg=self.theme.bg, fg=self.theme.text, selectcolor=self.theme.surface,
                                     activebackground=self.theme.bg, activeforeground=self.theme.accent,
                                     font=(self.theme.font_family, self.theme.font_size), command=self._toggle_mode)
        self.rb_api.pack(side=tk.LEFT)

        # API Key Row
        self.kf = tk.Frame(self.win, bg=self.theme.surface, padx=10, pady=5,
                           highlightbackground=self.theme.border, highlightthickness=1)

        self.api_lbl = tk.Label(self.kf, text="[KEY] API Key:", bg=self.theme.surface, fg=self.theme.text_dim,
                                font=(self.theme.font_family, self.theme.font_size))
        self.api_lbl.pack(side=tk.LEFT)

        self.api_entry = tk.Entry(self.kf, textvariable=self.api_key_var, show="*",
                                  bg=self.theme.entry_bg, fg=self.theme.text, insertbackground=self.theme.text,
                                  font=(self.theme.font_family, self.theme.font_size), bd=0, relief=tk.FLAT)
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=3)

        self.show_key_btn = tk.Button(self.kf, text="[*]", command=self.toggle_key_vis,
                                      bg=self.theme.surface_variant, fg=self.theme.text,
                                      font=(self.theme.font_family, self.theme.font_size - 1),
                                      activebackground=self.theme.surface, bd=0, relief=tk.FLAT, padx=6, cursor="hand2")
        self.show_key_btn.pack(side=tk.LEFT, padx=(0, 4))

        # Test IA Button
        self.verify_btn = tk.Button(self.win, text="[?] Probar Conexion / Estado de la IA", command=self.verify_connection,
                                    bg=self.theme.surface, fg=self.theme.accent,
                                    font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                    activebackground=self.theme.surface_variant, bd=0, relief=tk.FLAT, pady=4, cursor="hand2",
                                    highlightbackground=self.theme.border, highlightthickness=1)
        self.verify_btn.pack(fill=tk.X, padx=12, pady=(2, 4))

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(
            self.win, wrap=tk.WORD, state=tk.DISABLED,
            bg=self.theme.surface, fg=self.theme.text,
            font=(self.theme.font_family, self.theme.font_size + 1),
            bd=0, padx=12, pady=10, highlightthickness=1, highlightbackground=self.theme.border
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 6))

        # Configure Text Tags
        self._config_chat_tags()

        # Quick action chips
        chips_frame = tk.Frame(self.win, bg=self.theme.bg, padx=12, pady=2)
        chips_frame.pack(fill=tk.X)

        chips = [
            ("[JARVIS] Renombrar", lambda: self.insert_chip("/ren ")),
            ("[JARVIS] Crear", lambda: self.insert_chip("/create ")),
            ("[JARVIS] Archivos", lambda: self.send_custom("/list")),
            ("[!] Troll Mode", lambda: self.toggle_troll()),
            ("[?] Quien soy?", lambda: self.send_custom("Quien soy yo y cual es mi IP real?")),
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

        # Input Area
        inp = tk.Frame(self.win, bg=self.theme.bg, padx=12, pady=8)
        inp.pack(fill=tk.X)

        self.entry = tk.Entry(inp, bg=self.theme.entry_bg, fg=self.theme.text,
                              insertbackground=self.theme.text,
                              font=(self.theme.font_family, self.theme.font_size + 1),
                              bd=0, relief=tk.FLAT, highlightbackground=self.theme.border, highlightthickness=1)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.focus()

        self.send_btn = tk.Button(inp, text="Enviar >>", command=self.send_message,
                                  bg=self.theme.accent, fg=self.theme.accent_text,
                                  font=(self.theme.font_family, self.theme.font_size, "bold"),
                                  activebackground=self.theme.surface_variant,
                                  bd=0, relief=tk.FLAT, padx=14, cursor="hand2")
        self.send_btn.pack(side=tk.RIGHT)

        self._toggle_mode()
        self._append_system(
            f"Oie {self.user_info.username} ya llegue wei, se que estas en {self.user_info.public_ip} asi que apura tus preguntas pq ando jodida :v\n"
        )

        self.user_info.add_listener(self._on_ip_update)

    def _config_chat_tags(self):
        self.chat_area.tag_configure("user_hdr", foreground=self.theme.accent,
                                     font=(self.theme.font_family, self.theme.font_size, "bold"))
        self.chat_area.tag_configure("user_txt", foreground=self.theme.text,
                                     font=(self.theme.font_family, self.theme.font_size + 1))
        self.chat_area.tag_configure("bot_hdr",  foreground=self.theme.accent,
                                     font=(self.theme.font_family, self.theme.font_size, "bold"))
        self.chat_area.tag_configure("bot_txt",  foreground=self.theme.text,
                                     font=(self.theme.font_family, self.theme.font_size + 1))
        self.chat_area.tag_configure("system",   foreground=self.theme.text_dim,
                                     font=(self.theme.font_family, self.theme.font_size, "italic"))

    def _reapply_theme(self):
        if not self.win or not tk.Toplevel.winfo_exists(self.win):
            return
        self.win.configure(bg=self.theme.bg)
        self.win.attributes("-alpha", self.theme.opacity)
        self.title_lbl.configure(fg=self.theme.accent, bg=self.theme.surface,
                                 font=(self.theme.font_family, self.theme.font_size + 2, "bold"))
        self.header_status.configure(font=(self.theme.font_family, self.theme.font_size - 1))
        self.chat_area.configure(bg=self.theme.surface, fg=self.theme.text,
                                 font=(self.theme.font_family, self.theme.font_size + 1),
                                 highlightbackground=self.theme.border)
        self._config_chat_tags()
        self.entry.configure(bg=self.theme.entry_bg, fg=self.theme.text, insertbackground=self.theme.text,
                             font=(self.theme.font_family, self.theme.font_size + 1),
                             highlightbackground=self.theme.border)
        self.send_btn.configure(bg=self.theme.accent, fg=self.theme.accent_text,
                                font=(self.theme.font_family, self.theme.font_size, "bold"))
        self.verify_btn.configure(bg=self.theme.surface, fg=self.theme.accent,
                                  font=(self.theme.font_family, self.theme.font_size - 1, "bold"),
                                  highlightbackground=self.theme.border)
        for btn in getattr(self, "chip_btns", []):
            btn.configure(bg=self.theme.surface_variant, fg=self.theme.text_dim,
                          font=(self.theme.font_family, self.theme.font_size - 1))

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

    def clear_chat(self):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.configure(state=tk.DISABLED)
        self.history = []
        self._append_system(f"Chat reiniciado con {self.user_info.username} ({self.user_info.public_ip}). Apura con tus preguntas :v\n")

    def _toggle_mode(self):
        mode = self.mode_var.get()
        self.config["chat_mode"] = mode
        save_config(self.config)
        if mode == "api":
            self.kf.pack(fill=tk.X, padx=12, pady=(0, 4), before=self.verify_btn)
        else:
            self.kf.pack_forget()

    def _append_user(self, text):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"[USER] {self.user_info.username}:\n", "user_hdr")
        self.chat_area.insert(tk.END, f"{text}\n\n", "user_txt")
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def _append_bot(self, text):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "[BOCCHI] Bocchi-chan:\n", "bot_hdr")
        self.chat_area.insert(tk.END, f"{text}\n\n", "bot_txt")
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def _append_system(self, text):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"[SISTEMA] {text}\n", "system")
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)

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
                from transformers import pipeline
                self.parent.after(0, lambda: self._append_system("[..] Verificando modelo local SmolLM..."))
                if not self.local_pipe:
                    self.local_pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-135M-Instruct")
                self.parent.after(0, lambda: self._append_system("[+] Modelo local SmolLM listo para usarse offline!"))
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
            from transformers import pipeline
            if not self.local_pipe:
                self.parent.after(0, lambda: self._append_system("[..] Cargando SmolLM2 en memoria..."))
                self.local_pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-135M-Instruct")

            sys_prompt = self.get_system_prompt()
            msgs = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": text}
            ]
            out = self.local_pipe(msgs, max_new_tokens=70)
            reply = out[0]['generated_text'][-1]['content']
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

        # CMD
        for m in re.finditer(r'\[JARVIS:\s*CMD\s+["\']?([^"\'\n]+?)["\']?\]', reply_text, re.IGNORECASE):
            c = m.group(1).strip()
            ok, msg = self.jarvis.run_cmd(c)
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
        self.set_state("standing")
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
            "standing":     (STAND_FRAMES,  15, 50+random.randint(0,100),   0,     0),
            "walking":      (WALK_FRAMES,   5,  80+random.randint(0,120),   random.choice([-1,1])*speed, 0),
            "walk_back":    (WALK_BACK,     8,  40+random.randint(0,60),    random.choice([-1,1])*2, 0),
            "sitting":      (SIT_FRAMES,    10, 100+random.randint(0,150),  0,     0),
            "guitar":       (GUITAR_FRAMES, 8,  120+random.randint(0,120),  0,     0),
            "ceiling_idle": (LIE_FRAMES,    12, 100+random.randint(0,150),  0,     0),
            "blob":         (BLOB_FRAMES,   8,  60+random.randint(0,80),    0,     0),
            "ghost":        (GHOST_FRAMES,  10, 50+random.randint(0,80),    0,     0),
            "box":          (BOX_FRAMES,    18, len(BOX_FRAMES)*18,         0,     0),
            "falling":      (FALL_FRAMES,   2,  9999,                       random.randint(-2,2), 0),
            "kneel":        (KNEEL_FRAMES,  10, 40+random.randint(0,60),    0,     0),
            "carry":        (CARRY_FRAMES,  15, 80+random.randint(0,100),   0,     0),
            "depress":      (DEPRESS_FRAMES,15, 100+random.randint(0,100),  0,     0),
            "away":         (AWAY_FRAMES,   10, 60+random.randint(0,80),    0,     0),
            "climb_left":   (CLIMB_FRAMES,  6,  80+random.randint(0,120),   0,     0),
            "climb_right":  (CLIMB_FRAMES,  6,  80+random.randint(0,120),   0,     0),
            "ceiling_walk": (WALK_FRAMES,   5,  80+random.randint(0,120),   random.choice([-1,1])*speed, 0),
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
        pool = (["standing"]*3 + ["walking"]*4 + ["walk_back"] +
                ["sitting"]*3 + ["guitar"]*2 + 
                ["blob"]*2 + ["ghost"] + ["box"] + ["kneel"] +
                ["carry", "depress", "away"])
        self.set_state(random.choice(pool), surface=SURFACE_FLOOR)
        
    def choose_next_ceiling_state(self):
        if random.random() < 0.5:
            self.set_state("ceiling_walk", surface=SURFACE_CEILING)
            self.vel_x = random.choice([-1, 1]) * self.WALK_SPEED
            self.vel_y = 0
        else:
            self.set_state("ceiling_idle", surface=SURFACE_CEILING)
            self.vel_x = 0
            self.vel_y = 0

    def tick(self):
        if self._follow_cursor_enabled and WIN32_AVAILABLE and not self.dragging and not self.dragging_window:
            self._move_towards_cursor()
        if not self.dragging and not self.dragging_window:
            self.physics()
            self.animate()
        self.root.after(DELAY, self.tick)

    def physics(self):
        if self.state == "falling":
            self.gravity = min(self.gravity + 1, 20)
            self.y      += self.gravity
            self.x      += self.vel_x
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.gravity = 0
                self.set_state("standing", SURFACE_FLOOR)
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
                self.vel_x = abs(self.vel_x)
                self.flipped = False
        elif self.x >= self.wall_rx:
            self.x = self.wall_rx
            if random.random() < self.CLIMB_CHANCE:
                self._start_climb(SURFACE_WALL_R, going_up=True)
            else:
                self.vel_x = -abs(self.vel_x)
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
            self.set_state("standing", SURFACE_FLOOR)

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
                self.vel_x = abs(self.vel_x)
                self.flipped = False
        elif self.x >= self.wall_rx:
            self.x = self.wall_rx
            if random.random() < 0.5:
                self._start_climb(SURFACE_WALL_R, going_up=False)
            else:
                self.vel_x = -abs(self.vel_x)
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
            self.set_state("standing", SURFACE_FLOOR)

    def on_double_click(self, e):
        self.show_speech(self.get_random_speech())

    def on_right_click(self, e):
        t = self.theme_manager
        menu = tk.Menu(self.root, tearoff=0,
                       bg=t.surface, fg=t.text,
                       activebackground=t.accent,
                       activeforeground=t.accent_fg,
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
                             activeforeground=t.accent_fg,
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
                            activeforeground=t.accent_fg,
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
                             activeforeground=t.accent_fg,
                             font=(t.font_family, t.font_size))
        troll_menu.add_command(label="[~] Rickroll sorpresa (YouTube)", command=self.troll_rickroll)
        troll_menu.add_command(label="[!] Simular Pantallazo Azul (BSOD)", command=self.troll_bluescreen)
        troll_menu.add_command(label="[#] Simular Hacker (HackerTyper)", command=self.troll_hackertyper)
        troll_menu.add_command(label="[?] Error falso del sistema", command=self.troll_fake_error)
        troll_menu.add_command(label="[>] Sacudir ventana activa", command=self.troll_shake_window)
        if WIN32_AVAILABLE:
            troll_menu.add_command(label="[~] Mover cursor al azar", command=self.troll_move_mouse)
            troll_menu.add_separator()

            win_lbl = ("[#] Ventanas [AUTO ON] >>" if self._auto_win_enabled
                       else "[#] Ventanas >>")
            win_menu = tk.Menu(troll_menu, tearoff=0,
                               bg=t.surface, fg=t.text,
                               activebackground=t.accent,
                               activeforeground=t.accent_fg,
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
                                activeforeground=t.accent_fg,
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
        try:
            rx = self.root.winfo_rootx() + e.x
            ry = self.root.winfo_rooty() + e.y
            menu.tk_popup(rx, ry)
        finally:
            menu.grab_release()

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
        if self.chat_win and hasattr(self.chat_win, "update_troll_btn"):
            self.chat_win.update_troll_btn()
        if self.troll_mode:
            self.show_speech("¡MODO TROLL ACTIVADO! 7w7\nPrepárate para la anarquía...")
        else:
            self.show_speech("Modo Troll desactivado [OFF]\nYa me porto bien, soy tu JARVIS UwU")

    def troll_rickroll(self):
        try:
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            self.show_speech("¡RICKROLLEADO! (ノ^∇^)ノ\nNever gonna give you up~ 7w7")
        except Exception:
            pass

    def troll_bluescreen(self):
        try:
            webbrowser.open("https://geekprank.com/blue-screen-death/")
            self.show_speech("¡PANTALLAZO AZUL! D:\nSe murio Windows alv :v")
        except Exception:
            pass

    def troll_hackertyper(self):
        try:
            webbrowser.open("https://hackertyper.net/")
            self.show_speech("¡HACKEANDO LA NASA...! 7w7\n[STATUS: ACCESS GRANTED]")
        except Exception:
            pass

    def troll_shake_window(self):
        if not WIN32_AVAILABLE:
            return
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd or hwnd == self._own_hwnd():
            hwnd = WindowDragger.pick_random_window(exclude=self._own_hwnd())
        if not hwnd:
            return
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
            def do_shake(step=0):
                if step < 6:
                    dx = random.randint(-40, 40)
                    dy = random.randint(-25, 25)
                    win32gui.MoveWindow(hwnd, x + dx, y + dy, w, h, True)
                    self.root.after(45, lambda: do_shake(step + 1))
                else:
                    win32gui.MoveWindow(hwnd, x + random.randint(30, 80), y + random.randint(20, 60), w, h, True)
            self.show_speech("¡Terremoto en tus ventanas! (ง'̀-'́)ง")
            do_shake()
        except Exception:
            pass

    def troll_fake_error(self):
        title, msg = self.get_fake_error()
        self.show_speech("Jijiji... 7w7")
        self.root.after(400, lambda: messagebox.showerror(title, msg))

    def _troll_autonomous_tick(self):
        if self.troll_mode:
            actions = [
                self.troll_fake_error,
                self.troll_shake_window,
                self.troll_minimize,
                self.troll_move_mouse,
                self.troll_rickroll,
                self.troll_bluescreen,
                self.troll_hackertyper
            ]
            weights = [25, 25, 20, 10, 8, 6, 6]
            chosen = random.choices(actions, weights=weights, k=1)[0]
            try:
                chosen()
            except Exception:
                pass
        next_ms = random.randint(25000, 60000)
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
        self.show_speech("¡A mimir esa ventana! (-.-)zzZ" if ok else "No hay ventana que minimizar ._.")

    def _wait_click_then(self, action_fn, hint_msg):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 :v")
            return
        self.show_speech(hint_msg)
        self._pending_action = action_fn

        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.01)
        overlay.geometry(f"{self.sw}x{self.sh}+0+0")
        overlay.config(cursor="crosshair")

        def on_overlay_click(e):
            sx = e.x_root
            sy = e.y_root
            overlay.destroy()
            fn = self._pending_action
            self._pending_action = None
            self.root.after(80, lambda: fn(sx, sy) if fn else None)

        def on_escape(e):
            overlay.destroy()
            self._pending_action = None
            self.show_speech("Cancelado [OK]")

        overlay.bind("<ButtonPress-1>", on_overlay_click)
        overlay.bind("<Escape>", on_escape)
        overlay.focus_force()
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
        menu = tk.Menu(self.root, tearoff=0,
                       bg=t.surface, fg=t.text,
                       activebackground=t.accent,
                       activeforeground=t.accent_fg,
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
        if self.bubble_win:
            try:
                self.bubble_win.destroy()
            except Exception:
                pass
        if self.bubble_after:
            self.root.after_cancel(self.bubble_after)

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

        close_btn = tk.Label(header_frame, text="[x]", bg=t.surface, fg=t.text_subtle,
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
        bw_w = bw.winfo_width()
        bw_h = bw.winfo_height()

        bx = int(self.x) + SIZE // 2 - bw_w // 2
        bx = max(10, min(bx, self.sw - bw_w - 10))

        if self.y < 120:
            by = int(self.y) + SIZE + 10
        else:
            by = int(self.y) - bw_h - 12
        by = max(10, min(by, self.sh - bw_h - 10))

        bw.geometry(f"{bw_w}x{bw_h}+{bx}+{by}")
        self.bubble_win   = bw
        self.bubble_after = self.root.after(4500, self.destroy_bubble)

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
        self.root.after(random.randint(15000, 30000), self.random_speech_tick)

    def random_speech_tick(self):
        if random.random() < 0.4:
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