from flask import Flask, request, jsonify, session, send_from_directory
import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import psycopg2.errors

# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask application
# The static folder is set to '../frontend' to serve the frontend files
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
# Enable CORS for cross-origin requests, allowing credentials
CORS(app, supports_credentials=True)
# Set a secret key for session management, defaulting to 'dev-secret'
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

# Get database connection details from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'nextstop')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '')

def get_db():
    """Establishes a connection to the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


@app.route('/')
def index():
    """Serves the index.html file from the static folder."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/register', methods=['POST'])
def register():
    """
    Handles user registration.
    - Expects a JSON payload with 'username' and 'password'.
    - Hashes the password for security.
    - Inserts the new user into the 'users' table.
    """
    conn = None
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'status': 'error', 'message': 'Missing username or password'}), 400

        username = data.get('username')
        password = data.get('password')
        hashed_password = generate_password_hash(password, method='scrypt')

        conn = get_db()
        if conn is None:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                        (username, hashed_password))
            conn.commit()

        return jsonify({'status': 'success', 'message': 'User registered successfully'}), 201

    except psycopg2.errors.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 409
    except psycopg2.Error as e:
        print(f"A database error occurred during registration: {e}")
        return jsonify({'status': 'error', 'message': 'A database error occurred'}), 500
    except Exception as e:
        print(f"An unexpected error occurred during registration: {e}")
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500
    finally:
        if conn:
            conn.close()


@app.route('/login', methods=['POST'])
def login():
    """
    Handles user login.
    - Expects a JSON payload with 'username' and 'password'.
    - Verifies the username and password against the database.
    - If successful, sets the user in the session.
    """
    conn = None
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'status': 'error', 'message': 'Missing username or password'}), 400

        username = data.get('username')
        password = data.get('password')

        conn = get_db()
        if conn is None:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT user_id, password_hash FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            return jsonify({'status': 'success', 'message': 'Login successful'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

    except Exception as e:
        print(f"An error occurred during login: {e}")
        return jsonify({'status': 'error', 'message': 'An internal error occurred'}), 500
    finally:
        if conn:
            conn.close()


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'status': 'success', 'message': 'Logged out successfully'}), 200


@app.route('/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'status': 'authenticated', 'user_id': session['user_id']}), 200
    return jsonify({'status': 'not authenticated'}), 401


if __name__ == "__main__":
    app.run(debug=True, port=5000)
