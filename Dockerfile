FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requisitos.txt

EXPOSE 8501

CMD ["streamlit", "run", "aplicación.py", "--server.port=8501", "--server.address=0.0.0.0"]
