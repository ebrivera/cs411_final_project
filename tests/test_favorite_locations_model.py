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
def test_add_favorite_location(session, sample_user, sample_favorite_location):
    """Test adding a favorite location for a user."""
    # Create a user first
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    # Verify the favorite location exists in the database
    favorite = session.query(FavoriteLocations).filter_by(user_id=sample_favorite_location["user_id"]).first()
    assert favorite is not None, "Favorite location should be created in the database."
    assert favorite.location_name == sample_favorite_location["location_name"], "Location name should match the input."

def test_add_duplicate_favorite_location(session, sample_user, sample_favorite_location):
    """Test adding a duplicate favorite location."""
    User.create_user(**sample_user)
    FavoriteLocations.add_favorite(**sample_favorite_location)

    with pytest.raises(ValueError, match=f"Location '{sample_favorite_location['location_name']}' is already a favorite."):
        FavoriteLocations.add_favorite(**sample_favorite_location)

# def test_add_favorite_location_non_existent_user(session, sample_favorite_location):
#     """Test adding a favorite location for a non-existent user."""
#     with pytest.raises(IntegrityError):  # Expect a database integrity error
#         FavoriteLocations.add_favorite(**sample_favorite_location)