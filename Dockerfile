# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install build-essential and other required packages
RUN apt-get update && apt-get install -y build-essential

# Install uv
RUN pip install uv

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies using uv sync and activate the virtual environment
RUN uv sync

# Create the hashes directory
RUN mkdir -p /app/hashes

# Set the HASH_DIR environment variable for hashes
ENV HASH_DIR=/app/hashes
ENV PATH="/app/.venv/bin:$PATH"

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]
