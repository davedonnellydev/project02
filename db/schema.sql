CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE lists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    list_name TEXT NOT NULL,
    priv BOOLEAN
);

CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    lists_id INTEGER REFERENCES lists(id),
    api_movie_id INTEGER NOT NULL,
    imdb_id TEXT NOT NULL,
    watched BOOLEAN,
    rating INTEGER,
    notes TEXT
    );