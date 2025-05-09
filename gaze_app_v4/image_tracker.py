import cv2
import time
import numpy as np
import collections
import tkinter as tk
import os
from datetime import datetime
from gaze_app_v4.gaze_tracker import gaze_tracker, startCalibration
from gaze_app_v4.optimized_heatmap import OptimizedGazeHeatmap

# Obtener la fecha del proyecto al inicio del módulo
FECHA_PROYECTO = datetime.now().strftime("%Y-%m-%d")
RESULTS_BASE_DIR = os.path.join("results", FECHA_PROYECTO)

def realizar_accion_i(image_path, screen_width, screen_height, last_gaze_points, window_name, output_dir):
    background_image = cv2.imread(image_path)
    if background_image is None:
        print(f"Error: No se pudo cargar la imagen desde {image_path}")
        return
    background_image = cv2.resize(background_image, (screen_width, screen_height))

    snapshot_heatmap = np.zeros((screen_height, screen_width), dtype=np.float32)
    for (_, pt) in last_gaze_points:
        x, y = pt
        if 0 <= x < screen_width and 0 <= y < screen_height:
            snapshot_heatmap[int(y), int(x)] += 1

    snapshot_heatmap = cv2.GaussianBlur(snapshot_heatmap, (81, 81), 0)
    snapshot_heatmap = cv2.normalize(snapshot_heatmap, None, 0, 255, cv2.NORM_MINMAX)
    snapshot_heatmap = snapshot_heatmap.astype(np.uint8)
    snapshot_colored = cv2.applyColorMap(snapshot_heatmap, cv2.COLORMAP_JET)

    heatmap_overlay = cv2.addWeighted(background_image, 0.5, snapshot_colored, 0.5, 0)
    timestamp = datetime.now().strftime("%H-%M-%S")
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(heatmap_overlay, f"Mapa de calor generado a las {timestamp}", 
                (20, screen_height - 20), font, 0.7, (255, 255, 255), 2)

    image_name = os.path.basename(image_path).split('.')[0]
    output_path = os.path.join(output_dir, f"heatmap_{image_name}_{timestamp}.jpg")
    cv2.imwrite(output_path, heatmap_overlay)

    # SHOW THE CAPTURE OF THE HEATMAP
    # temp_overlay = heatmap_overlay.copy()
    # cv2.putText(temp_overlay, "Imagen Guardada!", 
    #             (screen_width // 2 - 150, screen_height // 2), font, 1, (0, 255, 0), 3)
    # cv2.imshow(window_name, temp_overlay)
    # cv2.waitKey(1000)

def track_image(image_path, duration=8):
    root = tk.Tk()
    root.iconbitmap('./imagenes/eye_icon.ico')
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    
    background = cv2.imread(image_path)
    if background is None:
        print("Error al cargar la imagen:", image_path)
        return False
    background = cv2.resize(background, (screen_width, screen_height))
    
    heatmap = OptimizedGazeHeatmap(
        frame_shape=(screen_height, screen_width),
        blur_radius=70,
        decay_factor=0.98
    )
    
    gaze_history = collections.deque(maxlen=100)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return False

    window_name = "Image Tracking"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    show_heatmap = False
    heatmap_persistence = 30.0
    last_gaze_points = collections.deque()
    
    output_dir = RESULTS_BASE_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    last_i_time = time.time()
    start_time = time.time()
    
    esc_pressed = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        result, _ = gaze_tracker.process_gaze(frame)
        current_time = time.time()
        
        if result is not None:
            pointer = result
            gaze_history.append((current_time, pointer))
            heatmap.add_gaze_point(pointer[0], pointer[1])
            last_gaze_points.append((current_time, pointer))

        while last_gaze_points and (current_time - last_gaze_points[0][0] > heatmap_persistence):
            last_gaze_points.popleft()

        overlay = background.copy()
        
        # Puedes descomentar estas líneas si deseas dibujar la trayectoria:
        # if len(gaze_history) > 1:
        #     for i in range(1, len(gaze_history)):
        #         pt1 = gaze_history[i - 1][1]
        #         pt2 = gaze_history[i][1]
        #        cv2.line(overlay, pt1, pt2, (0, 255, 255), 2)
        #    if gaze_history:
        #        cv2.circle(overlay, gaze_history[-1][1], 10, (0, 0, 255), -1)
        
        heatmap_colored = heatmap.update()
        display_image = overlay.copy()
        
        if show_heatmap:
            display_image = heatmap.overlay_on_frame(display_image, heatmap_colored)
        
        cv2.imshow(window_name, display_image)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('h') or key == ord('H'):
            show_heatmap = not show_heatmap
        elif key == ord('r') or key == ord('R'):
            heatmap = OptimizedGazeHeatmap(
                frame_shape=(screen_height, screen_width),
                blur_radius=70,
                decay_factor=1
            )
        elif key == ord('a') or key == ord('A'):
            snapshot_heatmap = np.zeros((screen_height, screen_width), dtype=np.float32)
            for (_, pt) in last_gaze_points:
                x, y = pt
                if 0 <= x < screen_width and 0 <= y < screen_height:
                    snapshot_heatmap[int(y), int(x)] += 1
            snapshot_heatmap = cv2.GaussianBlur(snapshot_heatmap, (81, 81), 0)
            snapshot_heatmap = cv2.normalize(snapshot_heatmap, None, 0, 255, cv2.NORM_MINMAX)
            snapshot_heatmap = snapshot_heatmap.astype(np.uint8)
            snapshot_colored = cv2.applyColorMap(snapshot_heatmap, cv2.COLORMAP_JET)
            cv2.imshow("Heatmap Últimos 15 Segundos", snapshot_colored)
        elif key == ord('i') or key == ord('I'):
            realizar_accion_i(image_path, screen_width, screen_height, last_gaze_points, window_name, output_dir)
            last_i_time = current_time

        if current_time - last_i_time >= 6:
            realizar_accion_i(image_path, screen_width, screen_height, last_gaze_points, window_name, output_dir)
            last_i_time = current_time

        if key == 27 or current_time - start_time >= duration:
            esc_pressed = (key == 27)
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return esc_pressed

