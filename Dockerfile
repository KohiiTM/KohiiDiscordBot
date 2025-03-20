FROM python:3.9-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot directory and env file
COPY bot/ ./bot/
COPY .env .

# Set the working directory to the bot folder
WORKDIR /app/bot

# Run the bot
CMD ["python", "main.py"]
