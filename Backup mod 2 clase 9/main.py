# streamlit run main.py
import streamlit as st
import groq
import os
import tempfile
from datetime import datetime
import time
from PIL import Image
import pytesseract
from pdfminer.high_level import extract_text
from docx import Document
import pandas as pd
import json

# Configura Tesseract OCR (necesita instalación aparte)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ajustar según tu sistema

# Configuración de directorio para historial de chats
CHATS_DIR = "chat_history"
os.makedirs(CHATS_DIR, exist_ok=True)

# Modelos disponibles
MODELOS = {
    'compound-beta': "Modelo avanzado para respuestas detalladas",
    'compound-beta-mini': "Versión ligera de Compound Beta",
    'gemma2-9b-it': "Modelo eficiente de Google",
    'meta-llama/llama-4-scout-17b-16e-instruct': "Llama 4 optimizado para instrucciones"
}

# Extensiones permitidas agrupadas por tipo
EXTENSIONES_PERMITIDAS = {
    'imagen': ['png', 'jpg', 'jpeg', 'svg', 'bmp', 'gif'],
    'documento': ['pdf', 'docx', 'txt', 'rtf'],
    'codigo': ['py', 'html', 'css', 'js', 'json', 'xml', 'csv', 'md'],
    'datos': ['xlsx', 'xls', 'csv']
}

# ==================== FUNCIONES PARA HISTORIAL DE CHATS ====================

