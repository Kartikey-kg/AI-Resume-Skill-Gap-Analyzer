from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS

import sqlite3, os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

print("🚀 APP STARTING...")

# 🔒 SAFE IMPORT (prevents crash)
try:
    from resume_parser import extract_text
    from ml_skill_matcher import match_skills
except Exception as e:
    print("❌ ERROR LOADING ML MODULE:", e)

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
CORS(app)

# =====================
# FRONTEND ROUTES
# =====================

@app.route("/")
def root():
    return send_from_directory("../frontend", "login.html")

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory("../frontend", filename)

# =====================
# CONFIG
# =====================

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY,
        resume_name TEXT,
        matched_skills TEXT,
        missing_skills TEXT,
        score REAL,
        analyzed_at TEXT
    )
    """)

    conn.commit()
    conn.close()

# Initialize DB on start
init_db()

# =====================
# AUTH ROUTES
# =====================

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users VALUES (NULL,?,?,?)",
            (data["username"], data["email"], generate_password_hash(data["password"]))
        )

        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cur = conn.cursor()

        cur.execute("SELECT password FROM users WHERE username=?", (data["username"],))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[0], data["password"]):
            return jsonify({"message": "Login successful"})

        return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================
# ANALYSIS ROUTE
# =====================

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files["resume"]

        skills = [
            skill.strip().lower()
            for skill in request.form["skills"].split(",")
        ]

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        resume_text = extract_text(path)
        result = match_skills(resume_text, skills)

        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO analysis_results VALUES (NULL,?,?,?,?,?)
        """, (
            file.filename,
            ",".join(result["matched_skills"]),
            ",".join(result["missing_skills"]),
            result["score"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return jsonify(result)

    except Exception as e:
        print("❌ ANALYZE ERROR:", e)
        return jsonify({"error": str(e)}), 500

# =====================
# HISTORY ROUTE
# =====================

@app.route("/history")
def history():
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cur = conn.cursor()

        cur.execute("SELECT * FROM analysis_results ORDER BY analyzed_at DESC")
        rows = cur.fetchall()

        conn.close()

        return jsonify([
            {
                "resume": r[1],
                "matched": r[2],
                "missing": r[3],
                "score": r[4],
                "date": r[5]
            } for r in rows
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================
# RUN SERVER
# =====================

if __name__ == "__main__":
    print("🚀 RUNNING SERVER...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
