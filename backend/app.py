from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS

import sqlite3, os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from resume_parser import extract_text
from ml_skill_matcher import match_skills

app = Flask(__name__)
CORS(app)

# =====================
# FRONTEND ROUTES
# =====================

@app.route("/")
def root():
    return redirect("/login.html")

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory("../frontend", filename)


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users VALUES (NULL,?,?,?)",
        (data["username"], data["email"], generate_password_hash(data["password"]))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Signup successful"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (data["username"],))
    user = cur.fetchone()
    conn.close()

    if user and check_password_hash(user[0], data["password"]):
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]
    skills = [
    skill.strip().lower()
    for skill in request.form["skills"].split(",")
]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    resume_text = extract_text(path)
    result = match_skills(resume_text, skills)

    conn = sqlite3.connect(DB_NAME)
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

@app.route("/history")
def history():
    conn = sqlite3.connect(DB_NAME)
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
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
