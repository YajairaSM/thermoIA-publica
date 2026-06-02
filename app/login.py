"""
app/login.py
Módulo de autenticación para la app admin de ThermoIA.
Importar desde app.py con: from login import render_login, render_user_badge, logout
"""

import streamlit as st
import hashlib

# ── Credenciales ──────────────────────────────────────────────────────────────
# Cambia las contraseñas antes de publicar.
# Para mayor seguridad en producción usa st.secrets["passwords"]
USUARIOS = {
    "admin": {
        "password": hashlib.sha256("admin2026".encode()).hexdigest(),
        "nombre":   "Administrador",
    },
    "yajaira": {
        "password": hashlib.sha256("thermoIA2026".encode()).hexdigest(),
        "nombre":   "Yajaira",
    },
}

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verificar_login(usuario: str, password: str):
    u = USUARIOS.get(usuario.lower().strip())
    if u and u["password"] == _hash(password):
        return u
    return None

# ── Pantalla de login ─────────────────────────────────────────────────────────
def render_login() -> bool:
    """
    Muestra la pantalla de login si no hay sesión activa.
    Retorna True si el usuario ya está autenticado.
    """
    if st.session_state.get("autenticado"):
        return True

    # Ocultar sidebar en la pantalla de login
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #f8f7f5; }
    .stApp { background: #f8f7f5; }
    section[data-testid="stSidebar"] { display: none !important; }
    .block-container { max-width: 420px !important; padding-top: 10vh !important; }
    .stTextInput > div > div > input {
        background: #ffffff; border: 1px solid #ebebeb;
        border-radius: 10px; padding: 12px 16px;
        font-size: 0.9rem; color: #1a1a1a;
    }
    .stTextInput > div > div > input:focus {
        border-color: #E24B4A;
        box-shadow: 0 0 0 3px rgba(226,75,74,0.1);
    }
    .stButton > button {
        background: #1a1a1a; color: #ffffff; border: none;
        border-radius: 10px; font-weight: 500;
        padding: 12px; font-size: 0.9rem; width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.8; }
    </style>
    """, unsafe_allow_html=True)

    # Logo + título
    st.markdown(
        "<div style='text-align:center;margin-bottom:36px'>"
        "<div style='width:52px;height:52px;background:#E24B4A;border-radius:14px;"
        "display:flex;align-items:center;justify-content:center;margin:0 auto 14px'>"
        "<svg width='26' height='26' viewBox='0 0 24 24' fill='none' stroke='white'"
        " stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z'/>"
        "</svg></div>"
        "<div style='font-size:1.4rem;font-weight:600;color:#1a1a1a;margin-bottom:4px'>"
        "ThermoIA Admin</div>"
        "<div style='font-size:0.78rem;color:#999'>"
        "Panel de administración · David, Chiriquí</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # Card formulario
    st.markdown(
        "<div style='background:#ffffff;border-radius:16px;padding:32px 28px;"
        "border:1px solid #ebebeb;box-shadow:0 4px 24px rgba(0,0,0,0.06)'>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:0.88rem;font-weight:500;color:#1a1a1a;"
        "margin-bottom:18px'>Iniciar sesión</div>",
        unsafe_allow_html=True
    )

    usuario  = st.text_input("Usuario",     placeholder="Usuario",
                              label_visibility="collapsed")
    password = st.text_input("Contraseña",  placeholder="Contraseña",
                              type="password", label_visibility="collapsed")

    if st.session_state.get("login_error"):
        st.markdown(
            "<div style='background:#FCEBEB;border-radius:8px;padding:10px 14px;"
            "font-size:0.8rem;color:#A32D2D;margin:8px 0'>"
            "⚠ Usuario o contraseña incorrectos.</div>",
            unsafe_allow_html=True
        )

    ingresar = st.button("Ingresar", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;margin-top:20px'>"
        "<div style='font-size:0.7rem;color:#cccccc'>"
        "ThermoIA · Sistema de Alertas de Calor · David, Chiriquí, Panamá"
        "</div></div>",
        unsafe_allow_html=True
    )

    if ingresar:
        resultado = verificar_login(usuario, password)
        if resultado:
            st.session_state["autenticado"] = True
            st.session_state["usuario"]     = usuario
            st.session_state["nombre"]      = resultado["nombre"]
            st.session_state["login_error"] = False
            st.rerun()
        else:
            st.session_state["login_error"] = True
            st.rerun()

    return False


def logout():
    """Cierra la sesión y regresa al login."""
    for k in ["autenticado", "usuario", "nombre", "login_error"]:
        st.session_state.pop(k, None)
    st.rerun()


def render_user_badge():
    """Badge del usuario activo en el sidebar."""
    nombre  = st.session_state.get("nombre",  "Admin")
    usuario = st.session_state.get("usuario", "")
    st.sidebar.markdown(
        f"<div style='background:#f8f7f5;border-radius:10px;padding:10px 14px;"
        f"border:1px solid #ebebeb;margin-bottom:8px'>"
        f"<div style='font-size:0.65rem;color:#bbbbbb;margin-bottom:2px'>"
        f"Sesión activa</div>"
        f"<div style='font-size:0.88rem;font-weight:600;color:#1a1a1a'>{nombre}</div>"
        f"<div style='font-size:0.7rem;color:#bbbbbb'>@{usuario}</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        logout()
