import pandas as pd
import numpy as np
import os

# Crear carpeta de salida si no existe
os.makedirs("data", exist_ok=True)

def limpiar_predios():
    # Buscar archivo en raíz o en data/
    path = "predios_cmpc_rows (2).csv" if os.path.exists("predios_cmpc_rows (2).csv") else "data/predios_cmpc_rows (2).csv"
    df = pd.read_csv(path, sep=",", encoding="utf-8", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    for col in ["latitud", "longitud", "hectareas"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[(df["latitud"].between(-55, -30)) & (df["longitud"].between(-75, -65))]
    df.drop_duplicates(subset=["id"], inplace=True)
    df.to_csv("data/predios_limpios.csv", index=False)
    print(f"✅ Predios listos: {len(df)}")

def limpiar_inteligencia():
    path = "inteligencia_tactica_rows (4).csv" if os.path.exists("inteligencia_tactica_rows (4).csv") else "data/inteligencia_tactica_rows (4).csv"
    df = pd.read_csv(path, sep=",", encoding="utf-8", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df.dropna(subset=["fecha"], inplace=True)
    for col in ["latitud", "longitud"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.to_csv("data/inteligencia_limpiada.csv", index=False)
    print(f"✅ Inteligencia lista: {len(df)} eventos válidos")

limpiar_predios()
limpiar_inteligencia()
