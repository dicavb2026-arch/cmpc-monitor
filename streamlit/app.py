import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="CMPC Inteligencia Sur", layout="wide")
st.title("🌲 Dashboard de Monitoreo - Macrozona Sur")

try:
    if not os.path.exists("data/estado_predios.csv"):
        st.warning("🔄 Generando datos por primera vez... Por favor ejecuta el workflow en GitHub Actions.")
        st.stop()

    df = pd.read_csv("data/estado_predios.csv")
    if df.empty:
        st.info("📊 No hay datos aún. Esperando primera actualización automática.")
        st.stop()

    df["nivel"] = df["nivel"].str.upper().str.strip()

    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Críticos", len(df[df["nivel"]=="CRÍTICO"]))
    col2.metric("🟠 Altos", len(df[df["nivel"]=="ALTO"]))
    col3.metric("🟡 Medios/Bajos", len(df[df["nivel"].isin(["MEDIO","BAJO"])]))

    m = folium.Map(location=[-38.7, -72.6], zoom_start=7)
    for _, row in df.iterrows():
        color = {"CRÍTICO":"red", "ALTO":"orange", "MEDIO":"yellow", "BAJO":"green"}.get(row["nivel"], "gray")
        lat = row.get("latitud") if "latitud" in df.columns else -38.7
        lon = row.get("longitud") if "longitud" in df.columns else -72.6
        
        if not pd.isna(lat) and not pd.isna(lon):
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color=color,
                fill=True,
                fill_color=color,
                popup=f"<b>{row.get('predio', 'N/A')}</b><br>Comuna: {row.get('comuna', 'N/A')}<br>Score: {row.get('score', 0)}<br>Nivel: {row['nivel']}"
            ).add_to(m)
    st_folium(m, width=700)

    st.dataframe(df, use_container_width=True)

    with st.sidebar:
        st.download_button("📥 Descargar Tabla CSV", df.to_csv(index=False), file_name="estado_predios.csv")
        st.info("🔄 Se actualiza automáticamente cada 4 horas vía GitHub Actions.")
except Exception as e:
    st.error(f"Error al cargar el dashboard: {e}")
    st.stop()
