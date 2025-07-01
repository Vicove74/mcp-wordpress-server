from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Load credentials from .env file
load_dotenv()

WP_BASE_URL = os.getenv("WP_BASE_URL")  # e.g., https://melanita.net
WP_USERNAME = os.getenv("WP_USERNAME")  # e.g., vicove
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")  # app password

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "MCP server running"})

@app.route("/update", methods=["POST"])
def update_page():
    try:
        data = request.get_json()
        page_id = data["page_id"]
        new_content = data["new_content"]

        wp_url = f"{WP_BASE_URL}/wp-json/wp/v2/pages/{page_id}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "content": new_content
        }

        response = requests.post(
            wp_url,
            auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
            headers=headers,
            json=payload
        )

        try:
            response_json = response.json()
        except Exception:
            response_json = {"error": "Invalid JSON response", "text": response.text}

        return jsonify({
            "status": "ok" if response.status_code == 200 else "error",
            "status_code": response.status_code,
            "response": response_json
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
