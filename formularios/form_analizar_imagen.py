import customtkinter as ctk
import cv2
from PIL import Image, ImageDraw
import os
from tkinter import filedialog, Canvas
from config import (
    COLOR_VERDE, COLOR_VERDE_HOVER, COLOR_GRIS_CLARO, COLOR_GRIS_MEDIO, 
    COLOR_TEXTO, COLOR_TEXTO_SECUNDARIO, COLOR_BORDE, COLOR_CUERPO_PRINCIPAL,
    COLOR_BOTON_SECUNDARIO, COLOR_BOTON_SECUNDARIO_HOVER, COLOR_FONDO_IMAGEN
)
import threading
from util.util_imagenes import leer_imagen
from util.util_paths import resource_path

class FormularioAnalizarImagen():
    def __init__(self, panel_principal, controlador=None):           
        self.controlador = controlador
        
        self.imagen_original = None
        self.imagen_procesada = None
        self.archivo_imagen = None
        self.imagen_cargada = False 

        self.contenedor_exterior = ctk.CTkFrame(panel_principal, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.contenedor_exterior.pack(fill="both", expand=True)
        
        self.scrollbar = ctk.CTkScrollbar(self.contenedor_exterior)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = ctk.CTkCanvas(self.contenedor_exterior, bg=COLOR_CUERPO_PRINCIPAL, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)
        
        self.contenedor_principal = ctk.CTkFrame(self.canvas, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.contenedor_principal, 
            anchor="nw", 
            tags="self.contenedor_principal"
        )
        
        self.titulo_pagina = ctk.CTkLabel(
            self.contenedor_principal,
            text="Ingresa una imagen para iniciar el análisis de gaze tracking",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w",
            height=50
        )
        self.titulo_pagina.pack(fill="x", padx=20, pady=(20, 20), anchor="w")
        
        self.frame_carga = ctk.CTkFrame(
            self.contenedor_principal,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            corner_radius=0,
            height=600,
        )
        self.frame_carga.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.frame_carga.pack_propagate(False)
                
        self.canvas_area = Canvas(self.frame_carga, bg=COLOR_CUERPO_PRINCIPAL, highlightthickness=0)
        self.canvas_area.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.canvas_area.bind("<Configure>", self.dibujar_borde_punteado)
        
        self.contenedor_elementos_carga = ctk.CTkFrame(
            self.canvas_area,
            fg_color="transparent",
        )
        self.contenedor_elementos_carga.pack(expand=True, fill="both")
        
        self.mostrar_elementos_carga()
        
        self.preparar_elementos_imagen()
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.contenedor_principal.bind("<Configure>", self.on_frame_configure)
        
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel_windows)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel_linux)
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_mousewheel_macos)
        
    def on_canvas_configure(self, event):
        self.canvas.itemconfig("self.contenedor_principal", width=event.width)
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")  
    
    def on_mousewheel_macos(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta)), "units")
    
    def mostrar_elementos_carga(self):
        """Muestra los elementos para cargar una imagen"""
        if hasattr(self, 'frame_imagen_mostrada'):
            self.frame_imagen_mostrada.pack_forget()
            
        self.icono_documento = ctk.CTkLabel(
            self.contenedor_elementos_carga,
            text="",
            image=self.crear_icono_documento(),
            fg_color="transparent"
        )
        self.icono_documento.pack(pady=(100, 10))
        
        self.boton_seleccionar = ctk.CTkButton(
            self.contenedor_elementos_carga,
            text="Seleccionar Imagen",
            font=("Segoe UI", 13),
            fg_color=COLOR_BOTON_SECUNDARIO,
            text_color=COLOR_TEXTO,
            hover_color=COLOR_BOTON_SECUNDARIO_HOVER,
            height=36,
            width=180,
            corner_radius=18,
            command=self.seleccionar_imagen
        )
        self.boton_seleccionar.pack(pady=20)
        
        self.texto_info = ctk.CTkLabel(
            self.contenedor_elementos_carga,
            text="Solo archivos .jpg, .jpeg, .png con menos de 3MB",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXTO_SECUNDARIO
        )
        self.texto_info.pack(pady=(10, 100))
        
        self.canvas.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    def preparar_elementos_imagen(self):
        """Prepara los elementos para mostrar la imagen cargada (inicialmente ocultos)"""
        self.frame_imagen_mostrada = ctk.CTkFrame(
            self.contenedor_elementos_carga,
            fg_color="transparent"
        )
        
        self.label_imagen = ctk.CTkLabel(
            self.frame_imagen_mostrada, 
            text="",
            fg_color="transparent"
        )
        self.label_imagen.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        self.frame_botones_imagen = ctk.CTkFrame(
            self.frame_imagen_mostrada,
            fg_color="transparent",
        )
        self.frame_botones_imagen.pack(fill="x", pady=(10, 20))
        
        # Añadir espacio flexible a la izquierda para empujar los botones a la derecha
        ctk.CTkFrame(
            self.frame_botones_imagen,
            fg_color="transparent",
            width=300
        ).pack(side="left", expand=True, fill="x")
        
        self.boton_eliminar = ctk.CTkButton(
            self.frame_botones_imagen,
            text="Eliminar",
            font=("Segoe UI", 13),
            fg_color=COLOR_BOTON_SECUNDARIO,
            text_color=COLOR_TEXTO,
            hover_color=COLOR_BOTON_SECUNDARIO_HOVER,
            height=36,
            width=100,
            corner_radius=18,
            command=self.eliminar_imagen
        )
        self.boton_eliminar.pack(side="left", padx=(0, 10))
        
        self.boton_procesar = ctk.CTkButton(
            self.frame_botones_imagen,
            text="Continuar",
            font=("Segoe UI", 13),
            fg_color=COLOR_VERDE,
            text_color=COLOR_CUERPO_PRINCIPAL,
            hover_color=COLOR_VERDE_HOVER,
            height=36,
            width=150,
            corner_radius=18,
            command=self.ir_a_instrucciones_analisis
        )
        self.boton_procesar.pack(side="left", padx=(0, 20))
    
    def mostrar_imagen_cargada(self):
        """Muestra la imagen cargada en la interfaz"""
        if hasattr(self, 'icono_documento'):
            self.icono_documento.pack_forget()
        if hasattr(self, 'boton_seleccionar'):
            self.boton_seleccionar.pack_forget()
        if hasattr(self, 'texto_info'):
            self.texto_info.pack_forget()
            
        self.frame_imagen_mostrada.pack(fill="both", expand=True)
        
        if self.imagen_original is not None:
            self.label_imagen.configure(image=self.imagen_original)
            self.label_imagen.image = self.imagen_original
            
            self.canvas.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    def eliminar_imagen(self):
        """Elimina la imagen cargada y vuelve al estado inicial"""
        self.imagen_original = None
        self.imagen_procesada = None
        self.archivo_imagen = None
        self.imagen_cargada = False
        
        self.frame_imagen_mostrada.pack_forget()
        
        self.mostrar_elementos_carga()
        
        self.canvas.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    def dibujar_borde_punteado(self, event=None):
        """Dibuja un borde punteado alrededor del canvas"""
        self.canvas_area.delete("borde")
        
        width = self.canvas_area.winfo_width()
        height = self.canvas_area.winfo_height()
        dash_pattern = (4, 4)
        corner_radius = 10
        
        self.canvas_area.create_line(
            corner_radius, 2, 
            width - corner_radius, 2, 
            dash=dash_pattern, tags="borde", width=1, fill=COLOR_BORDE)
        self.canvas_area.create_line(
            width - 2, corner_radius, 
            width - 2, height - corner_radius, 
            dash=dash_pattern, tags="borde", width=1, fill=COLOR_BORDE)
        self.canvas_area.create_line(
            width - corner_radius, height - 2, 
            corner_radius, height - 2, 
            dash=dash_pattern, tags="borde", width=1, fill=COLOR_BORDE)
        self.canvas_area.create_line(
            2, height - corner_radius, 
            2, corner_radius, 
            dash=dash_pattern, tags="borde", width=1, fill=COLOR_BORDE)
        
        self.canvas_area.create_arc(
            2, 2, 
            corner_radius*2, corner_radius*2, 
            start=90, extent=90, 
            style="arc", outline=COLOR_BORDE, dash=dash_pattern, tags="borde", width=1)
        self.canvas_area.create_arc(
            width - corner_radius*2, 2, 
            width - 2, corner_radius*2, 
            start=0, extent=90, 
            style="arc", outline=COLOR_BORDE, dash=dash_pattern, tags="borde", width=1)
        self.canvas_area.create_arc(
            width - corner_radius*2, height - corner_radius*2, 
            width - 2, height - 2, 
            start=270, extent=90, 
            style="arc", outline=COLOR_BORDE, dash=dash_pattern, tags="borde", width=1)
        self.canvas_area.create_arc(
            2, height - corner_radius*2, 
            corner_radius*2, height - 2, 
            start=180, extent=90, 
            style="arc", outline=COLOR_BORDE, dash=dash_pattern, tags="borde", width=1)
    
    def crear_icono_documento(self):
        try:
            ruta_icono = resource_path(os.path.join("recursos", "icono_documento.png"))
            if os.path.exists(ruta_icono):
                return ctk.CTkImage(
                    light_image=Image.open(ruta_icono),
                    size=(50, 50)
                )
        except:
            pass
            
        img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        draw.rectangle((25, 25, 75, 85), outline=COLOR_BORDE, width=2, fill=COLOR_CUERPO_PRINCIPAL)
        
        arrow_points = [(50, 45), (40, 55), (45, 55), (45, 65), (55, 65), (55, 55), (60, 55)]
        draw.polygon(arrow_points, fill=COLOR_BORDE)
        
        img_ctk = ctk.CTkImage(light_image=img, size=(70, 70))
        return img_ctk
    
    def seleccionar_imagen(self):
        if self.imagen_cargada:
            self.mostrar_error("Ya hay una imagen cargada. Elimínela primero para cargar otra.")
            return
            
        tipos_archivo = [
            ("Imágenes", "*.jpg *.jpeg *.png"),
            ("Todos los archivos", "*.*")
        ]
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=tipos_archivo
        )
        
        if archivo:
            self.archivo_imagen = archivo
            self.cargar_imagen()
    
    def cargar_imagen(self):
        if not self.archivo_imagen:
            return
        def cargar_y_mostrar():
            try:
                tamaño_archivo = os.path.getsize(self.archivo_imagen) / (1024 * 1024)
                if tamaño_archivo > 3:
                    self.mostrar_error("El archivo seleccionado excede el límite de 3MB")
                    return
                # Previsualización rápida con Pillow
                imagen_previa = leer_imagen(self.archivo_imagen, (400, 400))
                self.imagen_original = imagen_previa
                self.imagen_cargada = True
                self.mostrar_imagen_cargada()
            except Exception as e:
                self.mostrar_error(f"Error: {str(e)}")
        threading.Thread(target=cargar_y_mostrar).start()

    def ir_a_instrucciones_analisis(self):
        """Navega a la pantalla de instrucciones de análisis"""
        if not self.imagen_cargada:
            self.mostrar_error("No hay imagen para analizar. Por favor, cargue una imagen primero.")
            return
        try:
            from formularios.form_instrucciones_analisis import FormularioInstruccionesAnalisis
            FormularioInstruccionesAnalisis(self.contenedor_exterior, self.controlador, rutas_imagenes=[self.archivo_imagen])
        except Exception as e:
            print(f"Error al navegar a pantalla de instrucciones: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_error(f"Error al cambiar de pantalla: {e}")
    
    def mostrar_error(self, mensaje):
        error_window = ctk.CTkToplevel()
        error_window.title("Error")
        error_window.geometry("400x200")
        error_window.resizable(False, False)
        
        label = ctk.CTkLabel(
            error_window,
            text=mensaje,
            font=("Segoe UI", 14)
        )
        label.pack(pady=50)
        
        btn = ctk.CTkButton(
            error_window, 
            text="Aceptar",
            command=error_window.destroy
        )
        btn.pack(pady=20)
        
        error_window.grab_set()
            
    def procesar_imagen(self):
        """Ejemplo simple de procesamiento de imagen"""
        if self.imagen_original is None:
            print("No hay imagen para procesar")
            return
            
        try:
            print("Procesando imagen...")
            
            gris = cv2.cvtColor(self.imagen_original, cv2.COLOR_BGR2GRAY)
            gris = cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)  # Convertir de nuevo a BGR para consistencia
            
            self.imagen_procesada = gris
            
            if self.controlador and hasattr(self.controlador, 'mostrar_secuencia_imagenes'):
                self.controlador.mostrar_secuencia_imagenes()
            else:
                self.mostrar_imagen_procesada()
            
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
            self.mostrar_error(f"Error al procesar la imagen: {e}")
             
    def mostrar_imagen_procesada(self):
        """Muestra la imagen procesada en una ventana temporal"""
        if self.imagen_procesada is None:
            return
            
        ventana = ctk.CTkToplevel()
        ventana.title("Imagen Procesada")
        ventana.geometry("800x600")
        
        frame_imagen = ctk.CTkFrame(ventana, fg_color=COLOR_FONDO_IMAGEN)
        frame_imagen.pack(fill="both", expand=True, padx=20, pady=20)
        
        label_imagen = ctk.CTkLabel(frame_imagen, text="")
        label_imagen.pack(fill="both", expand=True, padx=10, pady=10)
        
        if len(self.imagen_procesada.shape) == 2:  # Si es escala de grises
            img_rgb = cv2.cvtColor(self.imagen_procesada, cv2.COLOR_GRAY2RGB)
        else:  
            img_rgb = cv2.cvtColor(self.imagen_procesada, cv2.COLOR_BGR2RGB)
            
        pil_img = Image.fromarray(img_rgb)
        
        width, height = pil_img.size
        max_width = 760
        max_height = 520
        
        if width > max_width or height > max_height:
            ratio = min(max_width/width, max_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
            
        ctk_img = ctk.CTkImage(light_image=pil_img, size=pil_img.size)
        
        label_imagen.configure(image=ctk_img)
        label_imagen.image = ctk_img  
        
        btn_cerrar = ctk.CTkButton(
            ventana, 
            text="Cerrar", 
            command=ventana.destroy,
            fg_color=COLOR_BOTON_SECUNDARIO,
            text_color=COLOR_TEXTO,
            hover_color=COLOR_BOTON_SECUNDARIO_HOVER,
            height=36,
            width=120,
            corner_radius=18
        )
        btn_cerrar.pack(pady=20)
        
        self.canvas.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))