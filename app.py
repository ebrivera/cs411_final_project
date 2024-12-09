from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request

from weather_app.models import favorite_locations_model
from weather_app.models import user_model
from weather_app.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)



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
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Add the song to the playlist
        app.logger.info('Adding location:', location_name)
        favorite_locations_model.FavoriteLocations.add_favorite(user_id=user_id,location_name=location_name)
        app.logger.info("Location added to favorites: ", location_name)
        return make_response(jsonify({'status': 'success', 'location': location_name}), 201)
    except Exception as e:
        app.logger.error("Failed to add location: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/delete-favorite/<str:user_id>', methods=['DELETE'])
def delete_location(location_name: str) -> Response:
    """
    Route to delete a location by its name.

    Path Parameter:
        - user_id (int): The ID of the user.
        - location_name (str): The name of the location to delete

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        app.logger.info(f"Deleting location by name: {location_name}")
        favorite_locations_model.FavoriteLocations.delete_favorite(user_id=user_id,location_name=location_name)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error deleting location: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-favorites', methods=['GET'])
def get_all_favorites() -> Response:
    """
    Route to retrieve all songs in the catalog (non-deleted), with an option to sort by play count.

    Query Parameter:
        - sort_by_play_count (bool, optional): If true, sort songs by play count.

    Returns:
        JSON response with the list of songs or error message.
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        app.logger.info("Retrieving all favorites from the user's favorites")
        locations = favorite_locations_model.FavoriteLocations.get_favorites(user_id=user_id)
        return make_response(jsonify({'status': 'success', 'locations': locations}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving locations: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-favorite-by-id', methods=['GET'])
def get_favorite_by_ID(location_id: int) -> Response:
    """
    Route to retrieve a song by its ID.

    Path Parameter:
        - song_id (int): The ID of the song.

    Returns:
        JSON response with the song details or error message.
    """
    try:
        app.logger.info(f"Retrieving song by ID: {location_id}")
        location = favorite_locations_model.FavoriteLocations.get_favorite_by_id(location_id)
        return make_response(jsonify({'status': 'success', 'song': location}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving song by ID: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


############################################################
#
# User Management
#
############################################################

@app.route('/api/create-user', methods=['POST'])
def create_user(username, password) -> Response:
    """
    Route to add a song to the playlist by compound key (artist, title, year).

    Expected JSON Input:
        - artist (str): The artist's name.
        - title (str): The song title.
        - year (int): The year the song was released.

    Returns:
        JSON response indicating success of the addition or error message.
    """
    try:

        if not password or not username:
            return make_response(jsonify({'error': 'Invalid input. Username and password are required.'}), 400)

        user = user_model.User.create_user(username=username, password=password)


        app.logger.info(f"User created: {user}")
        return make_response(jsonify({'status': 'success', 'message': 'User created'}), 201)

    except Exception as e:
        app.logger.error(f"Error creating user: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/check-password', methods=['GET'])
def check_pass(username, password) -> Response:
    """
    Route to remove a song from the playlist by compound key (artist, title, year).

    Expected JSON Input:
        - artist (str): The artist's name.
        - title (str): The song title.
        - year (int): The year the song was released.

    Returns:
        JSON response indicating success of the removal or error message.
    """
    try:

        if not username or not password:
            return make_response(jsonify({'error': 'Invalid input. Username and password are required.'}), 400)

        password2 = user_model.User.check_password(username=username, password=password)
        if password2==password:
            app.logger.info(f"Passwords checked: {password} and {password2})")
            return make_response(jsonify({'status': 'success', 'message': 'Passwords match."'}), 200)

    except Exception as e:
        app.logger.error(f"Error checking password: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-id-by-username', methods=['GET'])
def get_id_by_user(username) -> Response:
    """
    Route to remove a song from the playlist by track number.

    Path Parameter:
        - track_number (int): The track number of the song to remove.

    Returns:
        JSON response indicating success of the removal or an error message.
    """
    try:
        app.logger.info(f"Getting ID for uername: {username}")

        ID = user_model.User.get_id_by_username(username=username)

        return make_response(jsonify({'status': 'success', 'message': f'ID for user {username} is {ID}'}), 200)

    except ValueError as e:
        app.logger.error(f"Error getting ID for user {username}: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error geting ID for user: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/update-password', methods=['POST'])
def update_password(user,password,newpass) -> Response:
    """
    Route to clear all songs from the playlist.

    Returns:
        JSON response indicating success of the operation or an error message.
    """
    try:
        app.logger.info('Updating password')
        if user_model.User.check_password(username=user, password=password) == True:
            user_model.User.update_password(username=user, new_password=newpass)
            return make_response(jsonify({'status': 'success', 'message': f'Password changed for {user}'}), 200)

    except Exception as e:
        app.logger.error(f"Error clearing the playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
