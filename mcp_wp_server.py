import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# WordPress настройки
WP_URL = os.environ.get('WP_URL', 'https://melanita.net')
WP_USER = os.environ.get('WP_USER', '')
WP_PASS = os.environ.get('WP_PASS', '')

@app.route('/')
def home():
    return {
        "status": "running",
        "message": "WordPress MCP Server",
        "config": {
            "wp_url": WP_URL,
            "wp_user": WP_USER,
            "wp_pass_set": bool(WP_PASS)
        }
    }

@app.route('/test')
def test():
    try:
        # Проста проверка на REST API
        url = f"{WP_URL}/wp-json/wp/v2/pages?per_page=1"
        response = requests.get(url, auth=(WP_USER, WP_PASS), timeout=10)
        
        return {
            "status": "success" if response.status_code == 200 else "error",
            "wp_status": response.status_code,
            "message": "Connection test completed",
            "url_tested": url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.route('/update', methods=['POST'])
def update_page():
    try:
        data = request.get_json()
        
        if not data or 'page_id' not in data or 'new_content' not in data:
            return {"error": "Need page_id and new_content"}, 400
        
        page_id = data['page_id']
        new_content = data['new_content']
        
        # WordPress REST API URL за обновяване
        url = f"{WP_URL}/wp-json/wp/v2/pages/{page_id}"
        
        # Данни за обновяване
        payload = {"content": new_content}
        
        # Изпращане на заявката
        response = requests.post(
            url, 
            json=payload, 
            auth=(WP_USER, WP_PASS),
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "page_id": page_id,
                "message": "Page updated successfully"
            }
        else:
            return {
                "status": "error",
                "code": response.status_code,
                "message": response.text[:200]
            }, 400
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
