import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


np.random.seed(0)
x = np.linspace(0, 10, 100)
datos_originales = np.sin(x) + np.random.normal(0, 0.3, size=100)

smoothing_factor = 0.36
last_smoothed = None
datos_suavizados = []

for punto in datos_originales:
    if last_smoothed is None:
        last_smoothed = punto
    else:
        last_smoothed = (smoothing_factor * punto + (1 - smoothing_factor) * last_smoothed)
    datos_suavizados.append(last_smoothed)

plt.figure(figsize=(12, 6))
plt.plot(x, datos_originales, label='Datos originales', alpha=0.5)
plt.plot(x, datos_suavizados, label='Suavizado exponencial', linewidth=2, color='orange')
plt.title('Suavizado Exponencial de Datos Ruidosos')
plt.xlabel('Tiempo')
plt.ylabel('Valor')
plt.legend()
plt.grid(True)
plt.show()
