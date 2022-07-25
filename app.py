from flask import Flask, render_template, request, redirect, session
import os
import psycopg2
import service

SECRET_KEY = os.environ.get('SECRET_KEY', 'b2d3de63a3d45dc05e53d717e8074103')

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return redirect(f"/user/{username}")
    else:
        username = None
    return render_template('index.html', username=username)

@app.route('/signup')
def signup():
    if 'userExists' in session:
        userExists = session['userExists']
    else:
        userExists = False
    if 'emailExists' in session:
        emailExists = session['emailExists']
    else:
        emailExists = False
    return render_template('signup.html', userExists=userExists, emailExists=emailExists)

@app.route('/check_new_user', methods=['POST'])
def check_new_user():
    username = request.form.get('username')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    checkUser = service.check_user(email, username)
    session['userExists'] = False
    session['emailExists'] = False
    if checkUser['userCount'] > 0 or checkUser['emailCount'] > 0:
        if checkUser['userCount'] > 0:
            session['userExists'] = True
        if checkUser['emailCount'] > 0:
            session['emailExists'] = False
        return redirect('/signup')
    else:
        hashed_password = service.encrypt_password(password)
        service.create_new_user(username,fname,lname,email,hashed_password)
        return render_template('login.html', username=username)

@app.route('/login')
def login():
    if 'username' in session:
        username = session["username"]
        return redirect(f"/user/{username}")
    else:
        username = None
        return render_template("login.html", username=username)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    db_password_results = service.authenticate_user(username)
    if db_password_results['rowCount'] == 0:
        print("Username not found")
        return redirect("/login")
    else:
        db_password = db_password_results['pwResults'][0][0]
        if service.check_password(password, db_password):
            print("Password accepted")
            session["username"] = username
            session["user_id"] = db_password_results['pwResults'][0][1]
            return redirect(f"/user/{username}")
        else:
            print("Password denied")
            return redirect("/")

@app.route('/user/<userpage>')
def user_page(userpage):
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
    else:
        username = None
    query = request.args.get('query')
    if query:
        results = service.movie_search(query)
    else:
        results = None
    list_of_lists = service.get_list_data(userpage)
    return render_template('userhome.html', username=username, userpage=userpage, query=query, results=results, list_of_lists=list_of_lists)


@app.route('/add_movie', methods=['POST'])
def add_movie():
    movie_list = request.form.getlist('movie_id')
    lists = request.form.getlist('lists')
    user_page = request.form.get('userpage')
    for list_id in lists:
        for movie_id in movie_list:
            error = service.add_movie_to_list(list_id,movie_id)
            print(error)
    return redirect(f'user/{user_page}')


@app.route('/new_list', methods=['POST'])
def new_list():
    return render_template('new_list.html')

@app.route('/create_list', methods=['POST'])
def create_list():
    list_name = request.form.get('list_name')
    private = request.form.get('private')
    user_id = session['user_id']
    username = session['username']
    service.create_new_list(user_id,list_name,private)
    return redirect(f'/user/{username}')

@app.route('/user/<userpage>/list/<list_id>', methods=['GET', 'POST'])
def display_list(userpage,list_id):
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
    else:
        username = None
    query = request.args.get('query')
    if query:
        results = service.movie_search(query)
    else:
        results = None
    list_of_lists = service.get_list_data(userpage)
    list_items = service.get_list_items(list_id)
    return render_template('userhome.html', username=username, userpage=userpage, query=query, results=results, list_of_lists=list_of_lists, list_id=list_id, list_items=list_items)

if __name__ == '__main__':
    app.run(debug=True)