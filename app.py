from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mysqldb import MySQL
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt
import re
import time
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# Secure session management configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') # Needed for session management
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents access to cookie via JavaScript
app.config['SESSION_COOKIE_SECURE'] = True    # Cookies are only sent over HTTPS
app.config['SESSION_PERMANENT'] = False        # Set to True if you want persistent sessions
app.config['REMEMBER_COOKIE_SECURE'] = True    # Secure remember me cookies

mysql = MySQL(app)


# DOS Limit
# "200 per hour" → each IP can make 200 requests per hour.
# "50 per minute" → each IP can make 50 requests per minute.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"]
)

limiter.init_app(app)


@app.after_request
def apply_security_headers(response):
    # Prevents browsers from MIME-sniffing a response away from the declared content type.
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Protects against clickjacking by disallowing the page to be displayed in a frame or iframe.
    response.headers["X-Frame-Options"] = "DENY"
    
    # Controls the amount of referrer information that is passed when navigating away from the site.
    response.headers["Referrer-Policy"] = "no-referrer"
    
    # Sets a Content Security Policy to restrict resource loading to the same origin.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https:; "
        "style-src 'self' 'unsafe-inline' https:; "
        "img-src 'self' data: https:; "
        "font-src 'self' https: data:;"
    )
    
    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"  
    
    # HSTS tell browsers to always connect to your site using HTTPS, which prevents downgrade attacks.
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

@app.route('/')
def home():
    return render_template('main.html')


# SIGNUP ROUTE (Rate limited)
# This route allows only 5 signup requests per minute per IP.
# It protects against spam accounts and brute-force attacks.
@app.route('/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    # Honeypot Anti-Spam
    honeypot = request.form.get('robot_test')
    if honeypot and honeypot.strip() != "":
        flash("Spam detected!", "danger")
        return redirect(url_for('login_page'))

    # Timestamp Anti-Bot (bots submit instantly)
    try:
        form_time = float(request.form.get("form_time", "0"))
    except:
        form_time = 0

    if time.time() - form_time < 2:  # less than 2 sec = bot
        flash("Bot behavior detected!", "danger")
        return redirect(url_for('login_page'))

    # Validate email
    email = request.form.get("email")
    password = request.form.get("signup-password")


    email_pattern = r"^[A-Za-z0-9_-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,4}$"
    if not re.match(email_pattern, email):
        flash("Invalid email format!", "danger")
        return redirect(url_for('login_page'))


    # Strong password validation
    password_pattern = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    if not re.match(password_pattern, password):
        flash("Password must be at least 8 characters, include 1 uppercase, 1 number, and 1 special character!", "danger")
        return redirect(url_for('login_page'))

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Save to database
    # All database operations use parameterized queries (%s placeholders), which prevents SQL injection attacks.
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, hashed_password)
        )
        mysql.connection.commit()
        flash('User created successfully!', 'success')

    except Exception:
        mysql.connection.rollback()
        flash('Email already exists or an error occurred!', 'danger')

    finally:
        cur.close()

    return redirect(url_for('login_page'))


@app.route('/login')
def login_page():
    return render_template('login_signup.html', time=time)



# LOGIN ROUTE (Rate limited)
# Allows only 5 login attempts per minute per IP.
# Prevents brute-force attacks and password guessing.
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit to prevent brute-force attacks
def login():
     
    # Validate email 
    email = request.form.get("email")
    password = request.form.get("login-password") 

    email_pattern = r"^[A-Za-z0-9_-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,4}$"
    if not re.match(email_pattern, email):
        flash("Invalid email format!", "danger")
        return redirect(url_for('login_page'))


    # SECURE ADMIN LOGIN
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH").encode()  # bcrypt hash from .env

    # Check if the login is for admin
    if email == admin_email and bcrypt.checkpw(password.encode('utf-8'), admin_password_hash):
        session['admin_logged_in'] = True  # << Set admin session
        flash("Admin logged in successfully!", "success")
        return redirect(url_for('admin'))  # Redirect to admin dashboard

    # CHECK USER IN DATABASE
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()

 
    # IF USER EMAIL EXISTS
    if user:
        stored_hash = user[2]  # Stored hashed password from DB

        # Verify password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            # LOGIN SUCCESS: set user session
            session['user_id'] = user[0]  # Track logged-in user by ID
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))  # Redirect to user dashboard
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login_page'))


    # EMAIL DOES NOT EXIST
    flash('Invalid email or password!', 'danger')
    return redirect(url_for('login_page'))


        
