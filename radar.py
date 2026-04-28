import pandas as pd
import plotly.express as px

# 1. CARGAR LOS DATOS
print("Cargando bases de datos...")
# Asegúrate de que los nombres de los archivos coincidan con los tuyos
df_acercamientos = pd.read_csv("asteroid_close_approaches_2015_2035 (1).csv")
df_asteroides = pd.read_csv("near_earth_asteroids_2025 (1).csv")

# 2. UNIR LAS BASES DE DATOS
# Usamos 'full_name' que es la columna que ambos archivos tienen en común
df_completo = pd.merge(df_acercamientos, df_asteroides, on="full_name", how="inner")

# 3. LIMPIAR LOS DATOS
# Nos quedamos solo con los que tienen un diámetro registrado para poder graficar su tamaño
df_limpio = df_completo.dropna(subset=['diameter_m', 'distance_au', 'velocity_km_s'])

# 4. CREAR EL RADAR INTERACTIVO
print("Generando el radar...")
fig = px.scatter(
    df_limpio,
    x="distance_au",           # Eje X: Qué tan cerca pasan de la Tierra
    y="velocity_km_s",         # Eje Y: Qué tan rápido van
    size="diameter_m",         # Tamaño del punto: El tamaño real del asteroide
    color="pha",               # Color: Si es peligroso (True) o no (False)
    hover_name="full_name",    # Al pasar el mouse, muestra el nombre
    hover_data={               # Datos extra al pasar el mouse
        "close_approach_date": True,
        "size_category": True,
        "pha": False,          # Lo ocultamos aquí porque ya lo indica el color
        "diameter_m": ":.2f",  # Muestra el diámetro con 2 decimales
        "velocity_km_s": ":.2f"
    },
    title="Radar de Alerta Temprana: Asteroides Cercanos (2015-2035)",
    labels={
        "distance_au": "Distancia Mínima a la Tierra (Unidades Astronómicas)",
        "velocity_km_s": "Velocidad de Impacto (km/s)",
        "diameter_m": "Diámetro (metros)",
        "pha": "¿Es Potencialmente Peligroso?"
    },
    color_discrete_map={True: '#ff3333', False: '#33cc33'}, # Peligrosos en rojo, inofensivos en verde
    size_max=60,               # Tamaño máximo de las burbujas para que no tapen todo
    template="plotly_dark"     # Le da un aspecto oscuro estilo radar espacial
)

# 5. MOSTRAR EL RESULTADO
fig.show()