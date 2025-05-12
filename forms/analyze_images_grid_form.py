import customtkinter as ctk
from PIL import Image, ImageDraw
import os
from tkinter import filedialog, Canvas
import tkinter as tk
from config import COLOR_VERDE, COLOR_VERDE_HOVER, COLOR_TEXTO, COLOR_TEXTO_SECUNDARIO, COLOR_BORDE, COLOR_CUERPO_PRINCIPAL, COLOR_BOTON_SECUNDARIO, COLOR_BOTON_SECUNDARIO_HOVER
import threading
from utils.image_utils import leer_imagen

class FormularioAnalizarImagenesGrid():
    def __init__(self, panel_principal, controlador=None):
        self.controlador = controlador
        self.max_imagenes = 9
        self.imagenes_originales = []
        self.archivos_imagenes = []

        self.contenedor_exterior = ctk.CTkFrame(panel_principal, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.contenedor_exterior.pack(fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.contenedor_exterior)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = ctk.CTkCanvas(self.contenedor_exterior, bg=COLOR_CUERPO_PRINCIPAL, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)

        self.contenedor_principal = ctk.CTkFrame(self.canvas, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.contenedor_principal, anchor="nw", tags="self.contenedor_principal")

        self.titulo_pagina = ctk.CTkLabel(
            self.contenedor_principal,
            text="Selecciona hasta 9 imágenes para analizar",
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

        self.contenedor_elementos_carga = ctk.CTkFrame(self.canvas_area, fg_color="transparent")
        self.contenedor_elementos_carga.pack(expand=True, fill="both")

        self.mostrar_elementos_carga()
        self.preparar_area_imagenes()

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
        self.icono_documento = ctk.CTkLabel(
            self.contenedor_elementos_carga,
            text="",
            image=self.crear_icono_documento(),
            fg_color="transparent"
        )
        self.icono_documento.pack(pady=(60, 10))

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
        self.texto_info.pack(pady=(10, 60))
        self.canvas.after(50, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def preparar_area_imagenes(self):
        self.frame_imagenes = ctk.CTkFrame(
            self.contenedor_elementos_carga,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            height=400
        )
        self.frame_imagenes.pack_propagate(False)
        self.grid_imagenes = ctk.CTkFrame(
            self.frame_imagenes,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            height=340
        )
        self.grid_imagenes.pack(padx=10, pady=(10, 0))
        self.grid_imagenes.pack_propagate(False)
        self.label_ayuda = ctk.CTkLabel(
            self.frame_imagenes,
            text="Solo archivos .jpg, .jpeg, .png con menos de 3MB",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXTO_SECUNDARIO,
            fg_color="transparent"
        )
        self.label_ayuda.pack(pady=(5, 5))
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
        self.boton_continuar.pack(pady=(5, 0))

    def crear_icono_documento(self):
        try:
            ruta_icono = os.path.join("recursos", "icono_documento.png")
            if os.path.exists(ruta_icono):
                return ctk.CTkImage(
                    light_image=Image.open(ruta_icono),
                    size=(40, 40)
                )
        except:
            pass
        img = Image.new('RGBA', (80, 80), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((20, 20, 60, 68), outline="#aaaaaa", width=2, fill="white")
        arrow_points = [(40, 36), (32, 44), (36, 44), (36, 54), (44, 54), (44, 44), (48, 44)]
        draw.polygon(arrow_points, fill="#aaaaaa")
        img_ctk = ctk.CTkImage(light_image=img, size=(56, 56))
        return img_ctk

    def dibujar_borde_punteado(self, event=None):
        self.canvas_area.delete("borde")
        width = self.canvas_area.winfo_width()
        height = self.canvas_area.winfo_height()
        dash_pattern = (4, 4)
        corner_radius = 10
        border_color = COLOR_BORDE
        self.canvas_area.create_line(corner_radius, 2, width - corner_radius, 2, dash=dash_pattern, tags="borde", width=1, fill=border_color)
        self.canvas_area.create_line(width - 2, corner_radius, width - 2, height - corner_radius, dash=dash_pattern, tags="borde", width=1, fill=border_color)
        self.canvas_area.create_line(width - corner_radius, height - 2, corner_radius, height - 2, dash=dash_pattern, tags="borde", width=1, fill=border_color)
        self.canvas_area.create_line(2, height - corner_radius, 2, corner_radius, dash=dash_pattern, tags="borde", width=1, fill=border_color)
        self.canvas_area.create_arc(2, 2, corner_radius*2, corner_radius*2, start=90, extent=90, style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)
        self.canvas_area.create_arc(width - corner_radius*2, 2, width - 2, corner_radius*2, start=0, extent=90, style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)
        self.canvas_area.create_arc(width - corner_radius*2, height - corner_radius*2, width - 2, height - 2, start=270, extent=90, style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)
        self.canvas_area.create_arc(2, height - corner_radius*2, corner_radius*2, height - 2, start=180, extent=90, style="arc", outline=border_color, dash=dash_pattern, tags="borde", width=1)

    def seleccionar_imagenes(self):
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
                            continue
                        imagen_previa = leer_imagen(archivo, (100, 100))
                        self.imagenes_originales.append(imagen_previa)
                        self.archivos_imagenes.append(archivo)
                        imagenes_cargadas += 1
                    except Exception as e:
                        print(f"Error al cargar la imagen {archivo}: {str(e)}")
                if imagenes_cargadas > 0:
                    if len(self.imagenes_originales) == imagenes_cargadas:
                        self.ocultar_elementos_carga()
                    self.mostrar_grid_imagenes()
                else:
                    self.mostrar_error("No se pudo cargar ninguna imagen.")
            threading.Thread(target=cargar_y_mostrar).start()

    def ocultar_elementos_carga(self):
        if hasattr(self, 'icono_documento'):
            self.icono_documento.pack_forget()
        if hasattr(self, 'boton_seleccionar'):
            self.boton_seleccionar.pack_forget()
        if hasattr(self, 'texto_info'):
            self.texto_info.pack_forget()
        self.frame_imagenes.pack(fill="both", expand=True)

    def mostrar_grid_imagenes(self):
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
                width=110,
                height=90,
                corner_radius=8
            )
            frame_celda.grid(row=fila, column=columna, padx=8, pady=8)
            frame_celda.grid_propagate(False)
            if i < total_imagenes:
                imagen_previa = self.imagenes_originales[i]
                label_imagen = ctk.CTkLabel(
                    frame_celda,
                    text="",
                    image=imagen_previa
                )
                label_imagen.image = imagen_previa
                label_imagen.pack(expand=True, fill="both", padx=2, pady=(6, 0))
                # Info debajo
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
                        font=("Segoe UI", 8),
                        text_color=COLOR_TEXTO_SECUNDARIO,
                        fg_color="transparent",
                        anchor="center",
                        justify="center"
                    )
                    label_info.pack(pady=(0, 4))
                # Botón eliminar
                btn_eliminar = ctk.CTkButton(
                    frame_celda,
                    text="✕",
                    font=("Segoe UI", 12, "bold"),
                    fg_color="#e57373",
                    text_color="white",
                    hover_color="#ef9a9a",
                    width=24,
                    height=24,
                    corner_radius=12,
                    command=lambda idx=i: self.eliminar_imagen(idx)
                )
                btn_eliminar.place(relx=0.92, rely=0.08, anchor="ne")
            else:
                boton_mas = ctk.CTkButton(
                    frame_celda,
                    text="+",
                    font=("Segoe UI", 20, "bold"),
                    fg_color="#555555",
                    text_color="white",
                    hover_color="#888888",
                    width=40,
                    height=40,
                    corner_radius=20,
                    command=self.seleccionar_imagenes
                )
                boton_mas.place(relx=0.5, rely=0.5, anchor="center")
        for i in range(columnas):
            self.grid_imagenes.grid_columnconfigure(i, weight=1)
        for i in range(filas):
            self.grid_imagenes.grid_rowconfigure(i, weight=1)

    def eliminar_imagen(self, indice):
        if 0 <= indice < len(self.imagenes_originales):
            self.imagenes_originales.pop(indice)
            self.archivos_imagenes.pop(indice)
            if len(self.imagenes_originales) == 0:
                self.frame_imagenes.pack_forget()
                self.mostrar_elementos_carga()
            else:
                self.mostrar_grid_imagenes()

    def mostrar_error(self, mensaje):
        ventana = ctk.CTkToplevel()
        ventana.title("Error")
        ventana.geometry("300x120")
        ventana.resizable(False, False)
        ventana.configure(fg_color="white")
        label = ctk.CTkLabel(
            ventana,
            text=mensaje,
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXTO,
            wraplength=250
        )
        label.pack(pady=10)
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
        ventana.grab_set()

    def continuar_al_analisis(self):
        try:
            from forms.analysis_instructions_form import FormularioInstruccionesAnalisis
            FormularioInstruccionesAnalisis(self.contenedor_exterior, self.controlador, rutas_imagenes=self.archivos_imagenes)
        except Exception as e:
            print(f"Error al navegar a pantalla de instrucciones: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc() 