DROP TABLE IF EXISTS list_items;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS lists;
DROP TABLE IF EXISTS users;


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
    tmdb_id INTEGER NOT NULL,
    imdb_id TEXT NOT NULL,
    title TEXT NOT NULL,
    release_date DATE,
    tagline TEXT,
    overview TEXT,
    runtime_in_min INTEGER,
    release_status TEXT,
    poster_url TEXT,
    user_count INTEGER
);

CREATE TABLE list_items (
    id SERIAL PRIMARY KEY,
    lists_id INTEGER NOT NULL REFERENCES lists(id),
    movie_id INTEGER NOT NULL REFERENCES movies(id),
    watched DATE,
    rating INTEGER,
    notes TEXT
    );