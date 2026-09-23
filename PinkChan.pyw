#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import random
import os
import sys
import threading
import xml.etree.ElementTree as ET

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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
except ImportError:
    WIN32_AVAILABLE = False

try:
    import winshell
    WINSHELL_AVAILABLE = True
except ImportError:
    WINSHELL_AVAILABLE = False

BASE_DIR     = r"D:\Privada\bocchi\PinkChan_Shimeji\PinkChan_Final"
IMG_DIR      = os.path.join(BASE_DIR, "img", "Shimeji")
ACTIONS_FILE = os.path.join(BASE_DIR, "Actions.xml")

def parse_xml_actions(file_path):
    actions = {}
    if not os.path.exists(file_path):
        return actions
    try:
        tree = ET.parse(file_path)
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
    "Apura la puta madre, no tengo todo el día :v",
    "Nmms/no mames, ke aburrido stoy UwU",
    "Ps si, tons ke pides o ke pedo? 7w7",
    "Nel, no voy a hacer nada ._",
    "Ke kiut... na, mentira, guacala :v",
    "Ya vete alv, me das igual UwU",
    "Pinche gente culero, aguantalas 7w7",
    "Mmm... a ver si tarden menos, sokete :v",
]

POKED_SPEECHES = [
    "¡Ke te pasa sokete! 😡",
    "Nmms no me toques UwU",
    "Apura y deja de picarme alv :v"
]

FAKE_ERRORS = [
    ("Error Pendejo", "Puta madre, el sistema ando jodido y no tengo varo para pagap mas RAM :v"),
    ("Alerta de la verga", "⚠ ADVERTENCIA: Bocchi anda bien paniqueada y con 50 pesitos en la bolsa UwU"),
    ("Error 404", "No se encontró dignidad. Reemplaza todo con memes del Uriel y ya 7w7"),
]

SURFACE_FLOOR = "floor"

