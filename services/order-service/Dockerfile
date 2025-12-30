FROM python:3.11-slim

WORKDIR /app

# Copy shared library first
COPY shared /app/shared

# Copy order service files
COPY services/order-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY services/order-service/app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
