import streamlit as st
import os
import re
import fitz
import pytesseract

from deep_translator import GoogleTranslator
from pdf2image import convert_from_path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# TESSERACT PARA STREAMLIT CLOUD
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

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

        # STREAMLIT CLOUD YA USARÁ POPPLER INSTALADO
        imagenes = convert_from_path(
            ruta_pdf
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

        fecha_match = re.search(
            r"\d{2}/\d{2}/\d{4}",
            texto_traducido
        )

        if fecha_match:

            fecha_nacimiento = fecha_match.group()

        if "casado" in texto_traducido.lower():

            estado_civil = "Casado"

        elif "soltero" in texto_traducido.lower():

            estado_civil = "Soltero"

        lineas = texto_traducido.split("\n")

        for linea in lineas:

            if "llamada" in linea.lower():

                nombre = linea.replace(
                    "Sobre la persona llamada:",
                    ""
                ).strip()

        lugar_match = re.search(
            r"en:\s*([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)",
            texto_traducido
        )

        if lugar_match:

            lugar_nacimiento = lugar_match.group(1).strip()

        # CREAR PDF
        if not os.path.exists("resultados"):
            os.makedirs("resultados")

        pdf_path = "resultados/documento_final.pdf"

        c = canvas.Canvas(
            pdf_path,
            pagesize=letter
        )

        # TÍTULO
        c.setFont("Helvetica-Bold", 15)

        c.drawString(
            150,
            770,
            "TRADUCCIÓN JURADA DEL ÁRABE"
        )

        # DATOS
        c.setFont("Helvetica", 11)

        c.drawString(
            70,
            720,
            f"Nombre: {nombre}"
        )

        c.drawString(
            70,
            700,
            f"Fecha de nacimiento: {fecha_nacimiento}"
        )

        c.drawString(
            70,
            680,
            f"Lugar de nacimiento: {lugar_nacimiento}"
        )

        c.drawString(
            70,
            660,
            f"Estado civil: {estado_civil}"
        )

        # TEXTO TRADUCIDO
        c.setFont("Helvetica", 10)

        texto = c.beginText(
            70,
            620
        )

        lineas_traducidas = texto_traducido.split("\n")

        for linea in lineas_traducidas[:30]:

            texto.textLine(linea)

        c.drawText(texto)

        # FIRMA
        c.setFont("Helvetica-Oblique", 10)

        c.drawString(
            320,
            120,
            "Documento generado automáticamente"
        )

        c.save()

        # INSERTAR SELLO
        pdf_documento = fitz.open(pdf_path)

        sello_path = "sellos/sello_mariam.png"

        pagina = pdf_documento[0]

        rect = fitz.Rect(
            430,
            720,
            530,
            820
        )

        pagina.insert_image(
            rect,
            filename=sello_path,
            overlay=True
        )

        pdf_documento.save(
            "resultados/documento_final_sellado.pdf"
        )

        pdf_documento.close()

        st.success("PDF generado correctamente ✅")

        with open(
            "resultados/documento_final_sellado.pdf",
            "rb"
        ) as pdf_file:

            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_file,
                file_name="documento_final.pdf",
                mime="application/pdf"
            )