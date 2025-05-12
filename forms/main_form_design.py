import customtkinter as ctk
from config import COLOR_BARRA_SUPERIOR, COLOR_GRIS_CLARO, COLOR_TEXTO

import utils.window_utils as window_utils
import utils.image_utils as util_img
from utils.path_utils import resource_path

# Pantallas
from forms.home_form import FormularioInicio
from forms.analyze_image_form import FormularioAnalizarImagen
from forms.sequence_form import FormularioSecuencia

class FormularioMaestroDesign(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurar el tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Variable para rastrear la página actual
        self.current_page = None
        
        # Colores personalizados
        self.color_verde = COLOR_BARRA_SUPERIOR
        self.color_gris_claro = COLOR_GRIS_CLARO
        self.color_texto = COLOR_TEXTO
        
        self.config_window()
        self.paneles()
        self.controles_barra_superior()        
        self.controles_menu_lateral()
        self.controles_cuerpo()
        # Abrir inicio por defecto
        self.cambiar_tab(0, self.abrir_inicio)

    def config_window(self):
        # Configuración inicial de la ventana
        self.title('Gaze Tracker')
        self.iconbitmap(resource_path("assets/eye_icon.ico"))

        w, h = 1024, 600
        window_utils.centrar_ventana(self, w, h)
        
        # Configurar transparencia
        self.attributes('-alpha', 0.98)  # 98% de opacidad

        # Configuración de colores
        self.configure(fg_color="white")

    def paneles(self):        
        # Crear paneles: barra superior, menú lateral y cuerpo principal
        self.barra_superior = ctk.CTkFrame(
            self, 
            height=50,
            fg_color=self.color_verde,
            corner_radius=0
        )
        self.barra_superior.pack(side="top", fill="x")      

        # Panel contenedor para menú lateral y cuerpo principal
        self.panel_contenido = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=0
        )
        self.panel_contenido.pack(side="top", fill="both", expand=True)

        # Menú lateral (izquierda)
        self.menu_lateral = ctk.CTkFrame(
            self.panel_contenido, 
            width=220,
            fg_color=self.color_gris_claro,
            corner_radius=0
        )
        self.menu_lateral.pack(side="left", fill="y", expand=False)
        
        # Espacio adicional después de la sombra
        self.espacio = ctk.CTkFrame(
            self.panel_contenido,
            width=15,
            fg_color="white",
            corner_radius=0
        )
        self.espacio.pack(side="left", fill="y", expand=False)
        
        # Cuerpo principal (derecha)
        self.cuerpo_principal = ctk.CTkFrame(
            self.panel_contenido, 
            fg_color="white"
        )
        self.cuerpo_principal.pack(side="right", fill="both", expand=True)
    
    def controles_barra_superior(self):
        # Configuración de la barra superior
        # Frame para el título y el ícono
        self.frame_titulo = ctk.CTkFrame(
            self.barra_superior,
            fg_color="transparent"
        )
        self.frame_titulo.pack(side="left", padx=20, pady=10)

        self.labelTitulo = ctk.CTkLabel(
            self.frame_titulo, 
            text="👁️GAZE TRACKER",
            text_color="white",
            font=("Segoe UI", 16, "bold")
        )
        self.labelTitulo.pack(side="left")

    def controles_menu_lateral(self):
        # Espacio superior
        ctk.CTkLabel(self.menu_lateral, text="", fg_color="transparent", height=20).pack()
        
        # Definir las opciones del menú
        self.tabs = []
        tabs_info = [
            ("Inicio", "🏠", self.abrir_inicio),
            ("Analizar", "🔍", self.abrir_analizar_imagen),  # Nombre más corto para texto más compacto
            ("Secuencia", "📷", self.abrir_secuencia),       # Nombre más corto para texto más compacto
        ]
        
        # Crear los botones del menú
        for i, (text, icon, comando) in enumerate(tabs_info):
            tab = ctk.CTkButton(
                self.menu_lateral,
                text=f"{icon}  {text}",
                font=("Segoe UI", 14),  # Cambiar a Segoe UI y aumentar tamaño
                fg_color="transparent",
                text_color=self.color_texto,
                hover_color="#e0e0e0",
                anchor="w",
                height=48,  # Aumentar altura del botón
                corner_radius=8,  # Aumentar redondeo de esquinas
                border_width=0,
                command=lambda cmd=comando, idx=i: self.cambiar_tab(idx, cmd)
            )
            tab.pack(side="top", fill="x", padx=12, pady=4)  # Aumentar el padding
            self.tabs.append(tab)
    
    def controles_cuerpo(self):
        # Frame vacío para el cuerpo principal
        self.contenido = ctk.CTkFrame(
            self.cuerpo_principal, 
            fg_color="white"
        )
        self.contenido.pack(fill="both", expand=True, padx=20, pady=20)

    def cambiar_tab(self, tab_index, comando):
        # Restablecer todas las pestañas
        for i, tab in enumerate(self.tabs):
            if i == tab_index:
                # Activar la pestaña seleccionada
                tab.configure(
                    fg_color=self.color_verde,
                    text_color="white", 
                    hover_color=self.color_verde
                )
            else:
                # Desactivar las demás pestañas
                tab.configure(
                    fg_color="transparent",
                    text_color=self.color_texto,
                    hover_color="#e0e0e0"
                )
        
        # Ejecutar el comando asociado a la pestaña
        comando()

    def abrir_inicio(self):   
        self.limpiar_panel(self.cuerpo_principal)     
        FormularioInicio(self.cuerpo_principal)
        
    def abrir_analizar_imagen(self):   
        self.limpiar_panel(self.cuerpo_principal)     
        FormularioAnalizarImagen(self.cuerpo_principal)

    def abrir_secuencia(self):           
        self.limpiar_panel(self.cuerpo_principal)     
        FormularioSecuencia(self.cuerpo_principal)

    def limpiar_panel(self, panel):
        # Función para limpiar el contenido del panel
        for widget in panel.winfo_children():
            # Intentar detener videos si es un FormularioInicio
            try:
                if hasattr(widget, '_FormularioInicio__instance'):
                    if hasattr(widget._FormularioInicio__instance, 'on_destruir'):
                        widget._FormularioInicio__instance.on_destruir()
            except Exception as e:
                print(f"Error al intentar detener video: {e}")
                
            # Intentar un enfoque alternativo para detectar el formulario
            for attr_name in dir(widget):
                if 'formulario' in attr_name.lower():
                    try:
                        formulario = getattr(widget, attr_name)
                        if hasattr(formulario, 'on_destruir'):
                            formulario.on_destruir()
                            print("Video detenido correctamente")
                    except Exception as e:
                        print(f"Error al intentar detener video (alternativo): {e}")

            # Destruir el widget
            widget.destroy() 