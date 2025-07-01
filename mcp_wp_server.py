@app.route("/ping", methods=["GET"])
def ping_wp():
    try:
        wp_url = "https://melanita.net/wp-json/"
        response = requests.get(wp_url, timeout=10)
        return jsonify({
            "status_code": response.status_code,
            "text": response.text[:300]  # само първите 300 символа
        })
    except Exception as e:
        return jsonify({"error": str(e)})
