FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    gcc \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    tk-dev \
    tcl-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requisitos.txt

EXPOSE 8501

CMD ["streamlit", "run", "aplicación.py", "--server.port=8501", "--server.address=0.0.0.0"]
