from PIL import ImageTk, Image

def leer_imagen(path, size):
    # Abrir la imagen original
    img = Image.open(path)
    original_width, original_height = img.size
    target_width, target_height = size

    # Calcular la nueva relación de aspecto
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    # Redimensionar manteniendo la relación de aspecto
    img = img.resize((new_width, new_height), Image.ADAPTIVE)
    return ImageTk.PhotoImage(img)  