# Use a small official Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies if you have requirements.txt
# (remove this if you don't use one)
RUN pip install --no-cache-dir requests python-dotenv

# Default command
CMD ["python", "main.py"]
