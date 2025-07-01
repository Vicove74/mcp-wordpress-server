
from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

@app.route("/mcp", methods=["POST"])
def handle_mcp_request():
    req = request.get_json()
    method = req.get("method")
    params = req.get("params", {})

    if method == "createPost":
        title = params.get("title", "Без заглавие")
        content = params.get("content", "")
        status = params.get("status", "publish")

        post_data = {
            "title": title,
            "content": content,
            "status": status
        }

        wp_response = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts",
            auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD),
            json=post_data
        )

        return jsonify({
            "jsonrpc": "2.0",
            "result": wp_response.json(),
            "id": req.get("id")
        })

    return jsonify({
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Методът не е намерен"},
        "id": req.get("id")
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
