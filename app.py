from flask import Flask
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=food_truck')
SECRET_KEY = os.environ.get('SECRET_KEY', 'b2d3de63a3d45dc05e53d717e8074103')

@app.route('/')
def index():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    connection.close()
    return '<p>Hey, it works!</p>'

if __name__ == '__main__':
    app.run(debug=True)