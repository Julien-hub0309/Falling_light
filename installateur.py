#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import venv
import platform
import subprocess
from pathlib import Path

JEU = "Falling Light"

DEPENDANCES = [
    "ursina",
    "numpy",
    "pillow",
]

ROOT = Path(__file__).resolve().parent


# ------------------------------------------------------------
# Utilitaires
# ------------------------------------------------------------

def info(msg):
    print(f"[INFO] {msg}")


def ok(msg):
    print(f"[OK] {msg}")


def erreur(msg):
    print(f"[ERREUR] {msg}")


def executer(cmd):
    print(">", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)


def est_dans_venv():
    return (
        hasattr(sys, "real_prefix")
        or sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    )


# ------------------------------------------------------------
# Bureau
# ------------------------------------------------------------

def dossier_bureau():
    home = Path.home()

    candidats = [
        home / "Desktop",
        home / "Bureau",
    ]

    for c in candidats:
        if c.exists():
            return c

    return home


# ------------------------------------------------------------
# Environnement virtuel
# ------------------------------------------------------------

def creer_venv():
    venv_dir = ROOT / ".venv"

    if not venv_dir.exists():
        info("Création de l'environnement virtuel...")
        venv.create(venv_dir, with_pip=True)
        ok("Environnement virtuel créé")

    systeme = platform.system()

    if systeme == "Windows":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"

    return python_exe


# ------------------------------------------------------------
# Dépendances
# ------------------------------------------------------------

def installer_dependances(python_exe):
    info("Mise à jour de pip...")

    try:
        executer([
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip"
        ])
    except Exception:
        pass

    info("Installation des dépendances...")

    try:
        executer([
            str(python_exe),
            "-m",
            "pip",
            "install",
            *DEPENDANCES
        ])

    except subprocess.CalledProcessError:

        if platform.system() == "Linux":

            info(
                "Tentative avec --break-system-packages..."
            )

            executer([
                str(python_exe),
                "-m",
                "pip",
                "install",
                "--break-system-packages",
                *DEPENDANCES
            ])

        else:
            raise

    ok("Dépendances installées")


# ------------------------------------------------------------
# Linux
# ------------------------------------------------------------

def raccourci_linux(python_exe):
    bureau = dossier_bureau()

    fichier = bureau / f"{JEU}.desktop"

    icon_png = ROOT / "asset" / "icon.jpeg"

    contenu = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={JEU}
Comment=Titanfall x Dying Light FPS
Exec="{python_exe}" "{ROOT / "titanfall.py"}"
Path={ROOT}
Terminal=false
Categories=Game;
"""

    if icon_png.exists():
        contenu += f"Icon={icon_png}\n"

    with open(fichier, "w", encoding="utf-8") as f:
        f.write(contenu)

    os.chmod(fichier, 0o755)

    ok(f"Raccourci créé : {fichier}")


# ------------------------------------------------------------
# macOS
# ------------------------------------------------------------

def raccourci_macos(python_exe):
    bureau = dossier_bureau()

    fichier = bureau / f"{JEU}.command"

    script = f'''#!/bin/bash
cd "{ROOT}"
"{python_exe}" "{ROOT / "titanfall.py"}"
'''

    with open(fichier, "w", encoding="utf-8") as f:
        f.write(script)

    os.chmod(fichier, 0o755)

    ok(f"Lanceur créé : {fichier}")


# ------------------------------------------------------------
# Windows
# ------------------------------------------------------------

def raccourci_windows(python_exe):

    try:
        from win32com.client import Dispatch

    except ImportError:

        info("Installation de pywin32...")

        executer([
            str(python_exe),
            "-m",
            "pip",
            "install",
            "pywin32"
        ])

        from win32com.client import Dispatch

    bureau = dossier_bureau()

    shortcut_path = str(
        bureau / f"{JEU}.lnk"
    )

    shell = Dispatch("WScript.Shell")

    shortcut = shell.CreateShortCut(shortcut_path)

    shortcut.TargetPath = str(python_exe)

    shortcut.Arguments = (
        f'"{ROOT / "titanfall.py"}"'
    )

    shortcut.WorkingDirectory = str(ROOT)

    icon_ico = ROOT / "assets" / "icon.ico"

    if icon_ico.exists():
        shortcut.IconLocation = str(icon_ico)

    shortcut.save()

    ok(f"Raccourci créé : {shortcut_path}")


# ------------------------------------------------------------
# Création raccourci
# ------------------------------------------------------------

def creer_raccourci(python_exe):

    systeme = platform.system()

    info("Création du raccourci...")

    if systeme == "Windows":
        raccourci_windows(python_exe)

    elif systeme == "Linux":
        raccourci_linux(python_exe)

    elif systeme == "Darwin":
        raccourci_macos(python_exe)

    else:
        erreur(f"Système non supporté : {systeme}")


# ------------------------------------------------------------
# Vérification des fichiers du jeu
# ------------------------------------------------------------

def verifier_jeu():

    principal = ROOT / "titanfall.py"

    if not principal.exists():
        raise FileNotFoundError(
            "Impossible de trouver titanfall.py"
        )


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print()
    print("=" * 60)
    print("INSTALLATEUR FALLING LIGHT")
    print("=" * 60)
    print()

    try:

        verifier_jeu()

        python_venv = creer_venv()

        installer_dependances(python_venv)

        creer_raccourci(python_venv)

        print()
        ok("Installation terminée avec succès !")
        print()

        print("Vous pouvez lancer le jeu depuis :")
        print(f"  {dossier_bureau()}")

    except Exception as e:

        erreur(str(e))

    print()
    input("Appuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()