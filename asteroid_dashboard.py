"""
🚀 RADAR DE ASTEROIDES CERCANOS — Dashboard Streamlit
Materia: Programación para Análisis de Datos
Datos: NASA JPL Close Approach Data (2015–2035) + Near Earth Asteroids 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Radar de Asteroides",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS mínimo para un look más espacial
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0a1a; }
    [data-testid="stSidebar"]          { background-color: #0d0d2b; }
    h1, h2, h3                         { color: #7ecfff; }
    .metric-container                  { background-color: #111130; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARGA Y PREPARACIÓN DE DATOS (cacheado)
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df_acercamientos = pd.read_csv(
        "asteroid_close_approaches_2015_2035 (1).csv",
        low_memory=False
    )
    df_asteroides = pd.read_csv(
        "near_earth_asteroids_2025 (1).csv",
        low_memory=False
    )

    df = pd.merge(df_acercamientos, df_asteroides, on="full_name", how="inner")
    df = df.dropna(subset=["diameter_m", "distance_au", "velocity_km_s"])
    df["close_approach_date"] = pd.to_datetime(df["close_approach_date"], errors="coerce")
    df["año"] = df["close_approach_date"].dt.year
    df["peligro_label"] = df["pha"].apply(lambda x: "⚠️ Peligroso (PHA)" if x else "✅ Inofensivo")

    # Coordenadas 3D aleatorias pero reproducibles
    rng = np.random.default_rng(42)
    n = len(df)
    theta = rng.uniform(0, 2 * np.pi, n)
    phi   = rng.uniform(0, np.pi, n)
    r     = df["distance_au"].values
    df["eje_x"] = r * np.sin(phi) * np.cos(theta)
    df["eje_y"] = r * np.sin(phi) * np.sin(theta)
    df["eje_z"] = r * np.cos(phi)

    return df


df = cargar_datos()


# ─────────────────────────────────────────────
# SIDEBAR — FILTROS GLOBALES
# ─────────────────────────────────────────────
st.sidebar.title("☄️ Controles del Radar")
st.sidebar.markdown("---")

# Filtro: solo peligrosos
solo_peligrosos = st.sidebar.toggle("Mostrar solo PHAs (peligrosos)", value=False)

# Filtro: categoría de tamaño
categorias = ["Todas"] + sorted(df["size_category"].dropna().unique().tolist())
cat_sel = st.sidebar.selectbox("Categoría de tamaño", categorias)

# Filtro: rango de años
año_min, año_max = int(df["año"].min()), int(df["año"].max())
rango_años = st.sidebar.slider(
    "Rango de años",
    año_min, año_max,
    (año_min, año_max)
)

# Filtro: rango de distancia
dist_min, dist_max = float(df["distance_au"].min()), float(df["distance_au"].max())
rango_dist = st.sidebar.slider(
    "Distancia máxima (UA)",
    dist_min, round(dist_max, 3),
    (dist_min, round(dist_max, 3)),
    step=0.001,
    format="%.3f UA"
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Fuente:** NASA JPL Small-Body Database  \n"
    "**Período:** 2015 – 2035  \n"
    "**PHA:** Potentially Hazardous Asteroid"
)

# ─── Aplicar filtros ───
mask = (
    (df["año"] >= rango_años[0]) &
    (df["año"] <= rango_años[1]) &
    (df["distance_au"] >= rango_dist[0]) &
    (df["distance_au"] <= rango_dist[1])
)
if solo_peligrosos:
    mask &= df["pha"] == True
if cat_sel != "Todas":
    mask &= df["size_category"] == cat_sel

df_f = df[mask].copy()


# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
col_titulo, col_logo = st.columns([5, 1])

with col_titulo:
    st.title("🛸 Radar de Asteroides Cercanos a la Tierra")
    st.caption("Visualización interactiva de acercamientos 2015 – 2035 | NASA JPL Data")

with col_logo:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg",
        width=110
    )

st.markdown("---")


# ─────────────────────────────────────────────
# KPIs PRINCIPALES
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("☄️ Total acercamientos", f"{len(df_f):,}")
k2.metric("⚠️ PHAs (peligrosos)",
          f"{df_f['pha'].sum():,}",
          delta=f"{df_f['pha'].mean()*100:.1f}% del total",
          delta_color="inverse")
k3.metric("📏 Diámetro promedio",
          f"{df_f['diameter_m'].mean():.1f} m")
k4.metric("🚀 Velocidad máx.",
          f"{df_f['velocity_km_s'].max():.1f} km/s")
k5.metric("🌕 Dist. mínima",
          f"{df_f['dist_lunar'].min():.2f} LD",
          help="Distancias lunares (1 LD ≈ 384,400 km)")

st.markdown("---")


# ─────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📡 Radar 2D",
    "🌐 Simulador 3D",
    "📊 Distribuciones",
    "📅 Serie de Tiempo",
    "🔍 Explorador de Datos",
    "🎬 Animación por Año",
])


# ══════════════════════════════════════════════
# TAB 1: RADAR 2D (tu radar.py mejorado)
# ══════════════════════════════════════════════
with tab1:
    st.subheader("📡 Radar de Alerta Temprana — Distancia vs. Velocidad")
    st.caption("Cada burbuja es un asteroide. El tamaño representa su diámetro real.")

    col_ctrl, _ = st.columns([1, 2])
    with col_ctrl:
        max_burbuja = st.slider("Tamaño máximo de burbuja", 20, 100, 50, key="burbuja_sz")

    fig_radar = px.scatter(
        df_f,
        x="distance_au",
        y="velocity_km_s",
        size="diameter_m",
        color="peligro_label",
        hover_name="full_name",
        hover_data={
            "close_approach_date": True,
            "size_category": True,
            "diameter_m": ":.1f",
            "velocity_km_s": ":.2f",
            "dist_lunar": ":.2f",
            "peligro_label": False,
        },
        labels={
            "distance_au": "Distancia mínima a la Tierra (UA)",
            "velocity_km_s": "Velocidad de impacto (km/s)",
            "diameter_m": "Diámetro (m)",
            "peligro_label": "Clasificación",
        },
        color_discrete_map={
            "⚠️ Peligroso (PHA)": "#ff3333",
            "✅ Inofensivo": "#33cc33",
        },
        size_max=max_burbuja,
        template="plotly_dark",
        title="",
    )
    fig_radar.update_layout(
        height=550,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,5,20,0.8)",
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Mini tabla de los más cercanos
    st.subheader("🔴 Top 10 acercamientos más cercanos")
    top_cercanos = (
        df_f[["full_name", "close_approach_date", "distance_au",
              "dist_lunar", "velocity_km_s", "diameter_m", "peligro_label"]]
        .sort_values("distance_au")
        .head(10)
        .rename(columns={
            "full_name": "Asteroide",
            "close_approach_date": "Fecha",
            "distance_au": "Dist. (UA)",
            "dist_lunar": "Dist. Lunar (LD)",
            "velocity_km_s": "Velocidad (km/s)",
            "diameter_m": "Diámetro (m)",
            "peligro_label": "¿Peligroso?",
        })
    )
    top_cercanos["Fecha"] = top_cercanos["Fecha"].dt.strftime("%Y-%m-%d")
    st.dataframe(top_cercanos, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# TAB 2: SIMULADOR 3D (tu radar2.py mejorado)
# ══════════════════════════════════════════════
with tab2:
    st.subheader("🌐 Simulador 3D — Vecindario Terrestre")
    st.caption(
        "La posición espacial es ilustrativa (ángulos aleatorios). "
        "La distancia al origen sí representa la UA real."
    )

    # Limitar puntos para que 3D no sea lento
    limite_3d = st.slider(
        "Máx. asteroides en 3D (más = más lento)", 500, 5000, 1500, step=500
    )
    df_3d = df_f.sample(min(limite_3d, len(df_f)), random_state=42)

    peligrosos  = df_3d[df_3d["pha"] == True]
    inofensivos = df_3d[df_3d["pha"] == False]

    fig3d = go.Figure()

    # Tierra
    fig3d.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers+text",
        marker=dict(size=14, color="#4da6ff", opacity=0.95),
        text=["🌍 Tierra"], textposition="top center",
        name="Tierra"
    ))

    # Inofensivos
    fig3d.add_trace(go.Scatter3d(
        x=inofensivos["eje_x"], y=inofensivos["eje_y"], z=inofensivos["eje_z"],
        mode="markers",
        marker=dict(
            size=np.clip(inofensivos["diameter_m"] / 25, 2, 12),
            color="lightgray", opacity=0.5
        ),
        hovertext=(
            inofensivos["full_name"] + "<br>" +
            "Tamaño: " + inofensivos["diameter_m"].round(0).astype(int).astype(str) + " m<br>" +
            "Dist: " + inofensivos["distance_au"].round(4).astype(str) + " UA<br>" +
            "Vel: " + inofensivos["velocity_km_s"].round(2).astype(str) + " km/s"
        ),
        hoverinfo="text",
        name="✅ Inofensivos"
    ))

    # Peligrosos
    fig3d.add_trace(go.Scatter3d(
        x=peligrosos["eje_x"], y=peligrosos["eje_y"], z=peligrosos["eje_z"],
        mode="markers",
        marker=dict(
            size=np.clip(peligrosos["diameter_m"] / 25, 4, 16),
            color="#ff4444", opacity=0.9,
            line=dict(color="#ff0000", width=1)
        ),
        hovertext=(
            peligrosos["full_name"] + "<br>" +
            "⚠️ POTENCIALMENTE PELIGROSO<br>" +
            "Tamaño: " + peligrosos["diameter_m"].round(0).astype(int).astype(str) + " m<br>" +
            "Dist: " + peligrosos["distance_au"].round(4).astype(str) + " UA<br>" +
            "Vel: " + peligrosos["velocity_km_s"].round(2).astype(str) + " km/s"
        ),
        hoverinfo="text",
        name="⚠️ Peligrosos (PHA)"
    ))

    fig3d.update_layout(
        scene=dict(
            xaxis=dict(title="X (UA)", backgroundcolor="black",
                       gridcolor="#1a1a2e", showbackground=True),
            yaxis=dict(title="Y (UA)", backgroundcolor="black",
                       gridcolor="#1a1a2e", showbackground=True),
            zaxis=dict(title="Z (UA)", backgroundcolor="black",
                       gridcolor="#1a1a2e", showbackground=True),
            bgcolor="black"
        ),
        paper_bgcolor="black",
        font=dict(color="white"),
        height=620,
        margin=dict(l=0, r=0, b=0, t=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="#333",
            borderwidth=1
        )
    )
    st.plotly_chart(fig3d, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3: DISTRIBUCIONES
# ══════════════════════════════════════════════
with tab3:
    st.subheader("📊 Distribuciones y Comparativas")

    col_a, col_b = st.columns(2)

    with col_a:
        # Distribución por categoría de tamaño
        conteos = df_f["size_category"].value_counts().reset_index()
        conteos.columns = ["Categoría", "Cantidad"]
        fig_cat = px.bar(
            conteos, x="Cantidad", y="Categoría", orientation="h",
            color="Cantidad", color_continuous_scale="Blues",
            template="plotly_dark", title="Asteroides por Categoría de Tamaño"
        )
        fig_cat.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)",
                              coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_b:
        # Histograma de velocidades
        fig_vel = px.histogram(
            df_f, x="velocity_km_s", color="peligro_label",
            nbins=60, barmode="overlay",
            color_discrete_map={
                "⚠️ Peligroso (PHA)": "#ff3333",
                "✅ Inofensivo": "#33cc33",
            },
            labels={"velocity_km_s": "Velocidad (km/s)", "peligro_label": ""},
            template="plotly_dark",
            title="Distribución de Velocidades"
        )
        fig_vel.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)",
                              legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_vel, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        # Box plot diámetro por categoría
        fig_box = px.box(
            df_f, x="size_category", y="diameter_m",
            color="peligro_label",
            color_discrete_map={
                "⚠️ Peligroso (PHA)": "#ff3333",
                "✅ Inofensivo": "#33cc33",
            },
            labels={
                "size_category": "Categoría",
                "diameter_m": "Diámetro (m)",
                "peligro_label": ""
            },
            template="plotly_dark",
            title="Diámetro por Categoría (Box Plot)"
        )
        fig_box.update_xaxes(tickangle=-20)
        fig_box.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)",
                              legend=dict(orientation="h", y=-0.35))
        st.plotly_chart(fig_box, use_container_width=True)

    with col_d:
        # Scatter velocidad vs diámetro
        fig_sc = px.scatter(
            df_f.sample(min(3000, len(df_f)), random_state=1),
            x="diameter_m", y="velocity_km_s",
            color="peligro_label",
            opacity=0.5,
            color_discrete_map={
                "⚠️ Peligroso (PHA)": "#ff3333",
                "✅ Inofensivo": "#33cc33",
            },
            labels={
                "diameter_m": "Diámetro (m)",
                "velocity_km_s": "Velocidad (km/s)",
                "peligro_label": ""
            },
            template="plotly_dark",
            title="Velocidad vs. Diámetro"
        )
        fig_sc.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)",
                              legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_sc, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4: SERIE DE TIEMPO
# ══════════════════════════════════════════════
with tab4:
    st.subheader("📅 Acercamientos a lo Largo del Tiempo")

    # Acercamientos por mes
    df_f["mes"] = df_f["close_approach_date"].dt.to_period("M").astype(str)
    por_mes = df_f.groupby(["mes", "peligro_label"]).size().reset_index(name="count")

    fig_ts = px.bar(
        por_mes, x="mes", y="count", color="peligro_label",
        color_discrete_map={
            "⚠️ Peligroso (PHA)": "#ff3333",
            "✅ Inofensivo": "#33cc33",
        },
        labels={"mes": "Mes", "count": "Número de acercamientos", "peligro_label": ""},
        template="plotly_dark",
        title="Acercamientos mensuales (2015 – 2035)"
    )
    fig_ts.update_layout(
        height=420, paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.2),
        xaxis=dict(tickangle=-45, nticks=30)
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # Por año — promedio de distancia
    por_año = df_f.groupby("año").agg(
        acercamientos=("full_name", "count"),
        dist_prom=("distance_au", "mean"),
        phas=("pha", "sum")
    ).reset_index()

    col_e, col_f = st.columns(2)
    with col_e:
        fig_na = px.line(
            por_año, x="año", y="acercamientos",
            markers=True, template="plotly_dark",
            title="Total de acercamientos por año",
            labels={"año": "Año", "acercamientos": "Acercamientos"}
        )
        fig_na.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_na, use_container_width=True)

    with col_f:
        fig_dp = px.line(
            por_año, x="año", y="dist_prom",
            markers=True, template="plotly_dark",
            color_discrete_sequence=["#ffd700"],
            title="Distancia promedio anual (UA)",
            labels={"año": "Año", "dist_prom": "Distancia promedio (UA)"}
        )
        fig_dp.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_dp, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 5: EXPLORADOR DE DATOS
# ══════════════════════════════════════════════
with tab5:
    st.subheader("🔍 Explorador de Asteroides")

    # Búsqueda por nombre
    busqueda = st.text_input("🔎 Buscar asteroide por nombre", placeholder="ej. 99942 Apophis")

    cols_mostrar = [
        "full_name", "close_approach_date", "distance_au", "dist_lunar",
        "velocity_km_s", "diameter_m", "size_category", "peligro_label",
        "class", "absolute_magnitude"
    ]

    df_exp = df_f[cols_mostrar].copy()
    df_exp["close_approach_date"] = df_exp["close_approach_date"].dt.strftime("%Y-%m-%d")
    df_exp = df_exp.rename(columns={
        "full_name": "Nombre",
        "close_approach_date": "Fecha acercamiento",
        "distance_au": "Dist. (UA)",
        "dist_lunar": "Dist. Lunar (LD)",
        "velocity_km_s": "Vel. (km/s)",
        "diameter_m": "Diámetro (m)",
        "size_category": "Categoría",
        "peligro_label": "¿Peligroso?",
        "class": "Clase orbital",
        "absolute_magnitude": "Magnitud abs. (H)",
    })

    if busqueda:
        df_exp = df_exp[df_exp["Nombre"].str.contains(busqueda, case=False, na=False)]
        st.caption(f"Resultados encontrados: {len(df_exp)}")

    st.dataframe(
        df_exp.sort_values("Dist. (UA)"),
        use_container_width=True,
        hide_index=True,
        height=450
    )

    # Descarga
    csv_export = df_exp.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar datos filtrados (.csv)",
        data=csv_export,
        file_name="asteroides_filtrados.csv",
        mime="text/csv"
    )

    # Estadísticas rápidas
    st.subheader("📐 Estadísticas del conjunto filtrado")
    st.dataframe(
        df_f[["distance_au", "velocity_km_s", "diameter_m", "dist_lunar"]]
        .describe()
        .T
        .rename(columns={
            "count": "Registros", "mean": "Media", "std": "Desv. Estándar",
            "min": "Mínimo", "25%": "Q1", "50%": "Mediana",
            "75%": "Q3", "max": "Máximo"
        })
        .round(4),
        use_container_width=True
    )


# ══════════════════════════════════════════════
# TAB 6: ANIMACIÓN POR AÑO
# ══════════════════════════════════════════════
with tab6:
    st.subheader("🎬 Animación de Acercamientos por Año")
    st.caption(
        "Cada burbuja es un asteroide. "
        "Usa el botón ▶ para reproducir o arrastra el slider de año."
    )

    col_anim1, col_anim2 = st.columns([1, 1])
    with col_anim1:
        max_por_año = st.slider(
            "Máx. asteroides por año (más = más lento)",
            100, 800, 300, step=100, key="anim_limit"
        )
    with col_anim2:
        eje_x_anim = st.selectbox(
            "Eje X",
            ["distance_au", "velocity_km_s", "diameter_m"],
            index=0,
            format_func=lambda c: {
                "distance_au": "Distancia (UA)",
                "velocity_km_s": "Velocidad (km/s)",
                "diameter_m": "Diámetro (m)",
            }[c],
            key="anim_x"
        )

    # Preparar datos: muestrear N asteroides por año para fluidez
    frames_list = []
    for yr, grupo in df_f.groupby("año"):
        muestra = grupo.sample(min(max_por_año, len(grupo)), random_state=int(yr))
        frames_list.append(muestra)
    df_anim = pd.concat(frames_list, ignore_index=True)
    df_anim["año_str"] = df_anim["año"].astype(str)

    # Límites fijos de los ejes para que la animación no salte de escala
    x_range = [df_anim[eje_x_anim].quantile(0.01), df_anim[eje_x_anim].quantile(0.99)]
    y_range = [df_anim["dist_lunar"].quantile(0.01), df_anim["dist_lunar"].quantile(0.99)]

    eje_x_label = {
        "distance_au": "Distancia mínima a la Tierra (UA)",
        "velocity_km_s": "Velocidad de impacto (km/s)",
        "diameter_m": "Diámetro (m)",
    }[eje_x_anim]

    fig_anim = px.scatter(
        df_anim,
        x=eje_x_anim,
        y="dist_lunar",
        size="diameter_m",
        color="peligro_label",
        animation_frame="año_str",
        animation_group="full_name",
        hover_name="full_name",
        hover_data={
            "close_approach_date": True,
            "velocity_km_s": ":.2f",
            "diameter_m": ":.0f",
            "size_category": True,
            "peligro_label": False,
            "año_str": False,
        },
        labels={
            eje_x_anim: eje_x_label,
            "dist_lunar": "Distancia Lunar (LD)",
            "diameter_m": "Diámetro (m)",
            "peligro_label": "Clasificación",
        },
        color_discrete_map={
            "⚠️ Peligroso (PHA)": "#ff3333",
            "✅ Inofensivo": "#33cc33",
        },
        size_max=55,
        range_x=x_range,
        range_y=y_range,
        template="plotly_dark",
    )

    fig_anim.update_layout(
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,5,20,0.9)",
        legend=dict(orientation="h", y=-0.15),
        # Velocidad de transición entre frames (ms)
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 800, "redraw": True},
                                 "fromcurrent": True}],
                 "label": "▶ Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0, "redraw": True},
                                   "mode": "immediate"}],
                 "label": "⏸ Pause", "method": "animate"},
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 10},
            "showactive": False,
            "type": "buttons",
            "x": 0.1, "xanchor": "right",
            "y": 0, "yanchor": "top",
        }],
        sliders=[{
            "currentvalue": {
                "prefix": "Año: ",
                "font": {"color": "#7ecfff", "size": 16},
            },
            "pad": {"t": 50},
        }],
    )

    # Añadir línea horizontal de referencia: 1 LD = la Luna
    fig_anim.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="#ffd700",
        annotation_text="🌕 1 distancia lunar",
        annotation_position="top right",
        annotation_font_color="#ffd700",
    )

    st.plotly_chart(fig_anim, use_container_width=True)

    st.info(
        "**¿Qué ves?**  Cada punto es un acercamiento de ese año. "
        "Los rojos son PHAs (Potentially Hazardous Asteroids). "
        "La línea dorada marca 1 distancia lunar (~384,400 km) — "
        "cualquier asteroide por debajo de ella pasó **más cerca que la Luna**."
    )
