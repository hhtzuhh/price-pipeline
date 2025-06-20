# Stage 1: Build dependencies (multi-stage build for smaller final image)
FROM python:3.11-slim-bookworm as builder

# Set environment variables for non-interactive installs
ENV PYTHONUNBUFFERED 1 \
    PYTHONDONTWRITEBYTECODE 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for some Python packages (e.g., psycopg2 for PostgreSQL)
# Make sure to clean up apt cache to keep image size small
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/* 

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir to prevent pip from storing cache, reducing image size
# --upgrade pip to ensure latest pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image for running the application
FROM python:3.11-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Expose the port your FastAPI application listens on
EXPOSE 8000

# Command to run your FastAPI application using Uvicorn (production-ready)
# Use gunicorn as a process manager for multiple workers, and uvicorn as the ASGI server
# Adjust workers based on your CPU cores (2-4 * num_cores is a common starting point)
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]
# If your main FastAPI app is in a different file/module, adjust "app.main:app" accordingly.
# E.g., if it's in `src/my_app.py` and the FastAPI instance is `fastapi_app`, it would be "src.my_app:fastapi_app"