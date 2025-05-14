from cx_Freeze import setup, Executable
import sys
import os

# Base para apps con GUI en Windows
base = "Win32GUI" if sys.platform == "win32" else None

# Archivos que deben incluirse en el build
include_files = [
    ("assets", "assets"),
    ("forms", "forms"),
    ("core", "core"),
    ("utils", "utils"),
    ("videos", "videos"),
    "config.py"
]

# Paquetes necesarios
packages = [
    "customtkinter",
    "PIL",
    "cv2",
    "numpy",
    "pyautogui",
    "sklearn",
    "matplotlib",
    "tkinter"
]

# Opciones de compilación
build_exe_options = {
    "packages": packages,
    "include_files": include_files,
    "include_msvcr": True,
    "optimize": 2
}

# Configuración para el MSI
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-1234-1234-1234567890ab}",  # Podés generar uno único si querés
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\\GazeTracker",
    "data": {
        "Shortcut": [
            (
                "DesktopShortcut",               # Atajo
                "DesktopFolder",                 # Lugar
                "Gaze Tracker",                  # Nombre visible
                "TARGETDIR",                     # Directorio del target
                "[TARGETDIR]GazeTracker.exe",    # Ejecutable
                None,                            # Argumentos
                "Gaze Tracker App",              # Descripción
                None,                            # Hotkey
                "IconId",                        # Icono
                None,                            # Trabajar en
                None,                            # Componente
                "TARGETDIR"                      # Directorio de instalación
            )
        ],
        "Icon": [
            ("IconId", os.path.join("assets", "eye_icon.ico"))
        ]
    }
}

# Ejecutable principal
executables = [
    Executable(
        script="main.py",
        base=base,
        target_name="GazeTracker.exe",
        icon="assets/eye_icon.ico",
        shortcut_name="Gaze Tracker",
        shortcut_dir="DesktopFolder"
    )
]

# Setup final
setup(
    name="GazeTracker",
    version="0.1",
    description="Gaze Tracker Desktop App",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=executables
)
