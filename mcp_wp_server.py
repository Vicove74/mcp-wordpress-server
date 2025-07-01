from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

WP_URL = os.getenv("WP_URL")  # Пример: https://melanita.net/wp-json/wp/v2/posts
WP_USER = os.getenv("WP_USER")  # Пример: Test
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")  # Application Password от WordPress

@app.route("/mcp", methods=["POST"])
def create_wp_post():
    data = request.get_json()

    post_data = {
        "title": data.get("title", "Без заглавие"),
        "content": data.get("content", ""),
        "status": data.get("status", "publish")
    }

    wp_response = requests.post(
        WP_URL,
        auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD),
        json=post_data
    )

    if wp_response.status_code == 201:
        return jsonify({"message": "Постът е създаден успешно!"}), 201
    else:
        return jsonify({"error": wp_response.text}), wp_response.status_code

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
