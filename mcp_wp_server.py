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
        return create_post(params, req.get("id"))
    elif method == "updatePage":
        return update_page(params, req.get("id"))

    return jsonify({
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Методът не е намерен"},
        "id": req.get("id")
    })

def create_post(params, req_id):
    post_data = {
        "title": params.get("title", "Без заглавие"),
        "content": params.get("content", ""),
        "status": params.get("status", "publish")
    }

    wp_response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD),
        json=post_data
    )

    return jsonify({
        "jsonrpc": "2.0",
        "result": wp_response.json(),
        "id": req_id
    })

def update_page(params, req_id):
    page_id = params.get("id")
    if not page_id:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Missing page ID"},
            "id": req_id
        })

    page_data = {}
    if "title" in params:
        page_data["title"] = params["title"]
    if "content" in params:
        page_data["content"] = params["content"]
    if "status" in params:
        page_data["status"] = params["status"]

    wp_response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/pages/{page_id}",
        auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD),
        json=page_data
    )

    try:
        response_json = wp_response.json()
    except Exception as e:
        response_json = {"error": "Invalid JSON response", "text": wp_response.text}

    return jsonify({
        "jsonrpc": "2.0",
        "result": response_json,
        "status_code": wp_response.status_code,
        "id": req_id
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
