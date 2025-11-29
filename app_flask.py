from flask import Flask
import socket
import os

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "application": os.getenv("APP_NAME", "FlaskApp"),
        "hostname": socket.gethostname(),
        "message": "Hello from Flask!"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
