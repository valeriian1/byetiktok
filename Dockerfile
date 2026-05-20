# Use a lightweight official Python 3.12 runtime image
FROM python:3.12-slim

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr to enable real-time logging
ENV PYTHONUNBUFFERED=1

# Establish working directory inside the container
WORKDIR /app

# Copy dependency specifications first to leverage Docker build cache layers
COPY requirements.txt .

# Install dependencies securely without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project modules into the working directory
COPY . .

# Run the Telegram bot service
CMD ["python", "main.py"]
