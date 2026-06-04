import joblib
import pandas as pd
import numpy as np

from pathlib import Path
from datetime import datetime, timedelta

from modules.logic import calcular_ic

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODELS_DIR = BASE_DIR / "models"


def cargar_modelos():

    return {
        "temp": joblib.load(MODELS_DIR / "om_xgb_temperatura.pkl"),
        "humedad": joblib.load(MODELS_DIR / "om_xgb_humedad.pkl"),
        "lluvia": joblib.load(MODELS_DIR / "om_xgb_lluvia.pkl"),
        "viento": joblib.load(MODELS_DIR / "om_xgb_viento.pkl"),
        "presion": joblib.load(MODELS_DIR / "om_xgb_presion.pkl"),
    }


def construir_features(d, hist):

    ic_hoy = calcular_ic(d["temp_max"], d["humedad"])

    ult = hist.tail(30)

    def sl(col, n, fallback):
        if len(ult) >= n:
            return float(ult[col].iloc[-n])
        return fallback

    def mm(col, n, fallback):
        vals = list(ult[col].values) + [fallback]
        return round(float(np.mean(vals[-n:])), 2)

    manana = datetime.today() + timedelta(days=1)

    dia_anio = manana.timetuple().tm_yday
    mes_num = manana.month

    estacion = 1 if mes_num in [12,1,2,3,4] else 0

    return pd.DataFrame([{

        "Temp_Max": d["temp_max"],
        "Temp_Min": d["temp_min"],
        "Temp_Prom": d["temp_prom"],
        "Humedad": d["humedad"],
        "Lluvia": d["lluvia"],
        "Lluvia_Hist": mm("Lluvia", 30, d["lluvia"]),
        "Presion": d["presion"],
        "Viento_Max": d["viento_max"],
        "Indice_Calor": ic_hoy,

        "Temp_Prom_lag1": sl("Temp_Prom", 1, d["temp_prom"]),
        "Temp_Prom_lag7": sl("Temp_Prom", 7, d["temp_prom"]),
        "Temp_Prom_lag30": sl("Temp_Prom", 30, d["temp_prom"]),

        "Temp_Max_lag1": sl("Temp_Max", 1, d["temp_max"]),
        "Temp_Max_lag7": sl("Temp_Max", 7, d["temp_max"]),

        "IC_lag1": sl("Indice_Calor", 1, ic_hoy),
        "IC_lag7": sl("Indice_Calor", 7, ic_hoy),

        "Lluvia_lag1": sl("Lluvia", 1, d["lluvia"]),
        "Lluvia_lag7": sl("Lluvia", 7, d["lluvia"]),

        "Viento_lag1": sl("Viento_Max", 1, d["viento_max"]),

        "Humedad_lag1": sl("Humedad", 1, d["humedad"]),
        "Humedad_lag7": sl("Humedad", 7, d["humedad"]),

        "Presion_lag1": sl("Presion", 1, d["presion"]),

        "Temp_Prom_m7": mm("Temp_Prom", 7, d["temp_prom"]),
        "Temp_Prom_m30": mm("Temp_Prom", 30, d["temp_prom"]),

        "Temp_Max_m7": mm("Temp_Max", 7, d["temp_max"]),

        "IC_m7": mm("Indice_Calor", 7, ic_hoy),
        "IC_m30": mm("Indice_Calor", 30, ic_hoy),

        "Lluvia_m7": mm("Lluvia", 7, d["lluvia"]),
        "Lluvia_m30": mm("Lluvia", 30, d["lluvia"]),

        "Humedad_m7": mm("Humedad", 7, d["humedad"]),

        "Presion_m7": mm("Presion", 7, d["presion"]),

        "Dia_Año": dia_anio,
        "Mes_Num": mes_num,
        "Estacion_Num": estacion
    }])