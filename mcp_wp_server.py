from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)


def wp_get(endpoint, params=None):
    return requests.get(f"{WP_URL}/wp-json/wp/v2/{endpoint}", auth=auth, params=params)


def wp_post(endpoint, data):
    return requests.post(f"{WP_URL}/wp-json/wp/v2/{endpoint}", auth=auth, json=data)


def wp_put(endpoint, data):
    return requests.put(f"{WP_URL}/wp-json/wp/v2/{endpoint}", auth=auth, json=data)


@app.route("/mcp", methods=["POST"])
def handle_request():
    req = request.get_json()
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    try:
        if method == "getPageByTitle":
            title = params.get("title")
            lang = params.get("lang", "bg")
            response = wp_get("pages", {"search": title, "lang": lang})
            return respond(req_id, response.json())

        elif method == "getTranslatedPageId":
            title = params.get("title")
            lang = params.get("lang")
            response = wp_get("pages", {"search": title})
            for page in response.json():
                if page.get("title", {}).get("rendered") == title:
                    page_id = page.get("id")
                    lang_response = wp_get(f"pages/{page_id}", {"lang": lang})
                    if lang_response.status_code == 200:
                        return respond(req_id, lang_response.json())
            return error_response(req_id, "Translation not found")

        elif method == "updatePageContentByTitle":
            title = params.get("title")
            content = params.get("content")
            lang = params.get("lang", "bg")
            response = wp_get("pages", {"search": title, "lang": lang})
            for page in response.json():
                if page.get("title", {}).get("rendered") == title:
                    page_id = page["id"]
                    update = wp_put(f"pages/{page_id}", {"content": content})
                    return respond(req_id, update.json())
            return error_response(req_id, "Page not found")

        elif method == "updateOrCreatePage":
            title = params.get("title")
            content = params.get("content")
            status = params.get("status", "publish")
            lang = params.get("lang", "bg")
            existing = wp_get("pages", {"search": title, "lang": lang})
            for page in existing.json():
                if page.get("title", {}).get("rendered") == title:
                    update = wp_put(f"pages/{page['id']}", {"content": content, "status": status})
                    return respond(req_id, update.json())
            create = wp_post("pages", {"title": title, "content": content, "status": status})
            return respond(req_id, create.json())

        else:
            return error_response(req_id, f"Unknown method '{method}'")

    except Exception as e:
        return error_response(req_id, str(e))


def respond(req_id, result):
    return jsonify({"jsonrpc": "2.0", "result": result, "id": req_id})


def error_response(req_id, message):
    return jsonify({"jsonrpc": "2.0", "error": {"code": -32000, "message": message}, "id": req_id})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
