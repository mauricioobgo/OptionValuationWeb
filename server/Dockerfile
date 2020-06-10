FROM python:3.8

RUN pip install Flask gunicorn
RUN pip install pandas gunicorn
RUN pip install scipy gunicorn

COPY src/ app/

WORKDIR /app

ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app