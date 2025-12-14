import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Sistema NIDS - Tesis", layout="wide")

# TÍTULO Y PRESENTACIÓN
st.title("🛡️ Sistema de Detección de Intrusos (NIDS)")
st.markdown("""
**Trabajo Final de Grado - Licenciatura en Gestión de Tecnologías de la Información**  
Este sistema utiliza **Inteligencia Artificial (Random Forest)** para analizar tráfico de red 
y detectar anomalías de seguridad en tiempo real.
""")

# BARRA LATERAL
st.sidebar.header("Panel de Control")
uploaded_file = st.sidebar.file_uploader("Cargar Log de Tráfico (.txt o .csv)", type=["txt", "csv"])

# FUNCIÓN PARA LIMPIAR DATOS (Igual que hicimos en Colab)
def preprocesar_datos(df):
    # Nombres de columnas (Mismos que en el entrenamiento)
    col_names = ["duration","protocol_type","service","flag","src_bytes",
    "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted","num_root",
    "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
    "is_host_login","is_guest_login","count","srv_count","serror_rate",
    "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate","class","difficulty"]
    
    # Si el archivo no tiene cabecera, se la ponemos
    if len(df.columns) == 43:
        df.columns = col_names
    
    # Guardamos la columna 'class' original para comparar (si existe)
    real_labels = None
    if 'class' in df.columns:
        real_labels = df['class']
        df = df.drop(['class', 'difficulty'], axis=1, errors='ignore')
    
    # Codificamos las columnas de texto a números (Manual simple para el demo)
    # NOTA: En un sistema real usaríamos el encoder guardado, pero para evitar errores
    # si aparecen protocolos nuevos, haremos un mapeo simple aquí para el prototipo.
    cols_text = ['protocol_type', 'service', 'flag']
    for col in cols_text:
        df[col] = df[col].astype('category').cat.codes
        
    return df, real_labels

# LÓGICA PRINCIPAL
if uploaded_file is not None:
    try:
        # Cargar modelo
        modelo = joblib.load('modelo_ia_nids.pkl')
        
        # Leer archivo subido
        df_raw = pd.read_csv(uploaded_file, header=None)
        
        st.write("### 1. Vista Previa de los Datos Cargados")
        st.dataframe(df_raw.head())
        
        # Procesar
        df_clean, real_labels = preprocesar_datos(df_raw.copy())
        
        # Botón de Predicción
        if st.button("🔍 ANALIZAR TRÁFICO CON IA"):
            with st.spinner('Analizando patrones de red...'):
                predicciones = modelo.predict(df_clean)
                probs = modelo.predict_proba(df_clean)
                
                # Agregar resultados al dataframe
                df_clean['Predicción'] = ['🔴 ATAQUE' if p == 1 else '🟢 NORMAL' for p in predicciones]
                df_clean['Confianza IA'] = [f"{max(probs[i])*100:.2f}%" for i in range(len(probs))]
                
                # Métricas de Gestión
                total = len(predicciones)
                ataques = np.sum(predicciones)
                normales = total - ataques
                
                # MOSTRAR RESULTADOS (KPIs)
                col1, col2, col3 = st.columns(3)
                col1.metric("Tráfico Analizado", f"{total} registros")
                col2.metric("Conexiones Seguras", f"{normales}", delta_color="normal")
                col3.metric("Amenazas Detectadas", f"{ataques}", delta_color="inverse")
                
                st.write("### 2. Detalle del Análisis")
                st.dataframe(df_clean[['protocol_type', 'src_bytes', 'dst_bytes', 'Predicción', 'Confianza IA']])
                
                # Gráfico simple
                if ataques > 0:
                    st.error(f"⚠️ ¡ALERTA! Se han detectado {ataques} conexiones maliciosas.")
                    fig_chart, ax = plt.subplots()
                    labels = ['Normal', 'Ataque']
                    sizes = [normales, ataques]
                    colors = ['#66b3ff', '#ff9999']
                    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig_chart)
                else:
                    st.success("✅ El sistema está limpio. No se detectaron amenazas.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.info("Asegúrate de subir un archivo con el formato correcto (KDDTrain o KDDTest).")

else:
    st.info("👈 Por favor, carga un archivo de log en el menú lateral para comenzar.")