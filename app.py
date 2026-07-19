import streamlit as st
import fitz  # Se instala como: pip install pymupdf
import io

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Compresor de PDF Local",
    page_icon="🔒",
    layout="centered"
)

st.title("🔒 Compresor de PDF 100% Local y Privado")
st.markdown("""
Esta aplicación procesa tus archivos **únicamente en la memoria de tu computadora**. 
Ningún dato se sube a internet, garantizando total confidencialidad para documentos delicados o historias clínicas.
""")

# Selector del archivo PDF original
uploaded_file = st.file_uploader("Cargá tu archivo PDF aquí", type=["pdf"])

if uploaded_file is not None:
    # Leer el archivo cargado en memoria local
    file_bytes = uploaded_file.read()
    input_size_mb = len(file_bytes) / (1024 * 1024)
    
    st.info(f"📁 **Archivo original:** {uploaded_file.name} ({input_size_mb:.2f} MB)")
    
    # Controles para ajustar la compresión
    st.subheader("Configuración de Compresión")
    
    col1, col2 = st.columns(2)
    with col1:
        dpi = st.slider("Resolución (DPI)", min_value=100, max_value=200, value=150, step=10, 
                        help="150 DPI es el estándar ideal para mantener texto escaneado muy nítido ocupando poco espacio.")
    with col2:
        calidad = st.slider("Calidad de compresión de imagen (%)", min_value=50, max_value=100, value=75, step=5,
                            help="Ajusta la calidad de compresión interna. 75% ofrece una reducción drástica de tamaño sin pérdida visual notoria.")

    # Botón para ejecutar el procesamiento local
    if st.button("Comprimir PDF Ahora", type="primary"):
        with st.spinner("Procesando y optimizando el documento localmente..."):
            try:
                # Abrir el documento original desde los bytes en memoria
                doc_original = fitz.open(stream=file_bytes, filetype="pdf")
                doc_comprimido = fitz.open()
                
                # Barra de progreso basada en las páginas del PDF
                total_paginas = len(doc_original)
                progreso = st.progress(0)
                
                for index, pagina in enumerate(doc_original):
                    # Renderizar la página como una imagen con el DPI seleccionado
                    pix = pagina.get_pixmap(dpi=dpi)
                    
                    # Crear una nueva página limpia con las mismas dimensiones originales
                    nueva_pagina = doc_comprimido.new_page(
                        width=pagina.rect.width, 
                        height=pagina.rect.height
                    )
                    
                    # Comprimir los pixeles renderizados a formato JPEG con la calidad definida
                    imagen_comprimida_bytes = pix.tobytes(output="jpg", jpg_quality=calidad)
                    
                    # Insertar la imagen optimizada cubriendo toda la superficie de la nueva página
                    nueva_pagina.insert_image(pagina.rect, stream=imagen_comprimida_bytes)
                    
                    # Actualizar barra de progreso
                    progreso.progress((index + 1) / total_paginas)
                
                # Escribir el documento final optimizando estructuras internas y removiendo basura
                bytes_salida = doc_comprimido.write(
                    garbage=4, 
                    deflate=True, 
                    clean=True
                )
                
                output_size_mb = len(bytes_salida) / (1024 * 1024)
                
                st.success(f"✅ **¡Procesamiento completado con éxito!**")
                
                # Mostrar métricas de la reducción
                st.metric(
                    label="Tamaño Final", 
                    value=f"{output_size_mb:.2f} MB", 
                    delta=f"-{((input_size_mb - output_size_mb) / input_size_mb) * 100:.1f}% de peso"
                )
                
                # Botón local para descargar el resultado generado
                st.download_button(
                    label="📥 Descargar PDF Comprimido",
                    data=bytes_salida,
                    file_name=f"comprimido_{uploaded_file.name}",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Cerrar documentos en memoria
                doc_original.close()
                doc_comprimido.close()
                
            except Exception as e:
                st.error(f"Ocurrió un error inesperado al procesar el documento: {str(e)}")
