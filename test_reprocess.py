from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('employee_time_tracking.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform user authentication
        session['logged_in'] = True
        return redirect(url_for('dashboard.html'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Fetch time logs for the logged-in employee
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM time_logs WHERE employee_id = ?', (session['employee_id'],))
    time_logs = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', time_logs=time_logs)

@app.route('/log_time', methods=['GET', 'POST'])
def log_time():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Insert time log into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO time_logs (employee_id, date, hours) VALUES (?, ?, ?)',
                     (session['employee_id'], request.form['date'], request.form['hours']))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard.html'))

    return render_template('log_time.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

