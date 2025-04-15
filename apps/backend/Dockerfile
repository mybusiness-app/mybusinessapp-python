FROM python:3.13-slim

WORKDIR /app

# Copy the entire project for installation
COPY . /app/

# Install the package in development mode
RUN pip install -e .

# Install additional dependencies if needed
RUN pip install uvicorn fastapi

# Expose the port
EXPOSE 8000

# Run the backend
CMD ["uvicorn", "mypetparlorapp.apps.backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 