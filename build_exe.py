"""
PyInstaller Packaging Script for Personal Local AI Workstation
Author: Hsini Mohamed (contact@hsini.dev | https://hsini.dev)
Compiles a single standalone .exe binary for zero-configuration client distribution.
"""

import os
import sys
import subprocess

def build():
    print("=" * 60)
    print("  [*] Compiling Personal_Local_AI_Workstation.exe ...")
    print("  [*] Author: Hsini Mohamed (https://hsini.dev)")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    launcher_path = os.path.join(base_dir, "launcher.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "Personal_Local_AI_Workstation",
        "--add-data", f"{os.path.join(base_dir, 'apps')};apps",
        "--add-data", f"{os.path.join(base_dir, 'core')};core",
        "--add-data", f"{os.path.join(base_dir, 'config')};config",
        "--add-data", f"{os.path.join(base_dir, 'workstation_env_audit.json')};.",
        "--clean",
        launcher_path
    ]

    print(f"[*] Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print("\n[+] SUCCESS! Executable built at: dist/Personal_Local_AI_Workstation.exe")

if __name__ == "__main__":
    build()
