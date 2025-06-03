# cd Clases
#  streamlit run Clases/clase7.py 
import streamlit as st 
import groq

MODELOS = ['chatpgt-mini', 'gemini-gpt','gpt-mino-os']

def configurar_pagina():
    st.set_page_config(page_title="Mi chatbot con Streamlit")
    st.title("Bienvenidos a mi chatbot")

def crear_cliente_groq():
    groq_api_key = st.secrets("GROQ_API_KEY")
    return groq.Groq(api_key = groq_api_key)

def mostrar_sidebar():
    st.sidebar.title("Elegi el modelo de IA")
    modelo = st.sidebar.selectbox("", MODELOS, index=0)
    st.write(f'**Elegiste el modelo** {modelo}')
    return modelo

def ejecutar_chat():
    configurar_pagina()
    modelo = mostrar_sidebar()
    print(modelo)

if __name__ == "__main__":
    ejecutar_chat()