def mostrar_pantalla_bienvenida():
    import tkinter as tk
    from tkinter import font as tkfont
    global root_bienvenida
    root_bienvenida = tk.Tk()
    root_bienvenida.configure(bg='#fafafa')
    root_bienvenida.attributes('-fullscreen', True)
    root_bienvenida.title('Zona de Calibración')
    label_title = tk.Label(
        root_bienvenida, text="ZONA DE CALIBRACIÓN",
        font=tkfont.Font(family="Segoe UI", size=26, weight="bold"),
        fg="#F39200", bg="#fafafa"
    )
    label_title.place(relx=0.5, rely=0.45, anchor="center")
    label_desc = tk.Label(
        root_bienvenida,
        text="Seguir únicamente con la vista en la misma posición\nlos puntos que aparecerán en pantalla",
        font=tkfont.Font(family="Segoe UI", size=14),
        fg="#545454", bg="#fafafa"
    )
    label_desc.place(relx=0.5, rely=0.51, anchor="center")
    label_press = tk.Label(
        root_bienvenida,
        text="Presiona ESPACIO para comenzar",
        font=tkfont.Font(family="Segoe UI", size=13, slant="italic"),
        fg="#545454", bg="#fafafa"
    )
    label_press.place(relx=0.5, rely=0.58, anchor="center")
    root_bienvenida.bind("<space>", lambda e: root_bienvenida.quit())
    root_bienvenida.bind("<Return>", lambda e: root_bienvenida.quit())
    root_bienvenida.focus_set()
    root_bienvenida.mainloop()

def cerrar_pantalla_bienvenida():
    global root_bienvenida
    if root_bienvenida:
        root_bienvenida.destroy()
        root_bienvenida = None

def mostrar_pantalla_finalizado():
    import tkinter as tk
    from tkinter import font as tkfont
    import os
    import platform
    root_final = tk.Tk()
    root_final.configure(bg='#fafafa')
    root_final.attributes('-fullscreen', True)
    root_final.title('Finalizado')
    label_title = tk.Label(
        root_final, text="FINALIZADO",
        font=tkfont.Font(family="Segoe UI", size=26, weight="bold"),
        fg="#F39200", bg="#fafafa"
    )
    label_title.place(relx=0.5, rely=0.45, anchor="center")
    # Texto con link
    def abrir_analisis(event=None):
        results_path = os.path.abspath('results')
        if platform.system() == 'Windows':
            os.startfile(results_path)
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open "{results_path}"')
        else:  # Linux and others
            os.system(f'xdg-open "{results_path}"')
        root_final.destroy()
    label_desc = tk.Label(
        root_final,
        text="Ver análisis ",
        font=tkfont.Font(family="Segoe UI", size=14),
        fg="#545454", bg="#fafafa"
    )
    label_desc.place(relx=0.5, rely=0.51, anchor="e")
    label_link = tk.Label(
        root_final,
        text="click aquí",
        font=tkfont.Font(family="Segoe UI", size=14, underline=True),
        fg="#545454", bg="#fafafa", cursor="hand2"
    )
    label_link.place(relx=0.5, rely=0.51, anchor="w")
    label_link.bind("<Button-1>", abrir_analisis)
    root_final.mainloop()

def track_images(image_paths, duration=8):
    mostrar_pantalla_bienvenida()
    cerrar_pantalla_bienvenida()
    startCalibration()
    for image_path in image_paths:
        print("Procesando imagen:", image_path)
        exit_flag = track_image(image_path, duration=duration)
        if exit_flag:
            break
    cv2.destroyAllWindows()
    mostrar_pantalla_finalizado()
