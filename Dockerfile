# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# write access permissions to the db folder
RUN chmod -R 777 /app/db

# Expose port for Gradio (default 7860)
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED 1

# Start the Gradio app
CMD ["python", "app.py"]
