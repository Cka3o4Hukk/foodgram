FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

#RUN python manage.py migrate && \
#    python manage.py collectstatic --no-input

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_main.wsgi"]