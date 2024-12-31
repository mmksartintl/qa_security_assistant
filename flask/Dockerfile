FROM genai_img

WORKDIR /app

COPY . .

EXPOSE 5000

CMD python3 init_db.py; flask --app main1.py run --host=0.0.0.0
