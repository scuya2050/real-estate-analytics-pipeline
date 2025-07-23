# Image
FROM python:3.13.5-slim

# set working directory
WORKDIR /web-scraper

# copy only requirements.txt first
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc \
      libpq-dev \
      libpq5 \
      build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    # Remove build deps, keep runtime
    && apt-get purge -y gcc libpq-dev build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
    
# install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy only what you need
COPY . .

# default command
CMD ["python", "./web_scraper.py"]