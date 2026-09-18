from flask import Blueprint, request, jsonify
import mysql.connector

from datetime import date, datetime

from config import MYSQL_CONFIG


issues_bp = Blueprint("issues", __name__)


def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


# -----------------------------------
# Get All Issues
# -----------------------------------
@issues_bp.route("/", methods=["GET"])
def get_issues():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            issues.*,
            books.title AS book_title,
            members.name AS member_name
        FROM issues
        JOIN books
            ON issues.book_id = books.id
        JOIN members
            ON issues.member_id = members.id
        ORDER BY issues.id DESC
        """
    )

    issues = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(issues)


# -----------------------------------
# Issue Book
# -----------------------------------
@issues_bp.route("/issue", methods=["POST"])
def issue_book():

    data = request.get_json()

    book_id = data.get("book_id")
    member_id = data.get("member_id")
    issue_date = data.get("issue_date")
    due_date = data.get("due_date")

    if not all([
        book_id,
        member_id,
        issue_date,
        due_date
    ]):
        return jsonify({
            "message": "All fields are required"
        }), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Check book
    cursor.execute(
        """
        SELECT available_copies
        FROM books
        WHERE id = %s
        FOR UPDATE
        """,
        (book_id,)
    )

    book = cursor.fetchone()

    if not book:
        cursor.close()
        db.close()

        return jsonify({
            "message": "Book not found"
        }), 404

    if book["available_copies"] <= 0:

        cursor.close()
        db.close()

        return jsonify({
            "message": "Book is currently unavailable"
        }), 400

    # Add issue
    cursor.execute(
        """
        INSERT INTO issues
        (
            book_id,
            member_id,
            issue_date,
            due_date,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            book_id,
            member_id,
            issue_date,
            due_date,
            "issued"
        )
    )

    # Decrease available copies
    cursor.execute(
        """
        UPDATE books
        SET available_copies =
            available_copies - 1
        WHERE id = %s
        """,
        (book_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "success": True,
        "message": "Book issued successfully"
    }), 201


# -----------------------------------
# Return Book
# -----------------------------------
@issues_bp.route("/<int:issue_id>/return", methods=["PUT"])
def return_book(issue_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM issues
        WHERE id = %s
        AND status = 'issued'
        """,
        (issue_id,)
    )

    issue = cursor.fetchone()

    if not issue:

        cursor.close()
        db.close()

        return jsonify({
            "message": "Active issue not found"
        }), 404

    return_date = date.today()

    due_date = issue["due_date"]

    fine = 0

    # Calculate late fine
    if return_date > due_date:

        late_days = (
            return_date - due_date
        ).days

        fine = late_days * 5

    # Update issue
    cursor.execute(
        """
        UPDATE issues
        SET
            return_date = %s,
            status = 'returned'
        WHERE id = %s
        """,
        (
            return_date,
            issue_id
        )
    )

    # Increase available copies
    cursor.execute(
        """
        UPDATE books
        SET available_copies =
            available_copies + 1
        WHERE id = %s
        """,
        (issue["book_id"],)
    )

    # Add fine
    if fine > 0:

        cursor.execute(
            """
            INSERT INTO fines
            (
                issue_id,
                amount,
                status
            )
            VALUES (%s, %s, %s)
            """,
            (
                issue_id,
                fine,
                "unpaid"
            )
        )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "success": True,
        "message": "Book returned successfully",
        "fine": fine
    })