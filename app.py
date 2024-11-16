from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime
import bcrypt  # Importing bcrypt for password hashing
#pip install Flask
#pip install mysql-connector-python
#pip install bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to keep sessions secure



from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



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

@app.route('/homepage')
@login_required
def homepage():
    user_role = session.get('user_role')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT name, event_date, location, seats_left 
        FROM events 
        WHERE event_date > CURDATE()
        ORDER BY seats_left DESC 
        LIMIT 3
    """)
    featured_events = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('homepage.html', user_role=user_role, featured_events=featured_events)


@app.route('/events')
@login_required
def events():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch events with available seats
    cursor.execute("""
        SELECT name, event_date, location 
        FROM events 
        WHERE seats_left > 0 
        ORDER BY event_date ASC
    """)
    events = cursor.fetchall()
    
    cursor.close()
    connection.close()

    user_role = session.get('user_role')
    return render_template('events.html', events=events, user_role=user_role)


# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['user'] = user['first_name']
            session['user_role'] = user['role']
            session['user_id'] = user['user_id']
            return redirect(url_for('homepage'))
        else:
            return "Invalid login credentials. Please try again."

    return render_template('login.html')

@app.route('/your_events')
@login_required
def your_events():
    if session.get('user_role') != 'user+organizer':
        return redirect(url_for('homepage'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Get the logged-in user's ID from the session
    user_id = session.get('user_id')
    
    # Debugging output
    print(f"Fetching events for user ID: {user_id}")
    
    # Fetch events created by the current user
    cursor.execute("SELECT * FROM events WHERE organizer_id = %s ORDER BY event_date", (user_id,))
    user_events = cursor.fetchall()
    
    # Debugging output to see fetched events
    print(f"Fetched events: {user_events}")
    
    cursor.close()
    connection.close()
    
    return render_template('your_events.html', user_events=user_events)


@app.route('/create_event', methods=['POST'])
@login_required
def create_event():
    if session.get('user_role') != 'user+organizer':
        return redirect(url_for('homepage'))
    
    # Retrieve form data
    event_name = request.form['event_name']
    event_date = request.form['event_date']
    location = request.form['location']
    total_seats = request.form['total_seats']
    ticket_price = request.form['ticket_price']  # Get ticket price from form
    description = request.form['description']
    
    # Get the logged-in user's ID from the session
    organizer_id = session.get('user_id')  # Assuming you stored user ID in session during login
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Check if the organizer_id exists in the users table
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = %s", (organizer_id,))
    if cursor.fetchone()[0] == 0:
        cursor.close()
        connection.close()
        return "Organizer ID does not exist.", 400  # Return an error if organizer ID is invalid
    
    # Insert the new event into the database
    cursor.execute("""
        INSERT INTO events (name, description, location, event_date, organizer_id, total_seats, seats_sold, ticket_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (event_name, description, location, event_date, organizer_id, total_seats, 0, ticket_price))  # seats_sold starts at 0
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('your_events'))

@app.route('/edit_event/<int:event_id>')
@login_required
def edit_event(event_id):
    # Implement edit event logic
    pass

@app.route('/delete_event/<int:event_id>')
@login_required
def delete_event(event_id):
    # Implement delete event logic
    pass

# Route to logout the user
@app.route('/logout')
def logout():
    session.pop('user', None)  # Clear the session
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
