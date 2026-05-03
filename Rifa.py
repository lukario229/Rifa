import streamlit as st

hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Esto oculta el botón de "Deploy" y otros elementos de la barra inferior */
    .stAppDeployButton {display:none;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. CONTADOR DE PARTICIPANTES ---
try:
    df_actual = cargar_datos_nube()
    total_inscritos = len(df_actual)
except:
    total_inscritos = 0

LIMITE_RIFA = 100 # Puedes cambiar este número al límite que quieras
cupos_libres = LIMITE_RIFA - total_inscritos

# Mostrar el contador de forma visual
st.subheader(f"📊 Estado de la Rifa: {total_inscritos} / {LIMITE_RIFA} participantes")
st.progress(total_inscritos / LIMITE_RIFA)

if cupos_libres <= 0:
    st.error("🚫 ¡Lo sentimos! Ya no quedan cupos disponibles.")
else:
    st.info(f"✅ ¡Aún quedan {cupos_libres} lugares! Regístrate abajo.")

    # --- 3. FORMULARIO CON VALIDACIÓN ---
    with st.form("registro_rifa"):
        nombre = st.text_input("Nombre Completo:")
        
        # Validación: Solo números y límite de caracteres (ej. 10 para un cel)
        telefono = st.text_input(
            "Número de Teléfono:", 
            max_chars=10, 
            help="Ingresa solo los 10 dígitos de tu número"
        )
        
        btn_enviar = st.form_submit_button("Participar ahora")

        if btn_enviar:
            # Verificación táctica: ¿Es realmente un número?
            if not telefono.isdigit():
                st.error("⚠️ Error: El teléfono debe contener solo números.")
            elif len(telefono) < 10:
                st.error("⚠️ Error: El número debe tener 10 dígitos.")
            elif nombre == "":
                st.warning("⚠️ Por favor, pon tu nombre.")
            else:
                # Aquí va tu función de guardar_en_nube
                exito = guardar_en_nube(nombre, telefono)
                if exito:
                    st.success("¡Registro exitoso! ¡Mucha suerte!")
                    st.balloons()
