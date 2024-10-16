from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Establishing connection to MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",  # or your MySQL server host
        user="root",
        password="Database2024",
        database="ticketwave"
    )
    return connection

# Route to display the signup form
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Fetch data from the form
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']

        # Connect to MySQL and insert the data
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Insert query (make sure your table matches these column names)
        cursor.execute('''INSERT INTO users (first_name, last_name, email, password, dob) 
                          VALUES (%s, %s, %s, %s, %s)''', 
                       (first_name, last_name, email, password, dob))
        connection.commit()
        cursor.close()
        connection.close()

        # Redirect or show success message
        return redirect('/success')

    return render_template('signup.html')

# Route for signup success (optional)
@app.route('/success')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to MySQL and check if the user exists
        connection = get_db_connection()
        cursor = connection.cursor()

        # Select query to find the user with matching email and password
        cursor.execute('''SELECT * FROM users WHERE email = %s AND password = %s''', 
                       (email, password))
        user = cursor.fetchone()  # Fetch one matching record
        
        cursor.close()
        connection.close()

        if user:
            # If a user is found, redirect to success or welcome page
            return "Login successful!"
        else:
            # If no user is found, show an error message
            return "Login failed! Invalid email or password."

    return render_template('login.html')

def success():
    return "Signup successful!"

if __name__ == '__main__':
    app.run(debug=True)