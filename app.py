import streamlit as st
import os
import re
import fitz
import pytesseract

from deep_translator import GoogleTranslator
from pdf2image import convert_from_path

# RUTA TESSERACT
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# RUTA POPPLER
POPPLER_PATH = r"D:\Usuarios\Lorena\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

st.set_page_config(page_title="Traductor Jurado IA")

st.title("📄 Traductor Jurado IA")

uploaded_file = st.file_uploader(
    "Subir documento PDF",
    type=["pdf"]
)

if uploaded_file:

    if not os.path.exists("archivos"):
        os.makedirs("archivos")

    ruta_pdf = os.path.join(
        "archivos",
        uploaded_file.name
    )

    with open(ruta_pdf, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Documento subido correctamente ✅")

    if st.button("Procesar documento"):

        st.info("Convirtiendo PDF a imágenes...")

        imagenes = convert_from_path(
            ruta_pdf,
            poppler_path=POPPLER_PATH
        )

        texto_extraido = ""

        st.info("Leyendo texto con OCR...")

        for imagen in imagenes:

            texto = pytesseract.image_to_string(
                imagen,
                lang="ara"
            )

            texto_extraido += texto + "\n"

        st.info("Traduciendo documento...")

        try:

            texto_traducido = GoogleTranslator(
                source='auto',
                target='es'
            ).translate(texto_extraido)

        except:

            texto_traducido = texto_extraido

        # EXTRAER DATOS
        nombre = "NO DETECTADO"
        fecha_nacimiento = "NO DETECTADO"
        lugar_nacimiento = "NO DETECTADO"
        estado_civil = "NO DETECTADO"
        tribunal = "Tribunal de Blida"
        fecha_sentencia = "NO DETECTADO"
        observaciones = "Sin observaciones"

        # BUSCAR FECHA
        fecha_match = re.search(
            r"\d{2}/\d{2}/\d{4}",
            texto_traducido
        )

        if fecha_match:

            fecha_nacimiento = fecha_match.group()
            fecha_sentencia = fecha_match.group()

        # ESTADO CIVIL
        if "casado" in texto_traducido.lower():

            estado_civil = "Casado"

        elif "soltero" in texto_traducido.lower():

            estado_civil = "Soltero"

        # NOMBRE
        lineas = texto_traducido.split("\n")

        for linea in lineas:

            if "llamada" in linea.lower():

                nombre = linea.replace(
                    "Sobre la persona llamada:",
                    ""
                ).strip()

        # LUGAR NACIMIENTO
        lugar_match = re.search(
            r"en:\s*([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)",
            texto_traducido
        )

        if lugar_match:

            lugar_nacimiento = lugar_match.group(1).strip()

        # TEXTO MÁS LARGO
        resultado = texto_traducido[:600]

        # CARGAR HTML
        with open(
            "plantillas/penales_argelia.html",
            "r",
            encoding="utf-8"
        ) as archivo_html:

            plantilla_html = archivo_html.read()

        # REEMPLAZAR VARIABLES
        html_final = plantilla_html.format(
            nombre=nombre,
            fecha_nacimiento=fecha_nacimiento,
            lugar_nacimiento=lugar_nacimiento,
            estado_civil=estado_civil,
            tribunal=tribunal,
            fecha_sentencia=fecha_sentencia,
            resultado=resultado,
            observaciones=observaciones
        )

        if not os.path.exists("resultados"):
            os.makedirs("resultados")

        # GUARDAR HTML TEMPORAL
        archivo_html_generado = "resultados/documento_traducido.html"

        with open(
            archivo_html_generado,
            "w",
            encoding="utf-8"
        ) as archivo_final_html:

            archivo_final_html.write(html_final)

        st.success("Documento generado correctamente ✅")

        with open(
            archivo_html_generado,
            "rb"
        ) as archivo_descarga:

            st.download_button(
                label="📥 Descargar Documento",
                data=archivo_descarga,
                file_name="documento_traducido.html",
                mime="text/html"
            )