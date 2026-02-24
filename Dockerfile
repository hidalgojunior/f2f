FROM python:3.12-slim

# set workdir
WORKDIR /app

# install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLASK_APP=run.py
ENV FLASK_ENV=development
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
