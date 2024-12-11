import pytest
from weather_app.models.favorite_locations_model import FavoriteLocations
from weather_app.models.user_model import User
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def sample_user():
    return {
        "username": "testuser",
        "password": "securepassword123"
    }

@pytest.fixture
def sample_favorite_location():
    return {
        "user_id": 1,  # This should correspond to a valid user created in the test
        "location_name": "Boston"
    }

##########################################################
# Adding Favorite Locations
##########################################################

def test_add_favorite_location(session, sample_user, sample_favorite_location):
    """Test adding a favorite location for a user."""
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    favorite = session.query(FavoriteLocations).filter_by(user_id=sample_favorite_location["user_id"]).first()
    assert favorite is not None, "Favorite location should be created in the database."
    assert favorite.location_name == sample_favorite_location["location_name"], "Location name should match the input."

def test_add_duplicate_favorite_location(session, sample_user, sample_favorite_location):
    """Test adding a duplicate favorite location."""
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    with pytest.raises(ValueError, match=f"Location '{sample_favorite_location['location_name']}' is already a favorite."):
        FavoriteLocations.add_favorite(**sample_favorite_location)

def test_add_favorite_location_non_existent_user(session, sample_favorite_location):
    """Test adding a favorite location for a non-existent user."""
    with pytest.raises(IntegrityError):  # Expect a database integrity error
        FavoriteLocations.add_favorite(**sample_favorite_location)

##########################################################
# Retrieving Favorite Locations
##########################################################

def test_get_favorites(session, sample_user, sample_favorite_location):
    """Test retrieving all favorite locations for a user."""
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    favorites = FavoriteLocations.get_favorites(user_id=sample_favorite_location["user_id"])
    assert len(favorites) == 1, "There should be one favorite location."
    assert favorites[0]["location_name"] == sample_favorite_location["location_name"], "Location name should match the input."

def test_get_favorites_empty(session, sample_user):
    """Test retrieving favorites when no favorites exist for a user."""
    User.create_user(**sample_user)
    favorites = FavoriteLocations.get_favorites(user_id=1)
    assert favorites == [], "Favorites should be empty for a new user."

##########################################################
# Deleting Favorite Locations
##########################################################

def test_delete_favorite_location(session, sample_user, sample_favorite_location):
    """Test deleting a favorite location."""
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    FavoriteLocations.delete_favorite(user_id=sample_favorite_location["user_id"], location_name=sample_favorite_location["location_name"])
    favorites = FavoriteLocations.get_favorites(user_id=sample_favorite_location["user_id"])
    assert len(favorites) == 0, "Favorite location should be deleted."

def test_delete_non_existent_favorite_location(session, sample_user, sample_favorite_location):
    """Test deleting a non-existent favorite location."""
    User.create_user(**sample_user)
    with pytest.raises(ValueError, match=f"Location '{sample_favorite_location['location_name']}' not found."):
        FavoriteLocations.delete_favorite(user_id=sample_favorite_location["user_id"], location_name=sample_favorite_location["location_name"])

##########################################################
# Weather Integration
##########################################################

@pytest.fixture
def mock_weather_client(mocker):
    """Fixture to provide a mock weather client."""
    client = mocker.Mock()
    client.get_weather.return_value = {"temp": 72, "description": "Sunny"}
    client.get_hourly_forecast.return_value = {"hourly": [{"hour": 1, "temp": 70}, {"hour": 2, "temp": 68}]}
    client.get_date_forecast.return_value = {"date": "2024-12-11", "temp": 65, "description": "Cloudy"}
    return client

def test_get_weather_for_favorite(session, sample_user, sample_favorite_location, mock_weather_client):
    """Test retrieving weather for a favorite location."""
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    mock_weather_client.get_weather.return_value = {"temp": 72, "description": "Sunny"}

    weather = FavoriteLocations.get_weather_for_favorite(
    location_name=sample_favorite_location["location_name"],
    weather_client=mock_weather_client
    )
    assert weather == {"temp": 72, "description": "Sunny"}, "Weather data should match the mocked data."

def test_get_all_favorites_with_weather(session, sample_user, sample_favorite_location, mock_weather_client):
    """Test retrieving all favorites with weather data."""
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    favorites_with_weather = FavoriteLocations.get_all_favorites_with_weather(
        user_id=sample_favorite_location["user_id"],
        weather_client=mock_weather_client
    )
    assert len(favorites_with_weather) == 1, "There should be one favorite location with weather data."
    assert "weather" in favorites_with_weather[0], "Weather data should be included in the response."
    assert favorites_with_weather[0]["weather"] == {"temp": 72, "description": "Sunny"}, "Weather data should match the mocked data."
