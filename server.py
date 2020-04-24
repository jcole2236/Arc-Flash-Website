from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt   
from datetime import datetime
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "gandalf"
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/forum")
def forum():
    if 'user_id' in session:
        mysql = connectToMySQL('forum_dash_db')
        query = "SELECT users.first_name, users.last_name, thoughts.id, thoughts.user_id, thoughts.content, thoughts.created_at FROM thoughts JOIN users ON users.id = thoughts.user_id ORDER BY thoughts.created_at DESC;"
        data = {
            'user': session['user_id'],
        }
        thoughts = mysql.query_db(query, data)
        return render_template("dashboard.html", thoughts=thoughts)
    else:
        return render_template("forum.html")

@app.route("/register", methods=["POST"])
def register_user():
    is_valid = True
    
    if len(request.form['first_name']) < 2:
        is_valid = False
        flash("First name must be at least 2 characters long")
    if len(request.form['last_name']) < 2:
        is_valid = False
        flash("Last name must be at least 2 characters long")
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Password must be at least 8 characters long")
    if request.form['c_password'] != request.form['password']:
        is_valid = False
        flash("Passwords must match")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please use a valid email address")
    else:
        mysql = connectToMySQL('forum_dash_db')
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {
            'email': request.form['email']
        }
        user = mysql.query_db(query, data)
        if user:
            is_valid = False
            flash("Email address already in use")
    
    if is_valid:
        mysql = connectToMySQL('forum_dash_db')
        query = "INSERT into users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(email)s, %(pass)s, NOW(), NOW())"
        data = {
            'fn': request.form['first_name'],
            'ln': request.form['last_name'],
            'email': request.form['email'],
            'pass': bcrypt.generate_password_hash(request.form['password'])
        }
        user_id = mysql.query_db(query, data)
        session['user_id'] = user_id
        session['fname'] = request.form['first_name']
        session['lname'] = request.form['last_name']

        return redirect("/dashboard")
    else:
        return redirect("/forum")

@app.route("/login", methods=["POST"])
def login_user():
    is_valid = True
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter your email")
    if len(request.form['password']) < 1:
        is_valid = False
        flash("Please enter your password")
    
    if not is_valid:
        return redirect("/forum")
    else:
        mysql = connectToMySQL('forum_dash_db')
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {
            'email': request.form['email']
        }
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]['password']
            if bcrypt.check_password_hash(hashed_password, request.form['password']):
                session['user_id'] = user[0]['id']
                session['fname'] = user[0]['first_name']
                session['lname'] = user[0]['last_name']
                return redirect("/dashboard")
            else:
                flash("Password is invalid")
                return redirect("/forum")
        else:
            flash("Please use a valid email address")
            return redirect("/forum")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def success():
    if 'user_id' not in session:
        return redirect('/forum')


    mysql = connectToMySQL('forum_dash_db')
    query = "SELECT * FROM users WHERE users.id = %(id)s"
    data = {
        'id': session['user_id']
    }
    user = mysql.query_db(query, data)

    mysql = connectToMySQL('forum_dash_db')
    query = "SELECT thoughts.user_id, thoughts.id as thoughts_id, users.first_name, users.last_name, thoughts.content, thoughts.created_at, COUNT(thoughts_id) as times_liked FROM liked_thoughts RIGHT JOIN thoughts ON thoughts.id = liked_thoughts.thoughts_id JOIN users ON thoughts.user_id = users.id GROUP BY thoughts_id ORDER BY thoughts.created_at DESC;"
    thoughts = mysql.query_db(query, data)

    mysql = connectToMySQL('forum_dash_db')
    query = "SELECT * FROM liked_thoughts WHERE users_id = %(user_id)s"
    data = {
        'user_id': session['user_id']
    }
    liked_thoughts = [thought['thoughts_id'] for thought in mysql.query_db(query, data)]

    return render_template("dashboard.html", user=user[0], thoughts=thoughts)

@app.route("/dashboard/create", methods=['POST'])
def new_thought():
    if 'user_id' not in session:
        return redirect("/forum")
        
    is_valid = True
    if len(request.form['content']) < 6:
        is_valid = False
        flash('Thought must be more than 5 characters')
    if len(request.form['content']) >=255:
        is_valid = False
        flash('Thought cannot be more than 255 characters')
    
    if is_valid:
        mysql = connectToMySQL('forum_dash_db')
        query = "INSERT INTO thoughts (user_id, content, created_at, updated_at) VALUES (%(id)s, %(con)s, NOW(), NOW());"
        data = {
            'id': session['user_id'],
            'con': request.form['content'],
        }
        thought = mysql.query_db(query, data)
        print(thought)
    return redirect("/dashboard")

@app.route('/dashboard/<thoughts_id>')
def thought_details(thoughts_id):
    mysql = connectToMySQL('forum_dash_db')
    query = "SELECT users.first_name, users.last_name, thoughts.id, thoughts.user_id, thoughts.content FROM thoughts JOIN users ON users.id = thoughts.user_id WHERE thoughts.id = %(id)s;"
    data = {
        'id': thoughts_id
    }
    thought = mysql.query_db(query, data)

    mysql = connectToMySQL('forum_dash_db')
    query = "SELECT liked_thoughts.users_id, liked_thoughts.thoughts_id, users.first_name, users.last_name FROM liked_thoughts JOIN users ON users_id = users.id WHERE thoughts_id = %(id)s;"
    data = {
        'id': thoughts_id
    }
    liked_thought = mysql.query_db(query, data)
    return render_template("user_thought.html", this_thought=thought[0], liked_thought=liked_thought)

@app.route("/dashboard/<thought_id>/add_like")
def like_thought(thought_id):
    mysql = connectToMySQL('forum_dash_db')
    query = "INSERT INTO liked_thoughts (users_id, thoughts_id) VALUES (%(user_id)s, %(thought_id)s)"
    data = {
        'user_id': session['user_id'],
        'thought_id': thought_id
    }
    mysql.query_db(query, data)

    return redirect(f'/dashboard/{thought_id}')

@app.route("/dashboard/<thought_id>/unlike")
def unlike_thought(thought_id):
    mysql = connectToMySQL('forum_dash_db')
    query = "DELETE FROM liked_thoughts WHERE users_id = %(user_id)s AND thoughts_id = %(thought_id)s"
    data = {
        'user_id': session['user_id'],
        'thought_id': thought_id
    }
    mysql.query_db(query, data)

    return redirect(f'/dashboard/{thought_id}')

@app.route('/dashboard/<thoughts_id>/destroy')
def delete_thought(thoughts_id):
    mysql = connectToMySQL('forum_dash_db')
    query = "DELETE FROM liked_thoughts WHERE thoughts_id = %(thought_id)s;"
    data = {
        'thought_id': thoughts_id,
    }
    mysql.query_db(query, data)

    mysql = connectToMySQL('forum_dash_db')
    query = "DELETE FROM thoughts WHERE id = %(thought_id)s;"
    mysql.query_db(query, data)

    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)