# cd Clases
# streamlit run clase6.py
import streamlit as st 


st.set_page_config(page_title="Mi chatbot con Streamlit", page_icon="😀")
st.title('Mi primera APP con streamlit en python')

nombre = st.text_input("cual es tu nombre papá???")

click = st.button("Saludar")

if click :
    st.write(f'Hola soy {nombre }. saludos desde TTT ( no tini) sino , TALENTO TECH TEENS')




Equipos = ["","River", "Independiente", "Racing", 'Boca Jr']

# equipo = st.selectbox('Elejí tu equipo favorito',options=Equipos )




message = st.chat_input()
print(message)


st.sidebar.title("CONFIGURACION DE MIS MODELOS")
equipo = st.sidebar._selectbox('Elejí tu equipo favorito',options=Equipos)
st.sidebar.write(f'tu equipo favorito es : {equipo}')