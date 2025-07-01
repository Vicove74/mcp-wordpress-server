import os
from flask import Flask, request, jsonify
import requests
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# WordPress настройки
WP_URL = os.environ.get('WP_URL', 'https://melanita.net')
WP_USER = os.environ.get('WP_USER', '')
WP_PASS = os.environ.get('WP_APP_PASSWORD', '')

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
    import socket
    import ssl
    
    debug_info = {
        "wp_url": WP_URL,
        "wp_user": WP_USER, 
        "wp_pass_set": bool(WP_PASS),
        "wp_pass_length": len(WP_PASS) if WP_PASS else 0
    }
    
    try:
        # Тест 1: Опитваме да resolve домейна
        import socket
        ip = socket.gethostbyname('melanita.net')
        debug_info["domain_ip"] = ip
        
        # Тест 2: Опитваме основна HTTP заявка
        import urllib.request
        basic_url = f"{WP_URL}/wp-json/"
        
        try:
            with urllib.request.urlopen(basic_url) as response:
                debug_info["basic_wp_json"] = "accessible"
        except Exception as e:
            debug_info["basic_wp_json_error"] = str(e)
        
        # Тест 3: Опитваме с requests
        url = f"{WP_URL}/wp-json/wp/v2/pages?per_page=1"
        print(f"Testing URL: {url}")
        print(f"Auth: {WP_USER}:{WP_PASS[:4]}...")
        
        response = requests.get(
            url, 
            auth=(WP_USER, WP_PASS), 
            timeout=10,
            verify=False,
            headers={'User-Agent': 'Railway-MCP-Server/1.0'}
        )
        
        debug_info["requests_status"] = response.status_code
        debug_info["requests_response"] = response.text[:200]
        
        return {
            "status": "success" if response.status_code == 200 else "error",
            "debug": debug_info
        }
        
    except Exception as e:
        debug_info["error"] = str(e)
        debug_info["error_type"] = type(e).__name__
        
        return {
            "status": "error",
            "debug": debug_info
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
            timeout=30,
            verify=False,  # Skip SSL verification for testing
            headers={'User-Agent': 'Railway-MCP-Server/1.0'}
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
    app.run(host='0.0.0.0', port=5000)
