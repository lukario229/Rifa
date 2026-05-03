import pandas as pd
import random
import requests
import time

# 0. CONFIGURACIÓN DE SECRETOS
try:
@@ -53,9 +52,8 @@
        return False

# --- LÓGICA DE GLOBOS ---
if "registro_exitoso" not in st.session_state:
    st.session_state.registro_exitoso = False
    st.session_state.numero_boleto = ""
if "mostrar_globos" not in st.session_state:
    st.session_state.mostrar_globos = False

# --- DATOS ACTUALES ---
df_actual = cargar_datos_nube()
@@ -65,12 +63,10 @@
# --- VISTA PÚBLICA ---
st.title("🎟️ Gran Rifa Solidaria")

# Mostrar globos y mensaje si el registro acaba de ocurrir
if st.session_state.registro_exitoso:
# Lanzar globos si el estado es verdadero
if st.session_state.mostrar_globos:
    st.balloons()
    st.success(f"✅ ¡Éxito! Tu boleto es: **{st.session_state.numero_boleto}**")
    st.session_state.registro_exitoso = False # Limpiar para que no salgan globos al recargar
    time.sleep(2) # Pausa para que vean el número antes de cualquier actualización
    st.session_state.mostrar_globos = False # Se apaga para la próxima recarga

st.write(f"### 📊 Cupos llenos: {total_inscritos} / {LIMITE_PARTICIPANTES}")
st.progress(total_inscritos / LIMITE_PARTICIPANTES)
@@ -109,15 +105,14 @@
                            break

                    if guardar_en_nube(nombre_input, tel_input, num):
                        st.session_state.registro_exitoso = True
                        st.session_state.numero_boleto = num
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
