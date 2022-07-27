from flask import Flask, render_template, request, redirect, session
import os
import service

SECRET_KEY = os.environ.get('SECRET_KEY', 'b2d3de63a3d45dc05e53d717e8074103')

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

@app.route('/')
def index():
    user = service.get_session_data()
    if user:
        username = user['username']
        return redirect(f"/user/{username}")
    else:
        return redirect("/login")

@app.route('/signup')
def signup():
    user = service.get_session_data()
    if 'userExists' in session:
        userExists = session['userExists']
    else:
        userExists = False
    if 'emailExists' in session:
        emailExists = session['emailExists']
    else:
        emailExists = False
    return render_template('signup.html', userExists=userExists, emailExists=emailExists, user=user)

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
        return redirect(f'/login?username={username}')

@app.route('/login')
def login():
    user = service.get_session_data()
    username = request.args.get('username')
    return render_template("login.html", user=user, username=username)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    user_data = service.authenticate_user(username)
    if user_data['rowCount'] == 0:
        print("Username not found")
        return redirect("/login")
    else:
        db_password = user_data['results'][0][5]
        if service.check_password(password, db_password):
            print("Password accepted")
            session["user_id"] = user_data['results'][0][0]
            session["username"] = user_data['results'][0][1]
            session["user_email"] = user_data['results'][0][2]
            session["user_fname"] = user_data['results'][0][3]
            session["user_lname"] = user_data['results'][0][4]
            return redirect(f"/user/{username}")
        else:
            print("Password denied")
            return redirect("/")


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


@app.route('/user/<userpage>')
def user_page(userpage):
    user = service.get_session_data()
    query = request.args.get('query')
    if query:
        results = service.movie_search(query)
    else:
        results = None
    list_of_lists = service.get_list_data(userpage)
    return render_template('userhome.html', user=user, userpage=userpage, query=query, results=results, list_of_lists=list_of_lists)


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
    user = service.get_session_data()
    return render_template('new_list.html', user=user)

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
    user = service.get_session_data()
    query = request.args.get('query')
    if query:
        results = service.movie_search(query)
    else:
        results = None
    edit = request.args.get('edit')
    list_of_lists = service.get_list_data(userpage)
    list_items = service.get_list_items(list_id)
    return render_template('userhome.html', user=user, userpage=userpage, query=query, results=results, list_of_lists=list_of_lists, list_id=list_id, list_items=list_items, edit=edit)

@app.route('/watched', methods=['POST'])
def watched():
    user = service.get_session_data()
    username = user['username']
    watched_date = request.form.get('watched_date')
    list_item_id = request.form.get('list_item_id')
    list_id = request.form.get('list_id')
    service.mark_as_watched(watched_date,list_item_id)
    return redirect(f"user/{username}/list/{list_id}")

@app.route('/delete_single', methods=['POST'])
def delete_single():
    user = service.get_session_data()
    username = user['username']
    list_item_id = request.form.get('list_item_id')
    list_id = request.form.get('list_id')
    service.delete_item(list_item_id)
    return redirect(f"user/{username}/list/{list_id}")

@app.route('/edit_list_item', methods=['POST'])
def edit_list_item():
    user = service.get_session_data()
    username = user['username']
    list_item_id = request.form.get('list_item_id')
    list_id = request.form.get('list_id')
    return redirect(f"user/{username}/list/{list_id}?edit={list_item_id}")

@app.route('/confirm_edits', methods=['POST'])
def confirm_edits():
    user = service.get_session_data()
    username = user['username']
    list_item_id = request.form.get('list_item_id')
    list_id = request.form.get('list_id')
    watched_date = request.form.get('watched_date')
    rating = request.form.get('rating')
    notes = request.form.get('notes')
    service.update_list_item(watched_date, rating, notes, list_item_id)
    return redirect(f"user/{username}/list/{list_id}")


if __name__ == '__main__':
    app.run(debug=True)