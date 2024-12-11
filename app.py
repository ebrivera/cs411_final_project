from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
import logging

from weather_app import db
from weather_app.models import favorite_locations_model
from weather_app.models.user_model import User
from weather_app.utils.sql_utils import check_database_connection, check_table_exists
from weather_app.utils.weather_client import WeatherClient


# Load environment variables from .env file
load_dotenv()
def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
            db.create_all()  # Recreate all tables

    ####################################################
    #
    # Healthchecks
    #
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)


    @app.route('/api/db-check', methods=['GET'])
    def db_check() -> Response:
        """
        Route to check if the database connection and songs table are functional.

        Returns:
            JSON response indicating the database health status.
        Raises:
            404 error if there is an issue with the database.
        """
        try:
            app.logger.info("Checking database connection...")
            check_database_connection()
            app.logger.info("Database connection is OK.")
            app.logger.info("Checking if songs table exists...")
            check_table_exists("favorite_locations")
            app.logger.info("Favorite_locations table exists.")
            app.logger.info("Checking if users table exists")
            check_table_exists("users")
            app.logger.info("Users table exists")
            app.logger.info("Checking if favorite_locations table exists")
            check_table_exists("favorite_locations")
            app.logger.info("Favorite_locations table exists")
            return make_response(jsonify({'database_status': 'healthy'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 404)


    ##########################################################
    #
    # Favorite Locations Management
    #
    ##########################################################

    @app.route('/api/add-favorite', methods=['POST'])
    def add_location() -> Response:
        """
        Route to add a new location to favorite locations.

        Expected JSON Input:
            - location_name (str): the location's name
            - user_id (int): The user ID .

        Returns:
            JSON response indicating the success of the location addition.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the location to the favorites.
        """
        app.logger.info('Adding a new location to favorites')
        try:
            data = request.get_json()

            user_id = data.get('user_id')
            location_name = data.get('location_name')

            if not user_id or not location_name:
                app.logger.error('Invalid input: user_id and location_name are required')
                return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

            # Add the song to the playlist
            app.logger.info('Adding location:', location_name)
            favorite_locations_model.FavoriteLocations.add_favorite(user_id=user_id,location_name=location_name)
            app.logger.info("Location added to favorites: ", location_name)
            return make_response(jsonify({'status': 'success', 'location': location_name}), 201)
        except Exception as e:
            app.logger.error("Failed to add location: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/delete-favorite/<int:user_id>/<string:location_name>', methods=['DELETE'])
    def delete_location(user_id: int, location_name: str) -> Response:
        """
        Route to delete a location by its name.

        Path Parameter:
            - user_id (int): The ID of the user.
            - location_name (str): The name of the location to delete

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info(f"Deleting location by name: {location_name}")
            favorite_locations_model.FavoriteLocations.delete_favorite(user_id=user_id,location_name=location_name)
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Errorw deleting location: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/get-favorites', methods=['GET'])
    def get_all_favorites() -> Response:
        """
        Route to retrieve all favorites for specific user,

        Query Parameter:

        Returns:
            JSON response with the list of songs or error message.
        """
        try:
            user_id = request.args.get("user_id")
            if not user_id:
                app.logger.error("Invalid input: 'user_id' is required.")
                
            app.logger.info("Retrieving all favorites from the user's favorites")
            locations = favorite_locations_model.FavoriteLocations.get_favorites(user_id=user_id)
            return make_response(jsonify({'status': 'success', 'locations': locations}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving locations: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/get-favorite-by-id', methods=['GET'])
    def get_favorite_by_ID(location_id: int) -> Response:
        """
        Route to retrieve a location by its ID.

        Path Parameter:
            - location_id (int): The ID of the location.

        Returns:
            JSON response with the location weather or error message.
        """
        try:
            app.logger.info(f"Retrieving weather at location: {location_id}")
            weather = favorite_locations_model.FavoriteLocations.get_favorite_by_id(location_id, WeatherClient())
            return make_response(jsonify({'status': 'success', 'song': weather}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving location by ID: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-weather-for-favorite', methods=['GET'])
    def get_weather_for_favorite(location_name) -> Response:
        """
        Route to retrieve the weather at a specific location by its name.

        Path Parameter:
            - location_name (str): The name of the desired location

        Returns:
            JSON response with the song details or error message.
        """
        try:
            weather_client = WeatherClient()
            app.logger.info(f"Retrieving weather by location name: {location_name}")
            weather = favorite_locations_model.FavoriteLocations.get_weather_for_favorite(location_name, weather_client)
            return make_response(jsonify({'status': 'success', 'Weather at desired location': weather}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving weather at location by name: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        

    @app.route('/api/get-all-favorites-with-weather', methods=['GET'])

    def get_weather_for_favorites() -> Response:
        """
        Route to retrieve weather information for all favorite locations of a user.

        Expected JSON Input:
            - user_id (int): The ID of the user.

        Returns:
            JSON response with the list of favorite locations and their weather data.
        """
        try:
            user_id = request.args.get("user_id")
            if not user_id:
                app.logger.error("Invalid input: 'user_id' is required.")

            app.logger.info("Fetching weather data for all favorite locations for user_id %d", user_id)

            # Assuming you have an initialized WeatherClient instance (e.g., weather_client)
            from weather_app.utils.weather_client import WeatherClient  # Import your weather client utility
            weather_client = WeatherClient()

            locations_with_weather = favorite_locations_model.FavoriteLocations.get_all_favorites_with_weather(user_id, weather_client)
            return make_response(jsonify({'status': 'success', 'locations': locations_with_weather}), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving weather data for favorites: {e}")
            return make_response(jsonify({'error': str(e)}), 500)
        

    ############################################################
    #
    # User Management
    #
    ############################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the user.
            - password (str): The password for the user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue creating the user.
        """
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                app.logger.error("Invalid input: 'username' and 'password' are required.")
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            app.logger.info(f"Creating user: {username}")
            User.create_user(username, password)
            app.logger.info(f"User created successfully: {username}")
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        
        except Exception as e:
            app.logger.error(f"Error creating user: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        try: 
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                    app.logger.error("Invalid login payload.")
                    raise BadRequest("Both username and password are required.")
            
            if User.check_password(username, password):
                    user_id = User.get_id_by_username(username)
                    app.logger.info(f"User '{username}' logged in successfully")
                    return make_response(jsonify({'status': 'success', 'message': 'Login successful', 'user_id': user_id}), 200)
            else:
                app.logger.warning(f"Invalid login attempt for username '{username}'")
                return make_response(jsonify({'status': 'error', 'error': 'Invalid username or password'}), 401)
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500




    @app.route('/api/update-password', methods=['PUT'])
    def update_password() -> Response:
        """
        Route to remove a location from the user's favorite locations.

        Path Parameter:
            - username (str): User's username.

        Returns:
            JSON response indicating the success of the password update.
        """
        try:
            data = request.get_json()
            username = data.get('username')
            old_password = data.get('old_password')
            new_password = data.get('new_password')

            if not username or not old_password or not new_password:
                app.logger.error("Invalid input: 'username', 'old_password', and 'new_password' are required.")
                raise BadRequest("All fields ('username', 'old_password', 'new_password') are required.")

            # Verify current password
            if not User.check_password(username=username, password=old_password):
                app.logger.warning(f"Password mismatch for user '{username}'.")
                raise Unauthorized("Current password is incorrect.")

            # Update password
            User.update_password(username=username, new_password=new_password)
            app.logger.info(f"Password updated successfully for user '{username}'.")

            return make_response(jsonify({'status': 'success', 'message': 'Password updated successfully'}), 200)
        except Exception as e:
            app.logger.error(f"Error updating password: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)