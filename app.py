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
def success():
    return "Signup successful!"

if __name__ == '__main__':
    app.run(debug=True)
