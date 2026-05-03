import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURACIÓN VISUAL (OCULTAR ANUNCIO) ---
st.set_page_config(page_title="Registro de Rifa - Heliu", page_icon="🎫")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. LÓGICA DE DATOS Y CONTADOR ---
# Función para cargar datos (necesaria para el contador)
def cargar_datos_nube():
    url = st.secrets["URL_API"]
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

df_admin = cargar_datos_nube()
total_registrados = len(df_admin)
LIMITE_PARTICIPANTES = 50 # Basado en tu programa de rifa de 50 personas

# --- 3. INTERFAZ DE USUARIO ---
st.title("🎫 Registro de Rifa")
st.write(f"### 📊 Cupos: {total_registrados} / {LIMITE_PARTICIPANTES}")
st.progress(total_registrados / LIMITE_PARTICIPANTES)

if total_registrados >= LIMITE_PARTICIPANTES:
    st.error("🚫 Lo sentimos, el cupo de la rifa está lleno.")
else:
    with st.container():
        nombre_input = st.text_input("Nombre Completo:")
        # Integración de límite de caracteres y solo números
        tel_input = st.text_input("Número de Teléfono:", max_chars=10, help="Ingresa los 10 dígitos")
        
        if st.button("Registrar"):
            # Validaciones integradas
            if not tel_input.isdigit():
                st.error("⚠️ Error: El teléfono debe contener solo números.")
            elif len(tel_input) < 10:
                st.error("⚠️ Error: El número debe tener 10 dígitos.")
            elif nombre_input == "":
                st.warning("⚠️ Por favor, ingresa tu nombre.")
            else:
                # Tu lógica original de envío
                num = total_registrados + 1
                exito = guardar_en_nube(nombre_input, tel_input, num)
                
                if exito:
                    st.success(f"✅ ¡Registro exitoso! Tu número es: **{num}**")
                    st.balloons()
                else:
                    st.error("Error al conectar con la nube.")

# --- PANEL DE ADMINISTRADOR ---
with st.expander("🔐 Acceso Administrador"):
    clave = st.text_input("Contraseña de seguridad:", type="password")
    # Uso de la llave secreta para mayor seguridad
    if clave == st.secrets["PASSWORD_ADMIN"]:
        st.subheader("📊 Gestión de Participantes")
        st.dataframe(df_admin, use_container_width=True)
