import streamlit as st
import pandas as pd
import random
import requests

# --- CONFIGURACIÓN DE SEGURIDAD (Se lee desde la pestaña de Secrets) ---
# Ya no pegamos el link aquí directamente por seguridad.
try:
    URL_API = st.secrets["URL_API"]
except:
    st.error("⚠️ No se encontró la URL de la API en los Secretos de Streamlit.")
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

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

st.markdown(f"""
<div class="info-box">
    <h3 style='margin-top:0;'>📋 Información de la Rifa</h3>
    <p><b>Encargado:</b> Heliu Gahel Ciañez</p>
    <p><b>Descripción:</b> Registra tus datos para participar. Los datos se sincronizan de forma segura en la nube.</p>
    <hr style='border-color:#444;'>
    <p><b>💳 Datos de Transferencia:</b><br>
    Banco: [Tu Banco]<br>
    CLABE: 0000 0000 0000 0000 00</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📝 Formulario de Registro", expanded=True):
    nombre_input = st.text_input("Nombre Completo:")
    tel_input = st.text_input("Número de Teléfono:")
    
    if st.button("Registrar Participación"):
        if nombre_input and tel_input:
            with st.spinner("Conectando con la base de datos..."):
                df_actual = cargar_datos_nube()
                
                if len(df_actual) < 50:
                    while True:
                        num = f"{random.randint(0, 9999):04d}"
                        if num not in df_actual['Boleto'].values:
                            break
                    
                    exito = guardar_en_nube(nombre_input, tel_input, num)
                    
                    if exito:
                        st.success(f"✅ ¡Registro exitoso! Tu número es: **{num}**")
                        st.balloons()
                    else:
                        st.error("Error al conectar con la nube. Revisa los Secretos.")
                else:
                    st.error("Lo sentimos, el cupo de la rifa está lleno.")
        else:
            st.warning("Por favor, completa todos los campos para participar.")

# --- PANEL DE CONTROL ADMINISTRADOR ---
st.write("---")
with st.expander("🔐 Acceso Administrador"):
    clave = st.text_input("Contraseña de seguridad:", type="password")
    if clave == "admin123":
        st.subheader("📊 Gestión de Participantes")
        df_admin = cargar_datos_nube()
        
        if not df_admin.empty:
            st.dataframe(df_admin, use_container_width=True)
            st.info(f"Total de registros: {len(df_admin)}")
            st.caption("Tip: Para actualizar pagos, abre tu Google Sheet directamente.")
        else:
            st.info("No hay registros detectados en la nube.")