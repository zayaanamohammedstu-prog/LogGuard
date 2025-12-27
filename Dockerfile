FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p data models logs

# Train model on sample data
RUN python train_model.py

# Expose Flask port
EXPOSE 5000

# Run the application
CMD ["python", "web_app/app.py"]