def generar_nombre_por_defecto(mensajes):
    """Genera un nombre para el chat basado en un resumen de los primeros mensajes"""
    try:
        # Obtener los primeros 5 mensajes del usuario
        mensajes_usuario = [m["content"] for m in mensajes if m["role"] == "user"][:5]
        
        # Crear un texto base combinando los mensajes
        texto_completo = " ".join(mensajes_usuario)
        
        # Generar un resumen de máximo 6 palabras
        palabras = texto_completo.split()[:6]
        resumen = " ".join(palabras).lower()
        
        # Limpiar el texto para nombre de archivo
        caracteres_permitidos = "abcdefghijklmnopqrstuvwxyz0123456789"
        texto_limpio = "".join(c if c.lower() in caracteres_permitidos else "_" for c in resumen)
        texto_limpio = texto_limpio.strip("_").replace("__", "_")
        
        # Si no hay contenido válido, usar 'chat'
        if not texto_limpio or len(texto_limpio) < 3:
            texto_limpio = "chat"
        
        # Buscar si ya existe un chat con ese nombre base
        chats_existentes = [f for f in os.listdir(CHATS_DIR) if f.startswith(texto_limpio)]
        numero = f"{len(chats_existentes):02d}"  # Formato 00, 01, etc.
        
        # Combinar con número de versión si hay chats existentes
        if len(chats_existentes) > 0:
            nombre_final = f"{texto_limpio}_{numero}"
        else:
            nombre_final = texto_limpio
            
        return nombre_final
        
    except Exception:
        # Fallback con timestamp si hay algún error
        return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def guardar_chat(nombre_chat, mensajes):
    """Guarda el chat actual en un archivo JSON"""
    try:
        # Asegurarse de que el nombre no tenga caracteres inválidos
        nombre_valido = "".join(c if c.isalnum() or c in " -_." else "_" for c in nombre_chat)
        nombre_valido = nombre_valido.strip()
        
        if not nombre_valido:
            nombre_valido = generar_nombre_por_defecto(mensajes)
        
        # Asegurarse de que la extensión sea .json
        if not nombre_valido.lower().endswith('.json'):
            nombre_valido += '.json'
        
        with open(os.path.join(CHATS_DIR, nombre_valido), "w", encoding="utf-8") as f:
            json.dump(mensajes, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error al guardar chat: {str(e)}")
        return False

def cargar_chat(nombre_chat):
    """Carga un chat desde un archivo JSON"""
    try:
        with open(os.path.join(CHATS_DIR, f"{nombre_chat}.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Chat no encontrado")
        return None
    except Exception as e:
        st.error(f"Error al cargar chat: {str(e)}")
        return None

def listar_chats():
    """Lista todos los chats guardados"""
    try:
        chats = [f.replace(".json", "") for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
        return sorted(chats, reverse=True)  # Más recientes primero
    except Exception as e:
        st.error(f"Error al listar chats: {str(e)}")
        return []

def eliminar_chat(nombre_chat):
    """Elimina un chat guardado"""
    try:
        os.remove(os.path.join(CHATS_DIR, f"{nombre_chat}.json"))
        return True
    except Exception as e:
        st.error(f"Error al eliminar chat: {str(e)}")
        return False

# ==================== FUNCIONES PRINCIPALES ====================

def configurar_pagina():
    st.set_page_config(
        page_title="ChatBot Multifuncional",
        page_icon="🤖",
        layout="wide"
    )
    st.title("💬 ChatBot con Historial de Chats")

def crear_cliente_groq():
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY")
        if not groq_api_key:
            st.error("API key no configurada. Por favor configura GROQ_API_KEY en los secrets.")
            st.stop()
        return groq.Groq(api_key=groq_api_key)
    except Exception as e:
        st.error(f"Error al crear cliente Groq: {str(e)}")
        st.stop()

def procesar_archivo(uploaded_file):
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        contenido = ""
        
        if file_extension in EXTENSIONES_PERMITIDAS['imagen']:
            imagen = Image.open(tmp_file_path)
            contenido = pytesseract.image_to_string(imagen)
            st.image(imagen, caption=f"Imagen subida: {uploaded_file.name}", use_column_width=True)
            
        elif file_extension == 'pdf':
            contenido = extract_text(tmp_file_path)
            st.success(f"PDF procesado: {uploaded_file.name} (páginas: {len(contenido.split('\x0c'))})")
            
        elif file_extension == 'docx':
            doc = Document(tmp_file_path)
            contenido = '\n'.join([para.text for para in doc.paragraphs])
            st.success(f"Documento Word procesado: {uploaded_file.name}")
            
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(tmp_file_path)
            contenido = f"Datos tabulares:\n{df.to_string()}"
            st.dataframe(df.head())
            
        elif file_extension == 'csv':
            df = pd.read_csv(tmp_file_path)
            contenido = f"Datos CSV:\n{df.to_string()}"
            st.dataframe(df.head())
            
        else:
            with open(tmp_file_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            if file_extension in EXTENSIONES_PERMITIDAS['codigo']:
                st.code(contenido, language=file_extension)
            else:
                st.text_area(f"Contenido de {uploaded_file.name}", contenido, height=200)
        
        os.unlink(tmp_file_path)
        
        return {
            "nombre": uploaded_file.name,
            "tipo": file_extension,
            "contenido": contenido[:10000]
        }
        
    except Exception as e:
        st.error(f"Error al procesar archivo: {str(e)}")
        return None

def mostrar_sidebar():
    with st.sidebar:
        st.title("⚙️ Configuración")
        
        # Configuración del modelo
        modelo = st.selectbox(
            'Selecciona un modelo',
            options=list(MODELOS.keys()),
            format_func=lambda x: f"{x} - {MODELOS[x]}",
            index=0
        )
        
        st.divider()
        st.subheader("📚 Gestión de Chats")
        
        # Lista de chats guardados con búsqueda
        chats_guardados = listar_chats()
        chat_seleccionado = st.selectbox(
            "Chats guardados",
            options=chats_guardados,
            index=0 if chats_guardados else None,
            key="chat_seleccionado"
        )
        
        # Botones de gestión de chats
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar chat", help="Guarda el chat actual"):
                if hasattr(st.session_state, 'mensajes') and st.session_state.mensajes:
                    nombre_por_defecto = generar_nombre_por_defecto(st.session_state.mensajes)
                    nombre_chat = st.text_input(
                        "Nombre para este chat:",
                        value=nombre_por_defecto,
                        key="nombre_chat_input"
                    )
                    if nombre_chat:
                        if guardar_chat(nombre_chat, st.session_state.mensajes):
                            st.success("Chat guardado correctamente")
                            # Iniciar nuevo chat después de guardar
                            st.session_state.mensajes = [{
                                "role": "assistant",
                                "content": "¡Hola! Soy un asistente vistual y estoy para servirte.",
                                "timestamp": datetime.now().isoformat()
                            }]
                            st.session_state.current_chat_name = None
                            time.sleep(1)
                            st.rerun()
        
        with col2:
            if chat_seleccionado and st.button("📂 Cargar chat", help="Carga el chat seleccionado"):
                mensajes = cargar_chat(chat_seleccionado)
                if mensajes:
                    st.session_state.mensajes = mensajes
                    st.session_state.current_chat_name = chat_seleccionado
                    st.success(f"Chat '{chat_seleccionado}' cargado")
                    time.sleep(1)
                    st.rerun()
        
        # Botones adicionales
        col3, col4 = st.columns(2)
        with col3:
            if st.button("🧹 Nuevo chat", help="Comienza una nueva conversación"):
                st.session_state.mensajes = [{
                    "role": "assistant",
                    "content": "¡Hola! Soy un asistente vistual y estoy para servirte.",
                    "timestamp": datetime.now().isoformat()
                }]
                st.session_state.current_chat_name = None
                st.rerun()
        
        with col4:
            if chat_seleccionado and st.button("🗑️ Eliminar chat", type="secondary", help="Elimina el chat seleccionado"):
                if eliminar_chat(chat_seleccionado):
                    st.success(f"Chat '{chat_seleccionado}' eliminado")
                    time.sleep(1)
                    st.rerun()
        
        # Funciones de importar/exportar
        st.divider()
        st.subheader("🔄 Importar/Exportar")
        
        # Exportar chat actual
        if hasattr(st.session_state, 'mensajes') and st.session_state.mensajes:
            chat_json = json.dumps(st.session_state.mensajes, ensure_ascii=False, indent=2)
            nombre_exportacion = f"{st.session_state.current_chat_name or 'chat_exportado'}.json"
            st.download_button(
                label="📤 Exportar chat actual",
                data=chat_json,
                file_name=nombre_exportacion,
                mime="application/json",
                help="Descarga el chat actual como archivo JSON"
            )
        
        # Importar chat
        uploaded_chat = st.file_uploader(
            "📥 Importar chat (JSON)",
            type=["json"],
            accept_multiple_files=False,
            help="Sube un archivo JSON previamente exportado"
        )
        
        if uploaded_chat:
            try:
                mensajes = json.load(uploaded_chat)
                if isinstance(mensajes, list) and all("role" in msg and "content" in msg for msg in mensajes):
                    st.session_state.mensajes = mensajes
                    nombre_archivo = uploaded_chat.name.replace(".json", "")
                    st.session_state.current_chat_name = nombre_archivo
                    st.success(f"Chat '{nombre_archivo}' importado correctamente")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("El archivo no tiene el formato correcto")
            except Exception as e:
                st.error(f"Error al importar chat: {str(e)}")
        
        st.divider()
        st.markdown('ℹ️ **Formatos soportados:**')
        st.markdown('- **Imágenes:** PNG, JPG, JPEG, SVG, BMP, GIF')
        st.markdown('- **Documentos:** PDF, DOCX, TXT, RTF')
        st.markdown('- **Código:** PY, HTML, CSS, JS, JSON, XML, CSV, MD')
        st.markdown('- **Datos:** XLSX, XLS, CSV')
    
    return modelo

def inicializar_estado_chat():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [{
            "role": "assistant",
            "content": "¡Hola! Soy un asistente vistual y estoy para servirte.",
            "timestamp": datetime.now().isoformat()
        }]
    if "current_chat_name" not in st.session_state:
        st.session_state.current_chat_name = None

def obtener_mensajes_previos():
    if hasattr(st.session_state, 'mensajes'):
        for mensaje in st.session_state.mensajes:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])
                if "archivos" in mensaje and mensaje["archivos"]:
                    st.caption(f"Archivos adjuntos: {', '.join(mensaje['archivos'])}")
                if "timestamp" in mensaje:
                    st.caption(f"{datetime.fromisoformat(mensaje['timestamp']).strftime('%H:%M')}")

def obtener_respuesta_modelo(cliente, modelo, mensajes):
    try:
        with st.spinner(f"Analizando con {modelo}..."):
            api_messages = [{"role": m["role"], "content": m["content"]} for m in mensajes]
            respuesta = cliente.chat.completions.create(
                model=modelo,
                messages=api_messages,
                stream=False,
                temperature=0.7,
                max_tokens=2048
            )
            return respuesta.choices[0].message.content
    except Exception as e:
        st.error(f"Error al obtener respuesta: {str(e)}")
        return None

def autoguardar_chat():
    """Guarda automáticamente el chat si tiene suficientes mensajes"""
    if hasattr(st.session_state, 'mensajes') and len(st.session_state.mensajes) > 2:
        if not hasattr(st.session_state, 'current_chat_name') or not st.session_state.current_chat_name:
            st.session_state.current_chat_name = generar_nombre_por_defecto(st.session_state.mensajes)
        guardar_chat(st.session_state.current_chat_name, st.session_state.mensajes)

def ejecutar_chat():
    # 1. Inicializar estado del chat (PRIMERO)
    inicializar_estado_chat()
    
    # 2. Configurar página y cliente
    configurar_pagina()
    cliente = crear_cliente_groq()
    
    # 3. Mostrar sidebar (que ahora puede acceder a mensajes con seguridad)
    modelo = mostrar_sidebar()
    
    # Widget para subir archivos
    uploaded_files = st.file_uploader(
        "Sube archivos (PNG, PDF, DOCX, TXT, código, etc.)",
        type=sum(EXTENSIONES_PERMITIDAS.values(), []),
        accept_multiple_files=True
    )
    
    # Procesar archivos subidos
    archivos_procesados = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Procesando {uploaded_file.name}..."):
                archivo_procesado = procesar_archivo(uploaded_file)
                if archivo_procesado:
                    archivos_procesados.append(archivo_procesado)
    
    # Mostrar historial de chat
    obtener_mensajes_previos()
    
    # Campo de entrada de mensaje
    if prompt := st.chat_input("Escribe tu mensaje o pregunta sobre los archivos..."):
        # Construir contexto con archivos si existen
        contexto_archivos = ""
        if archivos_procesados:
            contexto_archivos = "\n\nContexto de archivos subidos:\n"
            for archivo in archivos_procesados:
                contexto_archivos += f"\n--- {archivo['nombre']} ({archivo['tipo']}) ---\n{archivo['contenido']}\n"
        
        mensaje_completo = f"{prompt}\n{contexto_archivos}"
        
        user_msg = {
            "role": "user",
            "content": mensaje_completo,
            "timestamp": datetime.now().isoformat(),
            "archivos": [a['nombre'] for a in archivos_procesados]
        }
        st.session_state.mensajes.append(user_msg)
        
        with st.chat_message("user"):
            st.markdown(prompt)
            if archivos_procesados:
                st.caption(f"Archivos adjuntos: {', '.join([a['nombre'] for a in archivos_procesados])}")
            st.caption(f"{datetime.now().strftime('%H:%M')}")
        
        respuesta = obtener_respuesta_modelo(cliente, modelo, st.session_state.mensajes)
        
        if respuesta:
            assistant_msg = {
                "role": "assistant",
                "content": respuesta,
                "timestamp": datetime.now().isoformat(),
                "model": modelo
            }
            st.session_state.mensajes.append(assistant_msg)
            
            with st.chat_message("assistant"):
                st.markdown(respuesta)
                st.caption(f"{datetime.now().strftime('%H:%M')} • {modelo}")
            
            # Autoguardar después de cada interacción completa
            autoguardar_chat()

if __name__ == '__main__':
    ejecutar_chat()