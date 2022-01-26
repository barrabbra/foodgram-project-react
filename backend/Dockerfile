FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN mkdir -p static_backend/fonts
COPY arial.ttf ./static_backend/fonts
RUN pip install -r requirements.txt
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]