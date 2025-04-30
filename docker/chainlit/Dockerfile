# Build the application and dependencies
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY apps/chainlit/ .

EXPOSE 8501

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8501"]