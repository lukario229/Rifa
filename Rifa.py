import streamlit as st
import pandas as pd
import random
import requests

# 0. Configuración de Secretos
try:
    URL_API = st.secrets["URL_API"]
    PASSWORD_ADMIN = st.secrets["PASSWORD_ADMIN"]
except:
    st.error("⚠️ No se encontraron los Secretos (URL_API o PASSWORD_ADMIN) en Streamlit.")
    st.stop()

# 1. Configuración visual y OCULTAR ANUNCIOS
st.set_page_config(page_title="Registro de Rifa - Heliu", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stSidebar"] { display: none; }
    
    /* Estética Táctica */
    .main { background-color: #000000; color: white; }
    .info-box { background-color: #1A1A1A; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 25px; }
    .stButton>button { width: 100%; background-color: #2E2E2E; color: white; border: 1px solid #444; height: 3em; }
    .stButton>button:hover { border-color: #ffffff; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funciones de conexión
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
    payload = {
        "Nombre": nombre,
        "Telefono": telefono,
        "Boleto": boleto
    }
    try:
        res = requests.post(URL_API, json=payload)
        return res.status_code == 200
    except:
        return False

# --- LÓGICA DE CONTROL ---
df_actual = cargar_datos_nube()
total_inscritos = len(df_actual)
LIMITE = 50

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

# INTEGRACIÓN DEL CONTADOR
st.write(f"### 📊 Cupos disponibles: {total_inscritos} / {LIMITE}")
st.progress(total_inscritos / LIMITE)

st.markdown(f"""
<div class="info-box">
    <h3 style='margin-top:0;'>📋 Información de la Rifa</h3>
    <p><b>Encargado:</b> lukario229</p>
    <p><b>Descripción:</b> Registra tus datos para participar. Solo se permiten 10 dígitos en el teléfono.</p>
    <hr style='border-color:#444;'>
    <p><b>💳 Datos de Transferencia:</b><br>
    Banco: [Tu Banco]<br>
    CLABE: 0000 0000 0000 0000 00</p>
</div>
""", unsafe_allow_html=True)

if total_inscritos >= LIMITE:
    st.error("🚫 Lo sentimos, el cupo de la rifa está lleno.")
else:
    with st.expander("📝 Formulario de Registro", expanded=True):
        nombre_input = st.text_input("Nombre Completo:")
        
        # INTEGRACIÓN DE LÍMITE Y SOLO NÚMEROS
        tel_input = st.text_input("Número de Teléfono:", max_chars=10, help="Ingresa los 10 dígitos de tu número")
        
        if st.button("Registrar Participación"):
            # VALIDACIONES TÁCTICAS
            if not nombre_input:
                st.warning("⚠️ Por favor, ingresa tu nombre.")
            elif not tel_input.isdigit():
                st.error("⚠️ Error: El teléfono debe contener solo números.")
            elif len(tel_input) < 10:
                st.error("⚠️ Error: El número debe tener 10 dígitos exactos.")
            else:
                with st.spinner("Conectando con la base de datos..."):
                    # Generar número de boleto único
                    while True:
                        num = f"{random.randint(0, 9999):04d}"
                        if num not in df_actual['Boleto'].values:
                            break
                    
                    exito = guardar_en_nube(nombre_input, tel_input, num)
                    
                    if exito:
                        st.success(f"✅ ¡Registro exitoso! Tu número es: **{num}**")
                        st.balloons()
                        st.rerun() # Refrescar para actualizar el contador
                    else:
                        st.error("Error al conectar con la nube. Revisa la URL_API.")

# --- PANEL DE CONTROL ADMINISTRADOR ---
st.write("---")
with st.expander("🔐 Acceso Administrador"):
    clave = st.text_input("Contraseña de seguridad:", type="password")
    if clave == PASSWORD_ADMIN:
        st.subheader("📊 Gestión de Participantes")
        if not df_actual.empty:
            st.dataframe(df_actual, use_container_width=True)
            st.info(f"Total de registros: {len(df_actual)}")
        else:
            st.info("No hay registros detectados en la nube.")
