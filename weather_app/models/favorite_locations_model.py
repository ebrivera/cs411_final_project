import logging
from typing import List
from dataclasses import asdict, dataclass
''
from sqlalchemy.exc import IntegrityError
from weather_app import db
from weather_app.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class FavoriteLocations(db.Model):
    """
    This class represents a user's favorite locations
    """
    __tablename__ = 'favorite_locations'

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_name: str = db.Column(db.String(100), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'location_name', name='user_location_uc'),)
    """
    A class to manage a list of favorite locations.

    Attributes:
        id (int): The ID of the user associated with the favorite locations.
        location_ids (List[int]): A list of IDs representing the user's favorite locations.
    """

    def __post_init__(self):
        """
        Validates the logic of a new favorite location
        """
        if not self.location_name:
            raise ValueError("Location name cannot be empty.")

    ##################################################
    # Locationa Management Functions
    ##################################################
    @classmethod
    def add_favorite(cls, user_id: int, location_name: str) -> None:
        """
        Adds a favorite location for a user.

        Args:
            user_id (int): The user's ID.
            location_name (str): The location to add.

        Raises:
            ValueError: If the location is already a favorite.
        """

        logger.info("Adding favorite location '%s' for user_id %d", location_name, user_id)
        favorite = cls(user_id=user_id, location_name=location_name)
        try:
            db.session.add(favorite)
            db.session.commit()
            logger.info("Successfully added favorite location '%s' for user_id %d", location_name, user_id)
        except IntegrityError:
            db.session.rollback()
            logger.error("Location '%s' already exists for user_id %d", location_name, user_id)
            raise ValueError(f"Location '{location_name}' is already a favorite.")
        except Exception as e:
            db.session.rollback()
            logger.error("Error adding favorite location '%s': %s", location_name, str(e))
            raise ValueError(f"Error adding favorite location: {str(e)}")

    @classmethod
    def get_favorites(cls, user_id: int) -> List[dict[str, Any]]:
        """
        Retrieves all favorite locations for a user.

        Args:
            user_id (int): The user's ID.

        Returns:
            List[dict[str, Any]]: List of favorite locations as dictionaries.
        """
        logger.info("Fetching favorite locations for user_id %d", user_id)
        favorites = cls.query.filter_by(user_id=user_id).all()
        if not favorites:
            logger.info("No favorite locations found for user_id %d", user_id)
            return []
        return [{'id': fav.id, 'location_name': fav.location_name} for fav in favorites]
    
    @classmethod
    def delete_favorite(cls, user_id: int, location_name: str) -> None:
        """
        Deletes a favorite location for a user.

        Args:
            user_id (int): The user's ID.
            location_name (str): The location to delete.

        Raises:
            ValueError: If the location is not found.
        """
        logger.info("Deleting favorite location '%s' for user_id %d", location_name, user_id)
        favorite = cls.query.filter_by(user_id=user_id, location_name=location_name).first()
        if not favorite:
            logger.error("Location '%s' not found for user_id %d", location_name, user_id)
            raise ValueError(f"Location '{location_name}' not found.")
        db.session.delete(favorite)
        db.session.commit()
        logger.info("Successfully deleted favorite location '%s' for user_id %d", location_name, user_id)

    @classmethod
    def get_favorite_by_id(cls, favorite_id: int) -> dict[str, Any]:
        """
        Retrieves a favorite location by its ID.

        Args:
            favorite_id (int): The ID of the favorite location.

        Returns:
            dict[str, Any]: The favorite location data.

        Raises:
            ValueError: If the favorite location is not found.
        """
        logger.info("Fetching favorite location by ID: %d", favorite_id)
        favorite = cls.query.filter_by(id=favorite_id).first()
        if not favorite:
            logger.error("Favorite location with ID %d not found", favorite_id)
            raise ValueError(f"Favorite location with ID {favorite_id} not found.")
        return asdict(favorite)
    
    ##################################################
    # Weather API Integration
    ##################################################

    @classmethod
    def get_weather_for_favorite(cls, location_name: str, weather_client: Any) -> dict[str, Any]:
        """
        Retrieves the weather data for a favorite location.

        Args:
            location_name (str): The name of the location.
            weather_client (WeatherClient): The weather client to use.

        Returns:
            dict[str, Any]: The weather data for the location.
        """
        return {}