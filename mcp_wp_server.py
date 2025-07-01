from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

WP_URL = "https://melanita.net/wp-json/wp/v2/pages"
WP_USER = "vicove"
WP_APP_PASSWORD = "x18dmaUqZuYQkqIZqnl1pFNv"

auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

@app.route("/mcp", methods=["POST"])
def create_or_update_page():
    data = request.get_json()
    params = data.get("params", {})
    title = params.get("title", "Без заглавие")
    content = params.get("content", "")
    status = params.get("status", "publish")

    # Проверка дали вече има такава страница
    search_url = f"{WP_URL}?search={title}"
    search_response = requests.get(search_url, auth=auth)
    
    if search_response.status_code == 200 and search_response.json():
        # Страницата съществува – взимаме ID и ъпдейтваме
        page_id = search_response.json()[0]["id"]
        update_url = f"{WP_URL}/{page_id}"
        response = requests.put(update_url, auth=auth, json={
            "title": title,
            "content": content,
            "status": status
        })
        action = "updated"
    else:
        # Няма такава страница – създаваме нова
        response = requests.post(WP_URL, auth=auth, json={
            "title": title,
            "content": content,
            "status": status
        })
        action = "created"

    try:
        result = response.json()
    except:
        result = {"error": "Invalid JSON response", "text": response.text}

    return jsonify({
        "jsonrpc": "2.0",
        "result": result,
        "action": action,
        "status_code": response.status_code
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
