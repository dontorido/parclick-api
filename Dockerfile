FROM python:3.11-slim

# Set a working directory
WORKDIR /app

# Install system deps required for some wheels (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port and start
ENV PORT=10000
EXPOSE 10000
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "120"]
