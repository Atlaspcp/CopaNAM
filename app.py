import streamlit as st
import random

st.title("🎯 Juego: Adivina el Número")

# Generamos el número secreto (Ojo: se reinicia en cada clic si no se usa algo llamado session_state, 
# pero para nivel inicial, que sea un número fijo o aleatorio por ejecución está bien para aprender)
secreto = 7 

intento = st.number_input("Introduce un número del 1 al 10", min_value=1, max_value=10)

if st.button("¿Habré acertado?"):
    if intento == secreto:
        st.balloons() # ¡Efecto visual de celebración!
        st.success("¡Felicidades! Ganaste.")
    elif intento < secreto:
        st.warning("Demasiado bajo...")
    else:
        st.warning("Demasiado alto...")
