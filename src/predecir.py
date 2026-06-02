"""
predecir_openmeteo.py v4 — Predictor Meteorológico
David, Chiriquí — Modelos entrenados con datos 1990–2026

Flujo limpio y consistente:
  5 modelos predicen → temperatura, humedad, lluvia, viento, presión
  Fórmula Rothfusz  → índice de calor (calculado)
  Tabla OMS         → nivel de alerta (calculado)

Uso:
    python predecir_openmeteo.py
"""

import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# ── Colores ANSI ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
ORANGE = "\033[38;5;208m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_FILE = BASE_DIR / "data" / "processed" / "dataset_features.csv"

# ── Utilidades visuales ───────────────────────────────────────────────────────
def linea(car="─", largo=57, color=CYAN):
    print(f"{color}{car * largo}{RESET}")

def titulo(texto, color=CYAN):
    linea("═", color=color)
    print(f"{BOLD}{color}  {texto}{RESET}")
    linea("═", color=color)

def seccion(texto):
    print(f"\n{BOLD}{BLUE}  ▸ {texto}{RESET}")
    print(f"{GRAY}  {'─' * 47}{RESET}")

def ok(texto):
    print(f"  {GREEN}{RESET} {texto}")

def error(texto):
    print(f"  {RED} ERROR:{RESET} {texto}")
    sys.exit(1)

def pedir_numero(mensaje, minimo, maximo, referencia=""):
    while True:
        try:
            if referencia:
                print(f"  {GRAY}  (ref: {referencia}){RESET}")
            valor = float(input(f"  {CYAN}▶{RESET} {mensaje}: "))
            if minimo <= valor <= maximo:
                return valor
            print(f"  {YELLOW} Ingresa un valor entre {minimo} y {maximo}{RESET}\n")
        except ValueError:
            print(f"  {YELLOW} Ingresa un número válido{RESET}\n")

def calcular_ic(temp, humedad):
    T, H = temp, humedad
    return round(
        -8.78469475556 + 1.61139411*T + 2.33854883889*H
        - 0.14611605*T*H - 0.012308094*T**2 - 0.0164248277778*H**2
        + 0.002211732*T**2*H + 0.00072546*T*H**2
        - 0.000003582*T**2*H**2, 1
    )

def nivel_desde_ic(ic):
    if ic >= 41:  return ("PELIGRO EXTREMO", RED,    "██████████", "🔴", "EVITAR salir. Riesgo severo para la salud.")
    elif ic >= 35: return ("PELIGRO",         ORANGE, "███████░░░", "🟠", "Limitar actividad al aire libre. Riesgo de golpe de calor.")
    elif ic >= 32: return ("PRECAUCION",      YELLOW, "████░░░░░░", "🟡", "Fatiga posible con exposición prolongada al sol.")
    else:          return ("NORMAL",           GREEN,  "██░░░░░░░░", "🟢", "Sin riesgo significativo. Condiciones normales.")

def safe_lag(series, n, fallback):
    return float(series.iloc[-n]) if len(series) >= n else fallback

# ── Encabezado ────────────────────────────────────────────────────────────────
print()
titulo("PREDICTOR METEOROLÓGICO v4 — David, Chiriquí", CYAN)
print(f"  {GRAY}Dataset Open-Meteo 1990–2026 | 5 modelos de regresión{RESET}\n")

# ── Selección de modelo ───────────────────────────────────────────────────────
seccion("Selección de modelo")
print(f"  {WHITE}[1]{RESET} Random Forest")
print(f"  {WHITE}[2]{RESET} XGBoost  {GRAY}(generalmente más preciso){RESET}")
print()

while True:
    opcion = input(f"  {CYAN}{RESET} Elige una opción (1 o 2): ").strip()
    if opcion in ["1", "2"]:
        break
    print(f"  {YELLOW}Ingresa 1 o 2{RESET}")

prefijo       = "om_rf"  if opcion == "1" else "om_xgb"
nombre_modelo = "Random Forest" if opcion == "1" else "XGBoost"
print()

# ── Cargar modelos ────────────────────────────────────────────────────────────
seccion("Cargando modelos")
try:
    m_temp    = joblib.load(MODELS_DIR / f"{prefijo}_temperatura.pkl")
    m_humedad = joblib.load(MODELS_DIR / f"{prefijo}_humedad.pkl")
    m_lluvia  = joblib.load(MODELS_DIR / f"{prefijo}_lluvia.pkl")
    m_viento  = joblib.load(MODELS_DIR / f"{prefijo}_viento.pkl")
    m_presion = joblib.load(MODELS_DIR / f"{prefijo}_presion.pkl")
    ok(f"5 modelos {nombre_modelo} cargados")
