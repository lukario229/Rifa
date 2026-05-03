import random
import requests

# 0. CONFIGURACIÓN DE SECRETOS (Caja fuerte)
# 0. CONFIGURACIÓN DE SECRETOS
try:
    URL_API = st.secrets["URL_API"]
    PASSWORD_ADMIN = st.secrets["PASSWORD_ADMIN"]
    # Datos de pago desde Secrets
    NOMBRE_PAGO = st.secrets["NOMBRE_PAGO"]
    BANCO_PAGO = st.secrets["BANCO_PAGO"]
    CUENTA_PAGO = st.secrets["CUENTA_PAGO"]
    # Ahora usamos el secreto del teléfono en la vista pública
    TEL_PAGO = st.secrets["TEL_PAGO"] 
except:
    st.error("⚠️ Error: Faltan configurar Secretos en Streamlit (URL, Contraseña o Datos de Pago).")
    st.error("⚠️ Error: Revisa tus Secretos en Streamlit.")
    st.stop()

# 1. ESTÉTICA Y ELIMINACIÓN DE ANUNCIOS
st.set_page_config(page_title="Registro de Rifa - lukario229", layout="centered", initial_sidebar_state="collapsed")
# 1. ESTÉTICA
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
# 2. FUNCIONES
def cargar_datos_nube():
    try:
        response = requests.get(URL_API)
@@ -56,68 +52,60 @@ def guardar_en_nube(nombre, telefono, boleto):
    except:
        return False

# --- LÓGICA DE CONTROL ---
# --- CONFIGURACIÓN DE LÍMITES (Aquí modificas el cupo) ---
df_actual = cargar_datos_nube()
total_inscritos = len(df_actual)
LIMITE = 50 

# MODIFICA ESTE NÚMERO PARA CAMBIAR EL LÍMITE TOTAL DE PERSONAS
LIMITE_PARTICIPANTES = 50 

# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

# 3. INTEGRACIÓN DEL CONTADOR
st.write(f"### 📊 Cupos llenos: {total_inscritos} / {LIMITE}")
st.progress(total_inscritos / LIMITE)
st.write(f"### 📊 Cupos llenos: {total_inscritos} / {LIMITE_PARTICIPANTES}")
st.progress(total_inscritos / LIMITE_PARTICIPANTES)

# 4. CAJA DE INFORMACIÓN (VERSION ANTIGUA FIJA)
# 4. CAJA DE INFORMACIÓN (Actualizada con Teléfono en vez de CLABE)
st.markdown(f"""
<div class="info-box">
    <h3 style='margin-top:0;'>📋 Información de Pago</h3>
    <p><b>👤 Beneficiario:</b> {NOMBRE_PAGO}</p>
    <p><b>🏦 Banco:</b> {BANCO_PAGO}</p>
    <p><b>🔢 Cuenta:</b> {CUENTA_PAGO}</p>
    <p><b>📞 Telefono:</b> {Telefono}</p>
    <p><b>📱 Teléfono de contacto:</b> {TEL_PAGO}</p>
    <hr style='border-color:#333;'>
    <p style='font-size: 0.9em; color: #bbb;'>Una vez realizado el pago, registra tus datos abajo para asignar tu boleto.</p>
    <p style='font-size: 0.9em; color: #bbb;'>Realiza tu pago y regístrate para recibir tu boleto.</p>
</div>
""", unsafe_allow_html=True)

if total_inscritos >= 50:
    st.error("🚫 Lo sentimos, el cupo de la rifa está lleno.")
if total_inscritos >= LIMITE_PARTICIPANTES:
    st.error("🚫 Cupo lleno.")
else:
    with st.expander("📝 Formulario de Registro", expanded=True):
        nombre_input = st.text_input("Nombre Completo:")
        
        # 5. VALIDACIÓN DE TELÉFONO
        tel_input = st.text_input("Número de Teléfono:", max_chars=10, help="Ingresa su número")
        tel_input = st.text_input("Número de Teléfono:", max_chars=10)

        if st.button("Registrar Participación"):
            if not nombre_input:
                st.warning("⚠️ Por favor, ingresa tu nombre.")
            elif not tel_input.isdigit() or len(tel_input) < 10:
                st.error("⚠️ Error: Ingresa un número de teléfono válido (10 dígitos).")
            else:
                with st.spinner("Sincronizando con la nube..."):
                    # Generar boleto único
            if nombre_input and len(tel_input) == 10:
                with st.spinner("Registrando..."):
                    
                    # --- CONFIGURACIÓN DE BOLETOS ---
                    # Para cambiar el rango (ej. del 0 al 100), modifica random.randint(0, 100)
                    while True:
                        num = f"{random.randint(0, 9999):04d}"
                        num = f"{random.randint(0, 9999):04d}" 
                        if num not in df_actual['Boleto'].values:
                            break

                    if guardar_en_nube(nombre_input, tel_input, num):
                        st.success(f"✅ ¡Registro exitoso! Tu número es: **{num}**")
                        st.success(f"✅ ¡Éxito! Tu boleto es: **{num}**")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Error al conectar con la base de datos.")
            else:
                st.warning("Revisa tus datos.")

# --- PANEL DE ADMINISTRADOR ---
# --- ADMINISTRADOR ---
st.write("---")
with st.expander("🔐 Acceso Administrador"):
    clave = st.text_input("Contraseña de seguridad:", type="password")
with st.expander("🔐 Administrador"):
    clave = st.text_input("Password:", type="password")
    if clave == PASSWORD_ADMIN:
        st.subheader("📊 Gestión de Participantes")
        if not df_actual.empty:
            st.dataframe(df_actual, use_container_width=True)
            st.info(f"Total de registros: {len(df_actual)}")
        else:
            st.info("No hay registros en la nube.")
        st.dataframe(df_actual, use_container_width=True)
