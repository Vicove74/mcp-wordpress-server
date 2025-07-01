from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

WP_URL = "https://melanita.net"
WP_USER = "Test"
WP_APP_PASSWORD = "S0UTTmwRhP0102DhfMn85p07".replace(" ", "")

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
