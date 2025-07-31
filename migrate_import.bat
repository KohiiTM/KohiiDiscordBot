@echo off
echo ========================================
echo Discord Bot Migration - Import Script
echo ========================================
echo.

echo This script should be run on the NEW PC after transferring files.
echo.
echo Prerequisites check:
echo - Docker Desktop installed? (Y/N)
set /p docker_ready="> "
if /i "%docker_ready%" neq "Y" (
    echo Please install Docker Desktop first, then run this script again.
    pause
    exit /b 1
)

echo.
echo Step 1: Extracting project files...
if exist "kohii-bot-migration.zip" (
    powershell Expand-Archive -Path "kohii-bot-migration.zip" -DestinationPath "." -Force
    echo Project files extracted successfully.
) else (
    echo kohii-bot-migration.zip not found in current directory.
    echo Please ensure you've copied the migration files here.
    pause
    exit /b 1
)

echo.
echo Step 2: Restoring data files...
if exist "migration_backup\.env" (
    copy "migration_backup\.env" ".env" >nul 2>&1
    echo Environment file restored.
) else (
    echo WARNING: .env file not found. You'll need to create it manually.
)

if exist "migration_backup\swear_counts.json" (
    copy "migration_backup\swear_counts.json" "bot\swear_counts.json" >nul 2>&1
    echo Swear counts data restored.
)

echo.
echo Step 3: Building and starting the bot...
docker-compose up --build -d

echo.
echo Step 4: Checking if bot started successfully...
timeout /t 10 /nobreak >nul
docker-compose ps

echo.
echo Step 5: Showing recent logs...
docker-compose logs --tail=20

echo.
echo ========================================
echo Import Complete!
echo ========================================
echo.
echo Your bot should now be running on this PC.
echo Check Discord to verify it's online.
echo.
echo Useful commands:
echo - docker-compose logs : View all logs
echo - docker-compose down : Stop the bot
echo - docker-compose up -d : Start the bot
echo.
pause