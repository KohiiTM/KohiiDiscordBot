@echo off
echo ========================================
echo Discord Bot Migration - Export Script
echo ========================================
echo.

echo Step 1: Stopping current container...
docker-compose down

echo.
echo Step 2: Creating backup directory...
if not exist "migration_backup" mkdir migration_backup

echo.
echo Step 3: Backing up important data...
copy "bot\swear_counts.json" "migration_backup\swear_counts.json" >nul 2>&1
copy ".env" "migration_backup\.env" >nul 2>&1
echo Data backed up to migration_backup folder

echo.
echo Step 4: Creating archive of entire project...
powershell Compress-Archive -Path "." -DestinationPath "kohii-bot-migration.zip" -Force

echo.
echo Step 5: Exporting Docker image (optional)...
docker save kohii-bot:latest -o kohii-bot-image.tar

echo.
echo ========================================
echo Export Complete!
echo ========================================
echo.
echo Files created:
echo - kohii-bot-migration.zip (complete project)
echo - kohii-bot-image.tar (docker image)
echo - migration_backup\ folder (important data)
echo.
echo Transfer these files to your new PC.
echo.
pause