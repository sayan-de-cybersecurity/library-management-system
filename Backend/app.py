import os
import sys

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    redirect,
    session
)

from flask_cors import CORS


# =========================================================
# PROJECT PATHS
# =========================================================

# Current directory:
# D:\Library-management\Backend

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Project directory:
# D:\Library-management

PROJECT_DIR = os.path.dirname(BASE_DIR)


# =========================================================
# IMPORT ROUTES
# =========================================================

# Make sure Python can find:
# routes/auth.py
# routes/books.py
# routes/members.py
# routes/issues.py

sys.path.insert(0, BASE_DIR)


from routes.auth import auth_bp
from routes.books import books_bp
from routes.members import members_bp
from routes.issues import issues_bp


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# SECRET KEY
# =========================================================

# Used by Flask to securely sign the session cookie.
#
# IMPORTANT:
# For production, replace this with a long random secret.

app.config["SECRET_KEY"] = (
    "library-management-secret-key-change-this"
)


# =========================================================
# SESSION CONFIGURATION
# =========================================================

# Session cookie settings

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Keep False while developing on localhost.
# Set True only when your application is served over HTTPS.

app.config["SESSION_COOKIE_SECURE"] = False


# =========================================================
# MYSQL CONFIGURATION
# =========================================================

# Keep these values synchronized with your config.py.

app.config["MYSQL_HOST"] = "localhost"

app.config["MYSQL_USER"] = "root"

app.config["MYSQL_PASSWORD"] = ""

app.config["MYSQL_DATABASE"] = "library_db"


# =========================================================
# CORS
# =========================================================

CORS(
    app,
    supports_credentials=True
)


# =========================================================
# REGISTER BLUEPRINTS
# =========================================================

app.register_blueprint(
    auth_bp,
    url_prefix="/api/auth"
)

app.register_blueprint(
    books_bp,
    url_prefix="/api/books"
)

app.register_blueprint(
    members_bp,
    url_prefix="/api/members"
)

app.register_blueprint(
    issues_bp,
    url_prefix="/api/issues"
)


# =========================================================
# PUBLIC FRONTEND PAGES
# =========================================================

@app.route("/")
def index():

    return send_from_directory(
        PROJECT_DIR,
        "index.html"
    )


@app.route("/index.html")
def index_page():

    return send_from_directory(
        PROJECT_DIR,
        "index.html"
    )


@app.route("/login.html")
def login_page():

    return send_from_directory(
        PROJECT_DIR,
        "login.html"
    )


@app.route("/register.html")
def register_page():

    return send_from_directory(
        PROJECT_DIR,
        "register.html"
    )


@app.route("/logout.html")
def logout_page():

    return send_from_directory(
        PROJECT_DIR,
        "logout.html"
    )


# =========================================================
# PROTECTED DASHBOARD
# =========================================================

@app.route("/dashboard.html")
def dashboard_page():

    # Check Flask server-side session.

    if "user_id" not in session:

        return redirect("/login.html")


    # User is authenticated.

    return send_from_directory(
        PROJECT_DIR,
        "dashboard.html"
    )


# =========================================================
# PROTECTED DASHBOARD ALIAS
# =========================================================

# This also allows:
#
# http://127.0.0.1:5000/dashboard
#
# instead of only:
#
# http://127.0.0.1:5000/dashboard.html

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login.html")


    return send_from_directory(
        PROJECT_DIR,
        "dashboard.html"
    )


# =========================================================
# FRONTEND CSS / JS / IMAGES / OTHER FILES
# =========================================================

@app.route("/<path:filename>")
def frontend_files(filename):

    # -----------------------------------------------------
    # Never allow the catch-all route to bypass dashboard
    # protection.
    # -----------------------------------------------------

    if filename == "dashboard.html":

        if "user_id" not in session:

            return redirect("/login.html")


        return send_from_directory(
            PROJECT_DIR,
            "dashboard.html"
        )


    # -----------------------------------------------------
    # Never treat API URLs as frontend files.
    # -----------------------------------------------------

    if filename.startswith("api/"):

        return jsonify({
            "success": False,
            "message": "API endpoint not found"
        }), 404


    # -----------------------------------------------------
    # Check whether requested frontend file exists.
    # -----------------------------------------------------

    file_path = os.path.join(
        PROJECT_DIR,
        filename
    )


    if os.path.isfile(file_path):

        return send_from_directory(
            PROJECT_DIR,
            filename
        )


    return jsonify({
        "success": False,
        "message": "Frontend file not found"
    }), 404


# =========================================================
# API HOME
# =========================================================

@app.route("/api")
def api_home():

    return jsonify({

        "success": True,

        "message":
            "Library Management System API",

        "status":
            "running"

    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():

    return jsonify({

        "success": True,

        "status":
            "OK",

        "message":
            "Backend is working"

    })


# =========================================================
# SESSION STATUS
# =========================================================

@app.route("/api/session")
def session_status():

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "logged_in": False,

            "message":
                "User is not logged in"

        }), 401


    return jsonify({

        "success": True,

        "logged_in": True,

        "user": {

            "id":
                session.get("user_id"),

            "student_name":
                session.get("student_name"),

            "erp_id":
                session.get("erp_id"),

            "student_email":
                session.get("student_email"),

            "phone_number":
                session.get("phone_number"),

            "role":
                session.get("role")

        }

    })


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({

        "success": False,

        "message":
            "Page or API endpoint not found"

    }), 404


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("          LIBRAHUB LIBRARY MANAGEMENT SYSTEM")
    print("=" * 65)

    print()
    print("Project Directory:")
    print(PROJECT_DIR)

    print()
    print("Backend:")
    print("http://127.0.0.1:5000")

    print()
    print("Homepage:")
    print("http://127.0.0.1:5000/")

    print()
    print("Login:")
    print("http://127.0.0.1:5000/login.html")

    print()
    print("Register:")
    print("http://127.0.0.1:5000/register.html")

    print()
    print("Dashboard:")
    print("http://127.0.0.1:5000/dashboard.html")

    print()
    print("Health:")
    print("http://127.0.0.1:5000/api/health")

    print()
    print("=" * 65)
    print()


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )