FROM python:3.13-slim

# Set environment variables
ENV PYTHONPATH=/workspace

WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . mypetparlorapp/

# Install the package in development mode
WORKDIR /workspace/mypetparlorapp
RUN pip install -e .

# Set up application
WORKDIR /workspace/mypetparlorapp/apps/backend

# Copy the service account key
COPY keys/mypetparlorapp-route-optimization-key.json ./keys/mypetparlorapp-route-optimization-key.json

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 