except FileNotFoundError as e:
    error(f"Archivo no encontrado: {e}\n  Ejecuta primero modelado_completo.ipynb")

# ── Cargar historial ──────────────────────────────────────────────────────────
try:
    hist = pd.read_csv(DATA_FILE)
    hist["Fecha"] = pd.to_datetime(hist["Fecha"])
    hist = hist.sort_values("Fecha").reset_index(drop=True)
    ok(f"Historial: {len(hist):,} días ({hist['Fecha'].min().year}–{hist['Fecha'].max().year})")
except FileNotFoundError:
    error("No se encontró dataset_features.csv en data_processed/")

# ── Ingreso de datos ──────────────────────────────────────────────────────────
hoy = datetime.today().date()
seccion(f"Datos meteorológicos de HOY ({hoy})")

temp_max  = pedir_numero("Temperatura Máxima    (°C)",   20.0, 42.0,   "típico 28–38°C")
temp_min  = pedir_numero("Temperatura Mínima    (°C)",   15.0, 30.0,   "típico 20–26°C")
temp_prom = pedir_numero("Temperatura Promedio  (°C)",   18.0, 36.0,   "típico 24–31°C")
humedad   = pedir_numero("Humedad               (%)",    20.0, 100.0,  "típico 60–90%")
lluvia    = pedir_numero("Lluvia del día        (mm)",    0.0, 200.0,  "0 si no llovió")
lluvia_h  = pedir_numero("Lluvia prom. histórico (mm)",  0.0,  30.0,  "típico 0–15 mm")
presion   = pedir_numero("Presión atmosférica   (hPa)", 990.0, 1025.0, "típico 1005–1015 hPa")
viento    = pedir_numero("Viento máximo         (km/h)",  0.0, 130.0,  "típico 10–80 km/h")

# Índice de calor de hoy
ic_hoy = calcular_ic(temp_max, humedad)

# ── Lags y medias móviles ─────────────────────────────────────────────────────
ult = hist.tail(30)

lag1_temp    = safe_lag(ult["Temp_Prom"],    1,  temp_prom)
lag7_temp    = safe_lag(ult["Temp_Prom"],    7,  temp_prom)
lag30_temp   = safe_lag(ult["Temp_Prom"],    30, temp_prom)
lag1_tmax    = safe_lag(ult["Temp_Max"],     1,  temp_max)
lag7_tmax    = safe_lag(ult["Temp_Max"],     7,  temp_max)
lag1_ic      = safe_lag(ult["Indice_Calor"], 1,  ic_hoy)
lag7_ic      = safe_lag(ult["Indice_Calor"], 7,  ic_hoy)
lag1_lluvia  = safe_lag(ult["Lluvia"],       1,  lluvia)
lag7_lluvia  = safe_lag(ult["Lluvia"],       7,  lluvia)
lag1_viento  = safe_lag(ult["Viento_Max"],   1,  viento)
lag1_humedad = safe_lag(ult["Humedad"],      1,  humedad)
lag7_humedad = safe_lag(ult["Humedad"],      7,  humedad)
lag1_presion = safe_lag(ult["Presion"],      1,  presion)

def media(col, n, fallback):
    vals = list(ult[col].values) + [fallback]
    return round(float(np.mean(vals[-n:])), 2)

m7_temp   = media("Temp_Prom",    7,  temp_prom)
m30_temp  = media("Temp_Prom",    30, temp_prom)
m7_tmax   = media("Temp_Max",     7,  temp_max)
m7_ic     = media("Indice_Calor", 7,  ic_hoy)
m30_ic    = media("Indice_Calor", 30, ic_hoy)
m7_lluvia = media("Lluvia",       7,  lluvia)
m30_lluvia= media("Lluvia",       30, lluvia)
m7_hum    = media("Humedad",      7,  humedad)
m7_pres   = media("Presion",      7,  presion)

manana   = datetime.today() + timedelta(days=1)
dia_anio = manana.timetuple().tm_yday
mes_num  = manana.month
estacion = 1 if mes_num in [12, 1, 2, 3, 4] else 0

