FROM python:3.10-slim

WORKDIR /app

COPY ./web/requirements.txt /app/requirements-web.txt
COPY ./sdk/requirements.txt /app/requirements-sdk.txt

COPY ./web /app
COPY ./sdk /app/sdk

RUN pip install --no-cache-dir -r requirements-web.txt
RUN pip install --no-cache-dir -r requirements-sdk.txt
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir sdk/

EXPOSE 8080

ENV FLASK_APP=app.py

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--timeout", "120", "app:app"]
