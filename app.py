import streamlit as st
import os
import re
import fitz
import pytesseract

from deep_translator import GoogleTranslator
from pdf2image import convert_from_path
from xhtml2pdf import pisa

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

        # GENERAR PDF
        pdf_generado = "resultados/documento_traducido.pdf"

        with open(
            pdf_generado,
            "wb"
        ) as pdf_file:

            pisa.CreatePDF(
                html_final,
                dest=pdf_file
            )

        # ABRIR PDF PARA SELLOS
        pdf_documento = fitz.open(pdf_generado)

        sello_path = "sellos/sello_mariam.png"

        # PÁGINA 1
        pagina1 = pdf_documento[0]

        rect1 = fitz.Rect(
            430,
            760,
            530,
            860
        )

        pagina1.insert_image(
            rect1,
            filename=sello_path,
            overlay=True
        )

        # PÁGINA 2
        if len(pdf_documento) > 1:

            pagina2 = pdf_documento[1]

            rect2 = fitz.Rect(
                390,
                640,
                510,
                760
            )

            pagina2.insert_image(
                rect2,
                filename=sello_path,
                overlay=True
            )

        pdf_documento.save(
            "resultados/documento_traducido_sellado.pdf"
        )

        pdf_documento.close()

        # UNIR TRADUCCIÓN + ORIGINAL
        pdf_final = fitz.open()

        pdf_traducido = fitz.open(
            "resultados/documento_traducido_sellado.pdf"
        )

        pdf_original = fitz.open(ruta_pdf)

        # PRIMERO TRADUCCIÓN
        pdf_final.insert_pdf(pdf_traducido)

        # DESPUÉS ORIGINAL
        pdf_final.insert_pdf(pdf_original)

        pdf_final.save(
            "resultados/documento_final_unido.pdf"
        )

        pdf_final.close()

        st.success("Documento final generado correctamente ✅")

        with open(
            "resultados/documento_final_unido.pdf",
            "rb"
        ) as archivo_final:

            st.download_button(
                label="📥 Descargar PDF Final",
                data=archivo_final,
                file_name="documento_final.pdf",
                mime="application/pdf"
            )