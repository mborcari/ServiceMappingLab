from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "lab")
DB_PASS = os.getenv("DB_PASS", "lab123")
DB_NAME = os.getenv("DB_NAME", "labdb")

@app.route("/")
def home():
    return {
        "application": "App1 + PostgreSQL",
        "database_host": DB_HOST
    }

@app.route("/db")
def db_test():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()

        return {"status": "ok", "db_time": result[0]}

    except Exception as e:
        return {"status": "error", "details": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
