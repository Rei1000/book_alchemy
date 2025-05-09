from flask import render_template, request, redirect, url_for, flash
import requests
import re  # For regular expressions for ISBN validation
from sqlalchemy import or_  # For OR conditions in search queries
from sqlalchemy.orm.exc import NoResultFound  # For catching NoResultFound exceptions
from datetime import datetime  # For date validation

"""
Flask application for managing a digital library with authors and books.
"""

cover_cache = {}  # Cache for book cover URLs to reduce API calls

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    import os

    app = Flask(__name__)
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'library.sqlite')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "super secret"  # Required for flash messages
    from data_models import db, Author, Book
    db.init_app(app)

except ImportError as e:
    print("Error importing a module:", e)
    exit()
except Exception as e:
    print("General error:", e)
    exit()


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Handles adding a new author.
    Displays a form on GET, and adds the author to the database on POST.
    Provides feedback on whether the operation was successful.
    """
    message = None

    if request.method == "POST":
        try:
            name = request.form.get("name").strip()  # Remove leading/trailing spaces
            birth_date = request.form.get("birthdate")
            date_of_death = request.form.get("date_of_death")

            # Validate author name
            if not name:
                message = "Name is a required field."
                return render_template("add_author.html", message=message)

            # Check if the name contains digits or starts with a space
            if any(char.isdigit() for char in name) or name[0].isspace():
                message = "Name must not contain numbers or start with a space."
                return render_template("add_author.html", message=message)

            from datetime import datetime

            # Convert date strings to datetime objects (only if dates are provided)
            birth = None
            death = None

            if birth_date:
                try:
                    birth = datetime.strptime(birth_date, "%Y-%m-%d")
                except ValueError:
                    message = "Invalid birth date format."
                    return render_template("add_author.html", message=message)

            if date_of_death:
                try:
                    death = datetime.strptime(date_of_death, "%Y-%m-%d")
                except ValueError:
                    message = "Invalid death date format."
                    return render_template("add_author.html", message=message)

            # Perform validations only if both dates are present
            if birth and death:
                today = datetime.today()

                if death < birth:
                    message = "Death date cannot be earlier than birth date."
                    return render_template("add_author.html", message=message)

                age_at_death = (death - birth).days // 365
                if age_at_death < 16:
                    message = "Author must have been at least 16 years old."
                    return render_template("add_author.html", message=message)

                if death > today:
                    message = "Death date cannot be in the future."
                    return render_template("add_author.html", message=message)
            elif death:  # If only death date is given, check if it is in the future
                today = datetime.today()
                if death > today:
                    message = "Death date cannot be in the future."
                    return render_template("add_author.html", message=message)

            # If we reach here, all validations passed
            new_author = Author(name=name, birth_date=birth, date_of_death=death)
            db.session.add(new_author)
            db.session.commit()
            message = "Author added successfully."

        except Exception as e:
            message = f"Error saving author: {e}"

    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Handles adding a new book.
    Displays a form with a dropdown list of existing authors on GET.
    Saves the book with the author in the database on POST.
    """
    message = None

    if request.method == "POST":
        try:
            isbn = request.form.get("isbn").strip()  # Remove leading/trailing spaces
            title = request.form.get("title").strip()  # Remove leading/trailing spaces
            publication_year = request.form.get("publication_year").strip()  # Remove spaces
            author_id = request.form.get("author_id")

            # ISBN format check: Only digits, length 10 or 13
            authors = Author.query.all()
            if not (isbn and title and author_id):
                message = "ISBN, title, and author are required fields."
                return render_template("add_book.html", authors=authors, message=message)
            if not isbn.isdigit() or len(isbn) not in [10, 13]:
                message = "ISBN must consist of 10 or 13 digits."
                return render_template("add_book.html", authors=authors, message=message)

            # Publication year validation
            if publication_year:
                try:
                    publication_year = int(publication_year)
                    if publication_year > datetime.now().year:
                        message = "Publication year must be in the past."
                        return render_template("add_book.html", authors=authors, message=message)
                except ValueError:
                    message = "Invalid publication year."
                    return render_template("add_book.html", authors=authors, message=message)
            else:
                publication_year = None  # Set to None if empty

            # Check if the ISBN exists in the OpenLibrary database
            isbn_found = False
            try:
                response = requests.get(f"https://openlibrary.org/isbn/{isbn}.json", timeout=5)
                if response.status_code == 200:
                    isbn_found = True
            except requests.exceptions.RequestException:
                pass  # Ignore errors when fetching ISBN from OpenLibrary

            new_book = Book(
                isbn=isbn,
                title=title,
                publication_year=publication_year,
                author_id=int(author_id)
            )
            db.session.add(new_book)
            db.session.commit()
            if isbn_found:
                message = "Book saved successfully. ISBN found in OpenLibrary."
            else:
                message = "Book saved successfully. ISBN not found in OpenLibrary."

        except Exception as e:
            message = f"Error saving book: {e}"

    # Retrieve authors for the dropdown list
    authors = Author.query.all()
    return render_template("add_book.html", authors=authors, message=message)