@app.route('/index')
def index():
    if not session.get('user_id'):  # If user is NOT logged in
        flash("Please log in first!", "danger")
        return redirect(url_for('login_page'))

    return render_template('index.html')  # If logged in → allow access



# ACTIVITY LOGGING ROUTE (Rate limited)

# Allows up to 20 activity log requests per minute per IP.
# Prevents attackers from spamming your database.
@app.route('/log_activity', methods=['POST'])
@limiter.limit("20 per minute")
def log_activity():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify(message="Unauthorized"), 401

    data = request.get_json()

    activityType = data['activityType']
    duration = data['duration']
    calories = data['calories']
    date = data['date']

    user_id = session['user_id']   # <-- IMPORTANT

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO activities (activityType, duration, calories, date, user_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (activityType, duration, calories, date, user_id)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify(message='Activity logged successfully!')


@app.route('/get_log_history', methods=['GET'])
def get_log_history():
    # 1. Check if the user is logged in
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]  # Logged-in user ID

    cur = mysql.connection.cursor()

    # 2. Return ONLY this user's activities
    query = """
        SELECT id, activityType, duration, calories, date
        FROM activities
        WHERE user_id = %s
        ORDER BY date DESC
    """

    cur.execute(query, (user_id,))
    activities = cur.fetchall()
    cur.close()

    return jsonify(activities=[
        {
            'id': a[0], 
            'activityType': a[1],
            'duration': a[2],
            'calories': a[3],
            'date': a[4]
        } for a in activities
    ])


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

    query = """
        SELECT 
            activities.id,
            users.email,
            activities.activityType,
            activities.duration,
            activities.calories,
            activities.date
        FROM activities
        LEFT JOIN users ON activities.user_id = users.id
        ORDER BY activities.id DESC
    """

    cur.execute(query)
    activities = cur.fetchall()
    cur.close()

    return jsonify([
        {
            'id': a[0],
            'email': a[1],
            'activityType': a[2],
            'duration': a[3],
            'calories': a[4],
            'date': a[5]
        }
        for a in activities
    ])


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
    # Check if admin is logged in
    if not session.get('admin_logged_in'):
        flash("You must be logged in as admin!", "danger")
        return redirect(url_for('login_page'))  # Redirect to login page
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

@app.route('/stats')
def get_stats():
    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM activities")
    total_activities = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(calories), 0) FROM activities")
    total_calories = cur.fetchone()[0]

    # Fetch all activity types with counts
    cur.execute("""
        SELECT activityType, COUNT(*) AS cnt
        FROM activities
        GROUP BY activityType
        ORDER BY cnt DESC
    """)
    results = cur.fetchall()

    # Handle cases
    if not results:
        most_common_activity = "No activities"
    else:
        highest_count = results[0][1]

        if highest_count == 1:
            most_common_activity = "No repeated activity types"
        else:
            most_common_activity = results[0][0]

    cur.close()

    return jsonify({
        "total_users": total_users,
        "total_activities": total_activities,
        "total_calories": total_calories,
        "most_common_activity": most_common_activity
    })



if __name__ == '__main__':
    app.run(
        host="0.0.0.0", 
        port=5000,
        debug=True, 
        ssl_context=("certificate.crt", "certificate.key")
    )
