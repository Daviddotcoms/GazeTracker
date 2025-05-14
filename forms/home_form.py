import customtkinter as ctk
import cv2
from PIL import Image
import threading
import time
import os

class FormularioInicio():
    def __init__(self, panel_principal, controlador=None):
        self.controlador = controlador
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        self.destruido = False
        
        self.cap = None
        self.is_playing = False
        self.video_thread = None
        self.video_length = 0 
        self.current_frame = 0 
        self.video_muted = False 
        
        self.last_action_time = 0
        self.debounce_interval = 0.5  
        
        self.ajustar_alturas = True
        
        # Crear el contenedor principal con scrollbar
        self.contenedor_exterior = ctk.CTkFrame(panel_principal, fg_color="white")
        self.contenedor_exterior.pack(fill="both", expand=True)
        
        # Crear el scrollbar
        self.scrollbar = ctk.CTkScrollbar(self.contenedor_exterior)
        self.scrollbar.pack(side="right", fill="y")
        
        # Canvas para el scrollbar
        self.canvas = ctk.CTkCanvas(self.contenedor_exterior, bg="white", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Configurar scrollbar para trabajar con el canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)
        
        # Frame dentro del canvas para el contenido
        self.contenedor_principal = ctk.CTkFrame(self.canvas, fg_color="white")
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.contenedor_principal, 
            anchor="nw", 
            tags="self.contenedor_principal"
        )
        
        # Crear las tres columnas horizontales
        self.columna_superior = ctk.CTkFrame(self.contenedor_principal, 
                                           fg_color="#f8f8f8",
                                           height=100,  
                                           corner_radius=20)
        self.columna_media = ctk.CTkFrame(self.contenedor_principal, 
                                        fg_color="#f8f8f8",
                                        height=100,  
                                        corner_radius=20)
        self.columna_inferior = ctk.CTkFrame(self.contenedor_principal, 
                                           fg_color="#f8f8f8",
                                           height=350,  
                                           corner_radius=20)
        
        self.columna_superior.pack(side="top", fill="both", expand=False, pady=(5, 10))
        self.columna_media.pack(side="top", fill="both", expand=False, pady=10)
        self.columna_inferior.pack(side="top", fill="both", expand=True, pady=(10, 5))
        
        self.frame_titulo_superior = ctk.CTkFrame(self.columna_superior, fg_color="transparent", corner_radius=0)
        self.frame_titulo_superior.pack(fill="x", padx=0, pady=0)
        
        self.titulo_superior = ctk.CTkLabel(self.frame_titulo_superior, 
                                          text="Gaze Tracker", 
                                          font=("Segoe UI", 14, "bold"),
                                          anchor="w", text_color="#00ae2a")
        self.titulo_superior.pack(fill="x", padx=20, pady=(5, 5))
        
        self.frame_desc_superior = ctk.CTkFrame(self.columna_superior, 
                                             fg_color="transparent", 
                                             width=self.columna_superior.winfo_width()-40,
                                             height=10,
                                             corner_radius=0)  
        self.frame_desc_superior.pack(fill="both", expand=True, padx=20, pady=(0, 5))
        self.frame_desc_superior.pack_propagate(False)  
        
        self.desc_superior = ctk.CTkLabel(self.frame_desc_superior, 
                                        text="El objetivo principal de este proyecto es crear un programa que utilice neuromarketing para modular la calidad de productos publicitaios mediante el análisis de imágenes y la generación de mapas de calor que identifiquen las áreas de mayor interés para los consumidores. Esto permitiá optimizar las estrategias publicitarias y mejorar la realizarán pruebas para validar el rendimeinto y la efectividad del programa.",
                                        font=("Segoe UI", 12),
                                        anchor="nw",
                                        justify="left",
                                        wraplength=800,
                                        text_color="#545454")
        self.desc_superior.pack(fill="both", expand=True)
        
        self.frame_titulo_media = ctk.CTkFrame(self.columna_media, fg_color="transparent", corner_radius=0)
        self.frame_titulo_media.pack(fill="x", padx=0, pady=0)
        
        self.titulo_media = ctk.CTkLabel(self.frame_titulo_media, 
                                       text="Funcionamiento", 
                                       font=("Segoe UI", 14, "bold"),
                                       anchor="w", text_color="#00ae2a")
        self.titulo_media.pack(fill="x", padx=20, pady=(5, 5))
        
        self.frame_desc_media = ctk.CTkFrame(self.columna_media, 
                                          fg_color="transparent", 
                                          width=self.columna_media.winfo_width()-40,
                                          height=10,
                                          corner_radius=0)  
        self.frame_desc_media.pack(fill="both", expand=True, padx=20, pady=(0, 5))
        self.frame_desc_media.pack_propagate(False)  
        
        self.desc_media = ctk.CTkLabel(self.frame_desc_media, 
                                     text="El sistema utiliza la cámara web integrada para detectar la mirada del usuario mediante la detección de pupilas, con el objetivo de analizar imágenes publicitarias. Se implementará un sistema de puntos de calor que permitirá identificar áreas de interés en las imágenes, facilitando así la toma de decisiones en estrategias publicitarias. Se realizarán pruebas para validar el rendimiento y la efectividad del programa.",
                                     font=("Segoe UI", 12),
                                     anchor="nw",
                                     justify="left",
                                     wraplength=800,
                                     text_color="#545454")
        self.desc_media.pack(fill="both", expand=True)
        
        self.titulo_inferior = ctk.CTkLabel(self.columna_inferior, 
                                          text="Video Explicativo", 
                                          font=("Segoe UI", 14, "bold"),
                                          anchor="w", text_color="#00ae2a")
        self.titulo_inferior.pack(fill="x", padx=20, pady=(20, 5))
        
        # Frame para el video
        self.video_frame = ctk.CTkFrame(self.columna_inferior, 
                                      fg_color="#e0e0e0",
                                      height=500,  # Aumentar la altura del frame
                                      corner_radius=16)
        self.video_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))  
        
        # Label para mostrar el video
        self.video_display = ctk.CTkLabel(self.video_frame, 
                                        text="",
                                        fg_color="#e0e0e0",
                                        corner_radius=12)
        self.video_display.pack(fill="both", expand=True, padx=10, pady=(10, 5))  
        
        # Frame para los controles de video
        self.controles_frame = ctk.CTkFrame(self.columna_inferior, 
                                           fg_color="#f8f8f8",
                                           height=60,
                                           corner_radius=15)
        self.controles_frame.pack(fill="x", expand=False, padx=20, pady=(0, 20))
        
        # Frame para el tiempo y la barra de progreso
        self.progreso_frame = ctk.CTkFrame(self.controles_frame, fg_color="transparent", corner_radius=0)
        self.progreso_frame.pack(fill="x", padx=10, pady=(5, 0))
        
        # Etiqueta para el tiempo actual
        self.tiempo_actual_label = ctk.CTkLabel(self.progreso_frame, 
                                               text="0:00", 
                                               font=("Segoe UI", 10),
                                               width=40)
        self.tiempo_actual_label.pack(side="left", padx=(5, 5))
        
        # Barra de progreso
        self.barra_progreso = ctk.CTkProgressBar(self.progreso_frame, 
                                                height=8,
                                                corner_radius=4,
                                                mode="determinate")
        self.barra_progreso.pack(side="left", fill="x", expand=True, padx=5)
        self.barra_progreso.set(0)  
        
        # Agregar evento de clic para la barra de progreso
        self.barra_progreso.bind("<Button-1>", self.establecer_progreso)
        
        # Etiqueta para la duración total
        self.duracion_label = ctk.CTkLabel(self.progreso_frame, 
                                          text="0:00", 
                                          font=("Segoe UI", 10),
                                          width=40)
        self.duracion_label.pack(side="left", padx=(5, 5))
        
        # Frame para los botones de control
        self.botones_frame = ctk.CTkFrame(self.controles_frame, fg_color="transparent", corner_radius=0)
        self.botones_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Botón de play/pause
        self.play_pause_button = ctk.CTkButton(self.botones_frame,
                                              text="⏸️",  
                                              font=("Segoe UI", 14),
                                              width=40,
                                              height=30,
                                              fg_color="#00ae2a",
                                              hover_color="#008a21",
                                              command=self.toggle_play_pause,
                                              corner_radius=12)
        self.play_pause_button.pack(side="left", padx=10)
        
        # Botón de reiniciar
        self.restart_button = ctk.CTkButton(self.botones_frame,
                                           text="⏮️",
                                           font=("Segoe UI", 14),
                                           width=40,
                                           height=30,
                                           fg_color="#555555",
                                           hover_color="#333333",
                                           command=self.reiniciar_video,
                                           corner_radius=12)
        self.restart_button.pack(side="left", padx=10)
        
        # Frame para el control de volumen
        self.volumen_frame = ctk.CTkFrame(self.botones_frame, fg_color="transparent", corner_radius=0)
        self.volumen_frame.pack(side="right", padx=10)
        
        # Botón de mute/unmute
        self.mute_button = ctk.CTkButton(self.volumen_frame,
                                        text="🔊",
                                        font=("Segoe UI", 14),
                                        width=40,
                                        height=30,
                                        fg_color="#555555",
                                        hover_color="#333333",
                                        command=self.toggle_mute,
                                        corner_radius=12)
        self.mute_button.pack(side="right", padx=5)
        
        # Barra de volumen
        self.volumen_slider = ctk.CTkSlider(self.volumen_frame,
                                           from_=0,
                                           to=100,
                                           number_of_steps=10,
                                           width=100)
        self.volumen_slider.pack(side="right", padx=5)
        self.volumen_slider.set(0.8)  
        
        # Configurar eventos para actualizar el scroll cuando cambia el tamaño
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.contenedor_principal.bind("<Configure>", self.on_frame_configure)
        
        self.columna_superior.bind("<Configure>", self.on_columna_resize)
        self.columna_media.bind("<Configure>", self.on_columna_resize)
        
        # También vincular los frames contenedores
        self.frame_desc_superior.bind("<Configure>", self.on_frame_desc_resize)
        self.frame_desc_media.bind("<Configure>", self.on_frame_desc_resize)
        
        # Configurar evento de rueda del ratón para scroll
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Actualizar los wraplength después de que la ventana se cargue
        self.columna_superior.after(100, self.ajustar_wraplength_inicial)
        
        # Realizar un ajuste de altura adicional después de un tiempo mayor
        self.columna_superior.after(800, self.ajuste_final_alturas)
        
        # Cargar el video automáticamente
        self.cargar_video()
    
    def on_canvas_configure(self, event):
        # Actualizar el ancho del scrollregion cuando el canvas cambia de tamaño
        self.canvas.itemconfig("self.contenedor_principal", width=event.width)
    
    def on_frame_configure(self, event):
        # Actualizar el scrollregion para incluir todo el contenido
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        # Permitir scroll con la rueda del ratón
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def debounce_check(self):
        """Comprueba si ha pasado suficiente tiempo desde la última acción"""
        current_time = time.time()
        if current_time - self.last_action_time < self.debounce_interval:
            return False
        self.last_action_time = current_time
        return True
    
    def cargar_video(self):
        if not self.debounce_check():
            return
            
        try:
            video_path = os.path.join("videos", "video.mp4")
            # Detener video anterior si existe
            self.detener_video(is_reset=True)
            
            # Abrir el video
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                return
            
            # Comprobar si el video tiene frames
            ret, frame = self.cap.read()
            if not ret:
                return
            
            # Resetear el video al inicio
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Obtener información del video
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.video_length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calcular y mostrar la duración total del video
            total_seconds = int(self.video_length / self.fps)
            mins = total_seconds // 60
            secs = total_seconds % 60
            self.duracion_label.configure(text=f"{mins}:{secs:02d}")
            
            # Mostrar el primer frame
            self.mostrar_frame(frame)
            
            self.is_playing = False
            self.play_pause_button.configure(text="▶️")
            
        except Exception as e:
            print(f"Error al cargar video: {str(e)}")
    def mostrar_frame(self, frame):
        """Muestra un frame en el widget de video"""
        if frame is None:
            return
            
        # Convertir el frame de BGR a RGB si es necesario
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            frame_rgb = frame
            
        # Obtener dimensiones del widget
        try:
            max_height = self.video_display.winfo_height()
            max_width = self.video_display.winfo_width()
            
            # Valores predeterminados si el widget no tiene tamaño aún
            if max_height <= 10 or max_width <= 10:
                max_height = 480
                max_width = 640
            else:
                # Asegurar un mínimo de tamaño
                max_height = max(max_height, 480)
                max_width = max(max_width, 640)
            
            # Redimensionar manteniendo la relación de aspecto
            height, width = frame_rgb.shape[:2]
            aspect_ratio = width / height
            
            if max_width / max_height > aspect_ratio:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            
            # Redimensionar el frame
            frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convertir a imagen para CustomTkinter
            pil_image = Image.fromarray(frame_resized)
            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(new_width, new_height)
            )
            
            # Actualizar el label
            self.video_display.configure(image=ctk_image)
            self.video_display.image = ctk_image  
        except Exception as e:
            print(f"Error al mostrar frame: {str(e)}")
    
    def actualizar_video(self):
        # Esperar un momento para que el widget tenga tamaño
        time.sleep(0.25)
        
        while self.is_playing and self.cap is not None and not self.destruido:
            try:
                # Verificar si el widget todavía existe
                if not hasattr(self, 'video_display') or not self.video_display.winfo_exists():
                    self.is_playing = False
                    break
                
                # Obtener el tiempo antes de procesar el frame
                tiempo_inicio = time.time()
                
                ret, frame = self.cap.read()
                if ret:
                    # Actualizar contador de frames y barra de progreso
                    self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                    self.actualizar_progreso()
                    
                    # Mostrar el frame
                    self.mostrar_frame(frame)
                    
                    # Calcular cuánto tiempo se tardó en procesar y mostrar el frame
                    tiempo_procesamiento = time.time() - tiempo_inicio
                    
                    # Calcular cuánto tiempo debe esperar para mantener la velocidad real (1x)
                    tiempo_por_frame = 1.0 / self.fps
                    tiempo_espera = max(0, tiempo_por_frame - tiempo_procesamiento)

                    if tiempo_espera > 0:
                        time.sleep(tiempo_espera)
                else:
                    # Si el video terminó, volver al inicio
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    # Esperar un momento antes de reiniciar
                    time.sleep(0.5)
            except Exception as e:
                time.sleep(1)  
                if not hasattr(self, 'video_display') or not self.video_display.winfo_exists():
                    self.is_playing = False
                    break
            
    def __del__(self):
        # Limpiar recursos al cerrar
        self.detener_video()
        
    def detener_video(self, is_reset=False):
        """Detiene la reproducción del video y libera los recursos"""
        if not is_reset:
            self.destruido = True
        self.is_playing = False
        
        if self.cap is not None:
            if self.video_thread is not None:
                if self.video_thread.is_alive():
                    self.video_thread.join(timeout=1.0)
            self.cap.release()
            self.cap = None
            
    def on_destruir(self):
        """Método para llamar cuando se va a destruir el formulario"""
        self.detener_video()
        
    def toggle_play_pause(self):
        """Alterna entre reproducir y pausar el video"""
        # Aplicar debounce
        if not self.debounce_check():
            return
            
        if self.cap is None:
            self.cargar_video()
            return
            
        if self.is_playing:
            # Pausar el video
            self.is_playing = False
            self.play_pause_button.configure(text="▶️")
        else:
            # Reproducir el video
            self.is_playing = True
            self.play_pause_button.configure(text="⏸️")
            
            # Si el hilo no está activo, iniciarlo nuevamente
            if self.video_thread is None or not self.video_thread.is_alive():
                self.video_thread = threading.Thread(target=self.actualizar_video)
                self.video_thread.daemon = True
                self.video_thread.start()
    
    def reiniciar_video(self):
        """Reinicia el video desde el principio"""
        if not self.debounce_check():
            return
            
        if self.cap is None:
            self.cargar_video()
            return
            
        # Reiniciar el video al frame 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.current_frame = 0
        self.actualizar_progreso()
        
        # Si estaba pausado, mantenerlo pausado pero mostrar el primer frame
        if not self.is_playing:
            ret, frame = self.cap.read()
            if ret:
                # Mostrar el primer frame
                self.mostrar_frame(frame)
                # Reiniciar posición para mantener coherencia
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def toggle_mute(self):
        """Activa o desactiva el sonido del video"""
        if not self.debounce_check():
            return
            
        if self.video_muted:
            # Activar sonido
            self.video_muted = False
            self.mute_button.configure(text="🔊")
            # Restaurar el nivel de volumen anterior
            valor_volumen = self.volumen_slider.get()
            # Aquí se implementaría el código para ajustar el volumen real
            # del video si se está utilizando alguna biblioteca de audio
        else:
            # Desactivar sonido
            self.video_muted = True
            self.mute_button.configure(text="🔇")
            # Guardar el nivel de volumen actual antes de mutear
            valor_volumen = self.volumen_slider.get()
            # Aquí se implementaría el código para silenciar el video
            # si se está utilizando alguna biblioteca de audio

    def actualizar_progreso(self):
        """Actualiza la barra de progreso y el tiempo actual del video"""
        if self.video_length > 0:
            # Actualizar la barra de progreso
            progreso = min(1.0, max(0.0, self.current_frame / self.video_length))
            self.barra_progreso.set(progreso)
            
            # Actualizar la etiqueta de tiempo actual
            current_seconds = int(self.current_frame / self.fps) if hasattr(self, 'fps') and self.fps > 0 else 0
            mins = current_seconds // 60
            secs = current_seconds % 60
            self.tiempo_actual_label.configure(text=f"{mins}:{secs:02d}")
    
    def establecer_progreso(self, event):
        """Permite al usuario hacer clic en la barra de progreso para saltar a esa posición"""
        if not self.debounce_check():
            return
            
        if self.cap is None or self.video_length <= 0:
            return
            
        try:
            # Calcular la posición relativa del clic en la barra de progreso
            barra_width = self.barra_progreso.winfo_width()
            if barra_width <= 0:
                return
                
            ratio = event.x / barra_width
            # Limitar el ratio entre 0 y 1
            ratio = max(0, min(1, ratio))
            
            # Calcular el frame al que saltar
            frame_to_jump = int(ratio * self.video_length)
            
            # Guardar estado actual de reproducción
            was_playing = self.is_playing
            
            # Pausar temporalmente solo si está reproduciendo
            if was_playing:
                self.is_playing = False
            
            # Establecer la posición del video
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_jump)
            self.current_frame = frame_to_jump
            
            # Actualizar vista
            ret, frame = self.cap.read()
            if ret:
                self.mostrar_frame(frame)
                # Retroceder un frame para que el siguiente read obtenga este frame
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_jump)
            
            # Actualizar la barra de progreso y la etiqueta de tiempo
            self.actualizar_progreso()
            
            # Restaurar estado de reproducción si estaba reproduciendo
            if was_playing:
                def restaurar_reproduccion():
                    self.is_playing = True
                    # Si no hay hilo de reproducción activo, iniciarlo
                    if self.video_thread is None or not self.video_thread.is_alive():
                        self.video_thread = threading.Thread(target=self.actualizar_video)
                        self.video_thread.daemon = True
                        self.video_thread.start()
                self.video_display.after(100, restaurar_reproduccion)
            
        except Exception as e:
            print(f"Error al establecer progreso: {str(e)}")
    def on_columna_resize(self, event):
        """Ajusta el wraplength del texto cuando se redimensiona la columna"""
        # Determinar qué label actualizar basado en el widget que disparó el evento
        if event.widget == self.columna_superior and hasattr(self, 'frame_desc_superior'):
            self.frame_desc_superior.configure(width=event.width-40) 
        elif event.widget == self.columna_media and hasattr(self, 'frame_desc_media'):
            self.frame_desc_media.configure(width=event.width-40) 
    
    def on_frame_desc_resize(self, event):
        """Ajusta el wraplength del texto cuando se redimensiona el frame contenedor"""
        # Determinar qué label actualizar basado en el widget que disparó el evento
        if event.widget == self.frame_desc_superior and hasattr(self, 'desc_superior'):
            # Establecer el wraplength a un poco menos que el ancho del contenedor
            new_width = max(200, event.width - 10)
            self.desc_superior.configure(wraplength=new_width)
        elif event.widget == self.frame_desc_media and hasattr(self, 'desc_media'):
            new_width = max(200, event.width - 10)
            self.desc_media.configure(wraplength=new_width)

    def ajustar_wraplength_inicial(self):
        """Ajusta el ancho inicial de los textos una vez que la ventana está cargada"""
        if hasattr(self, 'frame_desc_superior') and hasattr(self, 'desc_superior'):
            width = self.frame_desc_superior.winfo_width()
            if width > 50: 
                self.desc_superior.configure(wraplength=width-10)  
                
                # Ajustar altura automáticamente si es necesario
                if self.ajustar_alturas:
                    # Esperar a que el texto se ajuste
                    self.columna_superior.after(100, self.ajustar_altura_superior)
        
        if hasattr(self, 'frame_desc_media') and hasattr(self, 'desc_media'):
            width = self.frame_desc_media.winfo_width()
            if width > 50: 
                self.desc_media.configure(wraplength=width-10)  
                
                # Ajustar altura automáticamente si es necesario
                if self.ajustar_alturas:
                    # Esperar a que el texto se ajuste
                    self.columna_superior.after(100, self.ajustar_altura_media)
                
        # Programar otro ajuste en caso de que los frames aún no tengan su tamaño final
        self.columna_superior.after(300, self.segundo_ajuste_wraplength)
    
    def ajustar_altura_superior(self):
        """Ajusta la altura de la columna superior basándose en el contenido real"""
        if hasattr(self, 'desc_superior') and self.ajustar_alturas:
            try:
                # Forzar actualización de geometría
                self.desc_superior.update_idletasks()
                self.titulo_superior.update_idletasks()
                
                # Obtener la altura real requerida por el texto de descripción
                altura_desc = self.desc_superior.winfo_reqheight()
                
                # La altura total será la altura del texto más un margen razonable
                nueva_altura = altura_desc + 15
                
                # Aplicar la nueva altura al frame de descripción, no a la columna
                self.frame_desc_superior.configure(height=nueva_altura)
            except Exception as e:
                print(f"Error al ajustar altura superior: {e}")
                # Establecer una altura predeterminada segura
                self.frame_desc_superior.configure(height=60)
    
    def ajustar_altura_media(self):
        """Ajusta la altura de la columna media basándose en el contenido real"""
        if hasattr(self, 'desc_media') and self.ajustar_alturas:
            try:
                # Forzar actualización de geometría
                self.desc_media.update_idletasks()
                self.titulo_media.update_idletasks()
                
                # Obtener la altura real requerida por el texto de descripción
                altura_desc = self.desc_media.winfo_reqheight()
                
                # La altura total será la altura del texto más un margen razonable
                nueva_altura = altura_desc + 15
                
                # Aplicar la nueva altura al frame de descripción, no a la columna
                self.frame_desc_media.configure(height=nueva_altura)
                
                # Desactivar la bandera después de ajustar ambos frames
                self.ajustar_alturas = False
            except Exception as e:
                print(f"Error al ajustar altura media: {e}")
                # Establecer una altura predeterminada segura
                self.frame_desc_media.configure(height=60)
    
    def segundo_ajuste_wraplength(self):
        """Segundo intento de ajustar los wraplength después de cargar completamente"""
        self.ajustar_wraplength_inicial()

    def ajuste_final_alturas(self):
        """Realiza un ajuste final de las alturas después de que todo se haya cargado"""
        if hasattr(self, 'desc_superior') and hasattr(self, 'desc_media'):
            # Reactivar el ajuste de alturas
            self.ajustar_alturas = True
            
            # Llamar a los métodos de ajuste con un pequeño retardo entre ellos
            self.ajustar_altura_superior()
            self.columna_superior.after(100, self.ajustar_altura_media)