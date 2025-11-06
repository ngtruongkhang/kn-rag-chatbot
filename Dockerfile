# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and source code
COPY requirements.txt ./
COPY .env ./
COPY app.py ./
COPY app/ ./app/
COPY ui/ ./ui/
COPY db/ ./db/

# write access permissions to the db folder
RUN chmod -R 777 /app/db

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Gradio (default 7860)
EXPOSE 7860

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Start the Gradio app
CMD ["python", "app.py"]
