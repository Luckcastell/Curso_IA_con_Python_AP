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
import re

# Configura Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

# Extensiones permitidas
EXTENSIONES_PERMITIDAS = {
    'imagen': ['png', 'jpg', 'jpeg', 'svg', 'bmp', 'gif'],
    'documento': ['pdf', 'docx', 'txt', 'rtf'],
    'codigo': ['py', 'html', 'css', 'js', 'json', 'xml', 'csv', 'md'],
    'datos': ['xlsx', 'xls', 'csv']
}

# ==================== FUNCIONES MEJORADAS PARA HISTORIAL ====================

def generar_nombre_chat_auto(mensajes):
    """Genera un nombre automático basado en el contenido del chat"""
    try:
        # Obtener los primeros 5 mensajes relevantes
        textos = []
        for msg in mensajes[-5:]:
            if msg["role"] == "user" and len(msg["content"]) > 10:
                textos.append(msg["content"])
        
        if not textos:
            return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Unir textos y limpiar
        texto = " ".join(textos)[:200]  # Limitar tamaño
        texto = re.sub(r'\W+', ' ', texto)  # Eliminar caracteres especiales
        palabras = [p for p in texto.split() if len(p) > 3][:5]  # Palabras significativas
        
        if not palabras:
            return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        nombre_base = "_".join(palabras).lower()
        return f"{nombre_base}_{datetime.now().strftime('%H%M')}"
    except:
        return f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def guardar_chat(nombre_chat, mensajes, iniciar_nuevo=True):
    """Guarda el chat y opcionalmente inicia uno nuevo"""
    try:
        # Si el nombre está vacío, generamos uno automático
        if not nombre_chat.strip():
            nombre_chat = generar_nombre_chat_auto(mensajes)
        
        # Aseguramos que el nombre sea válido para archivo
        nombre_chat = re.sub(r'[\\/*?:"<>|]', "_", nombre_chat)
        nombre_chat = nombre_chat.strip() or "chat_sin_nombre"
        
        with open(os.path.join(CHATS_DIR, f"{nombre_chat}.json"), "w", encoding="utf-8") as f:
            json.dump(mensajes, f, ensure_ascii=False, indent=2)
        
        if iniciar_nuevo:
            st.session_state.mensajes = [{
                "role": "assistant",
                "content": "¡Nuevo chat iniciado! ¿En qué puedo ayudarte?",
                "timestamp": datetime.now().isoformat()
            }]
            st.session_state.current_chat_name = None
        
        return nombre_chat
    except Exception as e:
        st.error(f"Error al guardar chat: {str(e)}")
        return None

def cargar_chat(nombre_chat):
    try:
        with open(os.path.join(CHATS_DIR, f"{nombre_chat}.json"), "r", encoding="utf-8") as f:
            mensajes = json.load(f)
            st.session_state.current_chat_name = nombre_chat
            return mensajes
    except Exception as e:
        st.error(f"Error al cargar chat: {str(e)}")
        return None

