# Multi-stage build for optimized ML training environment
# Stage 1: Base environment with Python and dependencies
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Development environment
FROM base as development

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIPELINE_TEST=1

# Expose port for Dash dashboard
EXPOSE 8050

# Default command
CMD ["python", "scripts/train_ppo.py", "--episodes", "10"]

# Stage 3: Production environment
FROM base as production

# Copy only necessary files
COPY config.py .
COPY nodes.py .
COPY pipeline.py .
COPY methods/ methods/
COPY env/ env/
COPY ppo/ ppo/
COPY scripts/ scripts/

# Create necessary directories
RUN mkdir -p data/processed models logs

# Set production environment variables
ENV PYTHONUNBUFFERED=1
ENV PIPELINE_TEST=0

# Run training with optimized settings
CMD ["python", "scripts/train_ppo.py", "--episodes", "100"]
