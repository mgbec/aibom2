# Use regular Python ARM64 base image for HTTP server
FROM --platform=linux/arm64 python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose port 8080 for AgentCore
EXPOSE 8080

# Run the AgentCore app
CMD ["python", "-c", "from main import app; app.run(host='0.0.0.0', port=8080)"]