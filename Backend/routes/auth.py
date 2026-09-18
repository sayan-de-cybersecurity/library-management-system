from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

import mysql.connector

from config import MYSQL_CONFIG


# =========================================================
# AUTH BLUEPRINT
# =========================================================

auth_bp = Blueprint("auth", __name__)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    return mysql.connector.connect(**MYSQL_CONFIG)


# =========================================================
# REGISTER
# POST /api/auth/register
# =========================================================

@auth_bp.route("/register", methods=["POST"])
def register():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid request data"
            }), 400

        # -------------------------------------------------
        # Get registration data
        # -------------------------------------------------

        student_name = data.get("student_name", "").strip()
        erp_id = data.get("erp_id", "").strip()
        student_email = data.get("student_email", "").strip().lower()
        phone_number = data.get("phone_number", "").strip()
        password = data.get("password", "")

        # -------------------------------------------------
        # Required field validation
        # -------------------------------------------------

        if not student_name:
            return jsonify({
                "success": False,
                "message": "Student name is required"
            }), 400

        if not erp_id:
            return jsonify({
                "success": False,
                "message": "ERP ID is required"
            }), 400

        if not student_email:
            return jsonify({
                "success": False,
                "message": "Student email is required"
            }), 400

        if not phone_number:
            return jsonify({
                "success": False,
                "message": "Phone number is required"
            }), 400

        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400

        # -------------------------------------------------
        # Password validation
        # -------------------------------------------------

        if len(password) < 6:
            return jsonify({
                "success": False,
                "message": "Password must contain at least 6 characters"
            }), 400

        # -------------------------------------------------
        # Basic email validation
        # -------------------------------------------------

        if "@" not in student_email or "." not in student_email:
            return jsonify({
                "success": False,
                "message": "Please enter a valid student email"
            }), 400

        # -------------------------------------------------
        # Database connection
        # -------------------------------------------------

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # -------------------------------------------------
        # Check ERP ID
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE erp_id = %s
            """,
            (erp_id,)
        )

        existing_erp = cursor.fetchone()

        if existing_erp:

            cursor.close()
            db.close()

            return jsonify({
                "success": False,
                "message": "ERP ID is already registered"
            }), 409

        # -------------------------------------------------
        # Check student email
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE student_email = %s
            """,
            (student_email,)
        )

        existing_email = cursor.fetchone()

        if existing_email:

            cursor.close()
            db.close()

            return jsonify({
                "success": False,
                "message": "Student email is already registered"
            }), 409

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        password_hash = generate_password_hash(password)

        # -------------------------------------------------
        # Insert new student
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (
                student_name,
                erp_id,
                student_email,
                phone_number,
                password_hash,
                role
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                student_name,
                erp_id,
                student_email,
                phone_number,
                password_hash,
                "student"
            )
        )

        db.commit()

        cursor.close()
        db.close()

        # -------------------------------------------------
        # Success response
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "message": "Registration successful"
        }), 201

    except mysql.connector.Error as e:

        print("MySQL Error:", e)

        return jsonify({
            "success": False,
            "message": "Database error"
        }), 500

    except Exception as e:

        print("Registration Error:", e)

        return jsonify({
            "success": False,
            "message": "Registration failed"
        }), 500


# =========================================================
# LOGIN
# POST /api/auth/login
# =========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid request data"
            }), 400

        # -------------------------------------------------
        # Get login data
        # -------------------------------------------------

        student_email = data.get("student_email", "").strip().lower()
        password = data.get("password", "")

        # -------------------------------------------------
        # Validate fields
        # -------------------------------------------------

        if not student_email:
            return jsonify({
                "success": False,
                "message": "Student email is required"
            }), 400

        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400

        # -------------------------------------------------
        # Database connection
        # -------------------------------------------------

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # -------------------------------------------------
        # Find student
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                student_name,
                erp_id,
                student_email,
                phone_number,
                password_hash,
                role
            FROM users
            WHERE student_email = %s
            """,
            (student_email,)
        )

        user = cursor.fetchone()

        # -------------------------------------------------
        # User not found
        # -------------------------------------------------

        if not user:

            cursor.close()
            db.close()

            return jsonify({
                "success": False,
                "message": "Invalid student email or password"
            }), 401

        # -------------------------------------------------
        # Check password
        # -------------------------------------------------

        password_correct = check_password_hash(
            user["password_hash"],
            password
        )

        if not password_correct:

            cursor.close()
            db.close()

            return jsonify({
                "success": False,
                "message": "Invalid student email or password"
            }), 401

        # -------------------------------------------------
        # Create Flask session
        # -------------------------------------------------

        session["user_id"] = user["id"]
        session["student_name"] = user["student_name"]
        session["erp_id"] = user["erp_id"]
        session["student_email"] = user["student_email"]
        session["role"] = user["role"]

        # -------------------------------------------------
        # Close database
        # -------------------------------------------------

        cursor.close()
        db.close()

        # -------------------------------------------------
        # Login successful
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "student_name": user["student_name"],
                "erp_id": user["erp_id"],
                "student_email": user["student_email"],
                "phone_number": user["phone_number"],
                "role": user["role"]
            }
        }), 200

    except mysql.connector.Error as e:

        print("MySQL Error:", e)

        return jsonify({
            "success": False,
            "message": "Database error"
        }), 500

    except Exception as e:

        print("Login Error:", e)

        return jsonify({
            "success": False,
            "message": "Login failed"
        }), 500


# =========================================================
# LOGOUT
# POST /api/auth/logout
# =========================================================

@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logout successful"
    }), 200


# =========================================================
# CHECK CURRENT USER
# GET /api/auth/me
# =========================================================

@auth_bp.route("/me", methods=["GET"])
def get_current_user():

    # -----------------------------------------------------
    # Check whether user is logged in
    # -----------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Not logged in"
        }), 401

    # -----------------------------------------------------
    # Return logged-in user
    # -----------------------------------------------------

    return jsonify({
        "success": True,
        "user": {
            "id": session["user_id"],
            "student_name": session["student_name"],
            "erp_id": session["erp_id"],
            "student_email": session["student_email"],
            "role": session["role"]
        }
    }), 200