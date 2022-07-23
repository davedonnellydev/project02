import os
import psycopg2
import bcrypt

salt = bcrypt.gensalt()

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=movie_list')

def test():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    connection.close()



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