# 1. Pull the official Python image
FROM python:3.10-slim

# 2. Set environment variables (Required for Hugging Face later)
ENV HOME=/tmp \
    TRANSFORMERS_CACHE=/tmp/hf_cache \
    TORCH_HOME=/tmp/torch_cache \
    PYTHONUNBUFFERED=1

# 3. Create a working directory inside the container
WORKDIR /code

# 4. Install system tools needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy your requirements file first
COPY requirements.txt /code/requirements.txt

# 6. Install your Python dependencies
# 6. Install CPU-only PyTorch first, then install the rest of requirements
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 7. Copy the rest of your Python code into the container
COPY . /code

# 8. Create a secure, non-root user (Required for Hugging Face)
RUN useradd -m -u 1000 user && \
    chown -R user:user /code /tmp

# 9. Switch to that user
USER user

# 10. Expose the port we set in the docker-compose file
EXPOSE 7860

# 11. Command to start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]