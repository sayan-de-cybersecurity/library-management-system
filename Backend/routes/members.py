from flask import Blueprint, request, jsonify
import mysql.connector

from config import MYSQL_CONFIG


members_bp = Blueprint("members", __name__)


def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


# -----------------------------------
# Get Members
# -----------------------------------
@members_bp.route("/", methods=["GET"])
def get_members():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM members ORDER BY id DESC"
    )

    members = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(members)


# -----------------------------------
# Get Single Member
# -----------------------------------
@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM members WHERE id = %s",
        (member_id,)
    )

    member = cursor.fetchone()

    cursor.close()
    db.close()

    if not member:
        return jsonify({
            "message": "Member not found"
        }), 404

    return jsonify(member)


# -----------------------------------
# Add Member
# -----------------------------------
@members_bp.route("/", methods=["POST"])
def add_member():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    member_type = data.get(
        "member_type",
        "student"
    )

    if not name or not email:
        return jsonify({
            "message": "Name and email are required"
        }), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO members
        (
            name,
            email,
            phone,
            member_type
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            name,
            email,
            phone,
            member_type
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "success": True,
        "message": "Member added successfully"
    }), 201


# -----------------------------------
# Delete Member
# -----------------------------------
@members_bp.route("/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM members WHERE id = %s",
        (member_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "success": True,
        "message": "Member deleted successfully"
    })