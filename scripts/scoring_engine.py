import pandas as pd
import numpy as np
import math
import os

# Asegurar carpeta de salida
os.makedirs("data", exist_ok=True)

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad)*math.cos(lat2_rad)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generar_tabla_vacia():
    pd.DataFrame(columns=["predio", "comuna", "score", "nivel"]).to_csv("data/estado_predios.csv", index=False)
    print("⚠️ Datos insuficientes. Se generó tabla base.")
    exit()

try:
    predios = pd.read_csv("data/predios_limpios.csv")
    intel = pd.read_csv("data/inteligencia_limpiada.csv")
except Exception as e:
    print(f"❌ Error al leer CSVs: {e}")
    generar_tabla_vacia()

if predios.empty or intel.empty:
    generar_tabla_vacia()

# 🔑 CORRECCIÓN CRÍTICA: Forzar conversión de fechas y limpiar datos inválidos
intel["fecha"] = pd.to_datetime(intel["fecha"], errors="coerce", utc=True)
intel = intel.dropna(subset=["fecha", "latitud", "longitud"])

if intel.empty:
    print("⚠️ No hay eventos con fechas/coordenadas válidas.")
    generar_tabla_vacia()

hoy = pd.Timestamp.now(tz="UTC")
diff_days = (hoy - intel["fecha"]).dt.days.astype(float)
intel["peso_tiempo"] = np.where(diff_days <= 7, 1.0,
                     np.where(diff_days <= 30, 0.6,
                     np.where(diff_days <= 90, 0.3, 0.1)))

resultados = []
mapeo_nivel = {"CRÍTICO": 0.4, "ALTO": 0.3, "MEDIO": 0.2, "BAJO": 0.1}

for _, p in predios.iterrows():
    lat_p, lon_p = p.get("latitud"), p.get("longitud")
    if pd.isna(lat_p) or pd.isna(lon_p): continue

    distancias = [calcular_distancia_km(lat_p, lon_p, row["latitud"], row["longitud"]) for _, row in intel.iterrows()]
    indices_cercanos = [i for i, d in enumerate(distancias) if d < 20]
    proximos = intel.iloc[indices_cercanos]

    if len(proximos) == 0:
        score, nivel = 0.0, "BAJO"
    else:
        pesos_base = proximos["nivel_alerta"].map(mapeo_nivel).fillna(0.1)
        score = (pesos_base * proximos["peso_tiempo"]).sum() * 100
        score = min(score, 100.0)

        if score >= 75: nivel = "CRÍTICO"
        elif score >= 50: nivel = "ALTO"
        elif score >= 25: nivel = "MEDIO"
        else: nivel = "BAJO"

    resultados.append({
        "predio": p.get("nombre_predio", f"Predio_{p.get('id', 'X')}"),
        "comuna": p.get("comuna", "Desconocida"),
        "score": round(score, 1),
        "nivel": nivel
    })

pd.DataFrame(resultados).to_csv("data/estado_predios.csv", index=False)
print(f"✅ Scoring completado exitosamente para {len(resultados)} predios.")
