import os
import sys
import shutil

def create_shortcut():
    try:
        from win32com.client import Dispatch
        shell = Dispatch("WScript.Shell")
        desktop = shell.SpecialFolders("Desktop")

        shortcut = shell.CreateShortcut(os.path.join(desktop, "Gaze Tracker.lnk"))
        shortcut.TargetPath = os.path.join(sys.prefix, "GazeTracker.exe")
        shortcut.WorkingDirectory = sys.prefix
        shortcut.IconLocation = os.path.join(sys.prefix, "imagenes", "eye_icon.ico")
        shortcut.save()
    except Exception as e:
        print("Error creating shortcut:", e)

if __name__ == "__main__":
    if sys.argv[1] == "-install":
        create_shortcut()
