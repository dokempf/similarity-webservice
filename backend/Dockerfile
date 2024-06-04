FROM python:3.11-slim

WORKDIR /app

RUN pip install gunicorn

COPY . .

RUN pip install .
CMD ["gunicorn", "--timeout", "360", "--bind", "backend:8080", "similarity_webservice:create_app()"]
