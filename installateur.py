import argparse
import ast
import os
import platform
import re
import shutil
import subprocess
import sys
import venv
from pathlib import Path

JEU = "Falling Light"
ROOT = Path(__file__).resolve().parent
REQUIREMENTS = ROOT / "requirements.txt"
DEPENDANCES_DEFAUT = ["ursina", "numpy", "pillow", "pygame"]

# modules tiers connus (nom d'import) : ceux-là sont couverts par requirements.txt
MODULES_TIERS = {"ursina", "panda3d", "direct", "numpy", "PIL", "pygame"}
DOSSIERS_IGNORES = {".venv", "venv", "__pycache__", ".git", "node_modules"}
PAQUETS = ["armes", "bot", "classe", "HUD", "map", "parametres"]      # dossiers qui doivent être des paquets
ATTENDUS = {
    ".": ["titanfall.py", "etat.py", "effets.py", "partie.py"],
    "armes": ["arme.py", "couteaux.py", "fusil.py", "grenade.py", "modeles.py", "pistolet.py",
              "shotgun.py", "smg.py", "sniper.py", "titan.py"],
    "bot": ["allie.py", "ennemie.py", "joueur.py", "modeles.py", "navigation.py", "pilote.py",
            "zombie_commun.py", "zombie_jour.py", "zombie_nuit.py"],
    "classe": ["choix_classe.py", "classe_1.py", "classe_2.py", "classe_3.py", "classe_4.py"],
    "HUD": ["hud.py"],
    "map": ["batch.py", "elements.py", "loot.py", "map.py"],
    "parametres": ["clavier.py", "config.json", "config.py", "graphismes.py", "options.py", "souris.py"],
    "server": ["server_client.py", "server_commun.py", "server_game.py"],
}


# ------------------------------------------------------------ affichage ---
def info(m): print(f"[INFO] {m}")
def ok(m): print(f"[OK] {m}")
def avertir(m): print(f"[ATTENTION] {m}")
def reparer_msg(m): print(f"[CORRIGÉ] {m}")
def erreur(m): print(f"[ERREUR] {m}")


def executer(cmd):
    print(">", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)


# ---------------------------------------------------------- prérequis ---
def verifier_python():
    v = sys.version_info
    if v < (3, 9):
        raise RuntimeError(f"Python 3.9 minimum requis (version actuelle : {v.major}.{v.minor}).")
    if v >= (3, 14):
        avertir(f"Python {v.major}.{v.minor} est très récent : si l'installation d'ursina/panda3d échoue, "
                "utilisez Python 3.10 à 3.13.")


def lire_dependances():
    if REQUIREMENTS.exists():
        deps = [l.split("#", 1)[0].strip() for l in REQUIREMENTS.read_text(encoding="utf-8").splitlines()]
        deps = [d for d in deps if d]
        if deps:
            return deps
    return list(DEPENDANCES_DEFAUT)


# ------------------------------------------- structure + réparations sûres ---
def trouver_dossier(nom):
    """Dossier du projet dont le nom correspond sans tenir compte de la casse (ex. Craft / craft)."""
    for d in ROOT.iterdir():
        if d.is_dir() and d.name.lower() == nom.lower():
            return d
    return None


def verifier_structure(reparer=True):
    manquants = []
    if not (ROOT / "titanfall.py").exists():
        raise FileNotFoundError("Impossible de trouver titanfall.py à côté de l'installateur.")

    # paquets : init.py -> __init__.py, __init__.py manquant
    for nom in PAQUETS + ["craft"]:
        d = trouver_dossier(nom) if nom == "craft" else ROOT / nom
        if d is None or not d.is_dir():
            manquants.append(f"dossier {nom}/")
            continue
        init, faute = d / "__init__.py", d / "init.py"
        if not init.exists():
            if faute.exists():
                if reparer:
                    faute.rename(init)
                    reparer_msg(f"{d.name}/init.py renommé en __init__.py")
                else:
                    avertir(f"{d.name}/init.py devrait s'appeler __init__.py")
            elif nom != "craft":
                if reparer:
                    init.write_text("", encoding="utf-8")
                    reparer_msg(f"{d.name}/__init__.py créé (vide)")
                else:
                    avertir(f"{d.name}/__init__.py manquant")
            else:
                manquants.append(f"{d.name}/__init__.py")

    for dossier, fichiers in ATTENDUS.items():
        base = ROOT if dossier == "." else ROOT / dossier
        manquants += [f"{dossier}/{f}" if dossier != "." else f for f in fichiers if not (base / f).exists()]
    if manquants:
        avertir("Fichiers attendus introuvables : " + ", ".join(manquants))
    else:
        ok("Structure du projet complète")


