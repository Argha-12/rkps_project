from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite database connection and other routes...

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Process the form data (e.g., save it to a database, send an email, etc.)
        # For example, you might save the data to a database:
        # save_to_database(name, email, message)
        
        # Then you can redirect the user to a thank you page or any other page you want.
        return redirect(url_for('thank_you'))
    
    # If the request method is GET, just render the contact_us.html template.
    return render_template('contact_us.html')

if __name__ == '__main__':
    app.run(debug=True)
