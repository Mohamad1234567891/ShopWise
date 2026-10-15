#!/usr/bin/env python3
"""ShopWise one-command setup script.

Creates the virtual environment, installs every dependency, sets up the
Playwright Chromium browser and downloads the auxiliary resources (NLTK data
and, optionally, Argos Translate models). Uses ONLY the Python standard
library, so nothing needs to be installed before running it.

Usage:
    python3 Setup.py                        # full automatic setup (asks one question)
    python3 Setup.py --install-translations # same, but installs Argos models without asking
    python3 Setup.py --skip-translations    # same, but skips Argos models entirely
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ------------------------------------------------------------------ paths
ROOT = Path(__file__).resolve().parent            # the ShopWise folder
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"

IS_WINDOWS = os.name == "nt"
BIN_DIR = VENV_DIR / ("Scripts" if IS_WINDOWS else "bin")
VENV_PYTHON = BIN_DIR / ("python.exe" if IS_WINDOWS else "python")

# Packages the app needs; each one is imported at the end as a sanity check.
PACKAGES_TO_VERIFY = [
    "ddgs", "playwright", "bs4", "httpx", "curl_cffi", "lxml",
    "nltk", "requests", "langdetect", "argostranslate", "PySide6",
]

# Optional Argos Translate models (used to translate reviews into English).
TRANSLATION_MODELS = [
    "translate-tr_en", "translate-de_en", "translate-es_en",
    "translate-fr_en", "translate-it_en", "translate-pt_en",
    "translate-nl_en", "translate-ar_en", "translate-ru_en",
    "translate-ja_en", "translate-ko_en", "translate-zh_en",
]

TOTAL_STEPS = 8

# ------------------------------------------------------------- utilities
def log(message=""):
    print(message, flush=True)


def step(number, message):
    print(f"\n[{number}/{TOTAL_STEPS}] {message}", flush=True)


def ok(message=""):
    print(f"        [OK] {message}", flush=True)


def warn(message):
    print(f"        [!] {message}", flush=True)


def fail(message):
    print(f"\n[!!] {message}", flush=True)
    sys.exit(1)


def run(command):
    """Run a command with its output streamed live to the terminal."""
    print(f"        $ {' '.join(str(part) for part in command)}", flush=True)
    return subprocess.run([str(part) for part in command], cwd=ROOT)


def venv_executable(name):
    """Path of a console script installed inside the virtual environment."""
    return BIN_DIR / (f"{name}.exe" if IS_WINDOWS else name)


def interpreter_version(path):
    try:
        result = subprocess.run(
            [str(path), "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
            capture_output=True, text=True, timeout=30,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def pick_interpreter():
    """Return (path, version) of the best available Python >= 3.10."""
    version = interpreter_version(sys.executable)
    if version and tuple(int(p) for p in version.split(".")) >= (3, 10):
        return sys.executable, version

    candidates = ("python3.14", "python3.13", "python3.12", "python3.11",
                  "python3.10", "python3", "python", "py")
    for name in candidates:
        path = shutil.which(name)
        if not path:
            continue
        version = interpreter_version(path)
        if version and tuple(int(p) for p in version.split(".")) >= (3, 10):
            return path, version
    return None, version

# ---------------------------------------------------------------- steps
def create_venv(python):
    if VENV_PYTHON.exists():
        log("        A virtual environment already exists -> reusing it.")
        return

    if VENV_DIR.exists():
        log("        The existing .venv looks incomplete -> removing it.")
        shutil.rmtree(VENV_DIR, ignore_errors=True)

    log(f"        Creating the virtual environment at {VENV_DIR}")
    result = subprocess.run(
        [python, "-m", "venv", str(VENV_DIR)], cwd=ROOT,
        capture_output=True, text=True,
    )
    if result.stdout.strip():
        print(result.stdout, end="", flush=True)
    if result.stderr.strip():
        print(result.stderr, end="", flush=True)

    if result.returncode != 0 or not VENV_PYTHON.exists():
        error = (result.stderr or "") + (result.stdout or "")
        if "ensurepip" in error:
            fail("The venv module could not install pip. On Debian/Ubuntu run:\n"
                 "     sudo apt install python3-venv\n"
                 "     and then run this script again.")
        fail("Could not create the virtual environment. Check the error above "
             "and make sure your Python installation includes venv and pip.")


def upgrade_pip():
    result = run([VENV_PYTHON, "-m", "pip", "install", "--upgrade", "pip"])
    if result.returncode != 0:
        warn("pip upgrade failed - continuing anyway.")


def install_requirements():
    if not REQUIREMENTS.exists():
        fail(f"{REQUIREMENTS} not found - make sure you are running Setup.py "
             "from inside the ShopWise folder.")
    result = run([VENV_PYTHON, "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    if result.returncode != 0:
        fail("Dependency installation failed. Check the output above and try "
             "again - a network connection is required.")


def install_playwright():
    script = venv_executable("playwright")
    command = [script] if script.exists() else [VENV_PYTHON, "-m", "playwright"]
    result = run(command + ["install", "chromium"])
    if result.returncode != 0:
        if not IS_WINDOWS:
            log("        On Linux, missing system libraries may be the cause.")
            log("        Try: sudo .venv/bin/playwright install-deps chromium")
        fail("Could not install the Chromium browser. See the messages above.")


def download_nltk_data():
    code = ("import nltk; "
            "nltk.download('punkt_tab', quiet=True); "
            "nltk.download('stopwords', quiet=True); "
            "nltk.download('vader_lexicon', quiet=True); "
            "print('NLTK resources ready')")
    result = run([VENV_PYTHON, "-c", code])
    if result.returncode != 0:
        warn("Could not download the NLTK data now - it will be downloaded "
             "automatically the first time ShopWise runs.")


def install_translations(args):
    want = True
    if args.skip_translations:
        want = False
        log("        Skipping translation models (--skip-translations).")
    elif args.install_translations:
        log("        Installing translation models (--install-translations).")
    else:
        print()
        print("        Argos Translate models let ShopWise translate product")
        print("        reviews into English before the sentiment analysis.")
        print("        Optional, but recommended (~12 small language packages).")
        try:
            answer = input("        Install them now? [Y/n] ").strip().lower()
        except EOFError:
            answer = ""
        want = answer not in ("n", "no")

    if not want:
        if not args.skip_translations:
            log("        Skipping - you can install them later, see the Manual "
                "Setup section of the README.")
        return

    argospm = venv_executable("argospm")
    if not argospm.exists():
        warn("argospm was not found in the environment - skipping translation "
             "models.")
        warn("Install them later with: argospm update && argospm install "
             + " ".join(TRANSLATION_MODELS))
        return

    if run([argospm, "update"]).returncode != 0:
        warn("Could not update the Argos package index - skipping translation "
             "models.")
        return

    result = run([argospm, "install"] + TRANSLATION_MODELS)
    if result.returncode != 0:
        warn("Some translation models could not be installed.")
        warn("Install them later with: argospm install "
             + " ".join(TRANSLATION_MODELS))
    else:
        ok("Translation models installed.")


def verify():
    failed = []
    for package in PACKAGES_TO_VERIFY:
        result = subprocess.run(
            [str(VENV_PYTHON), "-c", f"import {package}"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"        [OK]  {package}", flush=True)
        else:
            print(f"        [!!]  {package} could not be imported", flush=True)
            failed.append(package)

    if failed:
        fail("Some packages could not be imported: " + ", ".join(failed) + "\n"
             "     Activate the environment and run "
             "'pip install -r requirements.txt' again.")

    # Extra check: the CLI also imports 'rich', which is not listed in
    # requirements.txt. Only warn - do not fail the whole setup for it.
    rich = subprocess.run([str(VENV_PYTHON), "-c", "import rich"],
                          cwd=ROOT, capture_output=True)
    if rich.returncode != 0:
        warn("Heads-up: the CLI also imports 'rich', but it is not in "
             "requirements.txt.")
        warn("If the CLI later fails with 'No module named rich', activate the "
             "environment and run: pip install rich")
    else:
        print("        [OK]  rich (already available)", flush=True)


def final_summary(started):
    log()
    log("=" * 72)
    log("  Setup complete!")
    log(f"  Virtual environment: {VENV_DIR}")
    log("=" * 72)
    log()
    log("To use ShopWise, activate the environment first:")
    if IS_WINDOWS:
        log('    Command Prompt : .venv\\Scripts\\activate')
        log('    PowerShell     : .venv\\Scripts\\Activate.ps1')
    else:
        log('    bash/zsh       : source .venv/bin/activate')
        log('    fish           : source .venv/bin/activate.fish')
    log()
    log("Then run, for example:")
    log('    python -m src.CLI "iphone 17"    # search in the terminal (CLI mode)')
    log('    python -m src.CLI GUI            # open the graphical interface')
    log()
    log('NOTE: if running ShopWise later gives an error like')
    log('"ModuleNotFoundError: No module named ..." (for example ddgs), it')
    log("means the virtual environment is not active - activate it first.")
    log(f"(Setup finished in {time.perf_counter() - started:.1f}s)")

# ------------------------------------------------------------------ main
def main():
    parser = argparse.ArgumentParser(
        description="Automatically set up ShopWise: virtual environment, "
                    "dependencies, Playwright browser and resources.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--install-translations", action="store_true",
                       help="install the Argos translation models without asking")
    group.add_argument("--skip-translations", action="store_true",
                       help="skip the Argos translation models entirely")
    args = parser.parse_args()

    started = time.perf_counter()

    print("=" * 72, flush=True)
    print("  ShopWise automatic setup", flush=True)
    print("=" * 72, flush=True)
    log()
    if IS_WINDOWS:
        os_name = "Windows"
    elif sys.platform == "darwin":
        os_name = "macOS"
    else:
        os_name = "Linux"
    log(f"  Operating system : {os_name}")
    log(f"  Project folder   : {ROOT}")

    step(1, "Checking the Python interpreter")
    python, version = pick_interpreter()
    if python is None:
        fail("ShopWise needs Python 3.10 or newer and none was found.\n"
             "     Install Python 3.10+ from https://www.python.org/downloads/ "
             "and run this script again.")
    log(f"        Using {python} (Python {version})")

    step(2, "Creating the virtual environment (.venv)")
    create_venv(python)
    ok(f"Virtual environment ready at {VENV_DIR}")

    step(3, "Upgrading pip inside the environment")
    upgrade_pip()

    step(4, "Installing dependencies from requirements.txt")
    install_requirements()
    ok("Dependencies installed")

    step(5, "Installing the Playwright Chromium browser")
    install_playwright()
    ok("Chromium ready")

    step(6, "Downloading NLTK language resources")
    download_nltk_data()

    step(7, "Argos Translate models (optional)")
    install_translations(args)

    step(8, "Verifying the installation")
    verify()
    ok("All checks passed")

    final_summary(started)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!!] Setup interrupted by the user.", flush=True)
        sys.exit(130)
