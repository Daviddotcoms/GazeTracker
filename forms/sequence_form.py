import customtkinter as ctk
from PIL import Image, ImageDraw
import os
from tkinter import filedialog, Canvas
import tkinter as tk
from config import  COLOR_BARRA_SUPERIOR, COLOR_BORDE, COLOR_BOTON_SECUNDARIO, COLOR_BOTON_SECUNDARIO_HOVER, COLOR_GRIS_MEDIO, COLOR_TEXTO, COLOR_TEXTO_SECUNDARIO, COLOR_VERDE_HOVER, COLOR_CUERPO_PRINCIPAL
import threading
from utils.image_utils import leer_imagen


class FormularioSecuencia():
    archivos_imagenes = []
    imagenes_originales = [] 

    def __init__(self, panel_principal, controlador=None):
        # Inicializar controlador
        self.controlador = controlador
        
        # Colores
        self.color_verde = COLOR_BARRA_SUPERIOR
        self.color_verde_hover = COLOR_VERDE_HOVER
        self.color_gris_medio = COLOR_GRIS_MEDIO   # Gris medio para elementos
        self.color_borde = COLOR_BORDE        # Color de bordes
        self.color_texto = COLOR_TEXTO        # Texto oscuro
        self.color_texto_secundario = COLOR_TEXTO_SECUNDARIO  # Texto secundario
        
        # Variables para las imágenes
        self.max_imagenes = 9          # Máximo número de imágenes permitidas
        
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
        
        # Título de la página
        self.titulo_pagina = ctk.CTkLabel(
            self.contenedor_principal,
            text="Ingresa las imágenes para iniciar el análisis de gaze tracking",
            font=("Segoe UI", 14, "bold"),
            text_color=self.color_texto,
            anchor="w",
            height=50
        )
        self.titulo_pagina.pack(fill="x", padx=20, pady=(20, 20), anchor="w")
        
        # Contenedor para la zona de carga de imágenes
        self.frame_carga = ctk.CTkFrame(
            self.contenedor_principal,
            fg_color="white",
            corner_radius=0,
            height=600  # Altura mínima para asegurar que hay suficiente contenido para scroll
        )
        self.frame_carga.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.frame_carga.pack_propagate(False)  # Impedir que el frame se redimensione automáticamente
        
        # Crear un canvas con borde punteado en lugar de un frame normal
        self.canvas_area = Canvas(self.frame_carga, bg="white", highlightthickness=0)
        self.canvas_area.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Dibujar borde punteado cuando el canvas esté listo
        self.canvas_area.bind("<Configure>", self.dibujar_borde_punteado)
        
        # Contenedor vertical para los elementos dentro del área de carga
        self.contenedor_elementos_carga = ctk.CTkFrame(
            self.canvas_area,
            fg_color="transparent",
        )
        self.contenedor_elementos_carga.pack(expand=True, fill="both")
        
        # Mostrar elementos para cargar imágenes
        self.mostrar_elementos_carga()
        
        # Preparar área para mostrar las imágenes cargadas
        self.preparar_area_imagenes()
        
        # Configurar eventos para actualizar el scroll cuando cambia el tamaño
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.contenedor_principal.bind("<Configure>", self.on_frame_configure)
        
        # Configurar eventos de rueda del ratón para diferentes sistemas operativos
        # Windows (MouseWheel)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel_windows)
        # Linux (Button-4 / Button-5)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel_linux)
        # macOS (Shift-MouseWheel para scroll vertical)
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_mousewheel_macos)
    
    def on_canvas_configure(self, event):
        # Actualizar el ancho del scrollregion cuando el canvas cambia de tamaño
        self.canvas.itemconfig("self.contenedor_principal", width=event.width)
    
    def on_frame_configure(self, event):
        # Actualizar el scrollregion para incluir todo el contenido
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel_windows(self, event):
        # Implementación específica para Windows
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_mousewheel_linux(self, event):
        # Implementación específica para Linux
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")  # Scroll hacia arriba
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")   # Scroll hacia abajo
    
    def on_mousewheel_macos(self, event):
        # Implementación específica para macOS
        self.canvas.yview_scroll(int(-1*(event.delta)), "units")
    
    def mostrar_elementos_carga(self):
        """Muestra los elementos para cargar imágenes"""
        # Icono de documento
        self.icono_documento = ctk.CTkLabel(
            self.contenedor_elementos_carga,
            text="",
            image=self.crear_icono_documento(),
            fg_color="transparent"
        )
        self.icono_documento.pack(pady=(100, 10))
        
        self.boton_seleccionar = ctk.CTkButton(
            self.contenedor_elementos_carga,
            text="Seleccionar Imágenes",
            font=("Segoe UI", 13),
            fg_color=COLOR_BOTON_SECUNDARIO,
            text_color=COLOR_TEXTO,
            hover_color=COLOR_BOTON_SECUNDARIO_HOVER,
            height=36,
            width=180,
            corner_radius=18,
            command=self.seleccionar_imagenes
        )
        self.boton_seleccionar.pack(pady=20)
        
        self.texto_info = ctk.CTkLabel(
            self.contenedor_elementos_carga,
            text="Solo archivos .jpg, .jpeg, .png con menos de 3MB (Max: 9 imágenes)",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXTO_SECUNDARIO
        )
        self.texto_info.pack(pady=(10, 100))
        # Actualizar el scroll region después de añadir elementos
        self.canvas.after(50, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    def preparar_area_imagenes(self):
        """Prepara el área para mostrar las imágenes cargadas (inicialmente oculto)"""
        self.frame_imagenes = ctk.CTkFrame(
            self.contenedor_elementos_carga,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            height=720
        )
        self.frame_imagenes.pack_propagate(False)
        # Grid de imágenes fijo
        self.grid_imagenes = ctk.CTkFrame(
            self.frame_imagenes,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            height=660
        )
        self.grid_imagenes.pack(padx=30, pady=(30, 0))
        self.grid_imagenes.pack_propagate(False)
        # Texto de ayuda centrado debajo del grid
        self.label_ayuda = ctk.CTkLabel(
            self.frame_imagenes,
            text="Solo archivos .jpg, .jpeg, .png con menos de 3MB",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXTO_SECUNDARIO,
            fg_color="transparent"
        )
        self.label_ayuda.pack(pady=(10, 10))
        # Botón continuar centrado
        self.boton_continuar = ctk.CTkButton(
            self.frame_imagenes,
            text="Continuar",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLOR_BOTON_SECUNDARIO,
            text_color=COLOR_TEXTO,
            hover_color=COLOR_BOTON_SECUNDARIO_HOVER,
            height=36,
            width=160,
            corner_radius=18,
            command=self.continuar_al_analisis
        )
        self.boton_continuar.pack(pady=(10, 0))
    
    def crear_icono_documento(self):
        """Crea un icono de documento para el área de carga"""
        try:
            # Intentar cargar imagen existente
            ruta_icono = os.path.join("recursos", "icono_documento.png")
            if os.path.exists(ruta_icono):
                return ctk.CTkImage(
                    light_image=Image.open(ruta_icono),
                    size=(50, 50)
                )
        except:
            pass
            
        # Si no existe o hay error, crear un icono genérico
        img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Dibujar un icono de documento con flecha hacia arriba para tema claro
        # Rectángulo principal del documento
        draw.rectangle((25, 25, 75, 85), outline="#aaaaaa", width=2, fill="white")
        
        # Dibujar la flecha hacia arriba
        arrow_points = [(50, 45), (40, 55), (45, 55), (45, 65), (55, 65), (55, 55), (60, 55)]
        draw.polygon(arrow_points, fill="#aaaaaa")
        
        # Convertir a formato CTkImage
        img_ctk = ctk.CTkImage(light_image=img, size=(70, 70))
        return img_ctk
    
    def dibujar_borde_punteado(self, event=None):
        """Dibuja un borde punteado alrededor del canvas"""
        self.canvas_area.delete("borde")  # Eliminar borde anterior si existe
        
        width = self.canvas_area.winfo_width()
        height = self.canvas_area.winfo_height()
        dash_pattern = (4, 4)  # Patrón de línea punteada (4px línea, 4px espacio)
        corner_radius = 10     # Radio de las esquinas redondeadas
        border_color = self.color_borde  # Color del borde para tema claro
        
        # Dibujar las líneas con esquinas redondeadas
        # Superior
        self.canvas_area.create_line(
            corner_radius, 2, 
            width - corner_radius, 2, 
            dash=dash_pattern, tags="borde", width=1, fill=border_color)
        # Derecha
        self.canvas_area.create_line(
            width - 2, corner_radius, 
            width - 2, height - corner_radius, 
            dash=dash_pattern, tags="borde", width=1, fill=border_color)
        # Inferior
        self.canvas_area.create_line(
            width - corner_radius, height - 2, 
            corner_radius, height - 2, 
            dash=dash_pattern, tags="borde", width=1, fill=border_color)
        # Izquierda
        self.canvas_area.create_line(
            2, height - corner_radius, 
            2, corner_radius, 
            dash=dash_pattern, tags="borde", width=1, fill=border_color)
        
        # Esquinas redondeadas (arcos)
        # Superior izquierda
        self.canvas_area.create_arc(
            2, 2, 
            corner_radius*2, corner_radius*2, 
            start=90, extent=90, 
            style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)
        # Superior derecha
        self.canvas_area.create_arc(
            width - corner_radius*2, 2, 
            width - 2, corner_radius*2, 
            start=0, extent=90, 
            style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)
        # Inferior derecha
        self.canvas_area.create_arc(
            width - corner_radius*2, height - corner_radius*2, 
            width - 2, height - 2, 
            start=270, extent=90, 
            style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)
        # Inferior izquierda
        self.canvas_area.create_arc(
            2, height - corner_radius*2, 
            corner_radius*2, height - 2, 
            start=180, extent=90, 
            style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)
    
    def seleccionar_imagenes(self):
        """Permite al usuario seleccionar múltiples imágenes"""
        if len(self.imagenes_originales) >= self.max_imagenes:
            self.mostrar_error(f"Ya se alcanzó el máximo de {self.max_imagenes} imágenes")
            return
        tipos_archivo = [
            ("Imágenes", "*.jpg *.jpeg *.png"),
        ]
        archivos = filedialog.askopenfilenames(
            title="Seleccionar Imágenes",
            filetypes=tipos_archivo
        )
        if archivos:
            if len(self.imagenes_originales) + len(archivos) > self.max_imagenes:
                exceso = len(self.imagenes_originales) + len(archivos) - self.max_imagenes
                self.mostrar_error(f"Solo se pueden cargar {self.max_imagenes} imágenes. Se ignorarán {exceso} imágenes.")
                archivos = archivos[:self.max_imagenes - len(self.imagenes_originales)]
            def cargar_y_mostrar():
                imagenes_cargadas = 0
                for archivo in archivos:
                    try:
                        tamaño_archivo = os.path.getsize(archivo) / (1024 * 1024)
                        if tamaño_archivo > 3:
                            print(f"Archivo demasiado grande (>3MB): {archivo}")
                            continue
                        # Previsualización rápida con Pillow
                        imagen_previa = leer_imagen(archivo, (180, 180))
                        self.imagenes_originales.append(imagen_previa)
                        self.archivos_imagenes.append(archivo)
                        imagenes_cargadas += 1
                    except Exception as e:
                        print(f"Error al cargar la imagen {archivo}: {str(e)}")
                if imagenes_cargadas > 0:
                    print(f"Se cargaron {imagenes_cargadas} imágenes correctamente")
                    if len(self.imagenes_originales) == imagenes_cargadas:
                        self.ocultar_elementos_carga()
                    self.mostrar_grid_imagenes()
                else:
                    self.mostrar_error("No se pudo cargar ninguna imagen.")
            threading.Thread(target=cargar_y_mostrar).start()
    
    def ocultar_elementos_carga(self):
        """Oculta los elementos iniciales de carga"""
        if hasattr(self, 'icono_documento'):
            self.icono_documento.pack_forget()
        if hasattr(self, 'boton_seleccionar'):
            self.boton_seleccionar.pack_forget()
        if hasattr(self, 'texto_info'):
            self.texto_info.pack_forget()
        
        # Mostrar el frame de imágenes
        self.frame_imagenes.pack(fill="both", expand=True)
    
    def mostrar_grid_imagenes(self):
        """Muestra las imágenes cargadas en un grid minimalista de 3x3, con info debajo de cada imagen y botones '+' en celdas vacías"""
        for widget in self.grid_imagenes.winfo_children():
            widget.destroy()
        columnas = 3
        filas = 3
        total_imagenes = len(self.imagenes_originales)
        for i in range(filas * columnas):
            fila = i // columnas
            columna = i % columnas
            frame_celda = ctk.CTkFrame(
                self.grid_imagenes,
                fg_color="#555555" if i >= total_imagenes else "#ffffff",
                width=240,
                height=140,
                corner_radius=10
            )
            frame_celda.grid(row=fila, column=columna, padx=18, pady=18)
            frame_celda.grid_propagate(False)
            if i < total_imagenes:
                imagen_previa = self.imagenes_originales[i]
                label_imagen = ctk.CTkLabel(
                    frame_celda,
                    text="",
                    image=imagen_previa
                )
                label_imagen.image = imagen_previa
                label_imagen.pack(expand=True, fill="both", padx=5, pady=(10, 0))
                # Mostrar info de la imagen debajo
                if i < len(self.archivos_imagenes):
                    try:
                        img = Image.open(self.archivos_imagenes[i])
                        width, height = img.size
                        size_mb = os.path.getsize(self.archivos_imagenes[i]) / (1024 * 1024)
                        texto_info = f"{width}x{height} px | {size_mb:.2f} MB"
                    except Exception:
                        texto_info = "Info no disponible"
                    label_info = ctk.CTkLabel(
                        frame_celda,
                        text=texto_info,
                        font=("Segoe UI", 10),
                        text_color=COLOR_TEXTO_SECUNDARIO,
                        fg_color="transparent",
                        anchor="center",
                        justify="center"
                    )
                    label_info.pack(pady=(0, 8))
            else:
                # Botón '+' grande y centrado en celdas vacías
                boton_mas = ctk.CTkButton(
                    frame_celda,
                    text="+",
                    font=("Segoe UI", 32, "bold"),
                    fg_color="#555555",
                    text_color="white",
                    hover_color="#888888",
                    width=80,
                    height=80,
                    corner_radius=40,
                    command=self.seleccionar_imagenes
                )
                boton_mas.place(relx=0.5, rely=0.5, anchor="center")
        for i in range(columnas):
            self.grid_imagenes.grid_columnconfigure(i, weight=1)
        for i in range(filas):
            self.grid_imagenes.grid_rowconfigure(i, weight=1)
    
    def eliminar_imagen(self, indice):
        """Elimina una imagen específica por su índice"""
        if 0 <= indice < len(self.imagenes_originales):
            # Eliminar la imagen y su ruta de las listas
            self.imagenes_originales.pop(indice)
            self.archivos_imagenes.pop(indice)
            
            # Si no quedan imágenes, volver al estado inicial
            if len(self.imagenes_originales) == 0:
                self.frame_imagenes.pack_forget()
                self.mostrar_elementos_carga()
            else:
                # Actualizar el grid de imágenes
                self.mostrar_grid_imagenes()
    
    def eliminar_todas_imagenes(self):
        """Elimina todas las imágenes cargadas"""
        # Limpiar las listas
        self.imagenes_originales = []
        self.archivos_imagenes = []
        
        # Volver al estado inicial
        self.frame_imagenes.pack_forget()
        self.mostrar_elementos_carga()
        
        # Actualizar el scroll region
        self.canvas.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en una ventana emergente"""
        ventana = ctk.CTkToplevel()
        ventana.title("Error")
        ventana.iconbitmap("./assets/eye_icon.ico")
        ventana.geometry("300x120")
        ventana.resizable(False, False)
        
        # Configurar tema claro para la ventana
        ventana.configure(fg_color="white")
        
        # Mensaje de error
        label = ctk.CTkLabel(
            ventana,
            text=mensaje,
            font=("Segoe UI", 14, "bold"),
            text_color=self.color_texto,
            wraplength=250
        )
        label.pack(pady=10)
        
        # Botón para cerrar
        btn = ctk.CTkButton(
            ventana, 
            text="Aceptar",
            command=ventana.destroy,
            fg_color="#cdcdcd",
            text_color="#333333",
            hover_color="#bebebe",
            height=36,
            width=120,
            corner_radius=18
        )
        btn.pack(pady=20)
        
        # Hacer la ventana modal
        ventana.grab_set()

    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito en una ventana emergente"""
        ventana = ctk.CTkToplevel()
        ventana.title("Éxito")
        ventana.iconbitmap("./assets/eye_icon.ico")
        ventana.geometry("400x200")
        ventana.resizable(False, False)
        
        # Configurar tema claro para la ventana
        ventana.configure(fg_color="white")
        
        # Mensaje de éxito
        label = ctk.CTkLabel(
            ventana,
            text=mensaje,
            font=("Segoe UI", 14, "bold"),
            text_color=self.color_verde,
            wraplength=350
        )
        label.pack(pady=50)
        
        # Botón para cerrar
        btn = ctk.CTkButton(
            ventana, 
            text="Aceptar",
            command=ventana.destroy,
            fg_color="#cdcdcd",
            text_color="#333333",
            hover_color="#bebebe",
            height=36,
            width=120,
            corner_radius=18
        )
        btn.pack(pady=20)
        
        # Hacer la ventana modal
        ventana.grab_set()

    def mostrar_info(self, titulo, mensaje):
        """Muestra información en una ventana emergente"""
        ventana = ctk.CTkToplevel()
        ventana.title(titulo)
        ventana.iconbitmap("./assets/eye_icon.ico")
        ventana.geometry("600x400")
        ventana.resizable(True, True)
        
        # Configurar tema claro para la ventana
        ventana.configure(fg_color="white")
        
        # Crear un frame con scroll para el texto
        frame = ctk.CTkFrame(ventana, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        # Texto
        texto = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, bg="white", fg="#333333")
        texto.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=texto.yview)
        
        # Insertar mensaje
        texto.insert("1.0", mensaje)
        
        # Botón para cerrar
        btn = ctk.CTkButton(
            ventana, 
            text="Aceptar",
            command=ventana.destroy,
            fg_color="#cdcdcd",
            text_color="#333333",
            hover_color="#bebebe",
            height=36,
            width=120,
            corner_radius=18
        )
        btn.pack(pady=10)
        
        # Hacer la ventana modal
        ventana.grab_set()

    def continuar_al_analisis(self):
        """Navega a la pantalla de instrucciones de análisis (solo navegación, sin ejecutar nada más)"""
        try:
            from forms.analysis_instructions_form import FormularioInstruccionesAnalisis
            FormularioInstruccionesAnalisis(self.contenedor_exterior, self.controlador, rutas_imagenes=self.archivos_imagenes)
        except Exception as e:
            print(f"Error al navegar a pantalla de instrucciones: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def limpiar_pantalla(self):
        """Limpia todos los elementos de la pantalla actual"""
        try:
            print("Limpiando pantalla de secuencia...")
            
            # Liberar los eventos de ratón para evitar conflictos
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
            self.canvas.unbind_all("<Shift-MouseWheel>")
            
            # Desempaquetar el contenedor principal
            self.contenedor_principal.pack_forget()
            
            # Destruir todos los widgets del contenedor principal
            for widget in self.contenedor_principal.winfo_children():
                widget.destroy()
            
            # Crear un nuevo contenedor principal
            self.contenedor_principal = ctk.CTkFrame(self.canvas, fg_color="white")
            self.canvas_window = self.canvas.create_window(
                (0, 0), 
                window=self.contenedor_principal, 
                anchor="nw", 
                tags="self.contenedor_principal"
            )
            
            # Actualizar el canvas
            self.canvas.update_idletasks()
            
            print("Pantalla de secuencia limpiada correctamente")
            return True
            
        except Exception as e:
            print(f"Error al limpiar pantalla: {e}")
            import traceback
            traceback.print_exc()
            return False