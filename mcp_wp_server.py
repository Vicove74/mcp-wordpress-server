from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

WP_URL = "https://melanita.net/wp-json/wp/v2/pages"
WP_USER = "vicove"
WP_APP_PASS = "x18dmaUqZuYQkqIZqnl1pFNv"

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "Server is reachable!"})

@app.route("/update", methods=["POST"])
def update_page():
    data = request.get_json()
    page_id = data.get("page_id")
    new_content = data.get("new_content")

    if not page_id or not new_content:
        return jsonify({"error": "Missing page_id or new_content"}), 400

    response = requests.post(
        f"{WP_URL}/{page_id}",
        auth=(WP_USER, WP_APP_PASS),
        headers={"Content-Type": "application/json"},
        json={"content": new_content}
    )

    if response.status_code == 200:
        return jsonify({"status": "success", "details": response.json()})
    else:
        return jsonify({"status": "fail", "response": response.text}), response.status_code
