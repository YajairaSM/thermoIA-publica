import pandas as pd
import requests
import streamlit as st
from pathlib import Path

# Buscamos la carpeta raíz (subiendo un nivel desde app/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FILE = BASE_DIR / "dataset_features.csv"

@st.cache_data(ttl=3600)
def obtener_datos_hoy():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 8.4273, "longitude": -82.4309,
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "surface_pressure", "wind_speed_10m"],
        "forecast_days": 1, "timezone": "America/Panama"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        h = data["hourly"]
        df = pd.DataFrame({"temp": h["temperature_2m"], "hum": h["relative_humidity_2m"]})
        return {
            "temp_max": round(df["temp"].max(), 1),
            "temp_min": round(df["temp"].min(), 1),
            "temp_prom": round(df["temp"].mean(), 1),
            "humedad": round(df["hum"].mean(), 1),
            "lluvia": round(sum(h["precipitation"]), 1),
            "presion": round(sum(h["surface_pressure"])/len(h["surface_pressure"]), 1),
            "viento_max": round(max(h["wind_speed_10m"]), 1),
            "ok": True
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

@st.cache_data
def cargar_historial():
    try:
        if DATA_FILE.exists():
            df = pd.read_csv(DATA_FILE)
            df["Fecha"] = pd.to_datetime(df["Fecha"])
            return df
    except:
        return None
    return None