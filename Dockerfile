FROM python:3.11-slim

# Sistema kitapxanaların ornatıw (Postgres ushın)
RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app

# Kitapxanalarnı júklew
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proekt kodların kóshiriw
COPY . .

# Media hám Static papkaların jaratıw
RUN mkdir -p /app/media /app/static

# Porttı ashıw
EXPOSE 8000