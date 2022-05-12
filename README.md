# Peewee
This directory contains the following Python apps:

- app.py
- diary.py
- students.py

## Motivation

Work with Flask and an ORM in Python to practice CRUD — storing, retrieving, updating and deleting information. 

### Installing

Simply activate the virtual environment which contains the associated packages (Flask, wtform, bcrypt)
Run the following command in terminal while in main directory:

    source ./bin/activate

### App

A social media application built with Flask. Contains a login and registration page. Users are stored in a local SQLite database. Password verification and form validation are enforced as well.

    Routes:
    - '/' index
    - '/login' login page
    - '/register' registration page

### Diary

This is a fun terminal application that allows a user to create and store notes in a database. Again I am using a local SQLite database for storage. A user can also delete and view notes that are stored in the database one by one.

### Students

A minimal Flask application. Running this file will create a local Students database and associated Student table. The table is populated with 5 student users and we simply log out the top student to the consule using the peewee ORM. 

**Built With**
- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/en/2.1.x/)
- [Peewee](http://docs.peewee-orm.com/en/latest/)
- [Jinja2](https://pypi.org/project/Jinja2/)
- [WTForms](https://wtforms.readthedocs.io/en/3.0.x/)