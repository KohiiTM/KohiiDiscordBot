#!/bin/bash
# Kohii Discord Bot Docker Setup Script

echo "Setting up Kohii Discord bot in Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found! Please create one before running this script."
    exit 1
fi

# Create Dockerfile
echo "Creating Dockerfile..."
cat > Dockerfile << 'EOF'
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
EOF

# Create requirements.txt with all needed dependencies
echo "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
discord.py==2.4.0
pymongo==4.10.1
python-dotenv==1.0.1
requests==2.32.3
pillow==11.0.0
Flask==3.0.3
Flask-Cors==5.0.0
Flask-PyMongo==2.3.0
EOF

# Build Docker image
echo "Building Docker image..."
docker build -t kohii-bot .

# Run container with enhanced logging
echo "Starting Kohii bot container..."
docker run -d \
    --name kohii-bot \
    --restart unless-stopped \
    -v "${PWD}/bot:/app/bot" \
    -v "${PWD}/.env:/app/.env" \
    --log-driver json-file \
    --log-opt max-size=10m \
    kohii-bot

echo "Setup complete! Kohii bot is now running in Docker."
echo ""
echo "Useful Docker commands:"
echo "- Check if your bot is running: docker ps"
echo "- View logs: docker logs kohii-bot"
echo "- Stop the bot: docker stop kohii-bot"
echo "- Start the bot again: docker start kohii-bot"
echo "- Remove the container: docker rm kohii-bot"
echo "- Remove the image: docker rmi kohii-bot"