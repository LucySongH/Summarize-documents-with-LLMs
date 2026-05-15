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

# Create Streamlit config to prevent connection timeouts
RUN mkdir -p /root/.streamlit && echo '\
[server]\n\
maxUploadSize = 200\n\
enableXsrfProtection = false\n\
[browser]\n\
gatherUsageStats = false\n\
' > /root/.streamlit/config.toml

# Expose ports
EXPOSE 8000 8501

# Start both backend and frontend
CMD ["python", "run_app.py"]
