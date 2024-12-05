#!/bin/bash

# Ensure the db folder exists
mkdir -p "$(dirname "$DB_PATH")"

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    # Drop and recreate the tables
    sqlite3 "$DB_PATH" < "$SQL_CREATE_TABLE_PATH"
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    # Create the database for the first time
    sqlite3 "$DB_PATH" < "$SQL_CREATE_TABLE_PATH"
    echo "Database created successfully."
fi