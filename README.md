# Kohii Discord Bot

Kohii is a Discord bot designed to enhance your study sessions with AI-powered assistance, Pomodoro timers, and productivity features. Perfect for students and learners who want to stay focused and get help when needed.

## Features

### Study Assistance

- **AI Chat**: Chat with an llm for help with homework, explanations, and study guidance
  - Multiple response styles (concise, detailed, technical, etc.)
  - Maintains conversation context for follow-up questions
  - Perfect for getting quick answers or detailed explanations
- **Pomodoro**: Manage study sessions with customizable timers
  - Start/stop/skip study and break phases
  - Track your study session history
  - Stay focused with timed intervals

### Productivity Tools

- **Chat Logs**: Keep track of important discussions and study group conversations
- **Auto Responses**: Set up automatic replies for common questions or fun moments
- **Avatar**: Quick access to user profile pictures
- **Coffee Collection**: Card collection system to reward study breaks (in progress)

## Setup

### Prerequisites

- Python 3.8+
- MongoDB (optional, for persistent storage)
- Discord Bot Token
- Google API Key (for Gemini AI features)
- Required Python packages (listed in `requirements.txt`)

### Installation

#### Option 1: Traditional Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/KohiiTM/KohiiDiscordBot.git
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
   GOOGLE_API=your_google_api_key
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

### Study Commands

- **/ask_kohii**: Start a chat session with the AI assistant

  - Ask questions about any subject
  - Get explanations in different styles
  - Continue the conversation with follow-up questions
  - Type 'stop session' to end the chat

- **/start**: Begin a Pomodoro study session
- **/stop**: End the current study session
- **/skip**: Move to the next phase of your study session
- **/session_history**: Review your past study sessions

### Utility Commands

- **/ping**: Check the bot's response time
- **/restart**: Restart the bot (admin only)
- **/shutdown**: Gracefully shut down the bot (owner only)
- **/avatar**: Get a user's profile picture
- **/collect**: Get a random coffee card (study break reward)
- **/my_cards**: View your coffee card collection
- **/trade**: Trade coffee cards with other users

## Development

### Project Structure

```
kohii/
├── bot/                # Main bot code
│   ├── cogs/          # Bot command modules
│   │   ├── gemini.py  # AI chat functionality
│   │   ├── pomodoro.py # Study timer features
│   │   └── ...        # Other features
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
