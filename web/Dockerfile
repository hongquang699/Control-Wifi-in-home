FROM python:3.12-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl iproute2 net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy application sources
COPY . .

EXPOSE 8080

CMD ["python", "backend/main.py", "8080"]
