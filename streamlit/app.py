import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CMPC Inteligencia Sur", layout="wide")
st.title("🌲 Dashboard de Monitoreo - Macrozona Sur")

try:
    if not os.path.exists("data/estado_predios.csv"):
        st.warning("🔄 Generando datos por primera vez... Ejecuta el workflow en GitHub Actions.")
        st.stop()

    df = pd.read_csv("data/estado_predios.csv")
    if df.empty:
        st.info("📊 No hay datos aún. Esperando actualización automática.")
        st.stop()

    df["nivel"] = df["nivel"].str.upper().str.strip()

    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Críticos", len(df[df["nivel"]=="CRÍTICO"]))
    col2.metric("🟠 Altos", len(df[df["nivel"]=="ALTO"]))
    col3.metric("🟡 Medios/Bajos", len(df[df["nivel"].isin(["MEDIO","BAJO"])]))

    # Mapa nativo de Streamlit (sin folium, carga instantánea)
    st.subheader("📍 Mapa de Predios y Nivel de Alerta")
    colores = df["nivel"].map({
        "CRÍTICO": "#FF0000",
        "ALTO": "#FFA500",
        "MEDIO": "#FFFF00",
        "BAJO": "#00FF00"
    })
    st.map(df, color=colores, size=120)

    st.subheader("📋 Tabla de Estado por Predio")
    st.dataframe(df, use_container_width=True)

    with st.sidebar:
        st.download_button("📥 Descargar Tabla CSV", df.to_csv(index=False), file_name="estado_predios.csv")
        st.info("🔄 Se actualiza automáticamente cada 4 horas vía GitHub Actions.")
except Exception as e:
    st.error(f"Error al cargar: {e}")
    st.stop()
