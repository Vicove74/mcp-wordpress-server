from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

WP_URL = os.getenv("WP_URL") or "https://melanita.net/wp-json/wp/v2/pages"
WP_USER = os.getenv("WP_USER") or "vicove"
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD") or "x18dmaUqZuYQkqIZqnl1pFNv"

@app.route("/mcp", methods=["POST"])
def create_or_update_page():
    data = request.get_json()
    title = data.get("title", "Без заглавие")
    content = data.get("content", "")
    status = data.get("status", "publish")

    auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

    try:
        # Потърси дали вече съществува такава страница
        search = requests.get(f"{WP_URL}?search={title}", auth=auth)
        if search.status_code == 200 and search.json():
            page_id = search.json()[0]["id"]
            wp_response = requests.put(
                f"{WP_URL}/{page_id}",
                auth=auth,
                json={"title": title, "content": content, "status": status}
            )
        else:
            wp_response = requests.post(
                WP_URL,
                auth=auth,
                json={"title": title, "content": content, "status": status}
            )

        try:
            return jsonify({
                "status_code": wp_response.status_code,
                "result": wp_response.json()
            })
        except Exception:
            return jsonify({
                "status_code": wp_response.status_code,
                "error": "Invalid JSON response",
                "text": wp_response.text
            })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
