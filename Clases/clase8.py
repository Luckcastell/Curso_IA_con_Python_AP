# cd Clases
# streamlit run clase8.py 
import streamlit as st
import groq  #API

MODELOS = ['chatpgt-mini', 'gemini-gpt', 'gpt-mino-os']

# CONFIGURAR PAGINA
def configurar_pagina():
    st.set_page_config(page_title="Mi Primer ChatBot con Python")
    st.title("Bienvenidos a mi Chatbot")

# CREAR UN CLIENTE GROQ => NOSOTROS
def crear_cliente_groq():
    groq_api_key = st.secrets["GROQ_API_KEY"]
    return groq.Groq(api_key=groq_api_key)
    
# MOSTRAR LA BARRA LATERAL 
def mostrar_sidebar():
    st.sidebar.title("Elegí tu modelo de IA favorito")
    modelo = st.sidebar.selectbox('Elegí tu modelo',MODELOS,index=0)
    st.write(f'**Elegiste el modelo** {modelo}')
    return modelo

#INICIALIZAR EL ESTADO DEL CHAT
def inicializar_estado_chat():
    if "mensajes"  not in st.session_state:
        st.session_state.mensajes = []

#MOSTRAR MENSAJES REVIOS
def obtener_mensajes_previos():
    for mensaje in st.session_state.mensajes: #recorre los mensajes de st.session_state.mensaje
        with st.chat_message(mensaje["role"]): #quien lo envia?
            st.markdown(mensaje["content"]) #Contenido del mensaje

#OBTENER MENSAJE USUARIO
def obtener_mensaje_usuario():
    return st.chat_input("Envia tu mensaje")

#GUARDAR LOS MENSAJES
def agregar_mensajes_previos(role, content):
    st.session_state.mensajes.append({"role": role , "content": content})

#MOSTRAR LOS MENSAJES EN PANTALLA
def mostrar_mensaje(role, content):
    with st.chat_message(role):
        st.markdown(content)

#LLAMAR EL MODELO DE GROQ


def ejecutar_chat():
    configurar_pagina()
    cliente = crear_cliente_groq()
    modelo = mostrar_sidebar()
    
    inicializar_estado_chat()
    mensaje_usuario = obtener_mensaje_usuario()
    # obtener_mensajes_previos
    print(mensaje_usuario)

# EJECUTAR LA APP( si __name__ es igual a __main__ se ejecuta la funcion, y __main__ es mi archivo principal)
if __name__ == '__main__':
    ejecutar_chat()