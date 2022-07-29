import psycopg2

conn = psycopg2.connect('dbname=movie_list')
cur = conn.cursor()
cur.execute('''
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

TRUNCATE users restart identity cascade;
TRUNCATE lists restart identity cascade;
TRUNCATE movies restart identity cascade;

INSERT INTO users(username,email,fname,lname,password) VALUES
('daveb','dave@ga.com','Dave','Buckley','$2b$12$GWwOl7kc3eAQW6gBa39LNOw11uIPm.4a2ex3BLTJ0ysu41aBZDYs6');
''')
conn.commit()
conn.close()