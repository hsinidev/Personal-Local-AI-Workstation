"""
Personal Local AI Workstation - Standalone Launcher & Client Runner
Author: Hsini Mohamed (https://hsini.dev | hsini.jk@gmail.com)
Zero-configuration one-click launcher for clients & production distribution.
"""

import os
import sys
import time
import socket
import webbrowser
import threading
import subprocess
import multiprocessing
from urllib.request import urlopen, Request

def get_base_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def check_and_start_ollama():
    print("[*] Checking local Ollama engine status...")
    try:
        req = Request("http://127.0.0.1:11434/api/tags", headers={"User-Agent": "WorkstationLauncher"})
        with urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                print("[+] Ollama engine is active and ready.")
                return True
    except Exception:
        pass

    print("[!] Ollama not responding on port 11434. Attempting background service startup...")
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time.sleep(2)
        print("[+] Ollama startup signal dispatched.")
        return True
    except Exception as e:
        print(f"[!] Note: Could not auto-start Ollama: {e}. Please ensure Ollama is installed.")
        return False

def run_server():
    base_dir = get_base_dir()
    serve_path = os.path.join(base_dir, "apps", "dashboard", "serve.py")
    
    # Fallback to relative path if not in _MEIPASS
    if not os.path.exists(serve_path):
        current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        serve_path = os.path.join(current_dir, "apps", "dashboard", "serve.py")

    if os.path.exists(serve_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("serve", serve_path)
        serve_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(serve_mod)
        if hasattr(serve_mod, "run"):
            serve_mod.run(port=3009)
        elif hasattr(serve_mod, "run_server"):
            serve_mod.run_server(port=3009)
    else:
        print(f"[!] Error: serve.py not found at {serve_path}")

def main():
    print("=" * 60)
    print("  [>] PERSONAL LOCAL AI WORKSTATION v2.0 (ADVANCED SUITE)")
    print("  [*] Developed by: Hsini Mohamed (hsini.jk@gmail.com)")
    print("  [*] Portfolio: https://hsini.dev")
    print("=" * 60)

    # 1. Check Ollama engine
    check_and_start_ollama()

    port = 3009
    url = f"http://localhost:{port}"

    # 2. Open default browser
    def open_browser():
        time.sleep(1.2)
        print(f"[+] Launching default browser to {url}...")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[!] Could not auto-open browser: {e}. Please visit {url} manually.")

    threading.Thread(target=open_browser, daemon=True).start()

    # 3. Start Server
    print(f"[*] Starting Local AI Workstation Dashboard on port {port}...")
    run_server()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
