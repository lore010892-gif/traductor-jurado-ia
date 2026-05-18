import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz
from deep_translator import GoogleTranslator
from pdf2image import convert_from_path
import pytesseract

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

opcion = st.selectbox(
    "Seleccione el proceso",
    [
        "Traducir documento",
        "Revisar traducción"
    ]
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

    st.write("### Archivo cargado")
    st.write(uploaded_file.name)

    if st.button("Procesar documento"):

        st.info("Convirtiendo PDF a imágenes...")

        imagenes = convert_from_path(
            ruta_pdf,
            poppler_path=POPPLER_PATH
        )

        texto_extraido = ""

        st.info("Leyendo texto árabe con OCR...")

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

        if not os.path.exists("resultados"):
            os.makedirs("resultados")

        pdf_path = "resultados/documento_traducido.pdf"

        c = canvas.Canvas(
            pdf_path,
            pagesize=letter
        )

        y = 750

        lineas = texto_traducido.split("\n")

        for linea in lineas:

            c.drawString(
                40,
                y,
                linea[:100]
            )

            y -= 20

            if y < 50:

                c.showPage()
                y = 750

        c.save()

        pdf_documento = fitz.open(pdf_path)

        sello_path = "sellos/sello_mariam.png"

        for pagina in pdf_documento:

            rect = fitz.Rect(
                400,
                650,
                550,
                780
            )

            pagina.insert_image(
                rect,
                filename=sello_path,
                overlay=True
            )

        pdf_documento.save(
            "resultados/documento_final.pdf"
        )

        pdf_documento.close()

        st.success("Documento traducido y sellado correctamente ✅")

        with open(
            "resultados/documento_final.pdf",
            "rb"
        ) as pdf_final:

            st.download_button(
                label="📥 Descargar PDF Final",
                data=pdf_final,
                file_name="documento_final.pdf",
                mime="application/pdf"
            )