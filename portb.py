#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
PINKCHAN SHIMEJI - PORT B FOR ANDROID (Android 8.0 Oreo to Android 15+)
=============================================================================
Este script permite correr y gestionar PinkChan Shimeji directamente en
dispositivos Android (Termux, Pydroid 3, QPython, UserLAnd o navegadores móviles).

Características:
  • Servidor web HTTP local optimizado para bajo consumo de batería y RAM.
  • Auto-lanzador en navegadores móviles (Chrome Android, Brave Android, etc.).
  • Integración con comandos de Termux / Linux (pkg, apt, pacman, hyfetch).
  • Detección de IP local para conectar desde la misma red Wi-Fi.
  • Compatible con Python 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14+
=============================================================================
"""

import os
import sys
import socket
import threading
import subprocess
import webbrowser
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
HOST = "0.0.0.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_local_ip():
    """Detecta la dirección IP local del dispositivo Android en la red Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class ShimejiHTTPHandler(SimpleHTTPRequestHandler):
    """Manejador HTTP que sirve portb.html por defecto."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html", "/portb"):
            self.path = "/portb.html"
        return super().do_GET()

    def log_message(self, format, *args):
        # Silenciar logs ruidosos para no saturar la terminal móvil
        pass

def open_android_browser(url):
    """Abre el navegador en Android priorizando Chrome y Brave (estrictamente no Edge)."""
    # 1. Intentar con intent de Android (Termux / am start)
    try:
        # Intentar con Chrome móvil
        res = subprocess.run(
            ["am", "start", "-a", "android.intent.action.VIEW", "-d", url, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"],
            capture_output=True
        )
        if res.returncode == 0:
            return True
    except Exception:
        pass

    try:
        # Intentar con Brave móvil
        res = subprocess.run(
            ["am", "start", "-a", "android.intent.action.VIEW", "-d", url, "-n", "com.brave.browser/com.google.android.apps.chrome.Main"],
            capture_output=True
        )
        if res.returncode == 0:
            return True
    except Exception:
        pass

    try:
        # Intent genérico de Android
        res = subprocess.run(
            ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
            capture_output=True
        )
        if res.returncode == 0:
            return True
    except Exception:
        pass

    # 2. Termux termux-open-url
    try:
        res = subprocess.run(["termux-open-url", url], capture_output=True)
        if res.returncode == 0:
            return True
    except Exception:
        pass

    # 3. xdg-open genérico
    try:
        res = subprocess.run(["xdg-open", url], capture_output=True)
        if res.returncode == 0:
            return True
    except Exception:
        pass

    # 4. Python webbrowser fallback
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False

def print_banner(local_ip, port):
    print("=" * 64)
    print("   🌸 PINKCHAN SHIMEJI - PORT B (ANDROID 8.0 - 15+) 🌸")
    print("=" * 64)
    print(f" [*] Servidor activo en tu Android:")
    print(f"     -> Local:   http://localhost:{port}/")
    print(f"     -> Red LAN: http://{local_ip}:{port}/")
    print(" [*] Skins incluidas: Konata, Bocchi, Monika, Natsuki, Sayori, Yuri")
    print(" [*] Física táctil, arrastre con inercia, escalado y chat drawer.")
    print("-" * 64)
    print(" Escribe comandos en esta consola o interactúa desde el navegador:")
    print("   • 'open'     -> Vuelve a abrir la ventana en el navegador")
    print("   • 'hyfetch'  -> Corre hyfetch en la consola")
    print("   • 'pkg'      -> Corre actualización de paquetes Termux (pkg update)")
    print("   • 'battery'  -> Consulta batería vía Termux-API")
    print("   • 'vibrate'  -> Prueba de vibración háptica")
    print("   • 'exit'     -> Detener el servidor")
    print("=" * 64)

def run_server():
    global PORT
    local_ip = get_local_ip()

    server = None
    for p in range(PORT, PORT + 20):
        try:
            server = ThreadingHTTPServer((HOST, p), ShimejiHTTPHandler)
            PORT = p
            break
        except OSError:
            continue

    if not server:
        print("[!] No se pudo abrir ningún puerto entre 8080 y 8100.")
        sys.exit(1)

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    url = f"http://localhost:{PORT}/"
    print_banner(local_ip, PORT)

    # Intentar abrir el navegador automáticamente tras 1 segundo
    def _delayed_open():
        time.sleep(1.2)
        open_android_browser(url)
    threading.Thread(target=_delayed_open, daemon=True).start()

    # Bucle interactivo en terminal móvil
    try:
        while True:
            cmd = input("\nPinkChan-Android> ").strip().lower()
            if not cmd:
                continue
            if cmd in ("exit", "quit", "q"):
                print("[*] Deteniendo servidor de PinkChan...")
                server.shutdown()
                break
            elif cmd == "open":
                open_android_browser(url)
                print(f"[+] Abriendo {url} en navegador móvil...")
            elif cmd in ("hyfetch", "neofetch"):
                subprocess.run("hyfetch 2>/dev/null || neofetch 2>/dev/null || uname -a", shell=True)
            elif cmd in ("pkg", "pkg update"):
                subprocess.run("pkg update -y", shell=True)
            elif cmd in ("battery", "bateria"):
                subprocess.run("termux-battery-status 2>/dev/null || cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo 'Batería: OK'", shell=True)
            elif cmd in ("vibrate", "vibrar"):
                subprocess.run("termux-vibrate -d 100 2>/dev/null || echo '[*] Vibración requerida vía Termux-API'", shell=True)
            elif cmd in ("ip", "lan"):
                print(f"IP Local: http://{local_ip}:{PORT}/")
            elif cmd in ("help", "?"):
                print("Comandos disponibles: open, hyfetch, pkg, battery, vibrate, ip, exit")
            else:
                # Ejecutar como comando shell de Termux
                subprocess.run(cmd, shell=True)
    except (KeyboardInterrupt, EOFError):
        print("\n[*] Saliendo de PinkChan Shimeji...")
        try:
            server.shutdown()
        except Exception:
            pass

if __name__ == "__main__":
    run_server()
