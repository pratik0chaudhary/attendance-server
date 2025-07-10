FROM python:3.8.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && pip install --upgrade pip

COPY . /app

RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations 

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "main.wsgi:application"]

