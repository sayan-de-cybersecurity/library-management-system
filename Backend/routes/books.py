from flask import Blueprint, request, jsonify
import mysql.connector

from config import MYSQL_CONFIG


books_bp = Blueprint("books", __name__)


def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


# -----------------------------------
# Get All Books
# -----------------------------------
@books_bp.route("/", methods=["GET"])
def get_books():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM books ORDER BY id DESC"
    )

    books = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(books)


# -----------------------------------
# Get Single Book
# -----------------------------------
@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM books WHERE id = %s",
        (book_id,)
    )

    book = cursor.fetchone()

    cursor.close()
    db.close()

    if not book:
        return jsonify({
            "message": "Book not found"
        }), 404

    return jsonify(book)


# -----------------------------------
# Add Book
# -----------------------------------
@books_bp.route("/", methods=["POST"])
def add_book():

    data = request.get_json()

    title = data.get("title")
    author = data.get("author")
    category = data.get("category")
    isbn = data.get("isbn")
    total_copies = int(data.get("total_copies", 1))

    if not title or not author:
        return jsonify({
            "message": "Title and author are required"
        }), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO books
        (
            title,
            author,
            category,
            isbn,
            total_copies,
            available_copies
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            title,
            author,
            category,
            isbn,
            total_copies,
            total_copies
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "success": True,
        "message": "Book added successfully"
    }), 201


# -----------------------------------
# Update Book
# -----------------------------------
@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):

    data = request.get_json()

    title = data.get("title")
    author = data.get("author")
    category = data.get("category")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE books
        SET title = %s,
            author = %s,
            category = %s
        WHERE id = %s
        """,
        (
            title,
            author,
            category,
            book_id
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "success": True,
        "message": "Book updated successfully"
    })


# -----------------------------------
# Delete Book
# -----------------------------------
@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM books WHERE id = %s",
        (book_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "success": True,
        "message": "Book deleted successfully"
    })