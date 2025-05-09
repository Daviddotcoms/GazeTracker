from cx_Freeze import Executable, setup

# Archivos y carpetas a incluir
include_files = [
    "formularios/",
    "gaze_app_v4/",
    "util/",
    "imagenes/",
    "videos/",
    "config.py"
]

# Paquetes que necesita tu app
packages = [
    "customtkinter",
    "mediapipe",
    "numpy",
    "cv2",
    "PIL",
    "pyautogui",
    "sklearn",
    "matplotlib"
]

# Tabla de directorios MSI
directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("GazeTrackerProgramMenu", "ProgramMenuFolder", "GazeTracker|Gaze Tracker")
]

# Datos MSI como íconos, ProgId y variables (si se usaran)
msi_data = {
    "Directory": directory_table,
    "Icon": [
        ("IconId", "imagenes\\eye_icon.ico"),
    ]
}

# Configuración MSI
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-1234-1234-1234567890ab}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\\GazeTracker",
    "data": msi_data
}

# Configuración del build
build_exe_options = {
    "include_files": include_files,
    "packages": packages,
    "zip_include_packages": ["encodings"],
    "excludes": ["unittest", "PySide6", "shiboken6"],
    "optimize": 1,
    "include_msvcr": True
}

# Ejecutable con shortcut al menú inicio
executables = [
    Executable(
        script="main.py",
        base="Win32GUI",
        target_name="GazeTracker.exe",
        icon="imagenes\\eye_icon.ico",
        shortcut_name="Gaze Tracker",
        shortcut_dir="GazeTrackerProgramMenu"
    )
]

# Setup general
setup(
    name="GazeTracker",
    version="0.1",
    description="Web-cam based gaze tracker desktop application",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=executables
)
