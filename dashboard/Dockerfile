FROM python:3.13.5-slim

WORKDIR /dashboard

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc \
      libpq-dev \
      libpq5 \
      build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y gcc libpq-dev build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "./run_streamlit.py"]
