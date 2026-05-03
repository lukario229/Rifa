import streamlit as st
import pandas as pd
import random
import requests

# 0. CONFIGURACIÓN DE SECRETOS (Caja fuerte)
try:
    URL_API = st.secrets["URL_API"]
    PASSWORD_ADMIN = st.secrets["PASSWORD_ADMIN"]
    # Nuevos secretos para los datos de pago
    NOMBRE_PAGO = st.secrets["NOMBRE_PAGO"]
    BANCO_PAGO = st.secrets["BANCO_PAGO"]
    CUENTA_PAGO = st.secrets["CUENTA_PAGO"]
    CLABE_PAGO = st.secrets["CLABE_PAGO"]
except:
    st.error("⚠️ Error: Faltan configurar Secretos en Streamlit (URL, Contraseña o Datos de Pago).")
    st.stop()

# 1. ESTÉTICA Y ELIMINACIÓN DE ANUNCIOS
st.set_page_config(page_title="Registro de Rifa - Heliu", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Ocultar anuncios y menús de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stSidebar"] { display: none; }
    
    /* Estética Táctica Oscura */
    .main { background-color: #000000; color: white; }
    .info-box { background-color: #1A1A1A; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 25px; }
    .stButton>button { width: 100%; background-color: #2E2E2E; color: white; border: 1px solid #444; height: 3em; }
    .stButton>button:hover { border-color: #ffffff; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIONES DE CONEXIÓN
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

# --- LÓGICA DE CONTROL ---
df_actual = cargar_datos_nube()
total_inscritos = len(df_actual)
LIMITE = 50 # Límite para tu proyecto universitario

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

# 3. INTEGRACIÓN DEL CONTADOR
st.write(f"### 📊 Cupos llenos: {total_inscritos} / {LIMITE}")
st.progress(total_inscritos / LIMITE)

# 4. DATOS DE PAGO SECRETOS (Ocultos en un acordeón)
with st.expander("🔓 Haz clic para ver datos de pago (Transferencia)"):
    st.info("Realiza tu pago y luego llena el formulario de registro.")
    st.code(f"""
Beneficiario: {NOMBRE_PAGO}
Banco: {BANCO_PAGO}
Cuenta: {CUENTA_PAGO}
CLABE: {CLABE_PAGO}
    """, language="text")
    st.caption("Puedes copiar los números usando el botón a la derecha del cuadro gris.")

if total_inscritos >= LIMITE:
    st.error("🚫 Lo sentimos, el cupo de la rifa está lleno.")
else:
    with st.expander("📝 Formulario de Registro", expanded=True):
        nombre_input = st.text_input("Nombre Completo:")
        
        # 5. VALIDACIÓN DE TELÉFONO (Solo 10 números)
        tel_input = st.text_input("Número de Teléfono:", max_chars=10, help="Ingresa tus 10 dígitos")
        
        if st.button("Registrar Participación"):
            if not nombre_input:
                st.warning("⚠️ Por favor, ingresa tu nombre.")
            elif not tel_input.isdigit() or len(tel_input) < 10:
                st.error("⚠️ Error: Ingresa un número de teléfono válido (10 dígitos).")
            else:
                with st.spinner("Sincronizando con la nube..."):
                    # Generar boleto único
                    while True:
                        num = f"{random.randint(0, 9999):04d}"
                        if num not in df_actual['Boleto'].values:
                            break
                    
                    if guardar_en_nube(nombre_input, tel_input, num):
                        st.success(f"✅ ¡Registro exitoso! Tu número es: **{num}**")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Error al conectar con la base de datos.")

# --- PANEL DE ADMINISTRADOR ---
st.write("---")
with st.expander("🔐 Acceso Administrador"):
    clave = st.text_input("Contraseña de seguridad:", type="password")
    if clave == PASSWORD_ADMIN:
        st.subheader("📊 Gestión de Participantes")
        if not df_actual.empty:
            st.dataframe(df_actual, use_container_width=True)
            st.info(f"Total de registros: {len(df_actual)}")
        else:
            st.info("No hay registros en la nube.")
