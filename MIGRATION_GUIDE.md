# Discord Bot Migration Guide

This guide will help you move your Discord bot from one PC to another.

## Method 1: Automated Migration (Recommended)

### On the Current PC:

1. **Run the export script:**
   ```bash
   migrate_export.bat
   ```
   This will:
   - Stop the current container
   - Backup important data (.env, swear_counts.json)
   - Create a complete project archive
   - Export the Docker image (optional)

2. **Transfer files to new PC:**
   - Copy `kohii-bot-migration.zip` to the new PC
   - Copy `migration_backup` folder to the new PC
   - (Optional) Copy `kohii-bot-image.tar` if you want to use the existing image

### On the New PC:

1. **Install prerequisites:**
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Make sure Docker is running

2. **Prepare the directory:**
   - Create a new folder for the bot
   - Copy the migration files into this folder

3. **Run the import script:**
   ```bash
   migrate_import.bat
   ```
   This will:
   - Extract the project files
   - Restore your data and environment variables
   - Build and start the bot container

## Method 2: Manual Migration

### Step 1: Prepare Current System
```bash
# Stop the bot
docker-compose down

# Backup important files
mkdir migration_backup
copy bot\swear_counts.json migration_backup\
copy .env migration_backup\
```

### Step 2: Transfer Project
Copy the entire project folder to the new PC, including:
- All source code
- docker-compose.yml
- Dockerfile
- requirements.txt
- .env file (handle securely)
- bot/swear_counts.json (user data)

### Step 3: Setup on New PC
```bash
# Install Docker Desktop first, then:

# Navigate to project directory
cd path\to\kohii

# Build and start
docker-compose up --build -d

# Check status
docker-compose ps
docker-compose logs
```

## Method 3: Using Docker Image Export

### Export (Current PC):
```bash
docker-compose down
docker save kohii-bot:latest -o kohii-bot.tar
```

### Import (New PC):
```bash
docker load -i kohii-bot.tar
# Then copy project files and run docker-compose up -d
```

## Important Notes

### Environment Variables (.env file)
Make sure your `.env` file contains:
```
DISCORD_TOKEN=your_discord_bot_token
GOOGLE_API=your_google_api_key
MONGO_USERNAME=your_mongo_username (if using MongoDB)
MONGO_PASSWORD=your_mongo_password (if using MongoDB)
TENOR_API_KEY=your_tenor_api_key (if using auto responses)
```

### Data Persistence
- `swear_counts.json` - Contains all user swear word counts
- Volume mounts ensure data persists between container restarts
- Make sure to backup these files before migration

### Troubleshooting

**Bot shows as offline:**
- Check if Docker container is running: `docker-compose ps`
- Check logs: `docker-compose logs`
- Verify .env file has correct Discord token

**Commands not working:**
- Bot may need time to sync slash commands
- Check logs for any cog loading errors
- Verify all dependencies installed correctly

**Missing data:**
- Ensure swear_counts.json was copied to bot/ directory
- Check file permissions

### Useful Commands

```bash
# View logs
docker-compose logs

# Restart bot
docker-compose restart

# Stop bot
docker-compose down

# Start bot
docker-compose up -d

# Rebuild if code changes
docker-compose up --build -d

# View running containers
docker ps
```

## Security Considerations

1. **Never commit .env files** to version control
2. **Transfer .env securely** (encrypted channels, secure file transfer)
3. **Regenerate tokens** if security is compromised
4. **Backup regularly** to prevent data loss

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify Docker is running properly
3. Ensure all required files were transferred
4. Check Discord Developer Portal for bot status