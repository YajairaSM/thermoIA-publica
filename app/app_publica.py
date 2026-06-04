"""
app/app_publica.py
Aplicación pública ThermoIA — sin login, solo recomendaciones y predicciones.

Ejecutar:
    streamlit run app/app_publica.py --server.port 8502
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# ── Path para encontrar modules/ ─────────────────────────────────────────────
APP_DIR  = Path(__file__).resolve().parent        # app/
sys.path.insert(0, str(APP_DIR))                  # permite: from modules.x import ...

from modules.logic        import calcular_ic, nivel_desde_ic, tiempo_seguro_exposicion
from modules.data_manager import obtener_datos_hoy
from modules.styles_publico import (
    apply_styles_publico, render_header_publico, render_seccion_pub,
    render_clima_cards_pub, render_alerta_banner, render_prediccion_publica,
    render_forecast_cards_pub, render_rec_cards_pub, render_simulador_pub,
)

st.set_page_config(
    page_title="ThermoIA",
    layout="wide",
    page_icon="🌡️",
    initial_sidebar_state="expanded"
)
apply_styles_publico()

# ── Fechas en español ─────────────────────────────────────────────────────────
DIAS_ES  = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
MESES_ES = ["","enero","febrero","marzo","abril","mayo","junio",
            "julio","agosto","septiembre","octubre","noviembre","diciembre"]

def fecha_es(dt):
    return f"{DIAS_ES[dt.weekday()]} {dt.day} de {MESES_ES[dt.month]}, {dt.year}"

# ── Pronóstico 7 días ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def obtener_pronostico_7dias():
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 8.4273, "longitude": -82.4309,
            "daily":  ["temperature_2m_max","temperature_2m_min",
                       "precipitation_sum","windspeed_10m_max"],
            "hourly": ["relative_humidity_2m"],
            "forecast_days": 7, "timezone": "America/Panama"
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
        d    = data["daily"]
        hum  = pd.Series(data["hourly"]["relative_humidity_2m"])
        hum_d = [round(hum[i*24:(i+1)*24].mean(), 1) for i in range(7)]
        df = pd.DataFrame({
            "fecha":    pd.to_datetime(d["time"]),
            "temp_max": d["temperature_2m_max"],
            "temp_min": d["temperature_2m_min"],
            "lluvia":   d["precipitation_sum"],
            "humedad":  hum_d
        })
        df["ic"]     = df.apply(lambda row: calcular_ic(row["temp_max"], row["humedad"]), axis=1)
        df["alerta"] = df["ic"].apply(nivel_desde_ic)
        return {"ok": True, "df": df}
    except Exception:
        return {"ok": False}

# ── Predicciones anteriores (lee del admin) ───────────────────────────────────
PRED_FILE = APP_DIR / "predicciones.csv"

def cargar_predicciones_pub():
    if PRED_FILE.exists():
        df = pd.read_csv(PRED_FILE)
        df["Fecha_Para"] = pd.to_datetime(df["Fecha_Para"])
        return df.sort_values("Fecha_Para", ascending=False).head(30)
    return None

# ── Datos ─────────────────────────────────────────────────────────────────────
hoy    = datetime.today()
manana = hoy + timedelta(days=1)

datos_hoy  = obtener_datos_hoy()
pronostico = obtener_pronostico_7dias()

if datos_hoy["ok"]:
    ic_hoy     = calcular_ic(datos_hoy["temp_max"], datos_hoy["humedad"])
    alerta_hoy = nivel_desde_ic(ic_hoy)
    if pronostico["ok"]:
        row0          = pronostico["df"].iloc[0]
        ic_manana     = round(row0["ic"], 1)
        alerta_manana = row0["alerta"]
        temp_manana   = round(row0["temp_max"], 1)
        lluvia_manana = round(row0["lluvia"], 1)
    else:
        ic_manana     = ic_hoy
        alerta_manana = alerta_hoy
        temp_manana   = datos_hoy["temp_max"]
        lluvia_manana = datos_hoy["lluvia"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;padding:12px 0 16px'>"
        "<div style='width:30px;height:30px;background:#E24B4A;border-radius:8px;"
        "display:flex;align-items:center;justify-content:center'>"
        "<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='white'"
        " stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z'/>"
        "</svg></div>"
        "<span style='font-size:0.95rem;font-weight:600;color:#1a1a1a'>ThermoIA</span>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border:none;border-top:1px solid #ebebeb;margin:0 0 12px'>",
                unsafe_allow_html=True)

    menu = st.radio("", [
        "Inicio",
        "Recomendaciones",
        "Pronóstico 7 días",
        "Predicciones Anteriores",
        "¿Qué es ThermoIA?",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border:none;border-top:1px solid #ebebeb;margin:12px 0'>",
                unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.72rem;color:#cccccc;line-height:2'>"
        "📍 David, Chiriquí · Panamá<br>"
        "🌐 Open-Meteo API<br>"
        "⏱ Actualización: cada hora"
        "</div>",
        unsafe_allow_html=True
    )
    if st.button("↺ Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
if menu == "Inicio":
    render_header_publico(fecha_es(hoy))

    if not datos_hoy["ok"]:
        st.error("No se pudo obtener datos del clima. Verifica tu conexión.")
        st.stop()

    render_alerta_banner(alerta_manana["recs"], alerta_manana["color"])

    # HOY
    render_seccion_pub("Condiciones de hoy")
    color_h = alerta_hoy["color"]
    st.markdown(
        f"<div style='background:#ffffff;border-radius:14px;padding:14px 20px;"
        f"border:1px solid #ebebeb;margin-bottom:14px;"
        f"display:flex;justify-content:space-between;align-items:center'>"
        f"<span style='font-size:0.85rem;color:#444'><b>{fecha_es(hoy)}</b>"
        f" &nbsp;·&nbsp; IC: <span style='color:{color_h};font-weight:600'>"
        f"{ic_hoy}°C</span></span>"
        f"<div style='display:inline-flex;align-items:center;gap:6px;"
        f"background:#f8f7f5;border-radius:8px;padding:4px 12px'>"
        f"<span>{alerta_hoy['icono']}</span>"
        f"<span style='font-size:0.75rem;font-weight:600;color:{color_h}'>"
        f"{alerta_hoy['nivel']}</span></div></div>",
        unsafe_allow_html=True
    )
    render_clima_cards_pub(datos_hoy)

    # MAÑANA
    render_seccion_pub("Predicción para mañana")
    render_prediccion_publica(
        alerta_manana, ic_manana, temp_manana, lluvia_manana, fecha_es(manana)
    )

    # 7 DÍAS
    render_seccion_pub("Pronóstico 7 días")
    if pronostico["ok"]:
        render_forecast_cards_pub(pronostico["df"])
    else:
        st.warning("No se pudo cargar el pronóstico.")

elif menu == "Recomendaciones":
    render_header_publico(fecha_es(hoy))
    render_seccion_pub("Nivel de alerta para mañana")
    color_m = alerta_manana["color"]
    st.markdown(
        f"<div style='background:#ffffff;border-radius:14px;padding:20px 24px;"
        f"border:1px solid #ebebeb;border-left:4px solid {color_m};margin-bottom:20px;"
        f"display:flex;align-items:center;gap:16px'>"
        f"<span style='font-size:2rem'>{alerta_manana['icono']}</span>"
        f"<div><div style='font-size:1.1rem;font-weight:600;color:#1a1a1a'>"
        f"{alerta_manana['nivel']}</div>"
        f"<div style='font-size:0.8rem;color:#888;margin-top:2px'>"
        f"Para {fecha_es(manana)} · IC: {ic_manana}°C · {alerta_manana['rango']}"
        f"</div></div></div>",
        unsafe_allow_html=True
    )
    render_seccion_pub("Recomendaciones detalladas")
    render_rec_cards_pub(alerta_manana["recs"], color_m)

    render_seccion_pub("¿Cuánto tiempo puedo estar al sol mañana?")
    actividad = st.selectbox("Selecciona tu actividad", [
        "Descanso (sentado/parado)",
        "Actividad ligera (caminar)",
        "Actividad moderada (trabajo físico)",
        "Ejercicio intenso (deporte)",
    ])
    minutos, mensaje = tiempo_seguro_exposicion(ic_manana, actividad)
    sim_color = "#2E7D32" if minutos > 60 else "#F57F17" if minutos > 15 else "#E24B4A"
    h = minutos // 60
    m = minutos % 60
    tiempo_txt = f"{h}h {m}m" if h > 0 and minutos > 0 else f"{m}m" if minutos > 0 else "0"
    render_simulador_pub(tiempo_txt, mensaje, sim_color)

elif menu == "Pronóstico 7 días":
    render_header_publico(fecha_es(hoy))
    render_seccion_pub("Pronóstico de los próximos 7 días")
    if pronostico["ok"]:
        render_forecast_cards_pub(pronostico["df"])
    else:
        st.warning("No se pudo cargar el pronóstico.")

elif menu == "Predicciones Anteriores":
    render_header_publico(fecha_es(hoy))
    render_seccion_pub("Historial de predicciones")
    df_p = cargar_predicciones_pub()
    if df_p is not None:
        colores_n = {"NORMAL":"#2E7D32","PRECAUCIÓN":"#F57F17",
                     "PELIGRO":"#E65100","PELIGRO EXTREMO":"#E24B4A"}
        for _, row in df_p.iterrows():
            c_n = colores_n.get(row["Nivel_Alerta"], "#E24B4A")
            fd  = pd.to_datetime(row["Fecha_Para"]).strftime("%d %b %Y")
            st.markdown(
                f"<div style='background:#ffffff;border-radius:12px;"
                f"padding:14px 18px;border:1px solid #ebebeb;"
                f"border-left:4px solid {c_n};margin-bottom:8px;"
                f"display:flex;align-items:center;justify-content:space-between'>"
                f"<div>"
                f"<div style='font-size:0.85rem;font-weight:500;color:#1a1a1a'>{fd}</div>"
                f"<div style='font-size:0.72rem;color:#888;margin-top:2px'>"
                f"Temp: {row['Temp_Max_Pred']}°C · IC: {row['Indice_Calor_Pred']}°C"
                f"</div></div>"
                f"<span style='font-size:0.75rem;font-weight:600;color:{c_n}'>"
                f"{row['Nivel_Alerta']}</span></div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<div style='background:#ffffff;border-radius:14px;padding:32px;"
            "text-align:center;border:1px solid #ebebeb'>"
            "<div style='font-size:2rem;margin-bottom:12px'>📭</div>"
            "<div style='font-size:0.9rem;color:#888'>"
            "Aún no hay predicciones registradas.</div></div>",
            unsafe_allow_html=True
        )

else:  # ¿Qué es ThermoIA?
    render_header_publico(fecha_es(hoy))
    render_seccion_pub("¿Qué es ThermoIA?")
    st.markdown(
        "<div style='background:#ffffff;border-radius:16px;padding:28px 24px;"
        "border:1px solid #ebebeb;margin-bottom:16px'>"
        "<div style='font-size:1rem;font-weight:600;color:#1a1a1a;margin-bottom:12px'>"
        "Tu asistente inteligente para el calor</div>"
        "<div style='font-size:0.87rem;color:#555;line-height:1.8'>"
        "ThermoIA es un sistema de predicción y alerta de calor desarrollado "
        "para la ciudad de David, Chiriquí, Panamá. Utiliza modelos de "
        "Inteligencia Artificial entrenados con más de 36 años de datos "
        "climáticos históricos para predecir las condiciones del día siguiente "
        "y emitir recomendaciones de salud personalizadas para la población."
        "</div></div>",
        unsafe_allow_html=True
    )
    items = [
        ("🤖","Inteligencia Artificial",
         "Modelos XGBoost entrenados con datos 1990–2026."),
        ("🌡","Índice de Calor",
         "Fórmula de Rothfusz (OMS) que combina temperatura y humedad real."),
        ("📅","Predicción diaria",
         "Predice las condiciones del día siguiente con datos en tiempo real."),
        ("⚠️","Alertas de salud",
         "Recomendaciones específicas según el nivel de riesgo climático."),
    ]
    c1, c2 = st.columns(2)
    for i, (ico, titulo, desc) in enumerate(items):
        col = c1 if i % 2 == 0 else c2
        with col:
            st.markdown(
                f"<div style='background:#ffffff;border-radius:12px;"
                f"padding:18px 16px;border:1px solid #ebebeb;margin-bottom:10px'>"
                f"<div style='font-size:1.5rem;margin-bottom:8px'>{ico}</div>"
                f"<div style='font-size:0.88rem;font-weight:600;color:#1a1a1a;"
                f"margin-bottom:4px'>{titulo}</div>"
                f"<div style='font-size:0.8rem;color:#888;line-height:1.6'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
