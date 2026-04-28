import pandas as pd
import numpy as np
import plotly.graph_objects as go

print("Iniciando secuencia de carga de datos...")
# 1. CARGAR DATOS
datos_acercamientos = pd.read_csv("asteroid_close_approaches_2015_2035 (1).csv")
datos_asteroides = pd.read_csv("near_earth_asteroids_2025 (1).csv")

# 2. FUSIONAR Y LIMPIAR
datos_fusionados = pd.merge(datos_acercamientos, datos_asteroides, on="full_name", how="inner")
datos_limpios = datos_fusionados.dropna(subset=['diameter_m', 'distance_au']).copy()

# 3. MATEMÁTICAS ESPACIALES (Generar coordenadas 3D)
# Usamos la distancia (UA) como el radio 'r' y generamos ángulos aleatorios
np.random.seed(42) # Para que las posiciones se mantengan iguales cada vez que corras el código
theta = np.random.uniform(0, 2 * np.pi, len(datos_limpios))
phi = np.random.uniform(0, np.pi, len(datos_limpios))
radio = datos_limpios['distance_au']

# Convertimos a coordenadas cartesianas (X, Y, Z)
datos_limpios['eje_x'] = radio * np.sin(phi) * np.cos(theta)
datos_limpios['eje_y'] = radio * np.sin(phi) * np.sin(theta)
datos_limpios['eje_z'] = radio * np.cos(phi)

# 4. CONSTRUIR EL ENTORNO 3D
fig = go.Figure()

# Añadir la Tierra en el centro exacto (0,0,0)
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers+text',
    marker=dict(size=15, color='#4da6ff', symbol='circle', opacity=0.9),
    text=["🌍 Tierra"], textposition="top center",
    name="Nuestro Planeta"
))

# Separar los asteroides para darles estilos distintos
peligrosos = datos_limpios[datos_limpios['pha'] == True]
inofensivos = datos_limpios[datos_limpios['pha'] == False]

# Añadir Asteroides Inofensivos (Grises)
fig.add_trace(go.Scatter3d(
    x=inofensivos['eje_x'], y=inofensivos['eje_y'], z=inofensivos['eje_z'],
    mode='markers',
    marker=dict(
        size=inofensivos['diameter_m'] / 30, # Escalar el tamaño real para la pantalla
        sizemin=2, color='lightgray', opacity=0.6
    ),
    hovertext=inofensivos['full_name'] + "<br>Tamaño: " + inofensivos['diameter_m'].astype(str) + "m",
    hoverinfo="text",
    name="Inofensivos"
))

# Añadir Asteroides Peligrosos (Rojos)
fig.add_trace(go.Scatter3d(
    x=peligrosos['eje_x'], y=peligrosos['eje_y'], z=peligrosos['eje_z'],
    mode='markers',
    marker=dict(
        size=peligrosos['diameter_m'] / 30,
        sizemin=4, color='#ff3333', opacity=0.9
    ),
    hovertext=peligrosos['full_name'] + "<br>Tamaño: " + peligrosos['diameter_m'].astype(str) + "m",
    hoverinfo="text",
    name="Peligrosos (PHA)"
))

# 5. DISEÑO DE LA "PANTALLA DE CONTROL"
fig.update_layout(
    title="Simulador 3D: Vecindario Terrestre",
    scene=dict(
        xaxis=dict(title='X (UA)', backgroundcolor="black", gridcolor="#222222", showbackground=True, zerolinecolor="white"),
        yaxis=dict(title='Y (UA)', backgroundcolor="black", gridcolor="#222222", showbackground=True, zerolinecolor="white"),
        zaxis=dict(title='Z (UA)', backgroundcolor="black", gridcolor="#222222", showbackground=True, zerolinecolor="white"),
        bgcolor="black"
    ),
    paper_bgcolor="black", font=dict(color="white"),
    margin=dict(l=0, r=0, b=0, t=50) # Quitar márgenes para que se vea más inmersivo
)

print("Desplegando simulación...")
fig.show()
