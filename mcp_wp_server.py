from flask import Flask, request, jsonify
from wordpress_xmlrpc import Client, WordPressPage
from wordpress_xmlrpc.methods import posts, users

app = Flask(__name__)

WP_URL = "https://melanita.net/xmlrpc.php"
WP_USER = "vicove"
WP_PASS = "x18dmaUqZuYQkqIZqnl1pFNv"

client = Client(WP_URL, WP_USER, WP_PASS)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})

@app.route("/get_page", methods=["POST"])
def get_page():
    try:
        data = request.get_json()
        page_id = data.get("page_id")
        if not page_id:
            return jsonify({"status": "error", "message": "Missing page_id"}), 400

        page = client.call(posts.GetPost(page_id))

        return jsonify({
            "status": "ok",
            "page_id": page.id,
            "title": page.title,
            "content": page.content
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/update", methods=["POST"])
def update_page():
    try:
        data = request.get_json()
        page_id = data.get("page_id")
        new_content = data.get("new_content")

        if not page_id or not new_content:
            return jsonify({"status": "error", "message": "Missing page_id or new_content"}), 400

        page = client.call(posts.GetPost(page_id))
        page.content = new_content
        client.call(posts.EditPost(page_id, page))

        return jsonify({"status": "ok", "message": f"Page {page_id} updated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
