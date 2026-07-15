FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run uvicorn on port 8080 which is expected by Cloud Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