# ── Vector de features ────────────────────────────────────────────────────────
X_nuevo = pd.DataFrame([{
    "Temp_Max": temp_max, "Temp_Min": temp_min, "Temp_Prom": temp_prom,
    "Humedad": humedad, "Lluvia": lluvia, "Lluvia_Hist": lluvia_h,
    "Presion": presion, "Viento_Max": viento, "Indice_Calor": ic_hoy,
    "Temp_Prom_lag1": lag1_temp, "Temp_Prom_lag7": lag7_temp, "Temp_Prom_lag30": lag30_temp,
    "Temp_Max_lag1": lag1_tmax,  "Temp_Max_lag7": lag7_tmax,
    "IC_lag1": lag1_ic,   "IC_lag7": lag7_ic,
    "Lluvia_lag1": lag1_lluvia,  "Lluvia_lag7": lag7_lluvia,
    "Viento_lag1": lag1_viento,
    "Humedad_lag1": lag1_humedad,"Humedad_lag7": lag7_humedad,
    "Presion_lag1": lag1_presion,
    "Temp_Prom_m7": m7_temp,  "Temp_Prom_m30": m30_temp,
    "Temp_Max_m7":  m7_tmax,
    "IC_m7": m7_ic, "IC_m30": m30_ic,
    "Lluvia_m7": m7_lluvia, "Lluvia_m30": m30_lluvia,
    "Humedad_m7": m7_hum,   "Presion_m7": m7_pres,
    "Dia_Año": dia_anio, "Mes_Num": mes_num, "Estacion_Num": estacion,
}])

# ── Predicciones ──────────────────────────────────────────────────────────────
pred_temp    = round(float(m_temp.predict(X_nuevo)[0]),    2)
pred_humedad = round(float(m_humedad.predict(X_nuevo)[0]), 1)
pred_lluvia  = round(max(0.0, float(m_lluvia.predict(X_nuevo)[0])), 1)
pred_viento  = round(float(m_viento.predict(X_nuevo)[0]),  1)
pred_presion = round(float(m_presion.predict(X_nuevo)[0]), 1)

# Índice de calor y nivel de alerta calculados — 100% consistentes
ic_manana = calcular_ic(pred_temp, pred_humedad)
alerta, color_alerta, barra, icono, recomendacion = nivel_desde_ic(ic_manana)

rangos = {
    "NORMAL":          "Índice < 32°C  →  sin riesgo significativo",
    "PRECAUCION":      "Índice 32–34°C →  fatiga posible",
    "PELIGRO":         "Índice 35–40°C →  golpe de calor posible",
    "PELIGRO EXTREMO": "Índice ≥ 41°C  →  golpe de calor muy probable",
}

# ── Resumen de hoy ────────────────────────────────────────────────────────────
seccion("Resumen de datos ingresados — HOY")
print(f"  {GRAY}Temperatura Máxima   :{RESET} {temp_max}°C")
print(f"  {GRAY}Temperatura Mínima   :{RESET} {temp_min}°C")
print(f"  {GRAY}Temperatura Promedio :{RESET} {temp_prom}°C")
print(f"  {GRAY}Humedad real         :{RESET} {humedad}%")
print(f"  {GRAY}Presión atmosférica  :{RESET} {presion} hPa")
print(f"  {GRAY}Lluvia               :{RESET} {lluvia} mm")
print(f"  {GRAY}Viento máximo        :{RESET} {viento} km/h")
print(f"  {GRAY}Índice de calor hoy  :{RESET} {BOLD}{ic_hoy}°C{RESET}  {GRAY}(sensación térmica de hoy){RESET}")

# ── Resultado final ───────────────────────────────────────────────────────────
print()
linea("═", color=color_alerta)
print(f"{BOLD}{color_alerta}  PREDICCIÓN PARA MAÑANA  {manana.strftime('%A %d/%m/%Y').upper()}{RESET}")
linea("═", color=color_alerta)
print()
print(f"  🌡  Temperatura máxima estimada      :  {BOLD}{WHITE}{pred_temp} °C{RESET}        {GRAY}(lo que marcará el termómetro){RESET}")
print(f"  💧  Humedad estimada          :  {BOLD}{WHITE}{pred_humedad} %{RESET}")
print(f"  🌧  Lluvia estimada           :  {BOLD}{WHITE}{pred_lluvia} mm{RESET}")
print(f"  💨  Viento máximo estimado    :  {BOLD}{WHITE}{pred_viento} km/h{RESET}")
print(f"  🔵  Presión atmosférica       :  {BOLD}{WHITE}{pred_presion} hPa{RESET}")
print()
print(f"  🌡  Índice de calor estimado  :  {BOLD}{color_alerta}{ic_manana} °C{RESET}        {GRAY}(calculado con temp {pred_temp}°C + humedad {pred_humedad}%){RESET}")
print()
print(f"  {icono}  Nivel de alerta           :  {BOLD}{color_alerta}{alerta}{RESET}")
print(f"      {color_alerta}{barra}{RESET}  {GRAY}({nombre_modelo}){RESET}")
print(f"      {GRAY}↳ {rangos.get(alerta, '')}{RESET}")
print()
print(f"  {BOLD}Recomendación:{RESET} {color_alerta}{recomendacion}{RESET}")
print()
linea("═", color=color_alerta)
print()
