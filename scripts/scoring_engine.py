import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

# 1. Cargar datos limpios
predios = pd.read_csv("data/predios_limpios.csv")
intel = pd.read_csv("data/inteligencia_limpiada.csv")

# 2. Forzar conversión de fechas a datetime (evita el error de str vs Timestamp)
intel["fecha"] = pd.to_datetime(intel["fecha"], errors="coerce", utc=True)
intel = intel.dropna(subset=["fecha"])
intel = intel.dropna(subset=["latitud", "longitud"])

# 3. Calcular decaimiento temporal
hoy = pd.Timestamp.now(tz="UTC")
diff_days = (hoy - intel["fecha"]).dt.days
intel["peso_tiempo"] = np.where(diff_days <= 7, 1.0,
                     np.where(diff_days <= 30, 0.6,
                     np.where(diff_days <= 90, 0.3, 0.1)))

# 4. Preparar coordenadas
if "latitud" not in predios.columns or "longitud" not in predios.columns:
    print("❌ Error: Los predios no tienen columnas latitud/longitud válidas.")
    exit()

predios_coords = predios[["latitud", "longitud"]].values
intel_coords = intel[["latitud", "longitud"]].values

if len(intel_coords) == 0:
    print("⚠️ No hay eventos con coordenadas válidas. Generando tabla base.")
    pd.DataFrame({"predio": predios["nombre_predio"], "comuna": predios["comuna"], "score": 0, "nivel": "BAJO"}).to_csv("data/estado_predios.csv", index=False)
    exit()

distancias = cdist(predios_coords, intel_coords) * 111  # km aproximados

# 5. Calcular scoring por predio
resultados = []
mapeo_nivel = {"CRÍTICO": 0.4, "ALTO": 0.3, "MEDIO": 0.2, "BAJO": 0.1}

for i, (_, p) in enumerate(predios.iterrows()):
    d = distancias[i]
    proximos = intel[d < 20]  # Buffer de 20km

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
        "predio": p.get("nombre_predio", f"Predio_{i}"),
        "comuna": p.get("comuna", "Desconocida"),
        "score": round(score, 1),
        "nivel": nivel
    })

df_resultado = pd.DataFrame(resultados)
df_resultado.to_csv("data/estado_predios.csv", index=False)
print(f"✅ Scoring completado exitosamente para {len(df_resultado)} predios.")
