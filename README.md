# 📚 Book Alchemy – A Flask Digital Library

**Book Alchemy** is a Flask-based web application for managing a digital library of books and authors. It allows users to add and view books with validated metadata, sort and search the database, and retrieve book covers from OpenLibrary.

---

## 🚀 Features

- ✍️ **Add Author**  
  Add authors with name, birth date, and (optionally) date of death. Input is validated for consistency and format.

- 📖 **Add Book**  
  Add books by ISBN, title, publication year, and assign to an author. ISBNs are validated both locally and via the OpenLibrary API.

- 🧾 **View Library**  
  View all books in a responsive grid with cover images and author details.

- ❌ **Delete Book**  
  Remove a book. Authors with no remaining books are also removed automatically.

- 🔍 **Search & Sort**  
  Search books by title or ISBN. Sort by title or author name.

- 🖼 **Cover Retrieval**  
  Automatically fetch cover images from OpenLibrary using ISBN.

- 🛡 **Validation & Error Handling**  
  Full input validation and graceful error handling with user-friendly messages.

---

## 🧪 Technologies Used

| Tool           | Purpose                         |
| -------------- | -------------------------------|
| Flask          | Web application framework       |
| SQLite         | Lightweight relational database |
| SQLAlchemy     | ORM for DB models               |
| Jinja2         | HTML templating                 |
| requests       | HTTP library for API access     |
| datetime       | Date validation logic           |
| OpenLibrary API| Fetch cover images & metadata   |

---

## 🌐 OpenLibrary API Integration

This application uses the [OpenLibrary Covers API](https://openlibrary.org/dev/docs/api/covers) to dynamically fetch book cover images based on ISBNs.

Example image URL format:

```
https://covers.openlibrary.org/b/isbn/<ISBN>-L.jpg
```

If a cover is not found, a local fallback image (`no_cover.jpeg`) is displayed.

Additionally, the app validates ISBNs using the [OpenLibrary Books API](https://openlibrary.org/dev/docs/api/books), for example:

```
https://openlibrary.org/isbn/<ISBN>.json
```

These API integrations ensure both usability and data reliability when adding books.

---

---

## 🛠️ Setup Instructions

1. **Clone this repo**
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Create virtual environment (optional)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   ... 
   >>> exit()
   ```

5. **Run the server**
   ```bash
   flask run --debug
   ```

6. **Open the browser**
   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 📁 Project Structure

```
├── app.py           # Flask app and routes
├── data_models.py   # SQLAlchemy models
├── setup.py         # One-time DB creation
├── templates/       # HTML templates (Jinja2)
│   ├── home.html
│   ├── add_author.html
│   └── add_book.html
├── static/          # CSS, images (e.g. no_cover.jpeg)
├── data/            # SQLite database file
│   └── library.sqlite
└── README.md        # Project info
```

---

## 🔮 Future Enhancements

- 🗃 Store cover URLs or images in DB for faster loading  
- 🔐 Add login & user roles  
- ✏️ Edit functionality for books and authors  
- 🧠 Smarter search (e.g. fuzzy match, filter by year)  
- ✅ Unit tests for routes and models  
- 🎨 Improved UI with CSS refactor or a frontend framework

---

## 📬 License & Contact

This is a personal/student project. Contributions or ideas are welcome!  


---
