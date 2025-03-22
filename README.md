# Kohii Discord Bot

Kohii is a versatile Discord bot designed to enhance your server with various features, including chat logging, Pomodoro sessions, auto-responses, and more.

## Features

- **Ping**: Check the bot's latency.
- **Restart**: Restart the bot (requires admin privileges).
- **Chat Logs**: Log and view chat messages.
- **Pomodoro**: Manage Pomodoro sessions for productivity.
- **Avatar**: Retrieve a user's profile picture.
- **Auto Responses**: Automatically respond to specific keywords.
- **Coffee Collection**: Collect and trade coffee-related cards.

## Setup

### Prerequisites

- Python 3.8+
- MongoDB
- Discord Bot Token
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/kohii.git
    cd kohii
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a [.env](http://_vscodecontentref_/0) file in the root directory and add your environment variables:

    ```env
    DISCORD_TOKEN=your_discord_token
    MONGO_USERNAME=your_mongo_username
    MONGO_PASSWORD=your_mongo_password
    ```

5. Run the bot:

    ```sh
    python bot/main.py
    ```

## Usage

### Commands

- **/ping**: Check the bot's latency.
- **/restart**: Restart the bot (admin only).
- **/shutdown**: Gracefully shut down the bot (owner only).
- **/start**: Start a new Pomodoro session.
- **/stop**: Stop the current Pomodoro session.
- **/skip**: Skip the current Pomodoro phase.
- **/session_history**: View your Pomodoro session history.
- **/avatar**: Retrieve a user's profile picture.
- **/collect**: Collect a random pair of coffee-related cards.
- **/my_cards**: View your collected coffee cards.
- **/trade**: Trade a coffee card with another user.
- **/clear_collection**: Clear all coffee cards from a user's collection (owner only).

### Event Listeners

- **on_message**: Log messages to MongoDB and handle auto-responses.
- **on_ready**: Log when the bot is ready and sync slash commands.
- **on_disconnect**: Close MongoDB connection when the bot disconnects.


## License

This project is licensed under the MIT License. See the [LICENSE](http://_vscodecontentref_/1) file for details.
