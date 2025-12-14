import streamlit as st
import pandas as pd
import joblib
import numpy as np
import time
import random
import matplotlib.pyplot as plt
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NeuroNIDS - Monitor en Tiempo Real",
    page_icon="🛡️",
    layout="wide"
)

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff00; }
    .stMetric { background-color: #262730; border: 1px solid #4e4e4e; }
    div[data-testid="stMetricValue"] { color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGAR IA ---
try:
    if not os.path.exists('modelo_ia_nids.pkl'):
        st.error("⚠️ No se encuentra el archivo 'modelo_ia_nids.pkl'.")
        st.stop()
    
    modelo = joblib.load('modelo_ia_nids.pkl')
    
    col_names = ["duration","protocol_type","service","flag","src_bytes",
    "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted","num_root",
    "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
    "is_host_login","is_guest_login","count","srv_count","serror_rate",
    "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate"]

except Exception as e:
    st.error(f"Error crítico cargando la IA: {e}")
    st.stop()

# --- SIMULACIÓN ---
def generar_trafico_simulado():
    datos = []
    for _ in range(10):
        # 1. Base: Creamos una conexión "limpia" (todo ceros es lo más normal)
        fila = [0] * len(col_names)
        
        # 2. Agregamos un poco de realismo "sano"
        fila[0] = random.randint(0, 2)      # Duración baja
        fila[1] = 1                         # Protocolo TCP (Simulado)
        fila[4] = random.randint(100, 1000) # Bytes enviados (Navegación normal)
        fila[5] = random.randint(200, 2000) # Bytes recibidos
        
        # 3. INYECTAR ATAQUE (Solo el 10% de las veces)
        if random.random() < 0.1: 
            fila[4] = 99999    # Bytes exagerados (Ataque DoS)
            fila[22] = 500     # Muchas conexiones al mismo tiempo
            fila[23] = 500     # srv_count alto
            
        datos.append(fila)
    return pd.DataFrame(datos, columns=col_names)

# --- INTERFAZ ---
st.title("🛡️ NeuroNIDS: Monitor de Amenazas Activo")
st.markdown("Monitor de tráfico de red potenciado por Inteligencia Artificial. **Estado: ONLINE**")

col1, col2, col3, col4 = st.columns(4)
kpi_total = col1.empty()
kpi_seguros = col2.empty()
kpi_amenazas = col3.empty()
kpi_riesgo = col4.empty()

chart_space = st.empty()
log_space = st.empty()

if 'historial_ataques' not in st.session_state:
    st.session_state['historial_ataques'] = 0
if 'historial_normal' not in st.session_state:
    st.session_state['historial_normal'] = 0

start_button = st.button('🔴 ACTIVAR MONITOR DE RED')

if start_button:
    st.toast("Iniciando captura de paquetes...")
    for i in range(100): 
        df_live = generar_trafico_simulado()
        predicciones = modelo.predict(df_live)
        
        nuevos_ataques = np.sum(predicciones)
        nuevos_normales = len(predicciones) - nuevos_ataques
        
        st.session_state['historial_ataques'] += int(nuevos_ataques)
        st.session_state['historial_normal'] += int(nuevos_normales)
        
        total = st.session_state['historial_ataques'] + st.session_state['historial_normal']
        
        kpi_total.metric("Paquetes Analizados", total)
        kpi_seguros.metric("Tráfico Legítimo", st.session_state['historial_normal'])
        kpi_amenazas.metric("Intrusiones Bloqueadas", st.session_state['historial_ataques'], delta_color="inverse")
        
        riesgo = (st.session_state['historial_ataques'] / total) * 100 if total > 0 else 0
        kpi_riesgo.metric("Nivel de Amenaza Actual", f"{riesgo:.1f}%")

        with chart_space.container():
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.barh(['Normal', 'Ataque'], [st.session_state['historial_normal'], st.session_state['historial_ataques']], color=['green', 'red'])
            ax.set_xlim(0, total + 10)
            st.pyplot(fig)

        if nuevos_ataques > 0:
            with log_space.container():
                st.error(f"⚠️ [ALERTA] Se detectaron {nuevos_ataques} intentos de intrusión.")
        
        time.sleep(1)
