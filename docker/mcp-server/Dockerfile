FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY common/mcp/ .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "-c", "from server import MCPServer; import os; MCPServer(os.environ['MYBUSINESS_API_URL'], os.environ['MYBUSINESS_API_KEY']).run()"] 