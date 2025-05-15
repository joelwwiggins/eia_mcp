FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the app with Uvicorn
CMD ["uvicorn", "initial_mcp:app", "--host", "0.0.0.0", "--port", "8000"]