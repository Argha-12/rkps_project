from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('your_database.db')  # Replace 'your_database.db' with your database file
    conn.row_factory = sqlite3.Row
    return conn

# Serve login page and handle login functionality
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials in the database
        conn = get_db_connection()
        cursor = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            return redirect(url_for('dashboard'))  # Redirect to the dashboard after successful login
        else:
            # Incorrect credentials, display error message
            return render_template('login.html', error='Invalid username or password')

    # Serve the login page
    return render_template('login.html')

# Serve the dashboard page
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        # Add logic to fetch data from the database for the dashboard
        # For example, fetching time logs or club events
        return render_template('dashboard.html')
    else:
        # Redirect to login page if not logged in
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
