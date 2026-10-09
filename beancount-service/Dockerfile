FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY beancount-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the beancount-service application code
COPY beancount-service/ .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
