from flask import Flask, request, jsonify, send_file
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("database.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/events", methods=["POST"])
def create_event():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Event data is required"}), 400

    name = data.get("name")
    date = data.get("date")
    location = data.get("location")
    description = data.get("description", "")

    if not name or not date or not location:
        return jsonify({
            "error": "Name, date and location are required"
        }), 400

    conn = sqlite3.connect("database.db")

    cursor = conn.execute("""
        INSERT INTO events (name, date, location, description)
        VALUES (?, ?, ?, ?)
    """, (name, date, location, description))

    event_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Event created successfully",
        "event_id": event_id
    })


@app.route("/events", methods=["GET"])
def get_events():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    events = conn.execute(
        "SELECT * FROM events"
    ).fetchall()

    conn.close()

    return jsonify([dict(event) for event in events])


@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Registration data is required"
        }), 400

    event_id = data.get("event_id")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    if not event_id or not name or not email or not phone:
        return jsonify({
            "error": "Event ID, name, email and phone are required"
        }), 400

    conn = sqlite3.connect("database.db")

    event = conn.execute(
        "SELECT id FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    if not event:
        conn.close()
        return jsonify({
            "error": "Event not found"
        }), 404

    conn.execute("""
        INSERT INTO registrations
        (event_id, name, email, phone)
        VALUES (?, ?, ?, ?)
    """, (event_id, name, email, phone))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Registration successful"
    })


@app.route("/registrations", methods=["GET"])
def get_registrations():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    registrations = conn.execute("""
        SELECT
            registrations.id,
            registrations.event_id,
            events.name AS event_name,
            registrations.name,
            registrations.email,
            registrations.phone
        FROM registrations
        JOIN events
        ON registrations.event_id = events.id
    """).fetchall()

    conn.close()

    return jsonify([
        dict(registration)
        for registration in registrations
    ])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)