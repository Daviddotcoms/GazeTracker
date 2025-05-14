from PIL import Image
import os
import customtkinter as ctk

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
MAX_IMAGE_MB = 3

def es_extension_valida(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def es_tamano_valido(path):
    size_mb = os.path.getsize(path) / (1024 * 1024)
    return size_mb <= MAX_IMAGE_MB

def leer_imagen(path, size):
    img = Image.open(path)
    original_width, original_height = img.size
    target_width, target_height = size

    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    # Redimensionar manteniendo la relación de aspecto
    img = img.resize((new_width, new_height), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(new_width, new_height))  