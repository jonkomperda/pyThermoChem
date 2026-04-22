#!/usr/bin/env python3
"""pyThermoChem launcher — installs missing dependencies then runs the app."""
import sys
import subprocess


# Standard library modules that could fail if Python is a minimal install
_STDLIB = [
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "csv",
    "json",
    "os",
    "sys",
]

# External dependencies (none currently, but add here as needed)
_EXTERNAL = {
}


def _try_import(modules):
    missing = []
    for mod in modules:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    return missing


def main():
    # Check stdlib
    missing_std = _try_import(_STDLIB)
    if missing_std:
        print("Missing standard library modules:")
        for mod in missing_std:
            print(f"  - {mod}")
        print("\nPython was installed without tkinter. Reinstall Python with Tk support.")
        print("  macOS:  brew install python-tk")
        print("  Ubuntu: sudo apt install python3-tk")
        print("  Windows: Reinstall Python, check 'tkinter' component")
        sys.exit(1)

    # Check external deps
    missing_ext = _try_import(list(_EXTERNAL.values()))
    if missing_ext:
        print("Missing packages. Installing...")
        pkgs = {mod: pkg for pkg, mod in _EXTERNAL.items() if mod in missing_ext}
        for mod in missing_ext:
            pkg = pkgs.get(mod, mod)
            print(f"  pip install {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + list(pkgs.values()))
        # Re-import to verify
        _try_import(missing_ext)

    # Launch app
    sys.path.insert(0, "src")
    from gui.app import App
    App().mainloop()


if __name__ == "__main__":
    main()
