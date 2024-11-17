from flask import Flask, request, redirect, url_for, flash, render_template
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='ecomDb',
            user='root',
            password=''
        )
        if conn.is_connected():
            print("Database connected successfully.")
        return conn
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error")
            return redirect(url_for('login'))

        try:
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                flash("Both email and password are required")
                return redirect(url_for('login'))

            cursor = conn.cursor()
            query = "SELECT password, role FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user and user[0] == password:
                role = user[1]
                if role == 'admin':
                    return redirect(url_for('admin_page'))
                elif role == 'superadmin':
                    return redirect(url_for('superadmin_page'))
                elif role == 'user':
                    return redirect(url_for('home'))
                else:
                    flash("Unknown role encountered")
                    return redirect(url_for('login'))
            else:
                flash("Invalid email or password")
                return redirect(url_for('login'))

        except Error as e:
            print(f"Login error: {e}")
            flash("An internal database error occurred")
            return redirect(url_for('login'))
        finally:
            if conn:
                conn.close()
    return render_template('login.html')

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Failed to connect to the database")
            return redirect(url_for('signup'))

        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not name or not email or not password or password != confirm_password:
                flash("All fields are required and passwords must match")
                return redirect(url_for('signup'))

            cursor = conn.cursor()
            query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, password, 'user'))
            conn.commit()
            flash("User registered successfully!")
            return redirect(url_for('login'))

        except Error as e:
            print(f"Error while inserting user data: {e}")
            flash("Failed to register user")
            return redirect(url_for('signup'))
        finally:
            if conn:
                conn.close()
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
