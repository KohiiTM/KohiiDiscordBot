# Kohii Discord Bot

Kohii is a versatile Discord bot designed to enhance your server with various features, including chat logging, Pomodoro sessions, auto-responses, and more. It also includes a Flask web server for additional functionality.

## Features

- **Ping**: Check the bot's latency
- **Restart**: Restart the bot (requires admin privileges)
- **Chat Logs**: Log and view chat messages
- **Pomodoro**: Manage Pomodoro sessions for productivity
- **Avatar**: Retrieve a user's profile picture
- **Auto Responses**: Automatically respond to specific keywords
- **Coffee Collection**: Collect and trade coffee-related cards
- **Web Interface**: Flask-based web server for additional functionality

## Setup

### Prerequisites

- Python 3.8+
- MongoDB
- Discord Bot Token
- Required Python packages (listed in `requirements.txt`)

### Installation

#### Option 1: Traditional Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/kohii.git
   cd kohii
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your environment variables:

   ```env
   DISCORD_TOKEN=your_discord_token
   MONGO_USERNAME=your_mongo_username
   MONGO_PASSWORD=your_mongo_password
   ```

5. Run the bot:
   ```sh
   python bot/main.py
   ```

#### Option 2: Docker Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/kohii.git
   cd kohii
   ```

2. Create a `.env` file as described above

3. Start the services using Docker Compose:
   ```sh
   docker-compose up -d
   ```

## Usage

### Commands

- **/ping**: Check the bot's latency
- **/restart**: Restart the bot (admin only)
- **/shutdown**: Gracefully shut down the bot (owner only)
- **/start**: Start a new Pomodoro session
- **/stop**: Stop the current Pomodoro session
- **/skip**: Skip the current Pomodoro phase
- **/session_history**: View your Pomodoro session history
- **/avatar**: Retrieve a user's profile picture
- **/collect**: Collect a random pair of coffee-related cards
- **/my_cards**: View your collected coffee cards
- **/trade**: Trade a coffee card with another user
- **/clear_collection**: Clear all coffee cards from a user's collection (owner only)

### Event Listeners

- **on_message**: Log messages to MongoDB and handle auto-responses
- **on_ready**: Log when the bot is ready and sync slash commands
- **on_disconnect**: Close MongoDB connection when the bot disconnects

### Web Interface

The bot includes a Flask web server that provides additional functionality. By default, it runs on port 5000.

## Development

### Project Structure

```
kohii/
├── bot/                # Main bot code
│   ├── cogs/          # Bot command modules
│   └── main.py        # Bot entry point
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt   # Python dependencies
└── setup.sh          # Setup script
```

### Testing

The project includes pytest for testing. Run tests using:

```sh
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
