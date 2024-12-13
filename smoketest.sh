#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

###############################################
#
# Database Reset Function
#
###############################################

reset_database() {
  echo "Resetting the database..."
  
  # Debug: Display the current values of DB_PATH and SQL_CREATE_TABLE_PATH
  echo "DB_PATH is: $DB_PATH"
  echo "SQL_CREATE_TABLE_PATH is: $SQL_CREATE_TABLE_PATH"
  
  # Check if the database file exists and remove it
  if [ -f "$DB_PATH" ]; then
    rm "$DB_PATH"
    echo "Existing database file removed."
  fi
  
  # Recreate the database
  if [ -f "$SQL_CREATE_TABLE_PATH" ]; then
    sqlite3 "$DB_PATH" < "$SQL_CREATE_TABLE_PATH"
    if [ $? -eq 0 ]; then
      echo "Database created successfully."
    else
      echo "Error: Failed to create database."
      exit 1
    fi
  else
    echo "Error: SQL_CREATE_TABLE_PATH does not exist."
    exit 1
  fi
  
  echo "Database reset successfully."
  
  # Restart Flask app to reload the database
  echo "Restarting Flask app..."
  pkill -f "python app.py"  # Stop any running Flask app
  nohup python app.py &>/dev/null &  # Start Flask app in the background
  sleep 3  # Wait for Flask app to restart
  echo "Flask app restarted."
}

###############################################
#
# Command-line Arguments
#
###############################################

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Reset the database
reset_database

###############################################
#
# Helper Function
#
###############################################

fail() {
  echo "$1"
  exit 1
}

###############################################
#
# Health Checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"' || fail "Health check failed."
  echo "Service is healthy."
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"' || fail "Database connection failed."
  echo "Database connection is healthy."
}

##########################################################
#
# User Management Tests
#
##########################################################

create_user() {
  echo "Creating a user..."
  response=$(curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "password123"}')

  echo "$response" | grep -q '"status": "user added"' || fail "Failed to create user. Response: $response"
  echo "User created successfully."
}

login_user() {
  echo "Logging in a user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "password123"}')

  echo "$response" | grep -q '"status": "success"' || fail "Failed to log in user. Response: $response"
  echo "User logged in successfully."
}

update_password() {
  echo "Updating password..."
  response=$(curl -s -X PUT "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d '{"username": "testuser", "old_password": "password123", "new_password": "newpassword123"}')

  echo "$response" | grep -q '"status": "success"' || fail "Failed to update password. Response: $response"
  echo "Password updated successfully."
}

##########################################################
#
# Favorite Locations Tests
#
##########################################################

add_favorite_location() {
  echo "Adding a favorite location..."
  response=$(curl -s -X POST "$BASE_URL/add-favorite" -H "Content-Type: application/json" \
    -d '{"user_id": 1, "location_name": "Boston"}')

  echo "$response" | grep -q '"status": "success"' || fail "Failed to add favorite location. Response: $response"
  echo "Favorite location added successfully."
}

get_favorite_locations() {
  echo "Getting favorite locations..."
  response=$(curl -s -X GET "$BASE_URL/get-favorites?user_id=1")

  echo "$response" | grep -q '"status": "success"' || fail "Failed to get favorite locations. Response: $response"
  echo "Favorite locations retrieved successfully."
}

delete_favorite_location() {
  echo "Deleting a favorite location..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-favorite/1/Boston")

  echo "$response" | grep -q '"status": "success"' || fail "Failed to delete favorite location. Response: $response"
  echo "Favorite location deleted successfully."
}

##########################################################
#
# Weather Integration Tests
#
##########################################################

get_weather_for_favorite() {
  echo "Getting weather for a favorite location..."
  response=$(curl -s -X GET "$BASE_URL/get-weather-for-favorite?location_name=Boston")

  echo "$response" | grep -q '"status": "success"' || fail "Failed to get weather for favorite location. Response: $response"
  echo "Weather for favorite location retrieved successfully."
}

get_all_favorites_with_weather() {
  echo "Getting weather for all favorite locations..."
  response=$(curl -s -X GET "$BASE_URL/get-all-favorites-with-weather?user_id=1")

  echo "$response" | grep -q '"status": "success"' || fail "Failed to get weather for all favorite locations. Response: $response"
  echo "Weather for all favorite locations retrieved successfully."
}

###############################################
#
# Run Tests
#
###############################################

check_health
check_db

# User Management Tests
create_user
login_user
update_password

# Favorite Locations Tests
add_favorite_location
get_favorite_locations
delete_favorite_location

# Weather Integration Tests
add_favorite_location
get_weather_for_favorite
get_all_favorites_with_weather

echo "All smoketests passed successfully!"
