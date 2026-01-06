FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY ./services/inventory-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./services/inventory-service/app /app/app

# Copy shared libraries
COPY ./shared /app/shared

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
