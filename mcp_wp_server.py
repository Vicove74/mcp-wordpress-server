import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "WordPress MCP Server is running!"

@app.route('/test')
def test():
    wp_url = os.environ.get('WP_URL', 'https://melanita.net')
    wp_user = os.environ.get('WP_USER', '')
    wp_pass = os.environ.get('WP_APP_PASSWORD', '')
    
    if not wp_pass:
        return {"error": "WP_APP_PASSWORD not set"}
    
    try:
        url = f"{wp_url}/wp-json/wp/v2/pages?per_page=1"
        response = requests.get(url, auth=(wp_user, wp_pass), timeout=15)
        
        return {
            "status": "ok",
            "wp_status": response.status_code,
            "url": url,
            "user": wp_user,
            "pass_length": len(wp_pass)
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    if not data:
        return {"error": "No data"}, 400
        
    page_id = data.get('page_id')
    content = data.get('new_content')
    
    if not page_id or not content:
        return {"error": "Need page_id and new_content"}, 400
    
    wp_url = os.environ.get('WP_URL', 'https://melanita.net')
    wp_user = os.environ.get('WP_USER', '')
    wp_pass = os.environ.get('WP_APP_PASSWORD', '')
    
    try:
        url = f"{wp_url}/wp-json/wp/v2/pages/{page_id}"
        payload = {"content": content}
        
        response = requests.post(url, json=payload, auth=(wp_user, wp_pass), timeout=30)
        
        if response.status_code == 200:
            return {"status": "success", "page_id": page_id}
        else:
            return {"error": response.text}, response.status_code
            
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
