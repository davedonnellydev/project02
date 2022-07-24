import os
import psycopg2
import bcrypt
import requests
import creds

salt = bcrypt.gensalt()

local_apikey = creds.api_key

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=movie_list')
API_KEY = os.environ.get('API_KEY', local_apikey)

def test():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    connection.close()

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
    cur.execute('SELECT password, id FROM users WHERE username = %s;', [username])
    results = cur.fetchall()
    db_password = dict()
    db_password['rowCount'] = cur.rowcount
    db_password['pwResults'] = results
    return db_password