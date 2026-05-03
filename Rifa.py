import streamlit as st
import pandas as pd
import random
import requests

# 0. CONFIGURACIÓN DE SECRETOS
try:
    URL_API = st.secrets["URL_API"]
    PASSWORD_ADMIN = st.secrets["PASSWORD_ADMIN"]
    NOMBRE_PAGO = st.secrets["NOMBRE_PAGO"]
    BANCO_PAGO = st.secrets["BANCO_PAGO"]
    CUENTA_PAGO = st.secrets["CUENTA_PAGO"]
    TEL_PAGO = st.secrets["TEL_PAGO"] 
except:
    st.error("⚠️ Error: Revisa tus Secretos en Streamlit.")
    st.stop()

# 1. ESTÉTICA
st.set_page_config(page_title="Registro de Rifa - lukario229", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #000000; color: white; }
    .info-box { background-color: #1A1A1A; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 25px; }
    .stButton>button { width: 100%; background-color: #2E2E2E; color: white; border: 1px solid #444; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIONES
def cargar_datos_nube():
    try:
        response = requests.get(URL_API)
        if response.status_code == 200:
            datos = response.json()
            if len(datos) > 1:
                return pd.DataFrame(datos[1:], columns=datos[0])
        return pd.DataFrame(columns=["Nombre", "Teléfono", "Boleto", "Pago"])
    except:
        return pd.DataFrame(columns=["Nombre", "Teléfono", "Boleto", "Pago"])

def guardar_en_nube(nombre, telefono, boleto):
    payload = {"Nombre": nombre, "Telefono": telefono, "Boleto": boleto}
    try:
        res = requests.post(URL_API, json=payload)
        return res.status_code == 200
    except:
        return False

# --- LÓGICA DE GLOBOS ---
if "mostrar_globos" not in st.session_state:
    st.session_state.mostrar_globos = False

# --- DATOS ACTUALES ---
df_actual = cargar_datos_nube()
total_inscritos = len(df_actual)
LIMITE_PARTICIPANTES = 50 

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

# Lanzar globos si el estado es verdadero
if st.session_state.mostrar_globos:
    st.balloons()
    st.session_state.mostrar_globos = False # Se apaga para la próxima recarga

st.write(f"### 📊 Cupos llenos: {total_inscritos} / {LIMITE_PARTICIPANTES}")
st.progress(total_inscritos / LIMITE_PARTICIPANTES)

# 4. CAJA DE INFORMACIÓN
st.markdown(f"""
<div class="info-box">
    <h3 style='margin-top:0;'>📋 Información de Pago</h3>
    <p><b>👤 Beneficiario:</b> {NOMBRE_PAGO}</p>
    <p><b>🏦 Banco:</b> {BANCO_PAGO}</p>
    <p><b>🔢 Cuenta:</b> {CUENTA_PAGO}</p>
    <p><b>📱 Teléfono de contacto:</b> {TEL_PAGO}</p>
    <hr style='border-color:#333;'>
<p style='font-size: 0.9em; color: #bbb;'>
1. <b>Realiza tu transferencia:</b> Usa los datos de cuenta de arriba.<br><br>
2. <b>Concepto de pago:</b> Es vital que pongas tu nombre completo como concepto.<br><br>
3. <b>Confirma tu registro:</b> Llena el formulario de abajo para generar tu número.<br><br>
4. <b>Envía tu comprobante:</b> Manda la captura al número de contacto para activar tu boleto.
</p>
</div>
""", unsafe_allow_html=True)

if total_inscritos >= LIMITE_PARTICIPANTES:
    st.error("🚫 Cupo lleno.")
else:
    with st.expander("📝 Formulario de Registro", expanded=True):
        nombre_input = st.text_input("Nombre Completo:")
        tel_input = st.text_input("Número de Teléfono:", max_chars=10)
        
        if st.button("Registrar Participación"):
            if nombre_input and len(tel_input) == 10:
                with st.spinner("Registrando..."):
                    while True:
                        num = f"{random.randint(0, 9999):04d}" 
                        if num not in df_actual['Boleto'].values:
                            break
                    
                    if guardar_en_nube(nombre_input, tel_input, num):
                        st.session_state.mostrar_globos = True
                        st.rerun()
            else:
                st.warning("Revisa tus datos.")

# --- ADMINISTRADOR ---
st.write("---")
with st.expander("🔐 Administrador"):
    clave = st.text_input("Password:", type="password")
    if clave == PASSWORD_ADMIN:
        st.dataframe(df_actual, use_container_width=True)
