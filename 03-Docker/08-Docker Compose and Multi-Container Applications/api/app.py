
from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "service": "lab08-api",
        "message": "Docker Compose lab API is running"
    })

@app.route("/db-health")
def db_health():
    try:
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            connect_timeout=3
        )
        conn.close()
        return jsonify({"database": "connected"}), 200
    except Exception as exc:
        app.logger.exception("Database health check failed")
        return jsonify({
            "database": "unavailable",
            "error": str(exc)
        }), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
