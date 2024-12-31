FROM python:3.10

RUN apt-get update && apt-get install -y pip

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install jinja2
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir sentence-transformers

COPY . .

CMD ["streamlit", "run", "main.py"]


