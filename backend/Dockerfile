FROM python:3.7-slim
WORKDIR /app
COPY ./api_foodgram /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api_foodgram.wsgi"]