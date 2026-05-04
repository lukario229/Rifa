import streamlit as st
import pandas as pd
import random
import requests

# --- CONFIGURACIÓN DE SEGURIDAD ---
try:
    # Estas llaves DEBEN existir en tus Secrets de Streamlit Cloud
    URL_API = st.secrets["URL_API"]
    PASS_ADMIN = st.secrets["PASSWORD_ADMIN"]
    ENCARGADO = st.secrets["NOMBRE_PAGO"]
    BANCO = st.secrets["BANCO_PAGO"]
    CUENTA = st.secrets["CUENTA_PAGO"]
    CONTACTO = st.secrets["TEL_PAGO"]
except KeyError as e:
    st.error(f"⚠️ Error de Configuración: Falta la llave {e} en los Secrets.")
    st.stop()

# 1. Estética y Configuración Visual
st.set_page_config(page_title="Rifa Solidaria - Heliu", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .info-box { background-color: #1A1A1A; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 25px; }
    .stButton>button { width: 100%; background-color: #2E2E2E; color: white; border: 1px solid #444; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. Funciones de Datos
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

# 3. Lógica del Contador
df_inicial = cargar_datos_nube()
LIMITE = 50
restantes = LIMITE - len(df_inicial)

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")
st.write(f"### 📊 Boletos disponibles: **{restantes}** / {LIMITE}")
st.progress(len(df_inicial) / LIMITE)

st.markdown(f"""
<div class="info-box">
    <h3 style='margin-top:0;'>📋 Información de Pago</h3>
    <p><b>Encargado:</b> {ENCARGADO}</p>
    <p><b>Banco:</b> {BANCO}</p>
    <p><b>Cuenta/CLABE:</b> {CUENTA}</p>
    <p><b>WhatsApp:</b> {CONTACTO}</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📝 Formulario de Registro", expanded=True):
    with st.form("registro_form", clear_on_submit=True):
        nombre_in = st.text_input("Nombre Completo:")
        tel_in = st.text_input("Teléfono (10 dígitos):", max_chars=10)
        btn = st.form_submit_button("Registrar Participación")
        
        if btn:
            # Mensaje de carga mientras se procesa la información
            with st.spinner("Cargando..."):
                if nombre_in and len(tel_in) == 10 and tel_in.isdigit():
                    if restantes > 0:
                        while True:
                            num = f"{random.randint(0, 9999):04d}"
                            if num not in df_inicial['Boleto'].values: break
                        
                        if guardar_en_nube(nombre_in, tel_in, num):
                            st.success(f"✅ ¡Éxito! Tu número es: **{num}**")
                            st.balloons()
                            st.cache_data.clear()
                        else:
                            st.error("Error al conectar con la base de datos.")
                    else:
                        st.error("Cupo lleno.")
                else:
                    st.warning("Revisa que el nombre esté completo y el teléfono tenga 10 números.")

# 4. Administrador
st.write("---")
with st.expander("🔐 Acceso Administrador"):
    if st.text_input("Password:", type="password") == PASS_ADMIN:
        st.dataframe(df_inicial, use_container_width=True)
