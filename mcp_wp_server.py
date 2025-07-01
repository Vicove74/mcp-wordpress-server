import os
import json
from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# WordPress конфигурация от Environment Variables
WP_URL = os.environ.get('WP_URL', 'https://your-wordpress-site.com')
WP_USER = os.environ.get('WP_USER', 'your_wp_username')
WP_PASS = os.environ.get('WP_PASS', 'your_application_password')

def log_message(message):
    """Проста функция за логване с timestamp"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")

@app.route('/', methods=['GET'])
def hello():
    """Основна страница за проверка дали сървърът работи"""
    return jsonify({
        "status": "running",
        "message": "WordPress MCP Server is operational",
        "endpoints": {
            "update_page": "POST /update",
            "get_page": "GET /page/<page_id>",
            "test_connection": "GET /test"
        }
    }), 200

@app.route('/test', methods=['GET'])
def test_wp_connection():
    """Тестване на връзката с WordPress без промяна на данни"""
    try:
        # Тестваме с GET заявка към WordPress REST API
        api_url = f"{WP_URL}/wp-json/wp/v2/pages"
        
        log_message(f"Testing connection to: {api_url}")
        
        response = requests.get(
            api_url,
            auth=(WP_USER, WP_PASS),
            timeout=30,
            params={'per_page': 1}  # Вземаме само 1 страница за тест
        )
        
        log_message(f"WordPress response status: {response.status_code}")
        
        if response.status_code == 200:
            pages = response.json()
            return jsonify({
                "status": "success",
                "message": "WordPress connection successful",
                "wp_url": WP_URL,
                "user": WP_USER,
                "pages_found": len(pages),
                "sample_page": pages[0] if pages else None
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "WordPress connection failed",
                "wp_url": WP_URL,
                "user": WP_USER,
                "status_code": response.status_code,
                "response": response.text[:500]  # Първите 500 символа
            }), 400
            
    except Exception as e:
        log_message(f"Connection test error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Connection test failed",
            "error": str(e),
            "wp_url": WP_URL,
            "user": WP_USER
        }), 500

@app.route('/page/<int:page_id>', methods=['GET'])
def get_page(page_id):
    """Получаване на информация за конкретна страница"""
    try:
        api_url = f"{WP_URL}/wp-json/wp/v2/pages/{page_id}"
        
        log_message(f"Getting page {page_id} from: {api_url}")
        
        response = requests.get(
            api_url,
            auth=(WP_USER, WP_PASS),
            timeout=30
        )
        
        if response.status_code == 200:
            page_data = response.json()
            return jsonify({
                "status": "success",
                "page": {
                    "id": page_data.get("id"),
                    "title": page_data.get("title", {}).get("rendered"),
                    "content": page_data.get("content", {}).get("rendered"),
                    "status": page_data.get("status"),
                    "modified": page_data.get("modified")
                }
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Page {page_id} not found or access denied",
                "status_code": response.status_code,
                "response": response.text[:500]
            }), response.status_code
            
    except Exception as e:
        log_message(f"Get page error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to get page",
            "error": str(e)
        }), 500

@app.route('/update', methods=['POST'])
def update_page():
    """Обновяване на WordPress страница"""
    try:
        # Проверка на JSON данните
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
            
        if 'page_id' not in data or 'new_content' not in data:
            return jsonify({
                "status": "error",
                "message": "Required fields: 'page_id' and 'new_content'",
                "received_fields": list(data.keys()) if data else []
            }), 400

        page_id = data['page_id']
        new_content = data['new_content']
        
        log_message(f"Updating page {page_id} with content length: {len(new_content)}")
        
        # Първо проверяваме дали страницата съществува
        api_url = f"{WP_URL}/wp-json/wp/v2/pages/{page_id}"
        
        get_response = requests.get(
            api_url,
            auth=(WP_USER, WP_PASS),
            timeout=30
        )
        
        if get_response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": f"Page {page_id} not found or not accessible",
                "status_code": get_response.status_code,
                "response": get_response.text[:500]
            }), 404
        
        # Подготвяме payload за обновяване
        # WordPress REST API очаква различен формат за съдържанието
        payload = {
            "content": new_content,
            "status": "publish"  # Уверяваме се че страницата е публикувана
        }
        
        # Добавяме допълнителни полета ако са подадени
        if 'title' in data:
            payload['title'] = data['title']
        if 'excerpt' in data:
            payload['excerpt'] = data['excerpt']
        
        log_message(f"Sending UPDATE request to: {api_url}")
        log_message(f"Payload keys: {list(payload.keys())}")
        
        # Изпращаме POST заявка за обновяване
        response = requests.post(
            api_url,
            json=payload,
            auth=(WP_USER, WP_PASS),
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        log_message(f"WordPress update response status: {response.status_code}")
        
        if response.status_code == 200:
            updated_page = response.json()
            return jsonify({
                "status": "success",
                "message": f"Page {page_id} updated successfully",
                "page_id": page_id,
                "updated_at": updated_page.get("modified"),
                "title": updated_page.get("title", {}).get("rendered"),
                "content_length": len(new_content)
            }), 200
        else:
            # Детайлно логване на грешката
            error_text = response.text
            log_message(f"Update failed with status {response.status_code}: {error_text}")
            
            try:
                error_json = response.json()
                error_message = error_json.get("message", "Unknown error")
                error_code = error_json.get("code", "unknown")
            except:
                error_message = error_text[:500]
                error_code = "parse_error"
            
            return jsonify({
                "status": "error",
                "message": "Failed to update WordPress page",
                "wp_error_code": error_code,
                "wp_error_message": error_message,
                "status_code": response.status_code,
                "page_id": page_id,
                "debug_info": {
                    "wp_url": WP_URL,
                    "user": WP_USER,
                    "payload_keys": list(payload.keys())
                }
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            "status": "error",
            "message": "Request timeout - WordPress site may be slow",
            "error_type": "timeout"
        }), 408
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "status": "error",
            "message": "Cannot connect to WordPress site",
            "error_type": "connection_error",
            "wp_url": WP_URL
        }), 503
        
    except Exception as e:
        log_message(f"Unexpected error in update_page: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Unexpected server error",
            "error": str(e),
            "error_type": "server_error"
        }), 500

@app.route('/pages', methods=['GET'])
def list_pages():
    """Листване на WordPress страници"""
    try:
        api_url = f"{WP_URL}/wp-json/wp/v2/pages"
        
        # Параметри за заявката
        params = {
            'per_page': request.args.get('per_page', 10),
            'page': request.args.get('page', 1),
            'status': 'publish'
        }
        
        response = requests.get(
            api_url,
            auth=(WP_USER, WP_PASS),
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            pages = response.json()
            simplified_pages = []
            
            for page in pages:
                simplified_pages.append({
                    "id": page.get("id"),
                    "title": page.get("title", {}).get("rendered"),
                    "status": page.get("status"),
                    "modified": page.get("modified"),
                    "link": page.get("link")
                })
            
            return jsonify({
                "status": "success",
                "pages": simplified_pages,
                "total_found": len(simplified_pages)
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to fetch pages",
                "status_code": response.status_code
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to list pages",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Локално стартиране за тестване
    app.run(debug=True, host='0.0.0.0', port=5000)
