import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from pathlib import Path

from login import render_login, render_user_badge, logout

# Verificar login — si no está autenticado se detiene aquí
if not render_login():
    st.stop()
 
from modules.styles import (
    apply_styles, render_header, render_seccion,
    render_clima_cards, render_prediccion_card,
    render_rec_cards, render_forecast_cards,
    get_sliding_recs, info_card, render_simulador_resultado
)
from modules.logic import calcular_ic, nivel_desde_ic, tiempo_seguro_exposicion
from modules.data_manager import obtener_datos_hoy, cargar_historial
from modules.models_helper import cargar_modelos, construir_features
 
st.set_page_config(
    page_title="ThermoIA",
    layout="wide",
    page_icon="🌡️",
    initial_sidebar_state="expanded"
)
apply_styles()
 
PRED_FILE = Path(__file__).resolve().parent / "predicciones.csv"
 
DIAS_ES  = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
MESES_ES = ["","enero","febrero","marzo","abril","mayo","junio",
            "julio","agosto","septiembre","octubre","noviembre","diciembre"]
 
def fecha_es(dt):
    return f"{DIAS_ES[dt.weekday()]} {dt.day} de {MESES_ES[dt.month]}, {dt.year}"
 
def guardar_prediccion(fecha_pred, fecha_para, temp, humedad,
                       lluvia, viento, presion, ic, nivel):
    nueva = pd.DataFrame([{
        "Fecha_Prediccion":  fecha_pred.strftime("%Y-%m-%d"),
        "Fecha_Para":        fecha_para.strftime("%Y-%m-%d"),
        "Temp_Max_Pred":     temp,
        "Humedad_Pred":      humedad,
        "Lluvia_Pred":       lluvia,
        "Viento_Pred":       viento,
        "Presion_Pred":      presion,
        "Indice_Calor_Pred": ic,
        "Nivel_Alerta":      nivel,
        "Hora_Registro":     fecha_pred.strftime("%H:%M")
    }])
    if PRED_FILE.exists():
        df_h = pd.read_csv(PRED_FILE)
        if (df_h["Fecha_Prediccion"] == fecha_pred.strftime("%Y-%m-%d")).any():
            return df_h
        df_h = pd.concat([df_h, nueva], ignore_index=True)
    else:
        df_h = nueva
    df_h.to_csv(PRED_FILE, index=False)
    return df_h
 
def cargar_predicciones():
    if PRED_FILE.exists():
        df = pd.read_csv(PRED_FILE)
        df["Fecha_Prediccion"] = pd.to_datetime(df["Fecha_Prediccion"])
        df["Fecha_Para"]       = pd.to_datetime(df["Fecha_Para"])
        return df.sort_values("Fecha_Prediccion", ascending=False).reset_index(drop=True)
    return None
 
@st.cache_data(ttl=3600)
def obtener_pronostico_7dias():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 8.4273, "longitude": -82.4309,
        "daily":  ["temperature_2m_max","temperature_2m_min",
                   "precipitation_sum","windspeed_10m_max"],
        "hourly": ["relative_humidity_2m"],
        "forecast_days": 7, "timezone": "America/Panama"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        d = data["daily"]
        hum = pd.Series(data["hourly"]["relative_humidity_2m"])
        hum_d = [round(hum[i*24:(i+1)*24].mean(), 1) for i in range(7)]
        df = pd.DataFrame({
            "fecha":      pd.to_datetime(d["time"]),
            "temp_max":   d["temperature_2m_max"],
            "temp_min":   d["temperature_2m_min"],
            "lluvia":     d["precipitation_sum"],
            "viento_max": d["windspeed_10m_max"],
            "humedad":    hum_d
        })
        df["ic"]     = df.apply(lambda r: calcular_ic(r["temp_max"], r["humedad"]), axis=1)
        df["alerta"] = df["ic"].apply(nivel_desde_ic)
        return {"ok": True, "df": df}
    except Exception as e:
        return {"ok": False, "error": str(e)}
 
# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_user_badge()  
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;padding:12px 0 16px'>"
        "<div style='width:30px;height:30px;background:#E24B4A;border-radius:8px;"
        "display:flex;align-items:center;justify-content:center'>"
        "<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='white' "
        "stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z'/>"
        "</svg></div>"
        "<span style='font-size:1rem;font-weight:600;color:#1a1a1a'>ThermoIA</span>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border:none;border-top:1px solid #ebebeb;margin:0 0 16px'>",
                unsafe_allow_html=True)
 
    menu = st.radio(
        "Navegación",
        ["Dashboard", "Recomendaciones", "Predicciones Anteriores",
         "Explorador Histórico", "Sobre el Modelo"],
        label_visibility="collapsed"
    )
 
    st.markdown("<hr style='border:none;border-top:1px solid #ebebeb;margin:16px 0'>",
                unsafe_allow_html=True)
    modelo_elegido = st.selectbox("Modelo IA", ["XGBoost", "Random Forest"])
    prefijo = "om_xgb" if modelo_elegido == "XGBoost" else "om_rf"
 
    st.markdown("<hr style='border:none;border-top:1px solid #ebebeb;margin:16px 0'>",
                unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.75rem;color:#bbbbbb;line-height:2'>"
        "📍 David, Chiriquí · Panamá<br>"
        "🌐 Open-Meteo API<br>"
        "🤖 Modelos entrenados 1990–2026<br>"
        "⏱ Datos actualizados cada hora"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if st.button("↺  Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
 
# ── Carga ─────────────────────────────────────────────────────────────────────
datos_hoy  = obtener_datos_hoy()
historial  = cargar_historial()
pronostico = obtener_pronostico_7dias()
hoy    = datetime.today()
manana = hoy + timedelta(days=1)
 
try:
    modelos    = cargar_modelos(prefijo)
    modelos_ok = True
except Exception as e:
    modelos_ok    = False
    modelos_error = str(e)
 
# ══════════════════════════════════════════════════════════════════════════════
#  VISTA 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if menu == "Dashboard":
 
    render_header(fecha_es(hoy))
 
    if not datos_hoy["ok"]:
        st.error("No se pudo conectar a Open-Meteo.")
        st.stop()
    if not modelos_ok:
        st.error(f"No se pudieron cargar los modelos: {modelos_error}")
        st.stop()
 
    X         = construir_features(datos_hoy, historial)
    pred_temp = round(float(modelos["temp"].predict(X)[0]), 1)
    pred_hum  = round(float(modelos["humedad"].predict(X)[0]), 1)
    pred_lluv = round(max(0.0, float(modelos["lluvia"].predict(X)[0])), 1)
    pred_vien = round(float(modelos["viento"].predict(X)[0]), 1)
    pred_pres = round(float(modelos["presion"].predict(X)[0]), 1)
    ic_hoy    = calcular_ic(datos_hoy["temp_max"], datos_hoy["humedad"])
    ic_manana = calcular_ic(pred_temp, pred_hum)
    alerta_hoy    = nivel_desde_ic(ic_hoy)
    alerta_manana = nivel_desde_ic(ic_manana)
 
    guardar_prediccion(hoy, manana, pred_temp, pred_hum, pred_lluv,
                       pred_vien, pred_pres, ic_manana, alerta_manana["nivel"])
 
    st.markdown(get_sliding_recs(alerta_manana["recs"], alerta_manana["color"]),
                unsafe_allow_html=True)
 
    # Bloque HOY
    render_seccion("Condiciones de hoy", "")
    color_h = alerta_hoy["color"]
    st.markdown(
        f"<div style='background:#ffffff;border-radius:14px;padding:16px 20px;"
        f"border:1px solid #ebebeb;margin-bottom:16px;"
        f"display:flex;justify-content:space-between;align-items:center'>"
        f"<div style='font-size:0.82rem;color:#444444'>"
        f"<span style='font-weight:600'>{fecha_es(hoy)}</span> &nbsp;·&nbsp; "
        f"IC hoy: <span style='color:{color_h};font-weight:600'>{ic_hoy}°C</span>"
        f"</div>"
        f"<div style='display:inline-flex;align-items:center;gap:6px;"
        f"background:#f8f7f5;border-radius:8px;padding:4px 12px'>"
        f"<span>{alerta_hoy['icono']}</span>"
        f"<span style='font-size:0.75rem;font-weight:600;color:{color_h}'>"
        f"{alerta_hoy['nivel']}</span>"
        f"</div></div>",
        unsafe_allow_html=True
    )
    render_clima_cards(datos_hoy)
 
    # Bloque MAÑANA
    render_seccion("Predicción para mañana", "")
    render_prediccion_card(
        alerta_manana, ic_manana, pred_temp, pred_hum,
        pred_lluv, pred_vien, pred_pres,
        datos_hoy, fecha_es(manana), modelo_elegido
    )
 
    # Pronóstico 7 días
    render_seccion("Pronóstico 7 días", "")
    if pronostico["ok"]:
        render_forecast_cards(pronostico["df"])
    else:
        st.warning("No se pudo cargar el pronóstico de 7 días.")
 
# ══════════════════════════════════════════════════════════════════════════════
#  VISTA 2 — RECOMENDACIONES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Recomendaciones":
 
    render_header(fecha_es(hoy))
 
    if datos_hoy["ok"] and modelos_ok:
        X         = construir_features(datos_hoy, historial)
        pred_temp = round(float(modelos["temp"].predict(X)[0]), 1)
        pred_hum  = round(float(modelos["humedad"].predict(X)[0]), 1)
        ic_pred   = calcular_ic(pred_temp, pred_hum)
        alerta    = nivel_desde_ic(ic_pred)
        color     = alerta["color"]
 
        render_seccion("Nivel de alerta para mañana", "")
        badges = {
            "PELIGRO EXTREMO": ("#FCEBEB","#A32D2D"),
            "PELIGRO":         ("#FFF3E0","#E65100"),
            "PRECAUCIÓN":      ("#FFFDE7","#F57F17"),
            "NORMAL":          ("#E8F5E9","#2E7D32"),
        }
        bg_b, txt_b = badges.get(alerta["nivel"], ("#f5f5f5","#444"))
        st.markdown(
            f"<div style='background:#ffffff;border-radius:14px;padding:20px 24px;"
            f"border:1px solid #ebebeb;border-left:4px solid {color};"
            f"margin-bottom:4px;display:flex;align-items:center;gap:16px'>"
            f"<span style='font-size:2rem'>{alerta['icono']}</span>"
            f"<div>"
            f"<div style='font-size:1.15rem;font-weight:600;color:#1a1a1a'>"
            f"{alerta['nivel']}</div>"
            f"<div style='font-size:0.8rem;color:#888888;margin-top:2px'>"
            f"Para {fecha_es(manana)} · IC estimado: {ic_pred}°C · "
            f"{alerta['rango']}</div>"
            f"</div></div>",
            unsafe_allow_html=True
        )
 
        render_seccion("Recomendaciones detalladas", "")
        render_rec_cards(alerta["recs"], color)
 
        render_seccion("Simulador de exposición", "")
        st.markdown(
            "<p style='font-size:0.85rem;color:#888888;margin-bottom:16px'>"
            "Selecciona tu actividad para conocer el tiempo máximo "
            "seguro de exposición al calor mañana.</p>",
            unsafe_allow_html=True
        )
        actividad = st.selectbox("Actividad que realizarás mañana", [
            "Descanso (sentado/parado)",
            "Actividad ligera (caminar)",
            "Actividad moderada (trabajo físico)",
            "Ejercicio intenso (deporte)",
        ])
        minutos, mensaje = tiempo_seguro_exposicion(ic_pred, actividad)
        sim_color = "#2E7D32" if minutos > 60 else "#F57F17" if minutos > 15 else "#E24B4A"
        if minutos > 0:
            h = minutos // 60
            m = minutos % 60
            tiempo_txt = f"{h}h {m}m" if h > 0 else f"{m}m"
        else:
            tiempo_txt = "0"
        render_simulador_resultado(tiempo_txt, mensaje, sim_color)
 
# ══════════════════════════════════════════════════════════════════════════════
#  VISTA 3 — PREDICCIONES ANTERIORES
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🕓  Predicciones Anteriores":
 
    render_header(fecha_es(hoy))
    render_seccion("Historial de predicciones emitidas", "")
 
    df_preds = cargar_predicciones()
 
    if df_preds is None or len(df_preds) == 0:
        st.markdown(
            "<div style='background:#ffffff;border-radius:14px;padding:32px;"
            "text-align:center;border:1px solid #ebebeb'>"
            "<div style='font-size:2rem;margin-bottom:12px'>📭</div>"
            "<div style='font-size:0.95rem;color:#888888'>"
            "Aún no hay predicciones guardadas.<br>"
            "Abre el Dashboard para generar la primera predicción."
            "</div></div>",
            unsafe_allow_html=True
        )
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Predicciones guardadas", len(df_preds))
        m2.metric("IC promedio predicho",
                  f"{df_preds['Indice_Calor_Pred'].mean():.1f}°C")
        m3.metric("IC máximo predicho",
                  f"{df_preds['Indice_Calor_Pred'].max():.1f}°C")
        nivel_top = df_preds["Nivel_Alerta"].value_counts().index[0].split()[0]
        m4.metric("Nivel más frecuente", nivel_top)
 
        render_seccion("Evolución del índice de calor predicho", "")
 
        fig, ax = plt.subplots(figsize=(13, 3.5), facecolor="#f8f7f5")
        ax.set_facecolor("#ffffff")
        df_plot = df_preds.sort_values("Fecha_Para")
        colores_n = {
            "NORMAL":          "#2E7D32",
            "PRECAUCIÓN":      "#F57F17",
            "PELIGRO":         "#E65100",
            "PELIGRO EXTREMO": "#E24B4A"
        }
        for _, row in df_plot.iterrows():
            c_p = colores_n.get(row["Nivel_Alerta"], "#E24B4A")
            ax.scatter(row["Fecha_Para"], row["Indice_Calor_Pred"],
                       color=c_p, s=60, zorder=3)
        ax.plot(df_plot["Fecha_Para"], df_plot["Indice_Calor_Pred"],
                color="#dddddd", linewidth=1.2, alpha=0.8, zorder=2)
        ax.axhline(32, color="#F57F17", linestyle="--",
                   linewidth=0.8, alpha=0.6, label="Precaución (32°C)")
        ax.axhline(35, color="#E65100", linestyle="--",
                   linewidth=0.8, alpha=0.6, label="Peligro (35°C)")
        ax.axhline(41, color="#E24B4A", linestyle="--",
                   linewidth=0.8, alpha=0.6, label="P. Extremo (41°C)")
        ax.legend(fontsize=8, facecolor="#ffffff",
                  edgecolor="#ebebeb", labelcolor="#666666")
        ax.set_ylabel("°C", color="#bbbbbb", fontsize=9)
        ax.tick_params(colors="#bbbbbb", labelsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        plt.setp(ax.xaxis.get_majorticklabels(),
                 rotation=30, ha="right", color="#bbbbbb")
        for spine in ax.spines.values():
            spine.set_edgecolor("#ebebeb")
        st.pyplot(fig)
        plt.close()
 
        render_seccion("Detalle de predicciones", "")
        df_t = df_preds.copy()
        df_t["Fecha_Prediccion"] = df_t["Fecha_Prediccion"].dt.strftime("%d %b %Y")
        df_t["Fecha_Para"]       = df_t["Fecha_Para"].dt.strftime("%d %b %Y")
        df_t = df_t.rename(columns={
            "Fecha_Prediccion":  "Hecha el",
            "Fecha_Para":        "Para el día",
            "Temp_Max_Pred":     "Temp (°C)",
            "Humedad_Pred":      "Humedad (%)",
            "Lluvia_Pred":       "Lluvia (mm)",
            "Viento_Pred":       "Viento (km/h)",
            "Presion_Pred":      "Presión (hPa)",
            "Indice_Calor_Pred": "Índice Calor",
            "Nivel_Alerta":      "Nivel",
            "Hora_Registro":     "Hora"
        })
        st.dataframe(
            df_t.style.background_gradient(subset=["Índice Calor"], cmap="YlOrRd"),
            use_container_width=True, hide_index=True
        )
        csv_data = df_preds.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Descargar historial CSV",
            data=csv_data,
            file_name="thermoIA_predicciones.csv",
            mime="text/csv"
        )
 
# ══════════════════════════════════════════════════════════════════════════════
#  VISTA 4 — EXPLORADOR HISTÓRICO
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Explorador Histórico":
 
    render_header(fecha_es(hoy))
    render_seccion("Explorador de datos 1990–2026", "")
 
    if historial is not None:
        historial["Año"] = historial["Fecha"].dt.year
        anios = sorted(historial["Año"].unique().tolist())
 
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            anio_sel = st.multiselect("Año(s)", options=anios,
                                       default=[anios[-2], anios[-1]])
        with col_f2:
            variable = st.selectbox("Variable", [
                "Indice_Calor","Temp_Max","Temp_Prom","Temp_Min",
                "Humedad","Lluvia","Presion","Viento_Max"
            ])
        with col_f3:
            tipo = st.selectbox("Tipo de gráfica", ["Línea","Área","Barra"])
 
        if not anio_sel:
            st.warning("Selecciona al menos un año.")
        else:
            df_f = historial[historial["Año"].isin(anio_sel)].copy()
 
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Días analizados", f"{len(df_f):,}")
            if "Indice_Calor" in df_f.columns:
                m2.metric("IC promedio",   f"{df_f['Indice_Calor'].mean():.1f}°C")
                m3.metric("IC máximo",     f"{df_f['Indice_Calor'].max():.1f}°C")
                dp = len(df_f[df_f["Indice_Calor"] >= 35])
                m4.metric("Días en peligro+", f"{dp:,}")
 
            render_seccion(f"{variable} — {', '.join(map(str,anio_sel))}", "")
 
            colores_v = {
                "Indice_Calor":"#E24B4A","Temp_Max":"#E65100","Temp_Prom":"#F57F17",
                "Temp_Min":"#999999","Humedad":"#378ADD","Lluvia":"#1D9E75",
                "Presion":"#534AB7","Viento_Max":"#1a1a1a"
            }
            c = colores_v.get(variable, "#E24B4A")
 
            fig, ax = plt.subplots(figsize=(13, 4), facecolor="#f8f7f5")
            ax.set_facecolor("#ffffff")
 
            if variable in df_f.columns:
                if tipo == "Línea":
                    ax.plot(df_f["Fecha"], df_f[variable],
                            color=c, linewidth=0.8, alpha=0.9)
                elif tipo == "Área":
                    ax.fill_between(df_f["Fecha"], df_f[variable],
                                    color=c, alpha=0.25)
                    ax.plot(df_f["Fecha"], df_f[variable],
                            color=c, linewidth=0.8)
                else:
                    ax.bar(df_f["Fecha"], df_f[variable],
                           color=c, alpha=0.7, width=1)
 
            if variable == "Indice_Calor":
                ax.axhline(32, color="#F57F17", linestyle="--",
                           linewidth=0.8, alpha=0.6, label="Precaución")
                ax.axhline(35, color="#E65100", linestyle="--",
                           linewidth=0.8, alpha=0.6, label="Peligro")
                ax.axhline(41, color="#E24B4A", linestyle="--",
                           linewidth=0.8, alpha=0.6, label="P.Extremo")
                ax.legend(fontsize=8, facecolor="#ffffff",
                          edgecolor="#ebebeb", labelcolor="#666666")
 
            ax.tick_params(colors="#bbbbbb", labelsize=8)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            plt.setp(ax.xaxis.get_majorticklabels(),
                     rotation=30, ha="right", color="#bbbbbb")
            for spine in ax.spines.values():
                spine.set_edgecolor("#ebebeb")
            st.pyplot(fig)
            plt.close()
 
            render_seccion("Registros recientes", "")
            cols_t = [c for c in ["Fecha","Temp_Max","Temp_Prom","Humedad",
                                   "Lluvia","Indice_Calor"] if c in df_f.columns]
            df_show = df_f[cols_t].sort_values("Fecha", ascending=False).head(100)
            st.dataframe(
                df_show.style.background_gradient(
                    subset=["Indice_Calor"] if "Indice_Calor" in df_show.columns else [],
                    cmap="YlOrRd"
                ),
                use_container_width=True, hide_index=True
            )
    else:
        st.warning("No se encontró dataset_features.csv.")
 
# ══════════════════════════════════════════════════════════════════════════════
#  VISTA 5 — SOBRE EL MODELO
# ══════════════════════════════════════════════════════════════════════════════
else:
    render_header(fecha_es(hoy))
    render_seccion("Metodología y arquitectura del sistema", "")
 
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(info_card("Fuente de datos",
            "Open-Meteo Historical Archive API<br>"
            "Coordenadas: David, Chiriquí (8.42°N, 82.43°W)<br>"
            "Período: 1990–2026 · 36 años de historia<br>"
            "13,000+ registros diarios<br>"
            "Variables: temperatura, humedad, lluvia, viento, presión"
        ), unsafe_allow_html=True)
        st.markdown(info_card("Feature Engineering",
            "Lags temporales: 1, 7 y 30 días<br>"
            "Medias móviles: 7 y 30 días<br>"
            "Índice de Calor — fórmula de Rothfusz (OMS)<br>"
            "Estacionalidad: verano panameño / lluvioso<br>"
            "35 features en total por registro"
        ), unsafe_allow_html=True)
 
    with col2:
        st.markdown(info_card("Modelos entrenados",
            "XGBoost Regressor — 5 modelos<br>"
            "Random Forest Regressor — 5 modelos<br>"
            "Variables predichas: temperatura, humedad,<br>"
            "lluvia, viento y presión<br>"
            "División cronológica 80/20 (no aleatoria)"
        ), unsafe_allow_html=True)
        st.markdown(info_card("Niveles de alerta — Rothfusz/OMS",
            "Fórmula que combina temperatura + humedad real<br>"
            "para calcular la sensación térmica real del cuerpo.<br><br>"
            "🟢 Normal: IC &lt; 32°C<br>"
            "🟡 Precaución: IC 32–34°C<br>"
            "🟠 Peligro: IC 35–40°C<br>"
            "🔴 Peligro Extremo: IC ≥ 41°C"
        ), unsafe_allow_html=True)
 
    if historial is not None and "Temp_Max" in historial.columns:
        render_seccion("Tendencia de calentamiento 1990–2026", "")
        anual = historial.groupby(historial["Fecha"].dt.year)["Temp_Max"].mean()
        fig, ax = plt.subplots(figsize=(13, 3.5), facecolor="#f8f7f5")
        ax.set_facecolor("#ffffff")
        ax.fill_between(anual.index, anual.values, alpha=0.1, color="#E24B4A")
        ax.plot(anual.index, anual.values, color="#E24B4A",
                linewidth=2, marker="o", markersize=4)
        z = np.polyfit(anual.index, anual.values, 1)
        p = np.poly1d(z)
        ax.plot(anual.index, p(anual.index), color="#bbbbbb",
                linewidth=1.2, linestyle="--", label="Tendencia")
        cambio = p(anual.index[-1]) - p(anual.index[0])
        ax.set_title(
            f"Temperatura Máxima Promedio Anual  (+{cambio:.2f}°C en 36 años)",
            color="#666666", fontsize=10, loc="left", pad=12
        )
        ax.tick_params(colors="#bbbbbb", labelsize=8)
        ax.legend(fontsize=8, facecolor="#ffffff",
                  edgecolor="#ebebeb", labelcolor="#666666")
        for spine in ax.spines.values():
            spine.set_edgecolor("#ebebeb")
        st.pyplot(fig)
        plt.close()