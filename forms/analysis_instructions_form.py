import customtkinter as ctk
from config import (
    COLOR_VERDE, COLOR_VERDE_HOVER, COLOR_GRIS_CLARO, COLOR_GRIS_MEDIO, 
    COLOR_TEXTO, COLOR_TEXTO_SECUNDARIO, COLOR_BORDE, COLOR_CUERPO_PRINCIPAL,
    COLOR_NARANJA, COLOR_NARANJA_HOVER, COLOR_GRIS_OSCURO, COLOR_GRIS_HOVER
)
from forms.sequence_form import FormularioSecuencia
from core.image_tracker import track_images

controlador_maestro = None

class FormularioInstruccionesAnalisis():

    def __init__(self, panel_principal, controlador=None, rutas_imagenes=None):
        self.controlador = controlador
        
        if self.controlador is None:
            global controlador_maestro
            self.controlador = controlador_maestro
            print(f"Usando controlador global: {type(self.controlador) if self.controlador else 'None'}")
        
        self.color_verde = COLOR_VERDE
        self.color_verde_hover = COLOR_VERDE_HOVER
        self.color_naranja = COLOR_NARANJA
        self.color_naranja_hover = COLOR_NARANJA_HOVER
        self.color_gris_claro = COLOR_GRIS_CLARO
        self.color_gris_medio = COLOR_GRIS_MEDIO
        self.color_borde = COLOR_BORDE
        self.color_texto = COLOR_TEXTO
        self.color_texto_secundario = COLOR_TEXTO_SECUNDARIO
        
        self.imagenes_originales = []
        self.rutas_imagenes = rutas_imagenes if rutas_imagenes is not None else []
        
        self.panel_principal = panel_principal
        
        for widget in self.panel_principal.winfo_children():
            widget.destroy()
        
        self.contenedor_principal = ctk.CTkFrame(panel_principal, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.contenedor_principal.pack(fill="both", expand=True)
        
        self.titulo_pagina = ctk.CTkLabel(
            self.contenedor_principal,
            text="Instrucciones Previas",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXTO,
            anchor="w",
            height=50
        )
        self.titulo_pagina.pack(fill="x", padx=20, pady=(20, 10), anchor="w")
        
        self.frame_contenido = ctk.CTkFrame(
            self.contenedor_principal,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            corner_radius=0,
            height=600
        )
        self.frame_contenido.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.frame_instrucciones = ctk.CTkFrame(
            self.frame_contenido,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            corner_radius=0
        )
        self.frame_instrucciones.pack(fill="x", pady=(0, 20))
        
        self.instrucciones = [
            "Seguir con la vista los puntos que aparecen en pantalla.",
            "Una vez finalizada la calibración, seguir en la misma postura.",
            "Esperar a la imagen a ser analizada.",
            "Analizar la imagen que visualiza en pantalla solo con el movimiento de la vista.",
            "Acabado el análisis podrá moverse."
        ]
        
        for i, texto in enumerate(self.instrucciones):
            frame_paso = ctk.CTkFrame(
                self.frame_instrucciones,
                fg_color=COLOR_CUERPO_PRINCIPAL
            )
            frame_paso.pack(fill="x", pady=(5, 0), anchor="w")
            
            ctk.CTkLabel(
                frame_paso,
                text=f"{i+1}. ",
                font=("Segoe UI", 12),
                text_color=COLOR_TEXTO,
                width=30
            ).pack(side="left", anchor="w")
            
            ctk.CTkLabel(
                frame_paso,
                text=texto,
                font=("Segoe UI", 12),
                text_color=COLOR_TEXTO,
                anchor="w"
            ).pack(side="left", fill="x", expand=True, anchor="w")
        
        self.frame_botones = ctk.CTkFrame(
            self.frame_contenido,
            fg_color=COLOR_CUERPO_PRINCIPAL
        )
        self.frame_botones.pack(fill="x", pady=(20, 10))
        
        ctk.CTkFrame(
            self.frame_botones,
            fg_color=COLOR_CUERPO_PRINCIPAL,
            width=300
        ).pack(side="left", expand=True, fill="x")

        self.boton_iniciar = ctk.CTkButton(
            self.frame_botones,
            text="Iniciar Análisis",
            font=("Segoe UI", 13),
            fg_color=COLOR_GRIS_OSCURO, 
            text_color=COLOR_TEXTO,
            hover_color=COLOR_GRIS_HOVER,
            height=36,
            width=150,
            corner_radius=18,
            command=self.iniciar_analisis
        )
        self.boton_iniciar.pack(side="right", padx=20)

    def establecer_imagenes(self, imagenes):
        """Establece las imágenes a procesar sin mostrarlas"""
        try:
            print(f"Recibiendo {len(imagenes) if imagenes else 0} imágenes")
            
            self.imagenes_originales = imagenes
            print("Imágenes almacenadas correctamente (sin mostrar previsualización)")
            
        except Exception as e:
            print(f"Error al establecer imágenes: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    def establecer_rutas_imagenes(self, rutas):
        """Establece las rutas de las imágenes para su uso posterior"""
        try:
            print(f"Recibiendo {len(rutas) if rutas else 0} rutas de imágenes en FormularioInstruccionesAnalisis")
            
            self.rutas_imagenes = rutas
            if len(self.rutas_imagenes) > 0:
                for i, ruta in enumerate(self.rutas_imagenes[:9]):
                    print(f"Ruta {i}: {ruta}")
                print("Rutas de imágenes guardadas correctamente")
        except Exception as e:
            print(f"Error al establecer rutas de imágenes: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    

    def limpiar_pantalla(self):
        """Limpia todos los elementos de la pantalla actual"""
        try:
            print("Limpiando pantalla...")
            
            self.contenedor_principal.pack_forget()
            
            for widget in self.contenedor_principal.winfo_children():
                widget.destroy()
                
            self.titulo_pagina = None
            self.frame_contenido = None
            self.frame_instrucciones = None
            self.frame_botones = None
            self.boton_iniciar = None
            
            self.contenedor_principal = ctk.CTkFrame(self.panel_principal, fg_color=COLOR_CUERPO_PRINCIPAL)
            self.contenedor_principal.pack(fill="both", expand=True)
            
            self.panel_principal.update_idletasks()
            
            print("Pantalla limpiada correctamente")
            return True
        except Exception as e:
            print(f"Error al limpiar pantalla: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en una ventana emergente"""
        ventana = ctk.CTkToplevel()
        ventana.title("Error")
        ventana.iconbitmap("./assets/eye_icon.ico")
        ventana.geometry("300x120")
        ventana.resizable(False, False)
        
        ventana.iconbitmap("./assets/eye_icon.ico")
        
        ventana.configure(fg_color="white")
        
        label = ctk.CTkLabel(
            ventana,
            text=mensaje,
            font=("Segoe UI", 14, "bold"),
            text_color=self.color_texto,
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
    
    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito en una ventana emergente"""
        ventana = ctk.CTkToplevel()
        ventana.title("Éxito")
        ventana.iconbitmap("./assets/eye_icon.ico")
        ventana.geometry("400x200")
        ventana.resizable(False, False)
        
        ventana.iconbitmap("./assets/eye_icon.ico")
        ventana.configure(fg_color="white")
        
        label = ctk.CTkLabel(
            ventana,
            text=mensaje,
            font=("Segoe UI", 14, "bold"),
            text_color=self.color_verde,
            wraplength=350
        )
        label.pack(pady=50)
        
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
    
    def iniciar_analisis(self):
        """Inicia el análisis usando las rutas de imágenes recibidas"""
        try:
            self.boton_iniciar.update_idletasks()
            print("Iniciando análisis...")
            if self.rutas_imagenes:
                track_images(self.rutas_imagenes, duration=40)
                FormularioSecuencia(self.panel_principal, self.controlador)
            else:
                self.mostrar_error("No hay rutas de imágenes para analizar.")
        except Exception as e:
            print(f"Error al iniciar análisis: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_error(f"Error al iniciar análisis: {e}")
        finally:
            # Restaurar el botón
            self.boton_iniciar.configure(text="Iniciar Análisis", state="normal", text_color=COLOR_TEXTO)
            self.boton_iniciar.update_idletasks() 