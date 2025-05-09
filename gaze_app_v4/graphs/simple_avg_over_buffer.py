import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(0)
x = np.linspace(0, 10, 100)
datos_originales = np.sin(x) + np.random.normal(0, 0.3, size=100)

N = 5

def promedio_buffer(datos, N):
    datos_suavizados = []
    for i in range(len(datos)):
        inicio = max(0, i - N + 1)
        ventana = datos[inicio:i+1]
        promedio = np.mean(ventana)
        datos_suavizados.append(promedio)
    return datos_suavizados

datos_suavizados = promedio_buffer(datos_originales, N)

plt.figure(figsize=(12, 6))
plt.plot(x, datos_originales, label='Datos originales', alpha=0.5)
plt.plot(x, datos_suavizados, label='Promedio con buffer', linewidth=2, color='orange')
plt.title('Promedio Simple sobre Buffer')
plt.xlabel('Tiempo')
plt.ylabel('Valor')
plt.legend()
plt.grid(True)
plt.show()
