FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy just the pyproject.toml first to leverage Docker cache
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir setuptools wheel && \
    pip install uv
# Copy the project files to the container
COPY . .

# Install the package in development mode
RUN uv pip install --system --no-cache-dir -e .

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Use a shell script as entrypoint to support different commands
COPY start_api.sh start_web_ui.sh ./
RUN chmod +x start_api.sh start_web_ui.sh

# Default command runs the API server
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
