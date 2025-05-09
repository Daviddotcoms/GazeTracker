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

Estructura de Carpetas

GazeTrackerApp
├─ config.py
├─ formularios
│  ├─ form_analizar_imagen.py
│  ├─ form_inicio.py
│  ├─ form_instrucciones_analisis.py
│  ├─ form_maestro_design.py
│  ├─ form_secuencia.py
│  └─ __init__.py
├─ gaze_app_v4
│  ├─ gaze_heatmap.py
│  ├─ gaze_tracker.py
│  ├─ graphs
│  │  ├─ exponential_avg.py
│  │  └─ simple_avg_over_buffer.py
│  ├─ image_tracker.py
│  ├─ optimized_heatmap.py
│  └─ __init__.py
├─ imagenes
│  └─ eye_icon.ico
├─ main.py
├─ pyproject.toml
├─ README.md
├─ requirements.txt
├─ util
│  ├─ util_imagenes.py
│  ├─ util_ventana.py
│  └─ __init__.py
└─ videos
   └─ video.mp4

```