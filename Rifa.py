import streamlit as st
import pandas as pd
import random
import requests

# --- CONFIGURACIÓN DE SEGURIDAD (Se lee desde la pestaña de Secrets) ---
try:
    URL_API = st.secrets["URL_API"]
    NOMBRE_ENCARGADO = st.secrets["NOMBRE_PAGO"]
    BANCO_RIFA = st.secrets["BANCO_PAGO"]
    CUENTA_RIFA = st.secrets["CUENTA_PAGO"]
    TEL_CONTACTO = st.secrets["TEL_PAGO"]
except:
    st.error("⚠️ Error: Faltan configurar Secretos en Streamlit (URL, Nombres o Datos de Pago).")
    st.stop()

# 1. Configuración visual y estética táctica
st.set_page_config(page_title="Registro de Rifa - Heliu", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
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
    payload = {"Nombre": nombre, "Telefono": telefono, "Boleto": boleto}
    try:
        res = requests.post(URL_API, json=payload)
        return res.status_code == 200
    except:
        return False

# --- LÓGICA DE CONTADOR ---
df_inicial = cargar_datos_nube()
total_actual = len(df_inicial)
LIMITE = 50
restantes = LIMITE - total_actual

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

# NUEVO CONTADOR VISUAL
st.write(f"### 📊 Boletos disponibles: **{restantes}** / {LIMITE}")
st.progress(total_actual / LIMITE)

st.markdown(f"""
<div class="info-box">
    <h3 style='margin-top:0;'>📋 Información de la Rifa</h3>
    <p><b>Encargado:</b> {NOMBRE_ENCARGADO}</p>
    <p><b>Descripción:</b> Registra tus datos para participar. Los datos se sincronizan de forma segura.</p>
    <hr style='border-color:#444;'>
    <p><b>💳 Datos de Transferencia:</b><br>
    <b>Banco:</b> {BANCO_RIFA}<br>
    <b>Cuenta/CLABE:</b> {CUENTA_RIFA}<br>
    <b>Contacto:</b> {TEL_CONTACTO}</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📝 Formulario de Registro", expanded=True):
    nombre_input = st.text_input("Nombre Completo:")
    tel_input = st.text_input("Número de Teléfono:", max_chars=10)
    
    if st.button("Registrar Participación"):
        if nombre_input and tel_input:
            with st.spinner("Conectando con la base de datos..."):
                df_actual = cargar_datos_nube()
                
                if len(df_actual) < LIMITE:
                    while True:
                        num = f"{random.randint(0, 9999):04d}"
                        if num not in df_actual['Boleto'].values:
                            break
                    
                    exito = guardar_en_nube(nombre_input, tel_input, num)
                    
                    if exito:
                        st.success(f"✅ ¡Registro exitoso! Tu número es: **{num}**")
                        st.balloons()
                        st.rerun() # Recargar para actualizar el contador
                    else:
                        st.error("Error al conectar con la nube.")
                else:
                    st.error("Lo sentimos, el cupo de la rifa está lleno.")
        else:
            st.warning("Por favor, completa todos los campos para participar.")

# --- PANEL DE CONTROL ADMINISTRADOR ---
st.write("---")
with st.expander("🔐 Acceso Administrador"):
    clave = st.text_input("Contraseña de seguridad:", type="password")
    if clave == st.secrets["PASSWORD_ADMIN"]:
        st.subheader("📊 Gestión de Participantes")
        if not df_inicial.empty:
            st.dataframe(df_inicial, use_container_width=True)
            st.info(f"Total de registros: {len(df_inicial)}")
        else:
            st.info("No hay registros detectados en la nube.")
