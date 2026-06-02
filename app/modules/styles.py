import streamlit as st
 
 
def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
 
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
        color: #1a1a1a;
    }
 
    .stApp { background: #f8f7f5; }
 
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #ebebeb;
    }
 
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #ebebeb;
    }
 
    [data-testid="stMetricLabel"] { color: #888888; font-size: 0.75rem; }
    [data-testid="stMetricValue"] { color: #1a1a1a; font-size: 1.4rem; }
 
    .stSelectbox > div, .stMultiSelect > div {
        background: #ffffff;
        border: 1px solid #ebebeb;
        border-radius: 10px;
    }
 
    .stButton > button {
        background: #1a1a1a;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-weight: 500;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
 
    .stRadio > label { color: #444444; }
    .stRadio > div { gap: 4px; }
 
    @keyframes gradiente {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
 
    @keyframes marquee {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
 
    @keyframes pulso {
        0%   { box-shadow: 0 0 0 0 rgba(226,75,74,0.3); }
        70%  { box-shadow: 0 0 0 10px rgba(226,75,74,0); }
        100% { box-shadow: 0 0 0 0 rgba(226,75,74,0); }
    }
 
    </style>
    """, unsafe_allow_html=True)
 
 
# ── Logo + header de la app ───────────────────────────────────────────────────
def render_header(fecha_hoy_str):
    st.markdown(
        f"<div style='display:flex;align-items:center;justify-content:space-between;"
        f"padding:20px 0 16px;border-bottom:1px solid #ebebeb;margin-bottom:28px'>"
        f"<div style='display:flex;align-items:center;gap:12px'>"
        f"<div style='width:38px;height:38px;background:#E24B4A;border-radius:10px;"
        f"display:flex;align-items:center;justify-content:center;flex-shrink:0'>"
        f"<svg width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='white' "
        f"stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
        f"<path d='M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z'/>"
        f"</svg></div>"
        f"<div>"
        f"<div style='font-size:1.15rem;font-weight:600;color:#1a1a1a;line-height:1.1'>ThermoIA</div>"
        f"<div style='font-size:0.72rem;color:#999999;margin-top:1px'>"
        f"Tu asistente inteligente para el monitoreo y prevención ante altas temperaturas</div>"
        f"</div></div>"
        f"<div style='text-align:right'>"
        f"<div style='font-size:0.7rem;color:#bbbbbb;letter-spacing:1.5px;text-transform:uppercase'>Hoy</div>"
        f"<div style='font-size:0.95rem;font-weight:500;color:#1a1a1a'>{fecha_hoy_str}</div>"
        f"<div style='font-size:0.7rem;color:#bbbbbb;margin-top:1px'>📍 David, Chiriquí, Panamá</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )
 
 
# ── Separador de sección elegante ────────────────────────────────────────────
def render_seccion(titulo, icono=""):
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;margin:28px 0 14px'>"
        f"<span style='font-size:0.65rem;font-weight:600;letter-spacing:2.5px;"
        f"text-transform:uppercase;color:#bbbbbb'>{icono} {titulo}</span>"
        f"<div style='flex:1;height:1px;background:#ebebeb'></div>"
        f"</div>",
        unsafe_allow_html=True
    )
 
 
# ── 6 tarjetas de clima de hoy ────────────────────────────────────────────────
def render_clima_cards(datos):
    items = [
        ("🌡", f"{datos['temp_max']}°C",       "Temp máx",  "#E24B4A"),
        ("🌡", f"{datos['temp_min']}°C",       "Temp mín",  "#888888"),
        ("💧", f"{datos['humedad']}%",          "Humedad",   "#378ADD"),
        ("🌧", f"{datos['lluvia']}mm",          "Lluvia",    "#378ADD"),
        ("💨", f"{datos['viento_max']}km/h",   "Viento",    "#1a1a1a"),
        ("🔵", f"{datos['presion']}hPa",        "Presión",   "#888888"),
    ]
    cols = st.columns(6)
    for col, (ico, val, lab, color) in zip(cols, items):
        with col:
            st.markdown(
                f"<div style='background:#ffffff;border-radius:12px;padding:16px 10px;"
                f"text-align:center;border:1px solid #ebebeb'>"
                f"<div style='font-size:1.3rem;margin-bottom:6px'>{ico}</div>"
                f"<div style='font-family:DM Mono,monospace;font-size:1.25rem;"
                f"font-weight:500;color:{color};line-height:1'>{val}</div>"
                f"<div style='font-size:0.65rem;color:#bbbbbb;text-transform:uppercase;"
                f"letter-spacing:1px;margin-top:4px'>{lab}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
 
 
# ── Tarjeta principal de predicción mañana ────────────────────────────────────
def render_prediccion_card(alerta, ic_manana, pred_temp, pred_hum,
                           pred_lluv, pred_vien, pred_pres,
                           datos_hoy, fecha_manana_str, modelo_elegido):
    color     = alerta["color"]
    nivel     = alerta["nivel"]
    icono     = alerta["icono"]
    rec_titulo = alerta["recs"][0]["titulo"]
    rec_desc   = alerta["recs"][0]["desc"][:110] + "..."
 
    # Badge de nivel
    badges = {
        "PELIGRO EXTREMO": ("#FCEBEB", "#A32D2D"),
        "PELIGRO":         ("#FFF3E0", "#E65100"),
        "PRECAUCIÓN":      ("#FFFDE7", "#F57F17"),
        "NORMAL":          ("#E8F5E9", "#2E7D32"),
    }
    bg_badge, txt_badge = badges.get(nivel, ("#f5f5f5", "#444"))
 
    anim = "animation:pulso 2s infinite;" if "EXTREMO" in nivel else ""
 
    col_main, col_met = st.columns([1, 1])
 
    with col_main:
        st.markdown(
            f"<div style='background:#ffffff;border-radius:16px;padding:28px 24px;"
            f"border:2px solid {color};height:100%;{anim}'>"
            f"<div style='font-size:0.65rem;color:#bbbbbb;letter-spacing:2px;"
            f"text-transform:uppercase;margin-bottom:4px'>Predicción para</div>"
            f"<div style='font-size:1rem;font-weight:500;color:#1a1a1a;"
            f"margin-bottom:20px'>{fecha_manana_str}</div>"
            f"<div style='display:inline-flex;align-items:center;gap:6px;"
            f"background:{bg_badge};border-radius:8px;padding:5px 12px;margin-bottom:16px'>"
            f"<span style='font-size:0.85rem'>{icono}</span>"
            f"<span style='font-size:0.75rem;font-weight:600;color:{txt_badge};"
            f"letter-spacing:1px'>{nivel}</span>"
            f"</div>"
            f"<div style='font-family:DM Mono,monospace;font-size:3rem;"
            f"font-weight:500;color:{color};line-height:1;margin-bottom:4px'>{ic_manana}°C</div>"
            f"<div style='font-size:0.72rem;color:#bbbbbb;margin-bottom:20px'>"
            f"Índice de calor · {alerta['rango']}</div>"
            f"<div style='background:#f8f7f5;border-radius:10px;padding:12px 14px'>"
            f"<div style='font-size:0.7rem;font-weight:600;color:{color};"
            f"margin-bottom:4px'>{rec_titulo}</div>"
            f"<div style='font-size:0.78rem;color:#666666;line-height:1.5'>{rec_desc}</div>"
            f"</div>"
            f"<div style='margin-top:14px;font-size:0.65rem;color:#cccccc'>"
            f"Modelo: {modelo_elegido}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
 
    with col_met:
        metricas = [
            ("🌡", "Temperatura máx",   f"{pred_temp}°C",  f"{round(pred_temp - datos_hoy['temp_max'],1)}° vs hoy"),
            ("💧", "Humedad",           f"{pred_hum}%",    f"{round(pred_hum - datos_hoy['humedad'],1)}% vs hoy"),
            ("🌧", "Lluvia estimada",   f"{pred_lluv}mm",  None),
            ("💨", "Viento máx",        f"{pred_vien}km/h",None),
            ("🔵", "Presión atmosf.",   f"{pred_pres}hPa", None),
        ]
        for ico, lab, val, delta in metricas:
            delta_html = ""
            if delta:
                d_color = "#E24B4A" if "+" in delta else "#378ADD"
                delta_html = f"<span style='font-size:0.7rem;color:{d_color}'>{delta}</span>"
            st.markdown(
                f"<div style='background:#ffffff;border-radius:12px;padding:14px 16px;"
                f"border:1px solid #ebebeb;margin-bottom:8px;"
                f"display:flex;align-items:center;justify-content:space-between'>"
                f"<div style='display:flex;align-items:center;gap:10px'>"
                f"<span style='font-size:1.2rem'>{ico}</span>"
                f"<span style='font-size:0.82rem;color:#666666'>{lab}</span>"
                f"</div>"
                f"<div style='text-align:right'>"
                f"<div style='font-family:DM Mono,monospace;font-size:1rem;"
                f"font-weight:500;color:#1a1a1a'>{val}</div>"
                f"{delta_html}</div></div>",
                unsafe_allow_html=True
            )
 
 
# ── Tarjetas de recomendación ─────────────────────────────────────────────────
def render_rec_cards(recs, color):
    badges_cons = {
        "#E24B4A": ("#FCEBEB", "#A32D2D"),
        "#FF6D00": ("#FFF3E0", "#E65100"),
        "#FFAB00": ("#FFFDE7", "#F57F17"),
        "#00C853": ("#E8F5E9", "#2E7D32"),
    }
    bg_c, txt_c = badges_cons.get(color, ("#f5f5f5", "#444"))
 
    for i in range(0, len(recs), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(recs):
                rec = recs[i + j]
                with col:
                    st.markdown(
                        f"<div style='background:#ffffff;border-radius:14px;"
                        f"padding:22px 20px;border:1px solid #ebebeb;"
                        f"border-top:3px solid {color};margin-bottom:12px'>"
                        f"<div style='font-size:1.8rem;margin-bottom:10px'>{rec['icono']}</div>"
                        f"<div style='font-size:0.95rem;font-weight:600;color:#1a1a1a;"
                        f"margin-bottom:8px'>{rec['titulo']}</div>"
                        f"<div style='font-size:0.82rem;color:#666666;line-height:1.65;"
                        f"margin-bottom:14px'>{rec['desc']}</div>"
                        f"<div style='background:{bg_c};border-radius:8px;"
                        f"padding:10px 12px'>"
                        f"<div style='font-size:0.65rem;font-weight:600;"
                        f"text-transform:uppercase;letter-spacing:1.5px;"
                        f"color:{color};margin-bottom:4px'>⚠ Consecuencia</div>"
                        f"<div style='font-size:0.78rem;color:{txt_c};"
                        f"line-height:1.5'>{rec['consecuencia']}</div>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )
 
 
# ── Tarjetas pronóstico 7 días ────────────────────────────────────────────────
def render_forecast_cards(df7):
    dias_es = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    cols = st.columns(7)
    for i, (col, (_, row)) in enumerate(zip(cols, df7.iterrows())):
        with col:
            a      = row["alerta"]
            color  = a["color"]
            emoji  = a["emoji"]
            nivel  = a["nivel"].split()[0]
            dia    = dias_es[row["fecha"].weekday()]
            fecha  = row["fecha"].strftime("%d %b")
            es_hoy = i == 0
 
            borde = f"border:2px solid {color}" if es_hoy else "border:1px solid #ebebeb"
            bg    = "#ffffff"
 
            st.markdown(
                f"<div style='background:{bg};border-radius:14px;padding:16px 8px;"
                f"text-align:center;{borde};position:relative'>"
                + (f"<div style='position:absolute;top:-9px;left:50%;transform:translateX(-50%);"
                   f"background:{color};color:white;font-size:0.6rem;font-weight:600;"
                   f"padding:2px 8px;border-radius:20px;letter-spacing:1px'>HOY+1</div>" if es_hoy else "")
                + f"<div style='font-size:0.65rem;font-weight:600;color:#bbbbbb;"
                f"letter-spacing:1.5px;text-transform:uppercase;margin-bottom:2px'>{dia}</div>"
                f"<div style='font-size:0.7rem;color:#cccccc;margin-bottom:10px'>{fecha}</div>"
                f"<div style='font-size:1.8rem;margin:6px 0'>{emoji}</div>"
                f"<div style='font-family:DM Mono,monospace;font-size:1.3rem;"
                f"font-weight:500;color:{color};line-height:1'>{round(row['temp_max'],1)}°</div>"
                f"<div style='font-size:0.72rem;color:#cccccc;margin-top:2px'>"
                f"{round(row['temp_min'],1)}°</div>"
                f"<div style='font-size:0.6rem;font-weight:600;letter-spacing:1px;"
                f"color:{color};margin-top:8px;text-transform:uppercase'>{nivel}</div>"
                f"<div style='font-size:0.65rem;color:#378ADD;margin-top:4px'>"
                f"💧 {round(row['lluvia'],1)}mm</div>"
                f"</div>",
                unsafe_allow_html=True
            )
 
 
# ── Marquee de alertas rápidas ────────────────────────────────────────────────
def get_sliding_recs(recs, color):
    items = "".join([
        f'<span style="display:inline-block;padding:0 32px;font-size:0.85rem;'
        f'color:#444444;font-weight:500">· {r["titulo"]}</span>'
        for r in recs * 2
    ])
    return (
        f"<div style='background:#ffffff;border-top:1px solid #ebebeb;"
        f"border-bottom:1px solid #ebebeb;overflow:hidden;"
        f"padding:10px 0;margin:0 0 24px'>"
        f"<div style='display:flex;white-space:nowrap;"
        f"animation:marquee 28s linear infinite'>{items}</div>"
        f"</div>"
    )
 
 
# ── Info card para "Sobre el Modelo" ─────────────────────────────────────────
def info_card(titulo, contenido):
    return (
        f"<div style='background:#ffffff;border-radius:14px;padding:20px;"
        f"border:1px solid #ebebeb;margin-bottom:12px'>"
        f"<div style='font-size:0.65rem;font-weight:600;letter-spacing:2px;"
        f"text-transform:uppercase;color:#E24B4A;margin-bottom:10px'>{titulo}</div>"
        f"<div style='font-size:0.85rem;color:#666666;line-height:1.8'>"
        f"{contenido}</div></div>"
    )
 
 
# ── Resultado del simulador ───────────────────────────────────────────────────
def render_simulador_resultado(tiempo_txt, mensaje, sim_color):
    st.markdown(
        f"<div style='background:#ffffff;border-radius:14px;padding:28px;"
        f"text-align:center;border:2px solid {sim_color};margin-top:16px'>"
        f"<div style='font-family:DM Mono,monospace;font-size:3rem;"
        f"font-weight:500;color:{sim_color};line-height:1'>{tiempo_txt}</div>"
        f"<div style='font-size:0.65rem;color:#bbbbbb;text-transform:uppercase;"
        f"letter-spacing:2px;margin-top:6px'>Tiempo máximo seguro de exposición</div>"
        f"<div style='font-size:0.85rem;color:#666666;margin-top:12px;line-height:1.6'>"
        f"{mensaje}</div>"
        f"</div>",
        unsafe_allow_html=True
    )