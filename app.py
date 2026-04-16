import streamlit as st
import random

st.title("Juego: Adivina el Número")

numero = 7 

intento = st.number_input("Introduce un número del 1 al 10", min_value=1, max_value=10)

if st.button("¿Habré acertado?"):
    if intento == numero:
        st.balloons()
        st.success("¡Felicidades! Ganaste.")
    elif intento < numero:
        st.warning("Demasiado bajo...")
    else:
        st.warning("Demasiado alto...")