def listar_chats():
    try:
        chats = [f.replace(".json", "") for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
        return sorted(chats, key=lambda x: os.path.getmtime(os.path.join(CHATS_DIR, f"{x}.json")), reverse=True)
    except Exception as e:
        st.error(f"Error al listar chats: {str(e)}")
        return []

def eliminar_chat(nombre_chat):
    try:
        os.remove(os.path.join(CHATS_DIR, f"{nombre_chat}.json"))
        return True
    except Exception as e:
        st.error(f"Error al eliminar chat: {str(e)}")
        return False

def exportar_chat(mensajes):
    """Prepara el chat para exportación"""
    try:
        return json.dumps(mensajes, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al exportar chat: {str(e)}")
        return None

def importar_chat(uploaded_file):
    """Importa un chat desde un archivo JSON"""
    try:
        mensajes = json.load(uploaded_file)
        if isinstance(mensajes, list) and all(isinstance(m, dict) for m in mensajes):
            return mensajes
        else:
            st.error("Formato de chat inválido")
            return None
    except Exception as e:
        st.error(f"Error al importar chat: {str(e)}")
        return None

# ==================== FUNCIONES PRINCIPALES ====================

def configurar_pagina():
    st.set_page_config(
        page_title="ChatBot Multifuncional",
        page_icon="🤖",
        layout="wide"
    )
    st.title("💬 ChatBot con Historial Avanzado")
    st.caption("Sube archivos, conversa y gestiona tu historial de chats completo")

def mostrar_sidebar():
    with st.sidebar:
        st.title("⚙️ Configuración")
        
        # 1. Selección de modelo
        modelo = st.selectbox(
            'Selecciona un modelo',
            options=list(MODELOS.keys()),
            format_func=lambda x: f"{x} - {MODELOS[x]}",
            index=0
        )
        
        st.divider()
        st.subheader("📚 Gestión de Chats")
        
        # 2. Lista de chats con búsqueda
        chats_guardados = listar_chats()
        chat_seleccionado = st.selectbox(
            "Chats guardados",
            options=chats_guardados,
            index=0 if chats_guardados else None,
            key="chat_seleccionado"
        )
        
        # 3. Botones de gestión
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar chat", help="Guarda el chat actual y limpia la conversación"):
                with st.expander("Opciones de guardado", expanded=True):
                    nombre_chat = st.text_input(
                        "Nombre del chat (dejar en blanco para nombre automático):",
                        value=generar_nombre_chat_auto(st.session_state.mensajes),
                        key="nombre_chat_input"
                    )
                    iniciar_nuevo = st.checkbox("Iniciar nuevo chat después de guardar", value=True)
                    
                    if st.button("✅ Confirmar guardado"):
                        nombre_guardado = guardar_chat(nombre_chat, st.session_state.mensajes, iniciar_nuevo)
                        if nombre_guardado:
                            st.success(f"Chat guardado como: '{nombre_guardado}'")
                            time.sleep(1)
                            st.rerun()
        
        with col2:
            if chat_seleccionado and st.button("📂 Cargar chat"):
                mensajes = cargar_chat(chat_seleccionado)
                if mensajes:
                    st.session_state.mensajes = mensajes
                    st.success(f"Chat '{chat_seleccionado}' cargado")
                    time.sleep(1)
                    st.rerun()
            
            if st.button("🧹 Nuevo chat"):
                st.session_state.mensajes = [{
                    "role": "assistant",
                    "content": "¡Nuevo chat iniciado! ¿En qué puedo ayudarte?",
                    "timestamp": datetime.now().isoformat()
                }]
                st.session_state.current_chat_name = None
                st.rerun()
        
        # 4. Importar/Exportar
        st.subheader("🔄 Importar/Exportar")
        
        # Exportar chat actual
        chat_exportado = exportar_chat(st.session_state.mensajes)
        st.download_button(
            label="📤 Exportar chat actual",
            data=chat_exportado if chat_exportado else "",
            file_name=f"{st.session_state.current_chat_name or 'chat_exportado'}.json",
            mime="application/json",
            disabled=not chat_exportado
        )
        
        # Importar chat
        uploaded_chat = st.file_uploader(
            "📥 Importar chat desde archivo",
            type=["json"],
            accept_multiple_files=False,
            key="chat_uploader"
        )
        
        if uploaded_chat:
            mensajes = importar_chat(uploaded_chat)
            if mensajes:
                st.session_state.mensajes = mensajes
                st.session_state.current_chat_name = uploaded_chat.name.replace(".json", "")
                st.success("Chat importado correctamente")
                time.sleep(1)
                st.rerun()
        
        # 5. Eliminar chat
        if chat_seleccionado and st.button("🗑️ Eliminar chat", type="secondary"):
            if eliminar_chat(chat_seleccionado):
                st.success(f"Chat '{chat_seleccionado}' eliminado")
                time.sleep(1)
                st.rerun()
        
        st.divider()
        st.markdown('ℹ️ **Formatos soportados:**')
        st.markdown('- **Imágenes:** PNG, JPG, JPEG, SVG, BMP, GIF')
        st.markdown('- **Documentos:** PDF, DOCX, TXT, RTF')
        st.markdown('- **Código:** PY, HTML, CSS, JS, JSON, XML, CSV, MD')
        st.markdown('- **Datos:** XLSX, XLS, CSV')
    
    return modelo

# ==================== RESTANTE DEL CÓDIGO (sin cambios) ====================

def inicializar_estado_chat():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [{
            "role": "assistant",
            "content": "¡Hola! Sube archivos y pregúntame sobre ellos.",
            "timestamp": datetime.now().isoformat()
        }]
    if "current_chat_name" not in st.session_state:
        st.session_state.current_chat_name = None

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

def obtener_mensajes_previos():
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

def ejecutar_chat():
    configurar_pagina()
    cliente = crear_cliente_groq()
    modelo = mostrar_sidebar()
    
    inicializar_estado_chat()
    
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

if __name__ == '__main__':
    ejecutar_chat()