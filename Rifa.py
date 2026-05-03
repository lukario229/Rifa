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
except KeyError as e:
    st.error(f"⚠️ Error: Falta configurar el secreto {e} en Streamlit.")
    st.stop()

# 1. ESTÉTICA
st.set_page_config(page_title="Rifa - Heliu", layout="centered")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .main { background-color: #000000; color: white; }
    .info-box { background-color: #1A1A1A; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 25px; }
    .stButton>button { width: 100%; background-color: #2E2E2E; color: white; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIONES CON CACHÉ
@st.cache_data(ttl=60)
def cargar_datos_nube():
    try:
        response = requests.get(URL_API, timeout=10)
        if response.status_code == 200:
            datos = response.json()
            if len(datos) > 1:
                return pd.DataFrame(datos[1:], columns=datos[0])
        return pd.DataFrame(columns=["Nombre", "Teléfono", "Boleto"])
    except:
        return pd.DataFrame(columns=["Nombre", "Teléfono", "Boleto"])

def guardar_en_nube(nombre, telefono, boleto):
    payload = {"Nombre": nombre, "Telefono": telefono, "Boleto": boleto}
    try:
        res = requests.post(URL_API, json=payload, timeout=15)
        return res.status_code == 200
    except:
        return False

# 3. LÓGICA DE ESTADO (Globos y Número)
if "mostrar_globos" not in st.session_state:
    st.session_state.mostrar_globos = False
if "numero_boleto" not in st.session_state:
    st.session_state.numero_boleto = ""

# Datos actuales
df_actual = cargar_datos_nube()
total_inscritos = len(df_actual)
LIMITE_PARTICIPANTES = 50 

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

# Mostrar éxito si el estado es verdadero
if st.session_state.mostrar_globos:
    st.balloons()
    st.success(f"✅ ¡Éxito! Tu boleto es: **{st.session_state.numero_boleto}**")
    st.session_state.mostrar_globos = False # Resetear para la próxima

st.write(f"### 📊 Cupos llenos: {total_inscritos} / {LIMITE_PARTICIPANTES}")
st.progress(min(total_inscritos / LIMITE_PARTICIPANTES, 1.0))

st.markdown(f"""
<div class="info-box">
    <h3 style='margin-top:0;'>📋 Información de Pago</h3>
    <p><b>👤 Beneficiario:</b> {NOMBRE_PAGO}</p>
    <p><b>🏦 Banco:</b> {BANCO_PAGO}</p>
    <p><b>🔢 Cuenta:</b> {CUENTA_PAGO}</p>
    <p><b>📱 Contacto:</b> {TEL_PAGO}</p>
    <hr style='border-color:#333;'>
    <p style='font-size: 0.9em; color: #bbb;'>
    1. Transfiere con tu <b>nombre</b> en el concepto.<br>
    2. Regístrate abajo para generar tu número.<br>
    3. Envía captura al contacto.
    </p>
</div>
""", unsafe_allow_html=True)

if total_inscritos >= LIMITE_PARTICIPANTES:
    st.error("🚫 Cupo lleno.")
else:
    with st.form("registro_form", clear_on_submit=True):
        nombre_input = st.text_input("Nombre Completo:")
        tel_input = st.text_input("Teléfono (10 dígitos):", max_chars=10)
        enviar = st.form_submit_button("Registrar Participación")
        
        if enviar:
            if nombre_input and len(tel_input) == 10:
                with st.spinner("Sincronizando..."):
                    # Generar número único
                    while True:
                        num = f"{random.randint(0, 9999):04d}"
                        if num not in df_actual['Boleto'].values:
                            break
                    
                    if guardar_en_nube(nombre_input, tel_input, num):
                        st.session_state.mostrar_globos = True
                        st.session_state.numero_boleto = num
                        st.cache_data.clear() # Forzar actualización de la lista
                        st.rerun()
                    else:
                        st.error("❌ Error de conexión con la base de datos.")
            else:
                st.warning("⚠️ Revisa tus datos (Nombre y Teléfono de 10 dígitos).")

# --- ADMINISTRADOR ---
st.write("---")
with st.expander("🔐 Administrador"):
    clave = st.text_input("Password:", type="password")
    if clave == PASSWORD_ADMIN:
        st.dataframe(df_actual, use_container_width=True)
