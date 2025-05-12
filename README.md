[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Daviddotcoms/GazeTracker)

# Gaze Tracker App


This is a Python 3.9.11 project about a webcam-based-gaze-tracking. It gaves you an aproximate position of where the user is looking in real time.

## Instalation:
Install these dependencies:
- customtkinter
- pillow
- opencv
- numpy
- scikit learn
- mediapipe
- pyautogui

```shell
pip install -r requirements.txt
```

## Run the project:
```shell
python main.py
```

## Additional Content:
####  You have some comments about some functionalities that are not fully implemented. 
**<span style="color:rgb(206, 42, 42)">DO NOT TOUCH ANYTHING OF THAT.</span>**

<!-- Warning for a GITHUB ALERT -->
<!-- > [!WARNING]  -->
> I´m using the python version 3.9.11. Try to use the same if you have problems. But remember, the project would run correctly on with these versions:
> - Python 3.8
> - Python 3.9
> - Python 3.10
>
> That is all, have fun and leave your star on the project 👌

```

# ESTRUCTURA DE CARPETAS

GazeTrackerApp
├─ assets
│  └─ eye_icon.ico
├─ config.py
├─ core
│  ├─ gaze_heatmap.py
│  ├─ gaze_tracker.py
│  ├─ graphs
│  │  ├─ exponential_avg.py
│  │  └─ simple_avg_over_buffer.py
│  ├─ image_tracker.py
│  ├─ optimized_heatmap.py
│  └─ __init__.py
├─ forms
│  ├─ analysis_instructions_form.py
│  ├─ analyze_image_form.py
│  ├─ home_form.py
│  ├─ main_form_design.py
│  ├─ sequence_form.py
│  └─ __init__.py
├─ installer.py
├─ main.py
├─ README.md
├─ requirements.txt
├─ setup.py
└─ utils
   ├─ image_utils.py
   ├─ path_utils.py
   ├─ ui_utils.py
   ├─ window_utils.py
   └─ __init__.py
```
You must need to add a video to see, because this is not the final project.

![Architecture](https://github.com/user-attachments/assets/1dc405b6-0941-4884-9d94-f06af3c393a6)
