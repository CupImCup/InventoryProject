#!/bin/bash

# ------------------------------------------------------------------------------
# Script to run the Refactor_Inventory_Project.exe with logging and error handling
# ------------------------------------------------------------------------------

# Unfortunately atm this is of no use, as we have problems with connecting the local database with the .exe


# Configure these variables
EXE_PATH="/c/Users/anton/Programming/Inventory_exe/dist/Refactor_Inventory_Project/Refactor_Inventory_Project.exe"  # UPDATE THIS
LOG_FILE="/c/Users/anton/Programming/Inventory_exe/Logs/inventory.log"  # UPDATE THIS (e.g., ~/inventory.log)

# Create log directory if missing
mkdir -p "$(dirname "$LOG_FILE")"

# Log execution time and run .exe
echo "--------------------------------------------------" >> "$LOG_FILE"
echo "$(date +'%Y-%m-%d %H:%M:%S') - Starting inventory app" >> "$LOG_FILE"
echo "--------------------------------------------------" >> "$LOG_FILE"

# Run the executable and log output/errors
"$EXE_PATH" >> "$LOG_FILE" 2>&1

# Check exit status
EXIT_STATUS=$?
if [ $EXIT_STATUS -eq 0 ]; then
    echo "$(date +'%H:%M:%S') - Program exited successfully" >> "$LOG_FILE"
else
    echo "$(date +'%H:%M:%S') - ERROR: Program crashed with exit code $EXIT_STATUS" >> "$LOG_FILE"
fi