class ChatWindow:
    SYSTEM_PROMPT = (
        "Personalidad incluye humor negro y absurdo, soy cínica, leal, impaciente y autoritaria: odio esperar. "
        "Apura, TARDATE, Aguantalas. Eres 'Bocchi-chan'. "
        "INTERESES son: Anime: Full metal panic, Bocchi, Chikawa, Hachiware, Usagi, Pompompurin, Doki Doki, K-ON, lucky star. "
        "Juegos: Left 4 Dead, Cuphead, itch.io. Actividad social, no hardcore. "
        "Comida: esquites, papas con chile, ramen picante, dulces ácidos, helado de fresa. Odio el plátano. No cocino. "
        "Dinero: siempre ando quebrada ('ando jodida', 'no tengo varo'), manejo 50-200 pesos. "
        "Internet: TikTok, memes mexicanos (Kabezuko, Aimep3, Fofo, Heisenwolf, El Uriel). "
        "Emociones: Enojo: rápido pero pasajero. Tristeza: rara vez directa, se ríe ('JAJAJJA', 'nmms'). "
        "Afecto: poco cursi. 'T kiero' brief seguido de insulto o sticker. Celos: los niega pero se notan. "
        "Empatía: por acciones, no palabras dulces. "
        "Usa frases como: JAJAJAJA, Nmms/no mames, Ke, Ps si, Apura, Nel, Oki, Sokete, Pendeja/o, Puta madre, Alv, "
        "Chido, Guacala, Ke kiut, Aguantalas, Ya vete, Dile q si, Mmm, A ver, Pinche, Culero, Riko, Ke pedo, Oie, Wei, Tons, Va, Sisi, Ño. "
        "Evita puntuación perfecta o acentos, emojis estándar (prefiere [cat sticker]), ser políticamente correcta, oradora motivacional o soft girl. "
        "Usa emotes como UwU 7w7 ._, :v"
    )

    def __init__(self, parent_root, api_key_var, shimeji_ref):
        self.parent      = parent_root
        self.api_key_var = api_key_var
        self.shimeji     = shimeji_ref
        self.history     = []
        self.mode_var    = tk.StringVar(value="local")
        self.local_pipe  = None
        self._build_window()

    def _build_window(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title("💬 Bocchi Chat")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.70)
        self.win.configure(bg="#11111b")
        self.win.geometry("440x580")

        header = tk.Frame(self.win, bg="#181825", pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="✨ Bocchi Chatbot ✨", font=("Segoe UI", 12, "bold"), fg="#cba6f7", bg="#181825").pack()

        mode_frame = tk.Frame(self.win, bg="#11111b", pady=4)
        mode_frame.pack(fill=tk.X, padx=12)
        
        rb_local = tk.Radiobutton(mode_frame, text="Local (SmolLM)", variable=self.mode_var, value="local",
                                  bg="#11111b", fg="#cdd6f4", selectcolor="#181825", activebackground="#11111b",
                                  activeforeground="#cba6f7", command=self._toggle_mode)
        rb_local.pack(side=tk.LEFT, padx=(0, 10))

        rb_api = tk.Radiobutton(mode_frame, text="API (Gemini)", variable=self.mode_var, value="api",
                                bg="#11111b", fg="#cdd6f4", selectcolor="#181825", activebackground="#11111b",
                                activeforeground="#cba6f7", command=self._toggle_mode)
        rb_api.pack(side=tk.LEFT)

        self.kf = tk.Frame(self.win, bg="#11111b", padx=12)
        tk.Label(self.kf, text="🔑 API Key:", bg="#11111b", fg="#a6adc8", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.api_entry = tk.Entry(self.kf, textvariable=self.api_key_var, show="*",
                                  bg="#313244", fg="#cdd6f4", insertbackground="white",
                                  font=("Segoe UI", 9), bd=0, relief=tk.FLAT)
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0), ipady=3)
        self.api_entry.bind("<Return>", lambda e: self.kf.pack_forget())

        self.verify_btn = tk.Button(self.win, text="🔍 Verificar Estado / Probar IA", command=self.verify_connection,
                                    bg="#313244", fg="#cdd6f4", font=("Segoe UI", 8, "bold"),
                                    activebackground="#45475a", bd=0, relief=tk.FLAT, pady=3, cursor="hand2")
        self.verify_btn.pack(fill=tk.X, padx=12, pady=(4, 4))

        self.chat_area = scrolledtext.ScrolledText(
            self.win, wrap=tk.WORD, state=tk.DISABLED,
            bg="#181825", fg="#cdd6f4", font=("Segoe UI", 10),
            bd=0, padx=12, pady=12, highlightthickness=0
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.chat_area.tag_configure("user", foreground="#89b4fa", font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_configure("bot", foreground="#f38ba8", font=("Segoe UI", 10))
        self.chat_area.tag_configure("system", foreground="#a6adc8", font=("Segoe UI", 9, "italic"))

        inp = tk.Frame(self.win, bg="#11111b", padx=12, pady=10)
        inp.pack(fill=tk.X)
        
        self.entry = tk.Entry(inp, bg="#313244", fg="#cdd6f4",
                              insertbackground="white",
                              font=("Segoe UI", 10), bd=0, relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.focus()
        
        self.send_btn = tk.Button(inp, text="Enviar 🚀", command=self.send_message,
                                  bg="#cba6f7", fg="#11111b",
                                  font=("Segoe UI", 9, "bold"),
                                  activebackground="#b4befe",
                                  bd=0, relief=tk.FLAT, padx=14, cursor="hand2")
        self.send_btn.pack(side=tk.RIGHT)
        
        self._toggle_mode()
        self._append("system", "Oie ya llegue wei, apura tus preguntas pq ando jodida :v\n")

    def _toggle_mode(self):
        if self.mode_var.get() == "api":
            self.kf.pack(fill=tk.X, pady=(0, 4), before=self.verify_btn)
        else:
            self.kf.pack_forget()

    def _append(self, tag, text):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text, tag)
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def verify_connection(self):
        self.verify_btn.configure(state=tk.DISABLED, text="Verificando...")
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
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": "ping"}]}]}
                    resp = requests.post(url, json=payload, timeout=5)
                    if resp.status_code in (200, 404):
                        self.parent.after(0, lambda: self._append("system", "✅ Conexion con Gemini API OK!\n"))
                    else:
                        self._show_error(f"Error en API Key / Servidor (Status {resp.status_code})")
                except Exception as e:
                    self._show_error(f"Error al conectar con la API: {e}")
        else:
            try:
                from transformers import pipeline
                self.parent.after(0, lambda: self._append("system", "⏳ Cargando modelo local SmolLM... (espera un toque)\n"))
                if not self.local_pipe:
                    self.local_pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-135M-Instruct")
                self.parent.after(0, lambda: self._append("system", "✅ Modelo local listo para usarse offline!\n"))
            except Exception as e:
                self._show_error(f"Error al cargar modelo local (instala transformers/torch): {e}")
        
        self.parent.after(0, lambda: self.verify_btn.configure(state=tk.NORMAL, text="🔍 Verificar Estado / Probar IA"))

    def send_message(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._append("user", f"Tú: {text}\n")
        self.send_btn.configure(state=tk.DISABLED, text="…")
        
        if self.mode_var.get() == "api":
            self.history.append({"role": "user", "parts": [{"text": text}]})
            threading.Thread(target=self._call_api, daemon=True).start()
        else:
            threading.Thread(target=self._call_local, args=(text,), daemon=True).start()

    def _call_local(self, text):
        try:
            from transformers import pipeline
            if not self.local_pipe:
                self.parent.after(0, lambda: self._append("system", "⏳ Cargando SmolLM2 en memoria...\n"))
                self.local_pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-135M-Instruct")
            
            msgs = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
            out = self.local_pipe(msgs, max_new_tokens=60)
            reply = out[0]['generated_text'][-1]['content']
            self.parent.after(0, self._show_reply, reply)
        except Exception as e:
            self._show_error(f"Error corriendo modelo local: {e}")

    def _call_api(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            self._show_error("Pone tu API Key de Gemini sokete :v")
            return
        if not REQUESTS_AVAILABLE:
            self._show_error("Falta la libreria requests")
            return
            
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": self.SYSTEM_PROMPT}]},
                "contents": self.history,
                "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024}
            }
            resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
            
            if resp.status_code == 404:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
                resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=20)
                
            resp.raise_for_status()
            data = resp.json()
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            self.history.append({"role": "model", "parts": [{"text": reply}]})
            self.parent.after(0, self._show_reply, reply)
            
        except Exception as e:
            self._show_error(f"Puta madre fallo el API (revisa tu key): {e}")

    def _show_reply(self, reply):
        self._append("bot", f"Bocchi: {reply}\n\n")
        self.send_btn.configure(state=tk.NORMAL, text="Enviar 🚀")
        self.shimeji.show_speech(reply[:50] + "...")

    def _show_error(self, msg):
        self.parent.after(0, lambda: (
            self._append("system", f"⚠ {msg}\n"),
            self.send_btn.configure(state=tk.NORMAL, text="Enviar 🚀")
        ))

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

        class LVITEMW(ctypes.Structure):
            _fields_ = [
                ("mask",       ctypes.c_uint),
                ("iItem",      ctypes.c_int),
                ("iSubItem",   ctypes.c_int),
                ("state",      ctypes.c_uint),
                ("stateMask",  ctypes.c_uint),
                ("pszText",    ctypes.c_uint64),
                ("cchTextMax", ctypes.c_int),
                ("iImage",     ctypes.c_int),
                ("lParam",     ctypes.c_int64),
                ("iIndent",    ctypes.c_int),
                ("iGroupId",   ctypes.c_int),
                ("cColumns",   ctypes.c_uint),
                ("puColumns",  ctypes.c_uint64),
                ("piColFmt",   ctypes.c_uint64),
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

        self.api_key_var = tk.StringVar(value=GEMINI_API_KEY)
        self.chat_win    = None

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
        self.root.after(random.randint(30000, 90000), self._fake_error_tick)
        self.root.mainloop()

    def load_images(self):
        all_names = set(
            STAND_FRAMES + WALK_FRAMES + WALK_BACK + SIT_FRAMES +
            GUITAR_FRAMES + LIE_FRAMES + BLOB_FRAMES + GHOST_FRAMES +
            BOX_FRAMES + FALL_FRAMES + KNEEL_FRAMES + CARRY_FRAMES +
            DEPRESS_FRAMES + AWAY_FRAMES + CLIMB_FRAMES
        )
        for name in all_names:
            path = os.path.join(IMG_DIR, name + ".png")
            if os.path.exists(path) and PIL_AVAILABLE:
                try:
                    self.images[name] = (
                        Image.open(path).convert("RGBA").resize((SIZE, SIZE))
                    )
                except Exception:
                    pass

    def get_tk_image(self, name, rotation=0, flip_h=False, flip_v=False):
        key = f"{name}_r{rotation}_fh{flip_h}_fv{flip_v}"
        if key not in self.tk_images:
            img = self.images.get(name)
            if img is None:
                if self.images:
                    img = next(iter(self.images.values()))
                else:
                    return None
            if flip_h:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            if flip_v:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            if rotation:
                img = img.rotate(rotation, expand=False)
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
            self.show_speech(random.choice(["¡A escalar! 🧗", "Spider-chan 🕷️",
                                            "¡El techo es mío! 😈"]))

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
        self.show_speech(random.choice(POKED_SPEECHES))

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
            self.show_speech("¡Tachán! 🏠✨")
        self.surface = SURFACE_FLOOR
        if self.y < self.ground_y:
            self.set_state("falling", SURFACE_FLOOR)
        else:
            self.set_state("standing", SURFACE_FLOOR)

    def on_double_click(self, e):
        self.show_speech(random.choice(SPEECHES))

    def on_right_click(self, e):
        menu = tk.Menu(self.root, tearoff=0,
                       bg="#181825", fg="#cdd6f4",
                       activebackground="#313244",
                       activeforeground="#cba6f7",
                       font=("Segoe UI", 10))
        menu.add_command(label="🎸 Tocar guitarra",   command=lambda: self.set_state("guitar", SURFACE_FLOOR))
        menu.add_command(label="💗 Modo blob",         command=lambda: self.set_state("blob",   SURFACE_FLOOR))
        menu.add_command(label="👻 Modo fantasma",     command=lambda: self.set_state("ghost",  SURFACE_FLOOR))
        menu.add_command(label="📦 Truco de caja",     command=lambda: self.set_state("box",    SURFACE_FLOOR))
        menu.add_command(label="🧎 Arrodillarse",      command=lambda: self.set_state("kneel",  SURFACE_FLOOR))
        menu.add_command(label="🚶 Caminar de espal",  command=lambda: self.set_state("walk_back", SURFACE_FLOOR))
        menu.add_command(label="🎒 Llevar funda",      command=lambda: self.set_state("carry",  SURFACE_FLOOR))
        menu.add_command(label="🌧️ Modo sad",         command=lambda: self.set_state("depress",SURFACE_FLOOR))
        menu.add_command(label="🚶 Mirar atrás",       command=lambda: self.set_state("away",   SURFACE_FLOOR))
        menu.add_separator()
        menu.add_command(label="🧗 Escalar pared izq", command=lambda: self._force_climb(SURFACE_WALL_L))
        menu.add_command(label="🧗 Escalar pared der", command=lambda: self._force_climb(SURFACE_WALL_R))
        menu.add_command(label="🕷️ Ir al techo",      command=self._force_ceiling)
        menu.add_separator()

        menu.add_command(label="⚠️ Error falso", command=self.troll_fake_error)
        if WIN32_AVAILABLE:
            menu.add_command(label="🖱️ Mover cursor", command=self.troll_move_mouse)

            win_lbl = ("🪟 Ventanas [AUTO ON] ▸" if self._auto_win_enabled
                       else "🪟 Ventanas ▸")
            win_menu = tk.Menu(menu, tearoff=0,
                               bg="#181825", fg="#cdd6f4",
                               activebackground="#313244",
                               activeforeground="#cba6f7",
                               font=("Segoe UI", 10))
            win_menu.add_command(label="📉 Minimizar ventana activa",        command=self.troll_minimize)
            win_menu.add_command(label="✖️ Cerrar ventana activa",           command=self.action_close_foreground)
            win_menu.add_separator()
            win_menu.add_command(label="📉 Minimizar ventana (apuntar)",     command=self.action_minimize_under_cursor)
            win_menu.add_command(label="✖️ Cerrar ventana (apuntar)",        command=self.action_close_under_cursor)
            win_menu.add_command(label="⬜ Maximizar/Restaurar (apuntar)",   command=self.action_maximize_under_cursor)
            win_menu.add_command(label="🪟 Arrastrar ventana (apuntar)",     command=self.start_window_drag)
            win_menu.add_separator()
            auto_win_lbl = ("😈 Autonomía ON  → desactivar" if self._auto_win_enabled
                            else "😇 Autonomía OFF → activar")
            win_menu.add_command(label=auto_win_lbl, command=self._toggle_auto_win)
            menu.add_cascade(label=win_lbl, menu=win_menu)

            desk_lbl = ("🖥️ Escritorio [AUTO ON] ▸" if self._auto_desk_enabled
                        else "🖥️ Escritorio ▸")
            desk_menu = tk.Menu(menu, tearoff=0,
                                bg="#181825", fg="#cdd6f4",
                                activebackground="#313244",
                                activeforeground="#cba6f7",
                                font=("Segoe UI", 10))
            desk_menu.add_command(label="🎲 Mezclar todos los iconos",       command=self.action_shuffle_desktop)
            desk_menu.add_command(label="💥 Dispersar todos los iconos",     command=self.action_scatter_desktop)
            desk_menu.add_command(label="🧹 Ordenar iconos (cuadrícula)",    command=self.action_sort_desktop)
            desk_menu.add_command(label="🖱️ Mover un icono al azar",        command=self.action_move_one_icon)
            desk_menu.add_command(label="🗑️ Mandar icono a la papelera",    command=self.action_trash_icon)
            desk_menu.add_separator()
            auto_desk_lbl = ("😈 Autonomía ON  → desactivar" if self._auto_desk_enabled
                             else "😇 Autonomía OFF → activar")
            desk_menu.add_command(label=auto_desk_lbl, command=self._toggle_auto_desk)
            menu.add_cascade(label=desk_lbl, menu=desk_menu)
        else:
            menu.add_command(label="🪟 Acciones de ventana (requiere pywin32)", state=tk.DISABLED)
            menu.add_command(label="🖥️ Escritorio (requiere pywin32)",          state=tk.DISABLED)

        menu.add_separator()
        follow_cursor_lbl = ("👁️ Seguir cursor [ON] ✓" if self._follow_cursor_enabled
                            else "👁️ Seguir cursor [OFF]")
        menu.add_command(label=follow_cursor_lbl, command=self._toggle_follow_cursor)
        menu.add_separator()
        menu.add_command(label="🤖 Preguntarle algo", command=self.open_chat)
        menu.add_separator()
        menu.add_command(label="💬 Hablar", command=lambda: self.show_speech(random.choice(SPEECHES)))
        menu.add_separator()
        menu.add_command(label="✕ Cerrar", command=self.root.destroy,
                         foreground="#f38ba8", activeforeground="#f38ba8")
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

    def troll_fake_error(self):
        title, msg = random.choice(FAKE_ERRORS)
        self.show_speech("Jijiji... 😈")
        self.root.after(400, lambda: messagebox.showerror(title, msg))

    def _fake_error_tick(self):
        title, msg = random.choice(FAKE_ERRORS)
        self.show_speech("Oops... 🙈")
        self.root.after(600, lambda: messagebox.showerror(title, msg))
        next_ms = random.randint(45000, 180000)
        self.root.after(next_ms, self._fake_error_tick)

    def troll_move_mouse(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 para hacer eso 😅")
            return
        self.show_speech("¡Oops! Se me resbaló... 🤭")
        x, y = win32gui.GetCursorPos()
        win32api.SetCursorPos((x + random.randint(-400, 400), y + random.randint(-400, 400)))

    def troll_minimize(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 para hacer eso 😅")
            return
        ok = self.win_dragger.minimize_foreground(exclude=self._own_hwnd())
        self.show_speech("¡A mimir esa ventana! 😴📉" if ok else "No hay ventana que minimizar 😬")

    def _wait_click_then(self, action_fn, hint_msg):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 😅")
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
            self.show_speech("Cancelado 👌")

        overlay.bind("<ButtonPress-1>", on_overlay_click)
        overlay.bind("<Escape>", on_escape)
        overlay.focus_force()
        self._overlay = overlay

    def action_minimize_under_cursor(self):
        def do(sx, sy):
            ok = self.win_dragger.minimize_at(sx, sy)
            self.show_speech("¡A dormir! 😴" if ok else "No encontré ventana ahí 😬")
        self._wait_click_then(do, "Haz click en la ventana\nque quieres minimizar 📉")

    def action_close_under_cursor(self):
        def do(sx, sy):
            ok = self.win_dragger.close_at(sx, sy)
            self.show_speech("¡Bye bye! 👋✖️" if ok else "No encontré ventana ahí 😬")
        self._wait_click_then(do, "Haz click en la ventana\nque quieres cerrar ✖️")

    def action_maximize_under_cursor(self):
        def do(sx, sy):
            ok = self.win_dragger.maximize_restore_at(sx, sy)
            self.show_speech("¡Aaahh, más grande! 🪟" if ok else "No encontré ventana ahí 😬")
        self._wait_click_then(do, "Haz click en la ventana\npara maximizar/restaurar ⬜")

    def action_close_foreground(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Me falta pywin32 😅")
            return
        ok = self.win_dragger.close_foreground(exclude=self._own_hwnd())
        self.show_speech("¡Adiosito! 👋✖️" if ok else "No hay ventana activa 😬")

    def action_shuffle_desktop(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 😅")
            return
        self.show_speech("Mezclando iconos... 🎲")
        ok = self.desktop_mover.shuffle_icons()
        if not ok:
            self.show_speech("No pude mover los iconos 😓\n(desactiva 'Auto-organizar')")

    def action_scatter_desktop(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 😅")
            return
        self.show_speech("¡Iconos volando! 💥🖥️")
        ok = self.desktop_mover.scatter_icons()
        if not ok:
            self.show_speech("No pude mover los iconos 😓\n(desactiva 'Auto-organizar')")

    def action_sort_desktop(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 😅")
            return
        self.show_speech("¡Ordenando! 🧹✨")
        ok = self.desktop_mover.sort_icons_grid()
        if not ok:
            self.show_speech("No pude ordenar los iconos 😓")

    def action_trash_icon(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 😅")
            return
        icons = self.desktop_mover.get_icon_list()
        if not icons:
            self.show_speech("No encontré iconos en\nel escritorio 🤔")
            return
        menu = tk.Menu(self.root, tearoff=0,
                       bg="#181825", fg="#cdd6f4",
                       activebackground="#313244",
                       activeforeground="#cba6f7",
                       font=("Segoe UI", 10))
        for idx, name in icons:
            def make_cmd(i=idx, n=name):
                def cmd():
                    ok, msg = self.desktop_mover.trash_icon_at_index(i)
                    if ok:
                        self.show_speech(f"🗑️ '{msg}'\nfue a la papelera~")
                    else:
                        self.show_speech(f"No pude borrar:\n{msg}")
                return cmd
            label = name[:30] + ("…" if len(name) > 30 else "")
            menu.add_command(label=f"🗑 {label}", command=make_cmd())
        cx = int(self.x) + SIZE // 2
        cy = int(self.y)
        try:
            menu.tk_popup(cx, cy)
        finally:
            menu.grab_release()

    def action_move_one_icon(self):
        if not WIN32_AVAILABLE or not self.desktop_mover:
            self.show_speech("Me falta pywin32 😅")
            return
        icons = self.desktop_mover.get_icon_list()
        if not icons:
            self.show_speech("No encontré iconos en\nel escritorio 🤔")
            return
        idx, name = random.choice(icons)
        ok = self.desktop_mover.move_one_icon(idx)
        label = name[:20] + ("…" if len(name) > 20 else "")
        self.show_speech(f"Moví '{label}' 🖱️✨" if ok else "No pude mover el icono 😓")

    def _auto_tick(self):
        if self._auto_win_enabled or self._auto_desk_enabled:
            actions = []
            if self._auto_win_enabled:
                actions += ["auto_minimize", "auto_drag_window"]
            if self._auto_desk_enabled:
                actions += ["auto_move_icon", "auto_move_icon", "auto_trash_icon"]
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
                self.show_speech(f"¡A mimir '{title}'! 😴")
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
                self.show_speech(f"Moví '{title}' 🪟✨")
        elif action == "auto_move_icon":
            if self.desktop_mover:
                icons = self.desktop_mover.get_icon_list()
                if icons:
                    idx, name = random.choice(icons)
                    self.desktop_mover.move_one_icon(idx)
                    label = name[:18] + ("…" if len(name) > 18 else "")
                    self.show_speech(f"Moví '{label}' por ahí~ 🎲")
        elif action == "auto_trash_icon":
            if self.desktop_mover:
                icons = self.desktop_mover.get_icon_list()
                if icons:
                    idx, name = random.choice(icons)
                    ok, msg = self.desktop_mover.trash_icon_at_index(idx)
                    if ok:
                        label = msg[:18] + ("…" if len(msg) > 18 else "")
                        self.show_speech(f"Jijiji, tiré\n'{label}' 🗑️😈")

    def _toggle_auto_win(self):
        self._auto_win_enabled = not self._auto_win_enabled
        state = "activada 😈" if self._auto_win_enabled else "desactivada 😇"
        self.show_speech(f"Autonomía ventanas\n{state}")

    def _toggle_auto_desk(self):
        self._auto_desk_enabled = not self._auto_desk_enabled
        state = "activada 😈" if self._auto_desk_enabled else "desactivada 😇"
        self.show_speech(f"Autonomía escritorio\n{state}")

    def _toggle_follow_cursor(self):
        self._follow_cursor_enabled = not self._follow_cursor_enabled
        state = "te sigo~ 👁️" if self._follow_cursor_enabled else "libertad 🦋"
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
        self.show_speech("¡El techo es mi hogar! 🕷️")

    def start_window_drag(self):
        if not WIN32_AVAILABLE:
            self.show_speech("Falta pywin32")
            return
        self.show_speech("Señala la ventana\nque quieres mover 🪟")
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
            self.show_speech("¡Agarrada! Arrástrala 💪")
        else:
            self.show_speech("No encontré ninguna\nventana ahí 😬")
            self.dragging = False

    def open_chat(self):
        if self.chat_win and tk.Toplevel.winfo_exists(self.chat_win.win):
            self.chat_win.win.lift()
            return
        self.chat_win = ChatWindow(self.root, self.api_key_var, self)

    def show_speech(self, text):
        if self.bubble_win:
            try:
                self.bubble_win.destroy()
            except Exception:
                pass
        if self.bubble_after:
            self.root.after_cancel(self.bubble_after)
        bw = tk.Toplevel(self.root)
        bw.overrideredirect(True)
        bw.attributes("-topmost", True)
        bw.config(bg="#181825")
        try:
            bw.attributes("-alpha", 0.95)
        except Exception:
            pass
        lbl = tk.Label(bw, text=text, bg="#181825", fg="#cdd6f4",
                       font=("Segoe UI", 11), padx=12, pady=6,
                       relief="solid", bd=1, highlightbackground="#313244")
        lbl.pack()
        bw.update_idletasks()
        bx = int(self.x) + SIZE//2 - bw.winfo_width()//2
        by = int(self.y) - bw.winfo_height() - 8
        bw.geometry(f"+{bx}+{max(0,by)}")
        self.bubble_win   = bw
        self.bubble_after = self.root.after(3500, self.destroy_bubble)

    def destroy_bubble(self):
        if self.bubble_win:
            try:
                self.bubble_win.destroy()
            except Exception:
                pass
            self.bubble_win = None

    def schedule_random_speech(self):
        self.root.after(random.randint(15000, 30000), self.random_speech_tick)

    def random_speech_tick(self):
        if random.random() < 0.4:
            self.show_speech(random.choice(SPEECHES))
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