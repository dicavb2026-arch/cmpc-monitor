import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="CMPC Inteligencia Sur", layout="wide")
st.title("🌲 Dashboard de Monitoreo - Macrozona Sur")

try:
    df = pd.read_csv("data/estado_predios.csv")
    df["nivel"] = df["nivel"].str.upper()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Críticos", len(df[df["nivel"]=="CRÍTICO"]))
    col2.metric("🟠 Altos", len(df[df["nivel"]=="ALTO"]))
    col3.metric("🟡 Medios/Bajos", len(df[df["nivel"].isin(["MEDIO","BAJO"])])

    m = folium.Map(location=[-38.7, -72.6], zoom_start=7)
    for _, row in df.iterrows():
        color = {"CRÍTICO":"red", "ALTO":"orange", "MEDIO":"yellow", "BAJO":"green"}[row["nivel"]]
        folium.CircleMarker(location=[row.get("latitud",-38.7), row.get("longitud",-72.6)],
                            radius=8, color=color, fill=True, fill_color=color,
                            popup=f"{row['predio']} | {row['comuna']} | Score: {row['score']}").add_to(m)
    st_folium(m, width=700)
    
    st.dataframe(df, use_container_width=True)
    
    with st.sidebar:
        st.download_button("📥 Descargar Tabla CSV", df.to_csv(index=False), file_name="estado_predios.csv")
        st.info("🔄 Se actualiza automáticamente cada 4 horas.")
except Exception as e:
    st.error(f"Esperando primera ejecución automática... (o haz clic en 'Run workflow' en GitHub): {e}")
