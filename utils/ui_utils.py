import customtkinter as ctk

def mostrar_error(mensaje, parent=None):
    error_window = ctk.CTkToplevel(parent)
    error_window.title("Error")
    error_window.geometry("800x200")
    error_window.resizable(False, False)
    label = ctk.CTkLabel(error_window, text=mensaje, font=("Segoe UI", 14))
    label.pack(pady=50)
    btn = ctk.CTkButton(error_window, text="Aceptar", command=error_window.destroy)
    btn.pack(pady=20)
    error_window.grab_set() 