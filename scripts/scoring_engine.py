import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

predios = pd.read_csv("data/predios_limpios.csv")
intel = pd.read_csv("data/inteligencia_limpiada.csv")
intel = intel.dropna(subset=["latitud", "longitud"])

hoy = pd.Timestamp.today()
diff = (hoy - intel["fecha"]).dt.days
intel["peso_tiempo"] = np.where(diff <= 7, 1.0, np.where(diff <= 30, 0.6, np.where(diff <= 90, 0.3, 0.1)))

predios_coords = predios[["latitud", "longitud"]].values
intel_coords = intel[["latitud", "longitud"]].values
distancias = cdist(predios_coords, intel_coords) * 111  # km aprox

resultados = []
for i, (_, p) in enumerate(predios.iterrows()):
    d = distancias[i]
    proximos = intel[d < 20]  # Buffer 20km
    if len(proximos) == 0:
        score, nivel = 0, "BAJO"
    else:
        mapeo = {"CRÍTICO": 0.4, "ALTO": 0.3, "MEDIO": 0.2, "BAJO": 0.1}
        proximos["peso_base"] = proximos["nivel_alerta"].map(mapeo).fillna(0.1)
        score = (proximos["peso_base"] * proximos["peso_tiempo"]).sum() * 100
        score = min(score, 100)
        if score >= 75: nivel = "CRÍTICO"
        elif score >= 50: nivel = "ALTO"
        elif score >= 25: nivel = "MEDIO"
        else: nivel = "BAJO"
    resultados.append({"predio": p["nombre_predio"], "comuna": p["comuna"], "score": round(score,1), "nivel": nivel})

pd.DataFrame(resultados).to_csv("data/estado_predios.csv", index=False)
print("✅ Scoring completado")
