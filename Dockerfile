# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install build-essential and other required packages
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies using uv sync and activate the virtual environment
RUN uv sync

# Set the environment variables first
ENV HASH_DIR=/app/hashes
ENV PATH="/app/.venv/bin:$PATH"

# Pre-download hrequests-cgo library during build to avoid download on each container start
RUN python -c "import hrequests; print('hrequests-cgo downloaded successfully')"

# Create the hashes directory
RUN mkdir -p /app/hashes

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]
