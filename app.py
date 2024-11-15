from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime
import bcrypt  # Importing bcrypt for password hashing
#pip install Flask
#pip install mysql-connector-python
#pip install bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to keep sessions secure

# Database connection function
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",  # MySQL host
        user="root",       # MySQL user
        password="Database2024",  # MySQL password
        database="ticketwave"  # Your database name
    )
    return connection

# Route for the home page
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')  # Encoding password for comparison
        
        # Connect to the database to verify user credentials
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            stored_password = user['password'].encode('utf-8')  # Fetching the hashed password from DB
            if bcrypt.checkpw(password, stored_password):  # Verify password
                # Store the user's info in session after successful login
                session['user'] = user['first_name']  # Storing the first name for greeting
                return redirect('/homepage')
            else:
                return "Invalid login credentials. Please try again."
        else:
            return "User not found. Please sign up."
        
        return redirect('/')

    return render_template('login.html')

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        dob = request.form['dob']
        password = request.form['password'].encode('utf-8')  # Encoding password for hashing
        role = request.form['purpose']
        Created_date = datetime.today()
        Update_date = datetime.today()
        # Hash the password with bcrypt
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Insert the new user into the database with the hashed password
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (first_name, last_name, email, dob, role, Created_date, Update_date, password) VALUES (%s, %s, %s, %s,%s, %s, %s, %s)",
                       (first_name, last_name, email, dob, role, Created_date, Update_date, hashed_password.decode('utf-8')))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect('/login')  # Redirect to login page after signup

    return render_template('signup.html')

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        # Fetch upcoming events and new events from the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch upcoming events (dummy query, modify based on your schema)
        cursor.execute("SELECT * FROM events WHERE event_date > CURDATE() ORDER BY event_date ASC LIMIT 3")
        upcoming_events = cursor.fetchall()

        # Fetch new events (dummy query, modify based on your schema)
        cursor.execute("SELECT * FROM events ORDER BY event_date ASC LIMIT 3")
        new_events = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('dashboard.html', user=session['user'], events=upcoming_events, new_events=new_events)
    else:
        return redirect('/login')

# Route for profile update (if needed)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' in session:
        if request.method == 'POST':
            # Handle profile update here (e.g., update user information in the database)
            pass

        return render_template('profile.html', user=session['user'])
    else:
        return redirect('/login')

# Route to logout the user
@app.route('/logout')
def logout():
    session.pop('user', None)  # Clear the session
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
