FROM python:3.12-slim

WORKDIR /app

# Copy the project files to the container
COPY . .

# Install dependencies
RUN pip install -e .

# Expose the API port
EXPOSE 8000

# Start the API server
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
