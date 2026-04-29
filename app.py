import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Tracker PAES", page_icon="📈")

st.title("📈 Mi Progreso Académico PAES")
st.markdown("Registra tus ensayos y visualiza tu evolución.")

# 1. Inicializar el estado de la sesión para guardar los datos
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(
        columns=["Ensayo", "Asignatura", "Buenas", "Malas", "Puntaje"]
    )

# 2. Formulario de ingreso en la barra lateral
with st.sidebar:
    st.header("Añadir Nuevo Ensayo")
    with st.form("formulario_datos"):
        nombre = st.text_input("Nombre del Ensayo", placeholder="Ej: Ensayo Mineduc #1")
        materia = st.selectbox("Asignatura", ["Competencia Lectora", "Competencia Matemática M1", "Matemática M2", "Ciencias", "Historia"])
        buenas = st.number_input("Cantidad de Buenas", min_value=0, max_value=75, step=1)
        malas = st.number_input("Cantidad de Malas", min_value=0, max_value=75, step=1)
        puntaje = st.number_input("Puntaje Obtenido", min_value=100, max_value=1000, step=1)
        
        btn_guardar = st.form_submit_button("Guardar Resultado")

    if btn_guardar:
        nuevo_dato = pd.DataFrame([{
            "Ensayo": nombre,
            "Asignatura": materia,
            "Buenas": buenas,
            "Malas": malas,
            "Puntaje": puntaje
        }])
        st.session_state.historico = pd.concat([st.session_state.historico, nuevo_dato], ignore_index=True)
        st.success("¡Ensayo registrado!")

# 3. Mostrar métricas y gráficos
if not st.session_state.historico.empty:
    df = st.session_state.historico

    # Métricas rápidas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Último Puntaje", f"{df['Puntaje'].iloc[-1]} pts")
    with col2:
        max_score = df['Puntaje'].max()
        st.metric("Puntaje Máximo", f"{max_score} pts")

    # Gráfico de Progreso
    st.subheader("Evolución del Puntaje")
    fig = px.line(
        df, 
        x="Ensayo", 
        y="Puntaje", 
        color="Asignatura",
        markers=True,
        text="Puntaje",
        title="Progreso por Ensayo"
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de datos
    st.subheader("Historial Detallado")
    st.dataframe(df, use_container_width=True)
    
    # Opción para descargar los datos
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar CSV", csv, "mi_progreso_paes.csv", "text/csv")
else:
    st.info("Aún no hay datos. Ingresa tu primer ensayo en el panel de la izquierda.")
