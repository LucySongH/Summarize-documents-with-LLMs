# Dockerfile — DocSum Application
# Base image: Python 3.11 slim (lightweight)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose ports
EXPOSE 8000 8501

# Start both backend and frontend
CMD ["python", "run_app.py"]
