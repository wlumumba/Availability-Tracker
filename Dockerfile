# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt using uv
RUN uv pip install --no-cache -r requirements.txt

# Create the hashes directory
RUN mkdir -p /app/hashes

# Set the HASH_DIR environment variable for hashes
ENV HASH_DIR=/app/hashes

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]
