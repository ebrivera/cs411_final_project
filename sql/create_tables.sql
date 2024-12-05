DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS favorite_locations;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    salt TEXT NOT NULL
);

CREATE TABLE favorite_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    location_name TEXT NOT NULL,
    UNIQUE(user_id, location_name),
    FOREIGN KEY (user_id) REFERENCES users(id)
);