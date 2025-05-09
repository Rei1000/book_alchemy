"""
Data models for the digital library.

This module defines the ORM classes `Author` and `Book` to map authors and books to a SQLite database.
It uses SQLAlchemy within a Flask application.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize a SQLAlchemy database object (activated with init_app() in app.py)
db = SQLAlchemy()

class Author(db.Model):
    """
    Data model for an author.
    Each author can have multiple books (1:n relationship).
    """
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(20))
    date_of_death = db.Column(db.String(20))

    # Relationship: An author can have multiple books
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self):
        return self.name


class Book(db.Model):
    """
    Data model for a book.
    Each book belongs to exactly one author.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}' author_id={self.author_id}>"

    def __str__(self):
        return self.title
