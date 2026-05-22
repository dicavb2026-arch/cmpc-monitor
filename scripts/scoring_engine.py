import pandas as pd
import numpy as np
import os
import math

# Función matemática para calcular distancia (sin librerías externas pesadas)
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en km
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# 1. Crear carpeta de salida si no existe
os.makedirs("data", exist_ok=True)

# 2. Cargar datos limpios (generados por clean_data.py)
try:
    predios = pd.read_csv("data/predios_limpios.csv")
    intel = pd.read_csv("data/inteligencia_limpiada.csv")
except:
    print("⚠️ Advertencia: Archivos CSV no encontrados. Esperando primera ejecución limpia.")
    predios = pd.DataFrame()
    intel = pd.DataFrame()

if not predios.empty and not intel.empty:
    # 3. Preparar fechas
    hoy = pd.Timestamp.today()
    diff_days = (hoy - intel["fecha"]).dt.days
    intel["peso_tiempo"] = np.where(diff_days <= 7, 1.0,
                         np.where(diff_days <= 30, 0.6,
                         np.where(diff_days <= 90, 0.3, 0.1)))

    # 4. Calcular distancias manualmente (Loop)
    resultados = []
    mapeo_nivel = {"CRÍTICO": 0.4, "ALTO": 0.3, "MEDIO": 0.2, "BAJO": 0.1}

    for _, p in predios.iterrows():
        lat_p, lon_p = p.get("latitud"), p.get("longitud")
        if pd.isna(lat_p) or pd.isna(lon_p): continue

        score = 0.0
        nivel = "BAJO"

        # Filtrar eventos cercanos (menor a 20km)
        eventos_cercanos = intel.apply(
            lambda row: calcular_distancia_km(lat_p, lon_p, row["latitud"], row["longitud"]) if not pd.isna(row.get("latitud")) else 9999, 
            axis=1
        )
        indices_cercanos = eventos_cercanos[eventos_cercanos < 20].index
        proximos = intel.loc[indices_cercanos]

        if len(proximos) > 0:
            pesos_base = proximos["nivel_alerta"].map(mapeo_nivel).fillna(0.1)
            score = (pesos_base * proximos["peso_tiempo"]).sum() * 100
            score = min(score, 100.0)

            if score >= 75: nivel = "CRÍTICO"
            elif score >= 50: nivel = "ALTO"
            elif score >= 25: nivel = "MEDIO"
            else: nivel = "BAJO"

        resultados.append({
            "predio": p.get("nombre_predio", f"Predio_Sin_Nombre"),
            "comuna": p.get("comuna", "Desconocida"),
            "score": round(score, 1),
            "nivel": nivel
        })

    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_csv("data/estado_predios.csv", index=False)
    print(f"✅ Scoring completado exitosamente para {len(df_resultado)} predios.")
else:
    # Si no hay datos, crear un CSV vacío para que Streamlit no falle
    pd.DataFrame(columns=["predio", "comuna", "score", "nivel"]).to_csv("data/estado_predios.csv", index=False)
    print("⚠️ Datos vacíos, creando archivo base.")
