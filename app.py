from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'user_db'

# Secure session management configurations
app.config['SECRET_KEY'] = 'f3d2b5e36c1c4d0e8c7eeb9f5db6c1e1a5e9f8d9d2a6e3b1a7c4d3f1e2b2a5c6' # Needed for session management
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents access to cookie via JavaScript
app.config['SESSION_COOKIE_SECURE'] = True    # Cookies are only sent over HTTPS
app.config['SESSION_PERMANENT'] = False        # Set to True if you want persistent sessions
app.config['REMEMBER_COOKIE_SECURE'] = True    # Secure remember me cookies

mysql = MySQL(app)


@app.after_request
def apply_security_headers(response):
    # Prevents browsers from MIME-sniffing a response away from the declared content type.
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Protects against clickjacking by disallowing the page to be displayed in a frame or iframe.
    response.headers["X-Frame-Options"] = "DENY"
    
    # Controls the amount of referrer information that is passed when navigating away from the site.
    response.headers["Referrer-Policy"] = "no-referrer"
    
    # Sets a Content Security Policy to restrict resource loading to the same origin.
    response.headers["X-Content-Security-Policy"] = "default-src 'self'"
    
    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"  
    
    # HSTS tell browsers to always connect to your site using HTTPS, which prevents downgrade attacks.
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['signup-email']
    password = request.form['signup-password']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        mysql.connection.commit()
        flash('User created successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Email already exists or an error occurred!', 'danger')
    finally:
        cur.close()
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return render_template('login_signup.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['login-email']
    password = request.form['login-password']
    
    # Predefined admin credentials
    admin_email = "admin@gmail.com"
    admin_password = "admin"  # Replace with your actual admin password

    if email == admin_email and password == admin_password:
        return redirect(url_for('admin'))  # Redirect to admin dashboard

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()

    if user:
        hashed_password = user[2]  # Assuming user[2] is the hashed password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):  # Ensure hashed_password is encoded
            return redirect(url_for('index'))  # Redirect to user dashboard
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login_page'))
    else:
        flash('Invalid email or password!', 'danger')
        return redirect(url_for('login_page'))
        
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/log_activity', methods=['POST'])
def log_activity():
    data = request.get_json()
    activityType = data['activityType']
    duration = data['duration']
    calories = data['calories']
    date = data['date']
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO activities (activityType, duration, calories, date) VALUES (%s, %s, %s, %s)",
                (activityType, duration, calories, date))
    mysql.connection.commit()
    cur.close()
    return jsonify(message='Activity logged successfully!')

@app.route('/get_log_history', methods=['GET'])
def get_log_history():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM activities")
    activities = cur.fetchall()
    cur.close()
    
    return jsonify(activities=[{'id': activity[0], 'activityType': activity[1], 'duration': activity[2], 'calories': activity[3], 'date': activity[4]} for activity in activities])

@app.route('/delete_activity/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM activities WHERE id = %s", (activity_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify(message='Activity deleted successfully!')

@app.route('/get_users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, email, password FROM users")
    users = cur.fetchall()
    cur.close()

    return jsonify([{'id': user[0], 'email': user[1], 'password': user[2]} for user in users])

@app.route('/get_activities', methods=['GET'])
def get_activities():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, activityType, duration, calories, date FROM activities")
    activities = cur.fetchall()
    cur.close()

    return jsonify([{'id': activity[0], 'activityType': activity[1], 'duration': activity[2], 'calories': activity[3], 'date': activity[4]} for activity in activities])

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify(message='User deleted successfully!')
    return jsonify(message='Activity deleted successfully!')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    email = data['email']
    password = data['password']

    try:
        # Hash the new password if provided
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET email=%s, password=%s WHERE id=%s", (email, hashed_password, user_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify(message='User updated successfully!'), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify(message='Error updating user: ' + str(e)), 400

@app.route('/update_activity/<int:activity_id>', methods=['PUT'])
def update_activity(activity_id):
    data = request.get_json()
    activityType = data['activityType']
    duration = data['duration']
    calories = data['calories']
    date = data['date']
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE activities SET activityType=%s, duration=%s, calories=%s, date=%s WHERE id=%s",
                (activityType, duration, calories, date, activity_id))
    mysql.connection.commit()
    cur.close()
    
    return jsonify(message='Activity updated successfully!')
    
    if user:
        return redirect(url_for('index'))  # Redirect to user dashboard
    else:
        flash('Invalid email or password!', 'danger')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()  # Clear user session
    return redirect(url_for('home'))  # Redirect to login_signup.html

if __name__ == '__main__':
    app.run(
        host="0.0.0.0", 
        port=5000,
        debug=True, 
        ssl_context=("certificate.crt", "certificate.key")
    )
