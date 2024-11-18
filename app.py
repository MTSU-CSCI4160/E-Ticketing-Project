from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from datetime import datetime
import bcrypt  # Importing bcrypt for password hashing
import qrcode
from io import BytesIO
import base64
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
        SELECT name, event_date, location, event_id 
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

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    connection = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE events SET name = %s, event_date = %s, location = %s WHERE event_id = %s
        """, (name, date, location, event_id))
        
        connection.commit()
        cursor.close()
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events'))
    
    # If GET request, fetch existing data
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
    event = cursor.fetchone()
    
    cursor.close()
    connection.close()

    return render_template('edit_event.html', event=event)  # Render the edit template

@app.route('/delete_event/<int:event_id>')
@login_required
def delete_event(event_id):
    # Implement delete event logic
    pass


@app.route('/event_detail/<int:event_id>')
@login_required
def event_detail(event_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch the specific event details
    cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
    event = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events'))
    
    return render_template('event_detail.html', event=event)

@app.route('/payment/<int:event_id>')
@login_required
def payment_page(event_id):
    quantity = request.args.get('quantity', 1, type=int)
    
    # Fetch the event details
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
        event = cursor.fetchone()

        if not event:
            flash('Event not found', 'error')
            return redirect(url_for('events'))

        # Convert event_date to datetime object if it's not already
        if isinstance(event['event_date'], str):
            event['event_date'] = datetime.strptime(event['event_date'], '%Y-%m-%d %H:%M:%S')

        return render_template('payment.html', event=event, quantity=quantity)

    finally:
        cursor.close()
        connection.close()

@app.route('/confirmation/<int:event_id>')
@login_required
def confirmation(event_id):
    # Fetch event details and recent purchase info
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
    event = cursor.fetchone()
    
    user_id = session.get('user_id')
    cursor.execute("""
        SELECT * FROM purchases 
        WHERE user_id = %s AND event_id = %s 
        ORDER BY purchase_date DESC LIMIT 1
    """, (user_id, event_id))
    purchase = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not event or not purchase:
        flash('Confirmation information not found', 'error')
        return redirect(url_for('homepage'))
    
    return render_template('confirmation.html', event=event, purchase=purchase)


@app.route('/process_payment/<int:event_id>', methods=['POST'])
@login_required
def process_payment(event_id):
    quantity = int(request.form['quantity'])
    user_id = session.get('user_id')

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Start a transaction
        connection.start_transaction()

        # Fetch event details
        cursor.execute("SELECT * FROM events WHERE event_id = %s FOR UPDATE", (event_id,))
        event = cursor.fetchone()

        if not event:
            raise ValueError("Event not found")

        if event['seats_left'] < quantity:
            raise ValueError("Not enough seats available")

        # Calculate total price
        total_price = event['ticket_price'] * quantity

        cursor.execute("UPDATE events SET seats_sold = seats_sold + %s WHERE event_id = %s", 
                       (quantity, event_id))

        # Generate QR code
        qr_data = f"User ID: {user_id}, Event ID: {event_id}, Tickets: {quantity}, Total: ${total_price}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert QR code to bytes
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code_binary = buffered.getvalue()

        # Insert sales record
        cursor.execute("""
            INSERT INTO sales (user_id, event_id, price, number_of_tickets, qr_code)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, event_id, total_price, quantity, qr_code_binary))

        # Commit the transaction
        connection.commit()

        flash('Ticket purchased successfully!', 'success')
        return redirect(url_for('ticket_confirmation', sale_id=cursor.lastrowid))

    except ValueError as e:
        connection.rollback()
        flash(str(e), 'error')
        return redirect(url_for('event_detail', event_id=event_id))

   # except Error as e:
      #  connection.rollback()
      #  flash('An error occurred while processing your purchase', 'error')
      #  return redirect(url_for('event_detail', event_id=event_id))

    finally:
        cursor.close()
        connection.close()

@app.route('/ticket_confirmation/<int:sale_id>')
@login_required
def ticket_confirmation(sale_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch sales details
        cursor.execute("""
            SELECT s.*, e.name as event_name, e.event_date
            FROM sales s
            JOIN events e ON s.event_id = e.event_id
            WHERE s.ticket_id = %s AND s.user_id = %s
        """, (sale_id, session.get('user_id')))
        sale = cursor.fetchone()

        if not sale:
            flash('Sale record not found', 'error')
            return redirect(url_for('homepage'))

        # Convert binary QR code to base64 for displaying in HTML
        qr_code_base64 = base64.b64encode(sale['qr_code']).decode('utf-8')

        return render_template('ticket_confirmation.html', sale=sale, qr_code=qr_code_base64)

    #except Error as e:
     #   flash('An error occurred while fetching sale details', 'error')
     #   return redirect(url_for('homepage'))

    finally:
        cursor.close()
        connection.close()


@app.route('/your_tickets')
@login_required
def your_tickets():
    user_id = session.get('user_id')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT s.*, e.name AS event_name, e.event_date
            FROM sales s
            JOIN events e ON s.event_id = e.event_id
            WHERE s.user_id = %s
        """, (user_id,))
        
        tickets = cursor.fetchall()
        
        # Convert QR code from binary to base64 for rendering
        for ticket in tickets:
            ticket['qr_code'] = base64.b64encode(ticket['qr_code']).decode('utf-8')

        return render_template('your_tickets.html', tickets=tickets)

    finally:
        cursor.close()
        connection.close()


# Route for the Contact Us page
@app.route('/contact_us')
def contact():
    return render_template('contact_us.html')

# Route to handle form submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Here you would typically process the data (e.g., save it to a database or send an email)
    # For demonstration purposes, we'll just print it to the console
    print(f"Name: {name}, Email: {email}, Message: {message}")

    # Flash a success message
    flash('Your message has been sent successfully!', 'success')
    
    # Redirect back to the contact page (or you could redirect to a thank you page)
    return redirect(url_for('contact_us'))

# route to log out user
@app.route('/logout')
def logout():
    session.pop('user', None)  # Clear the session
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
