import streamlit as st
import pandas as pd
import random
import requests

# 0. CONFIGURACIÓN DE SECRETOS (Con verificación de errores)
def get_secrets():
    try:
        return {
            "URL": st.secrets["URL_API"],
            "PASS": st.secrets["PASSWORD_ADMIN"],
            "NOM": st.secrets["NOMBRE_PAGO"],
            "BAN": st.secrets["BANCO_PAGO"],
            "CUE": st.secrets["CUENTA_PAGO"],
            "TEL": st.secrets["TEL_PAGO"]
        }
    except KeyError as e:
        st.error(f"⚠️ Error: Falta la variable {e} en los Secrets de Streamlit.")
        st.stop()

sec = get_secrets()

# 1. ESTÉTICA
st.set_page_config(page_title="Rifa - lukario229", layout="centered")
st.markdown("""<style>#MainMenu, footer, header {visibility: hidden;} .main { background-color: #000; color: #fff; } .info-box { background-color: #1A1A1A; padding: 20px; border-radius: 10px; border: 1px solid #333; }</style>""", unsafe_allow_html=True)

# 2. FUNCIONES
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        res = requests.get(sec["URL"], timeout=10)
        if res.status_code == 200:
            d = res.json()
            if len(d) > 1: return pd.DataFrame(d[1:], columns=d[0])
        return pd.DataFrame(columns=["Nombre", "Teléfono", "Boleto", "Pago"])
    except:
        return pd.DataFrame(columns=["Nombre", "Teléfono", "Boleto", "Pago"])

def enviar_datos(n, t, b):
    try:
        res = requests.post(sec["URL"], json={"Nombre": n, "Telefono": t, "Boleto": b}, timeout=15)
        return res.status_code == 200
    except: return False

# 3. LÓGICA
if "globos" not in st.session_state: st.session_state.globos = False

df = cargar_datos()
total = len(df)

# --- VISTA ---
st.title("🎟️ Gran Rifa Solidaria")
if st.session_state.globos:
    st.balloons()
    st.session_state.globos = False

st.write(f"### 📊 Cupos: {total} / 50")
st.progress(min(total / 50, 1.0))

st.markdown(f"""
<div class="info-box">
    <b>👤 Beneficiario:</b> {sec['NOM']}<br>
    <b>🏦 Banco:</b> {sec['BAN']}<br>
    <b>🔢 Cuenta:</b> {sec['CUE']}<br>
    <b>📱 Contacto:</b> {sec['TEL']}<br>
    <hr>
    1. Transfiere con tu nombre en el concepto.<br>
    2. Regístrate abajo y manda captura al contacto.
</div>
""", unsafe_allow_html=True)

if total >= 50:
    st.error("🚫 Cupo lleno.")
else:
    with st.form("reg_form", clear_on_submit=True):
        nom_in = st.text_input("Nombre Completo:")
        tel_in = st.text_input("Teléfono (10 dígitos):", max_chars=10)
        bot = st.form_submit_button("Registrar")
        
        if bot:
            if nom_in and len(tel_in) == 10:
                # Generar número
                usados = df['Boleto'].tolist() if not df.empty else []
                while True:
                    n_bol = f"{random.randint(0, 9999):04d}"
                    if n_bol not in usados: break
                
                if enviar_datos(nom_in, tel_in, n_bol):
                    st.session_state.globos = True
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Error de conexión con Google.")
            else:
                st.warning("⚠️ Datos inválidos.")

# --- ADMIN ---
with st.expander("🔐 Admin"):
    if st.text_input("Pass:", type="password") == sec["PASS"]:
        st.dataframe(df, use_container_width=True)
