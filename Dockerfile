FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
ENV FLASK_APP=app.main:app
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]