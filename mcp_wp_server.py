from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

# Финален и коректен адрес към WP REST API
WP_URL = "https://melanita.net/wp-json/wp/v2/pages"
WP_USER = "vicove"
WP_APP_PASSWORD = "x18dmaUqZuYQkqIZqnl1pFNv".replace(" ", "")

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

    try:
        response_json = wp_response.json()
    except Exception as e:
        response_json = {"error": "Invalid JSON response", "text": wp_response.text}

    return jsonify({
        "jsonrpc": "2.0",
        "result": response_json,
        "status_code": wp_response.status_code
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
