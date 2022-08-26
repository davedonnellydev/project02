from flask import Flask, render_template, request, redirect, session
import os
import service
import datetime
# from re import search

SECRET_KEY = os.environ.get('SECRET_KEY', 'b2d3de63a3d45dc05e53d717e8074103')

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)

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
    # referer = request.referrer
    # root = request.root_url
    # # needs a regex for user/username/list/number or user/username
    # substring = 'user'
    # if root and (search(substring, referer)):
    #     previous_path = referer.replace(root,"",1)
    # else:
    previous_path = None
    if 'message' in session:
        message = session['message']
        session.pop('message')
    else:
        message = None
    if user:
        username = user['username']
        return redirect(f"/user/{username}")
    else:
        return render_template("login.html", user=user, username=username, previous_path=previous_path, message=message)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    user_data = service.authenticate_user(username)
    # previous_path = request.form.get('previous_path')
    # print(previous_path)
    if user_data['rowCount'] == 0:
        print("Username not found")
        session['message'] = "Username not found"
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
            # if previous_path != 'None':
            #     return redirect(f"/{previous_path}")
            # else:
            return redirect(f"/user/{username}")
        else:
            print("Password denied")
            session['message'] = "Password incorrect"
            return redirect("/login")


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
    if user:
        if user['username'] == userpage:
            list_of_lists = service.get_user_list_data(userpage)
        else:
            list_of_lists = service.get_pub_user_list_data(userpage)
    else:
        list_of_lists = service.get_pub_user_list_data(userpage)
    path = request.path
    return render_template('userhome.html', user=user, userpage=userpage, query=query, results=results, list_of_lists=list_of_lists, path=path)


@app.route('/add_movie', methods=['POST'])
def add_movie():
    movie_list = request.form.getlist('movie_id')
    lists = request.form.getlist('lists')
    user_page = request.form.get('userpage')
    list_id = request.form.get('list_id')
    for list_id in lists:
        for movie_id in movie_list:
            error = service.add_movie_to_list(list_id,movie_id)
            print(error)
    return redirect(f'user/{user_page}/list/{list_id}')


@app.route('/new_list', methods=['POST'])
def new_list():
    user = service.get_session_data()
    return render_template('new_list.html', user=user)

@app.route('/create_list', methods=['POST'])
def create_list():
    list_name = request.form.get('list_name')
    form_private = request.form.get('private')
    if form_private:
        private = 't'
    else:
        private = 'f'
    user_id = session['user_id']
    username = session['username']
    service.create_new_list(user_id,list_name,private)
    return redirect(f'/user/{username}')

@app.route('/user/<userpage>/list/<list_id>', methods=['GET', 'POST'])
def display_list(userpage,list_id):
    user = service.get_session_data()
    query = request.args.get('query')
    searchAgain = request.args.get('searchAgain')
    sort = request.args.get('sort')
    if query:
        results = service.movie_search(query)
    else:
        results = None
    edit = request.args.get('edit')
    if user:
        list_of_lists = service.get_user_list_data(userpage)
    else:
        list_of_lists = service.get_pub_user_list_data(userpage)
    list_data = service.get_list_data(list_id)
    list_items = service.get_list_items(list_id)
    if sort == 'alphabetical':
        list_items.sort(key=service.alphabetical)
    elif sort == 'releaseDate':
        list_items.sort(key=service.released)
    else:
        list_items.sort(key=service.addedToList)
    if 'multi' in session:
        multi = session['multi']
    else:
        multi = 'no'
    path = request.path
    if list_data[0][3] == True:
        if user:
            if user['username'] == userpage:
                return render_template('userhome.html', user=user, userpage=userpage, query=query, results=results, list_of_lists=list_of_lists, list_id=list_id, list_items=list_items, list_data=list_data, edit=edit, multi=multi,path=path, searchAgain=searchAgain)
            else:
                return render_template('list_private.html', user=user,path=path)
        else:
            return render_template('list_private.html', user=user,path=path)
    else:
        return render_template('userhome.html', user=user, userpage=userpage, query=query, results=results, list_of_lists=list_of_lists, list_id=list_id, list_items=list_items, list_data=list_data, edit=edit, multi=multi,path=path, searchAgain=searchAgain)




@app.route('/select_multiple', methods=['POST'])
def select_multiple():
    userpage = request.form.get('userpage')
    list_id = request.form.get('list_id')
    session['multi'] = 'yes'
    return redirect(f'/user/{userpage}/list/{list_id}')

@app.route('/cancel_multiple_select', methods=['POST'])
def cancel_multiple_select():
    userpage = request.form.get('userpage')
    list_id = request.form.get('list_id')
    session['multi'] = 'no'
    return redirect(f'/user/{userpage}/list/{list_id}')



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


@app.route('/delete_multiple', methods=['POST'])
def delete_multiple():
    user = service.get_session_data()
    username = user['username']
    list_item_ids = request.form.getlist('list_item_id')
    list_id = request.form.get('list_id')
    for id in list_item_ids:
        service.delete_item(id)
    session['multi'] = 'no'
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
    print(watched_date)
    rating = request.form.get('rating')
    notes = request.form.get('notes')
    service.update_list_item(watched_date, rating, notes, list_item_id)
    return redirect(f"user/{username}/list/{list_id}")

@app.route('/settings', methods=['GET','POST'])
def settings():
    user = service.get_session_data()
    if 'message' in session:
        message = session['message']
        session.pop('message')
    else:
        message = None
    return render_template('settings.html', user=user, message=message)

@app.route('/update_safe_settings', methods=['POST'])
def update_safe_settings():
    user_email = request.form.get('email')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    user_id = session['user_id']
    username = session['username']
    service.update_settings(user_email,fname,lname,user_id)
    session.clear()
    user_data = service.authenticate_user(username)
    session["user_id"] = user_data['results'][0][0]
    session["username"] = user_data['results'][0][1]
    session["user_email"] = user_data['results'][0][2]
    session["user_fname"] = user_data['results'][0][3]
    session["user_lname"] = user_data['results'][0][4]
    return redirect("/settings")

@app.route('/update_password', methods=['POST'])
def update_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    user_id = session['user_id']
    username = session['username']

    password_check = service.authenticate_user(username)
    db_password = password_check['results'][0][5]
    if service.check_password(old_password, db_password):
        print("Password accepted")
        new_hashed_password = service.encrypt_password(new_password)
        print(new_hashed_password)
        service.change_password(new_hashed_password,user_id)
        session['message'] = "Password updated"
        return redirect(f"/settings")
    else:
        print("Password denied")
        session['message'] = "Password does not match"
        return redirect(f"/settings")


@app.route('/edit_list/<list_id>', methods=['GET', 'POST'])
def edit_list(list_id):
    user = service.get_session_data()
    list_data = service.get_list_data(list_id)
    return render_template('edit_list.html', user=user, list_data=list_data)

@app.route('/update_list', methods=['POST'])
def update_list():
    list_id = request.form.get('list_id')
    list_name = request.form.get('list_name')
    form_private = request.form.get('private')
    if form_private:
        private = 't'
    else:
        private = 'f'
    username = session['username']
    service.update_list_data(list_name,private,list_id)
    return redirect(f"user/{username}/list/{list_id}")

@app.route('/delete_list', methods=['POST'])
def delete_list():
    list_id = request.form.get('list_id')
    items = service.get_list_items(list_id)
    for item in items:
        service.delete_item(item[0])
    service.delete_list(list_id)
    username = session['username']
    return redirect(f'/user/{username}')


if __name__ == '__main__':
    app.run(debug=True)