import os
import psycopg2
import bcrypt
import requests
from flask import session
from dotenv import load_dotenv


def configure():
    load_dotenv()

configure()

salt = bcrypt.gensalt()

local_apikey = os.getenv('api_key')

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=movie_list')
API_KEY = os.environ.get('API_KEY', local_apikey)

def check_user(email, username):
    check = {}
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    SELECT * FROM users WHERE username=%s;
    ''', [username])
    check['userCount'] = cur.rowcount
    cur.execute('''
    SELECT * FROM users WHERE email=%s;
    ''', [email])
    check['emailCount'] = cur.rowcount
    conn.close()
    return check

def encrypt_password(string):
    return bcrypt.hashpw(string.encode(), bcrypt.gensalt()).decode()

def create_new_user(username,fname,lname,email,password):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO users (username,email,fname,lname,password)
    VALUES(%s,%s,%s,%s,%s);
    ''', [username,email,fname,lname,password])
    conn.commit()
    conn.close()

def check_password(string, hashed_string):
    return bcrypt.checkpw(string.encode(), hashed_string.encode())


def authenticate_user(username):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = %s;', [username])
    results = cur.fetchall()
    user_data = dict()
    user_data['rowCount'] = cur.rowcount
    user_data['results'] = results
    return user_data

def get_session_data():
    user = dict()
    if 'username' in session:
        user['user_id'] = session['user_id']
        user['username'] = session['username']
        user['user_email'] = session['user_email']
        user['user_fname'] = session['user_fname']
        user['user_lname'] = session['user_lname']
    return user

def movie_search(query):
    params = {
        "api_key": local_apikey,
        "language": "en-US",
        "page": 1,
        "include_adult": "true",
        "query": query
    }
    response = requests.get("https://api.themoviedb.org/3/search/movie", params=params)
    result = response.json()
    return result

def get_movie_info(movie_id):
    params = {
        "api_key": local_apikey,
        "language": "en-US"
    }
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params=params)
    result = response.json()
    return result

def create_new_list(user_id,list_name,private):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO lists (user_id,list_name,priv)
    VALUES(%s,%s,%s);
    ''', [user_id,list_name,private])
    conn.commit()
    conn.close()

def get_user_list_data(userpage):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE username = %s;', [userpage])
    result = cur.fetchall()
    user_id = result[0]
    cur.execute('SELECT * FROM lists WHERE user_id = %s;', [user_id])
    results = cur.fetchall()
    return results

def get_pub_user_list_data(userpage):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE username = %s;', [userpage])
    result = cur.fetchall()
    user_id = result[0]
    private = 'f'
    cur.execute('SELECT * FROM lists WHERE user_id = %s and priv=%s;', [user_id,private])
    results = cur.fetchall()
    return results

def get_list_data(list_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT * FROM lists WHERE id = %s;', [list_id])
    results = cur.fetchall()
    return results

def get_list_items(list_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT * FROM list_items l JOIN movies m ON l.movie_id=m.id WHERE lists_id = %s;', [list_id])
    results = cur.fetchall()
    return results

def add_movie_to_list(list_id,movie_id):
    error = ''
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT id FROM lists WHERE id=%s', [list_id])
    list_count = cur.rowcount
    cur.execute('SELECT id FROM movies WHERE tmdb_id=%s', [movie_id])
    movie_count = cur.rowcount
    if movie_count == 0:
        movie_data = get_movie_info(movie_id)
        print(movie_data['id'])
        cur.execute('''
        INSERT INTO movies (tmdb_id,imdb_id,title,release_date,tagline,overview,runtime_in_min,release_status,poster_url,user_count)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        ''', [movie_data['id'],movie_data['imdb_id'],movie_data['title'],movie_data['release_date'],movie_data['tagline'],movie_data['overview'],movie_data['runtime'],movie_data['status'],movie_data['poster_path'],1])
        conn.commit()
    if movie_count == 1:
        cur.execute('SELECT user_count FROM movies WHERE tmdb_id=%s', [movie_id])
        user_count = cur.fetchall()[0]
        updated_user_count = int(user_count[0]) + 1
        cur.execute('UPDATE movies SET user_count=%s WHERE tmdb_id=%s', [updated_user_count,movie_id])
        conn.commit()
    cur.execute('SELECT id FROM movies WHERE tmdb_id=%s', [movie_id])
    result = cur.fetchall()
    movie_db_id = result[0]
    cur.execute('SELECT id FROM list_items WHERE lists_id=%s and movie_id=%s', [list_id, movie_db_id])
    list_items_count = cur.rowcount
    if list_count == 1 and list_items_count == 0:
        cur.execute('''
        INSERT INTO list_items (lists_id,movie_id)
        VALUES(%s,%s);
        ''', [list_id,movie_db_id])
        conn.commit()
    else:
        error = 'List item already exists'
    conn.close()
    return error

def mark_as_watched(watched_date,list_item_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    UPDATE list_items
    SET watched=%s
    WHERE id=%s;
    ''', [watched_date,list_item_id])
    conn.commit()
    conn.close()

def delete_item(list_item_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    DELETE FROM list_items
    WHERE id=%s;
    ''', [list_item_id])
    conn.commit()
    conn.close()

def update_list_item(watched_date,rating,notes,list_item_id):
    if watched_date == '':
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
        UPDATE list_items
        SET rating=%s, notes=%s
        WHERE id=%s;
        ''', [rating,notes,list_item_id])
        conn.commit()
        conn.close()
    else:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
        UPDATE list_items
        SET watched=%s, rating=%s, notes=%s
        WHERE id=%s;
        ''', [watched_date,rating,notes,list_item_id])
        conn.commit()
        conn.close()

def update_settings(user_email,fname,lname,user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    UPDATE users
    SET email=%s, fname=%s, lname=%s
    WHERE id=%s;
    ''', [user_email,fname,lname,user_id])
    conn.commit()
    conn.close()

def change_password(new_hashed_password,user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    UPDATE users
    SET password=%s
    WHERE id=%s;
    ''', [new_hashed_password,user_id])
    conn.commit()
    conn.close()

def update_list_data(list_name,private,list_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    UPDATE lists
    SET list_name=%s, priv=%s
    WHERE id=%s;
    ''', [list_name,private,list_id])
    conn.commit()
    conn.close()

def delete_list(list_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('''
    DELETE FROM lists
    WHERE id=%s;
    ''', [list_id])
    conn.commit()
    conn.close()

def alphabetical(e):
    return e[9]

def addedToList(e):
    return e[0]

def released(e):
    return e[10]