# Weather App

Weather App is a Flask-based API that allows users to manage their favorite locations and retrieve weather data from these locations.
We are using the an external api (One Call API by OpenWeatherMap, the one outlined in the project example) for weather retrieval.
This App includes functionality for user management, weather retrieval, user login, and favorite location management.
The project is fully Dockerized and includes unit and smoke tests for quality assurance.

---

## Features

1. User Management
   - Create Users
   - Authenticate users with password verification
   - Update user passwords
2. Favorite Location Management:
   - Add, retrieve, and delete the favorite locations of a user
   - Retrieve weather data for the favorite locations of a user
3. API Health Checks:
   - Verify health with dedicated routes
4. Docker:
   - Fully containerized for easy deployment
5. Testing
   - Unit tests for `user_model.py`
   - Unit tests for `favorite_locations_model.py`
   - Smoke tests

---

## Routes

## 1. Health Checks

#### Route: `/api/health`

- Request Type: GET
- Purpose: Checks if the API service is running and operational
- Request Format: None
- Response Format: JSON
  ```json
  {
    "status": "healthy"
  }
  ```

#### Route: `/api/db-check`

- Request Type: GET
- Purpose: Verifies database connection and required tables exist
- Request Format: None
- Response Format: JSON
  ```json
  {
    "database_status": "healthy"
  }
  ```

### 2. User Management

#### Route: `/api/create-user`

- Request Type: POST
- Purpose: Creates a new user account
- Request Format: JSON
  ```json
  {
    "username": "newuser123",
    "password": "securepassword"
  }
  ```
- Response Format: JSON
  ```json
  {
    "status": "user added",
    "username": "newuser123"
  }
  ```

#### Route: `/api/login`

- Request Type: POST
- Purpose: Authenticates user credentials
- Request Format: JSON
  ```json
  {
    "username": "existinguser",
    "password": "userpassword"
  }
  ```
- Response Format: JSON
  ```json
  {
    "status": "success",
    "message": "Welcome, existinguser",
    "user_id": 123
  }
  ```

#### Route: `/api/update-password`

- Request Type: PUT
- Purpose: Updates user's password
- Request Format: JSON
  ```json
  {
    "username": "existinguser",
    "old_password": "currentpassword",
    "new_password": "newpassword"
  }
  ```
- Response Format: JSON
  ```json
  {
    "status": "success",
    "message": "Password updated successfully"
  }
  ```

### 3. Favorite Locations Management

#### Route: `/api/add-favorite`

- Request Type: POST
- Purpose: Adds a new location to user's favorites
- Request Format: JSON
  ```json
  {
    "user_id": 123,
    "location_name": "Boston, MA"
  }
  ```
- Response Format: JSON
  ```json
  {
    "status": "success",
    "location": "Boston, MA"
  }
  ```

#### Route: `/api/delete-favorite/<user_id>/<location_name>`

- Request Type: DELETE
- Purpose: Removes a location from user's favorites
- Request Format: Path Parameters
  - user_id: Integer
  - location_name: String
- Response Format: JSON
  ```json
  {
    "status": "success"
  }
  ```

#### Route: `/api/get-favorites`

- Request Type: GET
- Purpose: Retrieves all favorite locations for a user
- Request Format: Query Parameter
  - user_id: Integer
- Response Format: JSON
  ```json
  {
    "status": "success",
    "locations": ["Boston, MA", "New York, NY"]
  }
  ```

#### Route: `/api/get-all-favorites-with-weather`

- Request Type: GET
- Purpose: Retrieves weather information for all favorite locations of a user
- Request Format: Query Parameter
  - user_id: Integer
- Response Format: JSON
  ```json
  {
    "status": "success",
    "locations": [
      {
        "location_name": "Boston, MA",
        "weather_data": {
          "temperature": 72,
          "conditions": "sunny"
        }
      }
    ]
  }
  ```

---

## Project Structure

```
.
├── app.py
├── tests/
│   ├── test_favorite_locations_model.py
│   ├── test_random_utils.py
│   └── test_user_model.py
└── weather_app/
    ├── models/
    │   ├── favorite_locations_model.py
    │   └── user_model.py
    └── utils/
        ├── logger.py
        ├── random_utils.py
        ├── sql_utils.py
        └── weather_client.py
```

---

## Setup Instructions

1. Clone the repository
2. Create a `.env` file with the following template:
   ```
    DB_PATH=./db/weather_app.db
    SQL_CREATE_TABLE_PATH=./sql/create_tables.sql
    CREATE_DB=true
    API_KEY=<your api key here>
   ```
3. Build the Docker container:
   ```bash
   docker build -t weather-app .
   ```
4. Run the container:
   ```bash
   docker run -p 5000:5000 weather-app
   ```

---

## Testing

Run the tests using:

```bash
python -m pytest tests/
```
