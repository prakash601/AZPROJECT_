FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm ci && npm run build

# Copy built frontend to backend static directory
WORKDIR /app
RUN mkdir -p static && cp -r frontend/dist/* static/

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
