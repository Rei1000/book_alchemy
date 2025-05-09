"""
setup.py - Initializes the SQLite database for Book Alchemy.
This script creates the tables for authors and books.
It can be executed multiple times without overwriting existing tables.
"""

from flask import Flask
from data_models import db, Author, Book  # Import the DB object and the models
import os

# Define the Flask application locally within this script
app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'data', 'library.sqlite')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the DB with the app
db.init_app(app)

# Create tables
if __name__ == "__main__":
    try:
        with app.app_context():
            db.create_all()
            print("Tables created successfully.")
    except Exception as e:
        print("Error creating tables:", e)
