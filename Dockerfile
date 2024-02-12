FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY django_site .

CMD ["gunicorn", "django_site.wsgi:application", "--bind", "0.0.0.0:8000"]