# ------------------------------------------------ analyse statique des imports ---
def fichiers_python():
    for p in ROOT.rglob("*.py"):
        parts = p.relative_to(ROOT).parts
        if any(x in DOSSIERS_IGNORES or x.startswith(".") for x in parts[:-1]):
            continue
        yield p


def analyser(reparer=True):
    """Cherche : erreurs de syntaxe, imports locaux introuvables, modules tiers non listés, dossiers à la mauvaise casse."""
    fichiers = sorted(fichiers_python())
    stems = {p.stem for p in fichiers}
    dossiers = {d.name for d in ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")}
    stdlib = getattr(sys, "stdlib_module_names", None)
    rapport = {"syntaxe": [], "import": [], "tiers": []}
    casse_usage = {}                    # dossier réel -> orthographes utilisées dans les imports
    corrections = {}                    # fichier -> [(ligne, top, pkg)]

    for f in fichiers:
        rel = f.relative_to(ROOT)
        try:
            arbre = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as e:
            rapport["syntaxe"].append(f"{rel} : {e}")
            continue
        for n in ast.walk(arbre):
            if isinstance(n, ast.ImportFrom) and n.level:                      # import relatif
                if n.module:
                    base = f.parent
                    for _ in range(n.level - 1):
                        base = base.parent
                    p = base.joinpath(*n.module.split("."))
                    if not (p.is_dir() or p.with_name(p.name + ".py").exists()):
                        rapport["import"].append(f"{rel}:{n.lineno} import relatif introuvable : .{n.module}")
                continue
            if isinstance(n, ast.ImportFrom):
                noms = [n.module]
            elif isinstance(n, ast.Import):
                noms = [a.name for a in n.names]
            else:
                continue
            for nom in noms:
                top = nom.split(".")[0]
                if (stdlib is not None and top in stdlib) or top in MODULES_TIERS:
                    continue
                if top in dossiers or (ROOT / f"{top}.py").is_file():
                    continue
                if f.parent.name == "server" and (f.parent / f"{top}.py").is_file():
                    continue                                                   # script lancé directement
                vrai = next((d for d in dossiers if d.lower() == top.lower()), None)
                if vrai:
                    casse_usage.setdefault(vrai, set()).add(top)
                elif (f.parent / f"{top}.py").is_file() and f.parent != ROOT:
                    pkg = ".".join(f.parent.relative_to(ROOT).parts)
                    corrections.setdefault(f, []).append((n.lineno, top, pkg))
                elif top in stems:
                    rapport["import"].append(f"{rel}:{n.lineno} « {top} » existe dans le projet mais pas à la racine")
                elif stdlib is not None:
                    rapport["tiers"].append(f"{rel}:{n.lineno} module « {top} » non installé / absent de requirements.txt")

    # --- casse des dossiers (Craft vs craft) : on s'aligne sur ce que le code importe
    for vrai, usages in casse_usage.items():
        if len(usages) == 1 and reparer:
            cible = next(iter(usages))
            (ROOT / vrai).rename(ROOT / cible)
            reparer_msg(f"dossier {vrai}/ renommé en {cible}/ (le code importe « {cible} »)")
        else:
            rapport["import"].append(f"dossier {vrai}/ importé avec une autre casse : {sorted(usages)} "
                                     "(sensible à la casse sous Linux)")

    # --- imports frères (ex. bot/zombie_jour.py : `from zombie_commun import ...`)
    for f, items in corrections.items():
        lignes = f.read_text(encoding="utf-8").splitlines(keepends=True)
        modifie = False
        for no, top, pkg in items:
            l = lignes[no - 1]
            m1 = re.sub(rf"^(\s*from\s+){re.escape(top)}(\s+import\b)", rf"\g<1>{pkg}.{top}\g<2>", l, count=1)
            m2 = re.sub(rf"^(\s*)import\s+{re.escape(top)}\s*$", rf"\g<1>from {pkg} import {top}\n", l, count=1)
            nouv = m1 if m1 != l else m2
            rel = f.relative_to(ROOT)
            if reparer and nouv != l:
                lignes[no - 1], modifie = nouv, True
                reparer_msg(f"{rel}:{no} -> {nouv.strip()}")
            else:
                rapport["import"].append(f"{rel}:{no} « {top} » est dans le même dossier : utiliser « {pkg}.{top} »")
        if modifie:
            shutil.copy2(f, f.with_name(f.name + ".bak"))
            f.write_text("".join(lignes), encoding="utf-8")
    return rapport


def afficher_rapport(rapport):
    titres = {"syntaxe": "Erreurs de syntaxe", "import": "Imports à corriger", "tiers": "Modules tiers non couverts"}
    total = 0
    for cle, lignes in rapport.items():
        if lignes:
            total += len(lignes)
            erreur(titres[cle]) if cle == "syntaxe" else avertir(titres[cle])
            for l in lignes:
                print("   -", l)
    if total == 0:
        ok("Aucun problème détecté dans les imports")
    return total


# ----------------------------------------------------------------- venv ---
def python_du_venv():
    d = ROOT / ".venv"
    return d / "Scripts" / "python.exe" if platform.system() == "Windows" else d / "bin" / "python"


def creer_venv():
    py, d = python_du_venv(), ROOT / ".venv"
    if d.exists() and not py.exists():
        info("Environnement virtuel cassé : recréation...")
        shutil.rmtree(d, ignore_errors=True)
    if not d.exists():
        info("Création de l'environnement virtuel...")
        try:
            venv.create(d, with_pip=True)
        except Exception as e:
            shutil.rmtree(d, ignore_errors=True)
            aide = " Sous Debian/Ubuntu : sudo apt install python3-venv" if platform.system() == "Linux" else ""
            raise RuntimeError(f"Création du venv impossible ({e}).{aide}")
        ok("Environnement virtuel créé")
    return py


def installer_dependances(py):
    info("Mise à jour de pip...")
    try:
        executer([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    except subprocess.CalledProcessError:
        avertir("Mise à jour de pip impossible (on continue)")
    deps = lire_dependances()
    info("Installation des dépendances : " + ", ".join(deps))
    cmd = [str(py), "-m", "pip", "install", "--disable-pip-version-check"]
    cmd += ["-r", str(REQUIREMENTS)] if REQUIREMENTS.exists() else deps
    try:
        executer(cmd)
    except subprocess.CalledProcessError:
        raise RuntimeError("Échec de pip. Vérifiez votre connexion Internet et votre version de Python (3.10 à 3.13 conseillée).")
    ok("Dépendances installées")


def verifier_installation(py):
    code = "import ursina, numpy, PIL, pygame; print('ursina', getattr(ursina, '__version__', '?'))"
    try:
        sortie = subprocess.check_output([str(py), "-c", code], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Les bibliothèques sont installées mais ne s'importent pas :\n" + (e.output or "")[-600:])
    ok("Bibliothèques vérifiées : " + sortie.strip().splitlines()[-1])


# --------------------------------------------------------------- icônes ---
def preparer_icones(py):
    """Convertit asset/icon.jpeg en icon.png (Linux) et icon.ico (Windows)."""
    src = ROOT / "asset" / "icon.jpeg"
    if not src.exists():
        return
    png, ico = src.with_name("icon.png"), src.with_name("icon.ico")
    if png.exists() and ico.exists():
        return
    code = ("import sys; from PIL import Image; im=Image.open(sys.argv[1]).convert('RGBA'); w,h=im.size; s=min(w,h);"
            "im=im.crop(((w-s)//2,(h-s)//2,(w+s)//2,(h+s)//2)).resize((256,256)); im.save(sys.argv[2]);"
            "im.save(sys.argv[3], sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])")
    try:
        subprocess.check_call([str(py), "-c", code, str(src), str(png), str(ico)])
        ok("Icônes générées (asset/icon.png, asset/icon.ico)")
    except subprocess.CalledProcessError:
        avertir("Génération des icônes impossible (le raccourci n'aura pas d'icône)")


# ---------------------------------------------------------------- bureau ---
def dossier_bureau():
    home, systeme = Path.home(), platform.system()
    cmd = None
    if systeme == "Windows":
        cmd = ["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"]
    elif systeme == "Linux":
        cmd = ["xdg-user-dir", "DESKTOP"]
    if cmd:
        try:
            out = Path(subprocess.check_output(cmd, text=True, timeout=15).strip())
            if out.is_dir() and out != home:
                return out
        except Exception:
            pass
    for nom in ("Desktop", "Bureau", "Escritorio"):
        if (home / nom).is_dir():
            return home / nom
    return home


# ------------------------------------------------------------ raccourcis ---
def raccourci_linux(py):
    icone = next((p for p in (ROOT / "asset" / "icon.png", ROOT / "asset" / "icon.jpeg") if p.exists()), None)
    contenu = (f"[Desktop Entry]\nVersion=1.0\nType=Application\nName={JEU}\n"
               f"Comment=Titanfall x Dying Light FPS\n"
               f'Exec="{py}" "{ROOT / "titanfall.py"}"\nPath={ROOT}\nTerminal=false\nCategories=Game;\n')
    if icone:
        contenu += f"Icon={icone}\n"
    cibles = [dossier_bureau() / f"{JEU}.desktop"]
    menu = Path.home() / ".local" / "share" / "applications"
    if menu.parent.exists():
        menu.mkdir(parents=True, exist_ok=True)
        cibles.append(menu / f"{JEU}.desktop")
    for f in cibles:
        f.write_text(contenu, encoding="utf-8")
        os.chmod(f, 0o755)
        try:                                   # GNOME : marque le lanceur comme fiable
            subprocess.run(["gio", "set", str(f), "metadata::trusted", "true"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass
        ok(f"Raccourci créé : {f}")


def raccourci_macos(py):
    f = dossier_bureau() / f"{JEU}.command"
    f.write_text(f'#!/bin/bash\ncd "{ROOT}"\n"{py}" "{ROOT / "titanfall.py"}"\n', encoding="utf-8")
    os.chmod(f, 0o755)
    ok(f"Lanceur créé : {f}")


def raccourci_windows(py):
    def q(s):                                  # chaîne PowerShell entre apostrophes
        return "'" + str(s).replace("'", "''") + "'"
    pyw = py.with_name("pythonw.exe")          # pas de console noire derrière le jeu
    cible = pyw if pyw.exists() else py
    lnk = dossier_bureau() / f"{JEU}.lnk"
    ico = ROOT / "asset" / "icon.ico"
    ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut({q(lnk)});"
          f"$s.TargetPath={q(cible)};$s.Arguments={q(chr(34) + str(ROOT / 'titanfall.py') + chr(34))};"
          f"$s.WorkingDirectory={q(ROOT)};")
    if ico.exists():
        ps += f"$s.IconLocation={q(ico)};"
    ps += "$s.Save()"
    subprocess.check_call(["powershell", "-NoProfile", "-Command", ps])
    ok(f"Raccourci créé : {lnk}")


def creer_raccourci(py):
    systeme = platform.system()
    info("Création du raccourci...")
    try:
        {"Windows": raccourci_windows, "Linux": raccourci_linux, "Darwin": raccourci_macos}[systeme](py)
    except KeyError:
        avertir(f"Système non supporté pour le raccourci : {systeme}")
    except Exception as e:
        avertir(f"Raccourci non créé ({e}). Lancez le jeu avec : \"{py}\" titanfall.py")


# ------------------------------------------------------------------ main ---
def main():
    parser = argparse.ArgumentParser(description=f"Installateur {JEU}")
    parser.add_argument("--diagnostic", action="store_true", help="analyse seulement, ne modifie rien")
    args = parser.parse_args()

    print("\n" + "=" * 60 + f"\nINSTALLATEUR {JEU.upper()}\n" + "=" * 60 + "\n")
    code = 0
    try:
        verifier_python()
        verifier_structure(reparer=not args.diagnostic)
        info("Analyse du code (imports, syntaxe)...")
        afficher_rapport(analyser(reparer=not args.diagnostic))
        if not args.diagnostic:
            py = creer_venv()
            installer_dependances(py)
            verifier_installation(py)
            preparer_icones(py)
            creer_raccourci(py)
            print()
            ok("Installation terminée avec succès !")
            print(f"\nLancez le jeu depuis le raccourci ({dossier_bureau()})\nou avec : \"{py}\" titanfall.py")
    except Exception as e:
        erreur(str(e))
        code = 1
    print()
    if sys.stdin and sys.stdin.isatty():
        input("Appuyez sur Entrée pour quitter...")
    return code


if __name__ == "__main__":
    sys.exit(main())