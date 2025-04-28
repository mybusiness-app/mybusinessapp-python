FROM python:3.13-slim

WORKDIR /app

# Copy the entire project for installation
COPY . /app/

# Install the package in development mode
RUN pip install -e .

# Install additional dependencies
RUN pip install chainlit httpx

# Expose the port
EXPOSE 8501

# Run the frontend
CMD ["chainlit", "run", "mypetparlorapp/apps/frontend/app.py", "--host", "0.0.0.0", "--port", "8501"] 