def is_valid_isbn10(isbn):
    """Checks if a string is a valid ISBN-10."""
    isbn = re.sub(r'[^0-9X]', '', isbn.upper())
    if len(isbn) != 10:
        return False
    sum = 0
    for i in range(9):
        if not isbn[i].isdigit():
            return False
        sum += (i + 1) * int(isbn[i])
    if isbn[9] == 'X':
        sum += 10 * 10
    elif isbn[9].isdigit():
        sum += 10 * int(isbn[9])
    else:
        return False
    return sum % 11 == 0


def is_valid_isbn13(isbn):
    """Checks if a string is a valid ISBN-13."""
    isbn = re.sub(r'[^0-9]', '', isbn)
    if len(isbn) != 13:
        return False
    sum = 0
    for i in range(13):
        digit = int(isbn[i])
        if i % 2 == 0:
            sum += digit
        else:
            sum += 3 * digit
    return sum % 10 == 0


def is_valid_isbn(isbn):
    """Checks if a string is a valid ISBN-10 or ISBN-13."""
    return is_valid_isbn10(isbn) or is_valid_isbn13(isbn)


def get_book_cover(isbn, validate_isbn_api=True):
    """
    Retrieves the cover image and book page from OpenLibrary for an ISBN.
    Uses a cache to avoid repeated requests.
    Optional: Validates the ISBN via the OpenLibrary API.
    Returns a dictionary with 'img_url' and 'link_url'.
    Uses a fallback for invalid ISBNs or API errors.
    """
    if not isbn:
        return {
            "img_url": url_for("static", filename="no_cover.jpeg"),
            "link_url": "#",
            "tooltip": "No ISBN provided",
            "isbn_valid": False  # Flag indicating ISBN validity
        }

    if isbn in cover_cache:
        return cover_cache[isbn]

    is_locally_valid = is_valid_isbn(isbn)
    isbn_found_api = False  # Track ISBN validation status via API

    if validate_isbn_api and is_locally_valid:
        # API endpoint for ISBN search at OpenLibrary
        api_url = f"https://openlibrary.org/isbn/{isbn}.json"
        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            api_data = response.json()
            # If the API responds successfully, assume ISBN exists
            print(f"✅ ISBN '{isbn}' confirmed by OpenLibrary API.")
            link_url = f"https://openlibrary.org/isbn/{isbn}"
            isbn_found_api = True  # Set flag to True if ISBN is found
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error validating ISBN via API for '{isbn}': {e}")
            link_url = f"https://openlibrary.org/isbn/{isbn}" if is_locally_valid else "#"
        except (ValueError, KeyError) as e:
            print(f"⚠️ Invalid response from API for ISBN '{isbn}': e")
            link_url = f"https://openlibrary.org/isbn/{isbn}" if is_locally_valid else "#"
    else:
        link_url = f"https://openlibrary.org/isbn/{isbn}" if is_locally_valid else "#"

    try:
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
        response = requests.head(cover_url, allow_redirects=True, timeout=3)
        response.raise_for_status()

        print(f"✅ Cover found for ISBN {isbn}")
        result = {
            "img_url": cover_url,
            "link_url": link_url,
            "tooltip": "View information about this book on OpenLibrary" if is_locally_valid else "No book found (invalid ISBN)",
            "isbn_found": isbn_found_api,
            "isbn_valid": is_locally_valid
        }
        cover_cache[isbn] = result
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Error retrieving cover for ISBN {isbn}: e")
        fallback = {
            "img_url": url_for("static", filename="no_cover.jpeg"),
            "link_url": link_url,
            "tooltip": "View information about this book on OpenLibrary" if is_locally_valid else "No book found (invalid ISBN)",
            "isbn_found": isbn_found_api,
            "isbn_valid": is_locally_valid
        }
        cover_cache[isbn] = fallback
        return fallback


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Deletes a specific book from the database.
    If the book's author has no other books, the author is also deleted.
    Redirects to the home page after successful deletion and displays a success message.
    """
    try:
        book = Book.query.get_or_404(book_id)
        author_id = book.author_id
        db.session.delete(book)
        db.session.commit()
        flash(f"The book '{book.title}' was deleted successfully.", "success")

        # Check if the author has any other books
        other_books = Book.query.filter_by(author_id=author_id).first()
        if not other_books:
            author_to_delete = Author.query.get(author_id)
            if author_to_delete:
                db.session.delete(author_to_delete)
                db.session.commit()
                flash(f"Since '{author_to_delete.name}' has no more books, the author was also deleted.", "info")

        return redirect(url_for("home"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting the book: {e}", "error")
        return redirect(url_for("home"))


@app.route("/")
@app.route("/sort_books")
def home():
    """
    Home page of the application. Displays all books with their cover images.
    Allows sorting books by title or author.
    Allows searching for books.
    """
    sort_by = request.args.get('sort', 'title')  # Default: sort by title
    direction = request.args.get('direction', 'asc')  # Default: ascending
    search_query = request.args.get('search', '')  # Default: empty search term

    try:
        if search_query:
            # Remove leading/trailing spaces from the search query
            search_query = search_query.strip()
            # Search in title and ISBN (case-insensitive)
            search_filter = or_(
                Book.title.ilike(f"%{search_query}%"),
                Book.isbn.ilike(f"%{search_query}%")
            )

            if sort_by == 'title':
                if direction == 'asc':
                    books = Book.query.filter(search_filter).order_by(Book.title).all()
                else:
                    books = Book.query.filter(search_filter).order_by(Book.title.desc()).all()
            elif sort_by == 'author':
                if direction == 'asc':
                    books = Book.query.join(Author).filter(search_filter).order_by(Author.name).all()
                else:
                    books = Book.query.join(Author).filter(search_filter).order_by(Author.name.desc()).all()
            else:
                books = Book.query.filter(search_filter).all()  # Fallback
        else:  # No search
            if sort_by == 'title':
                if direction == 'asc':
                    books = Book.query.order_by(Book.title).all()
                else:
                    books = Book.query.order_by(Book.title.desc()).all()
            elif sort_by == 'author':
                if direction == 'asc':
                    books = Book.query.join(Author).order_by(Author.name).all()
                else:
                    books = Book.query.join(Author).order_by(Author.name.desc()).all()
            else:
                books = Book.query.all()  # Fallback

        books_with_covers = []
        for book in books:
            cover_info = get_book_cover(book.isbn, validate_isbn_api=True)
            books_with_covers.append({
                "book": book,
                "cover_url": cover_info["img_url"],
                "cover_link": cover_info["link_url"],
                "cover_tooltip": cover_info.get("tooltip"),
                "isbn_found": cover_info.get("isbn_found"),
                "isbn_valid": cover_info.get("isbn_valid")
            })
        # Check if any books were found
        if not books_with_covers and search_query:
            return render_template("home.html", books=[], sort_by=sort_by, direction=direction,
                                   search_query=search_query, message="No books found matching your search.")
        else:
            return render_template("home.html", books=books_with_covers, sort_by=sort_by, direction=direction,
                                   search_query=search_query, message=None)

    except Exception as e:
        # Log the error for debugging
        print(f"Error retrieving books: e")
        # Display a user-friendly error message
        return render_template("home.html", books=[], sort_by=sort_by, direction=direction,
                               search_query=search_query, message="An error occurred. Please try again later.")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
