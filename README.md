# A-Lister

A-Lister (working title) is a online 'to-watch' list keeper. A-Lister is a flask python app supported by a postgreSQL database, hosted on [github](https://github.com/davebdev/project02) and using heroku to deploy at [https://enigmatic-caverns-29903.herokuapp.com/](https://enigmatic-caverns-29903.herokuapp.com/). A-Lister uses an API developed at [The Movie DB](https://www.themoviedb.org/documentation/api) to supply all the movie data.

This has been created for Unit 2 of the General Assembly Software Engineering intensive (remote flex), cohort 08. This unit has been my first foray into Python.

## Database design

My approach to this app was to first try to get an understanding of the way the database would be structured. In tandem with this, I tried to come up with some wireframes for the pages that would appear, which solidified the user flow through the app, and also allowed me to amend the database structure to work with my intentions for the app, all before I'd written a single line of code. This approach meant I could properly size the scope of this project and remove a few extra things that I knew I wouldn't have time for in the week I had to build it. Some of the extra features I was hoping to incorporate were:
    - allowing users to 'follow' each other's lists/user pages
    - creating a search for public facing lists
    - a dynamic search bar which filtered results as the user types

The below diagram shows the simple structure of the database:

![a lister database structure](static/img/project02_db_structure.png)


## Wireframes

The following images are basic wireframes built to both illustrate function and page structure, but also serves as a user journey through the app.

### Sign up

![sign up wireframe](static/img/1_sign_up.jpeg)

### Login

![login wireframe](static/img/2_login.jpeg)

### Empty homepage (no lists)

![user homepage without lists wireframe](static/img/3_user_homepage_w_o_lists.jpeg)

### Create new list

![new list page wireframe](static/img/4_new_list_page.jpeg)

### Empty new list

![empty new list wireframe](static/img/5_empty_new_list.jpeg)

### Search for new movies to add

![search for new movies wireframe](static/img/6_search_for_new_movies.jpeg)

### User homepage (logged in) with several lists

![user homepage with lists wireframe](static/img/8_user_homepage_w_lists.jpeg)

### User homepage (not logged in), public facing

![user homepage public view wireframe](static/img/9_user_page_public_view.jpeg)