import os
import logging
from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import json

# Настройка на логване
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# WordPress конфигурация от Environment Variables
WP_URL = os.environ.get('WP_URL', 'https://your-wordpress-site.com').rstrip('/')
WP_USER = os.environ.get('WP_USER', 'your_wp_username')
WP_PASS = os.environ.get('WP_PASS', 'your_application_password')

def get_wp_headers():
    """Създава правилните headers за WordPress REST API"""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'MCP-WordPress-Server/1.0'
    }

def test_wp_connection():
    """Тества връзката с WordPress REST API"""
    try:
        test_url = f"{WP_URL}/wp-json/wp/v2/pages"
        response = requests.get(
            test_url,
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            headers=get_wp_headers(),
            timeout=10
        )
        logger.info(f"WordPress connection test: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"WordPress connection failed: {str(e)}")
        return False

@app.route('/', methods=['GET'])
def health_check():
    """Здравна проверка и тест на WordPress връзката"""
    wp_status = test_wp_connection()
    return jsonify({
        'status': 'running',
        'wordpress_connection': wp_status,
        'wp_url': WP_URL,
        'wp_user': WP_USER[:3] + '***' if WP_USER else 'not_set'
    }), 200

@app.route('/pages', methods=['GET'])
def list_pages():
    """Списък с WordPress страници"""
    try:
        api_url = f"{WP_URL}/wp-json/wp/v2/pages"
        params = {
            'per_page': 20,
            'status': 'publish,draft'
        }
        
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            headers=get_wp_headers(),
            params=params,
            timeout=15
        )
        
        logger.info(f"List pages response: {response.status_code}")
        
        if response.status_code == 200:
            pages = response.json()
            simplified_pages = []
            for page in pages:
                simplified_pages.append({
                    'id': page['id'],
                    'title': page['title']['rendered'],
                    'slug': page['slug'],
                    'status': page['status'],
                    'modified': page['modified']
                })
            return jsonify({'status': 'success', 'pages': simplified_pages})
        else:
            return jsonify({
                'status': 'error',
                'code': response.status_code,
                'message': response.text
            }), 500
            
    except Exception as e:
        logger.error(f"Error listing pages: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/page/<int:page_id>', methods=['GET'])
def get_page(page_id):
    """Вземане на конкретна страница"""
    try:
        api_url = f"{WP_URL}/wp-json/wp/v2/pages/{page_id}"
        
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            headers=get_wp_headers(),
            timeout=15
        )
        
        logger.info(f"Get page {page_id} response: {response.status_code}")
        
        if response.status_code == 200:
            page = response.json()
            return jsonify({
                'status': 'success',
                'page': {
                    'id': page['id'],
                    'title': page['title']['rendered'],
                    'content': page['content']['rendered'],
                    'slug': page['slug'],
                    'status': page['status']
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'code': response.status_code,
                'message': response.text
            }), 404 if response.status_code == 404 else 500
            
    except Exception as e:
        logger.error(f"Error getting page {page_id}: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/update', methods=['POST'])
def update_page():
    """Обновяване на WordPress страница - подобрена версия"""
    try:
        data = request.get_json()
        
        # Валидация на входните данни
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'page_id' not in data:
            return jsonify({'error': 'page_id is required'}), 400
            
        page_id = data['page_id']
        
        # Подготвяме payload за обновяване
        payload = {}
        
        # Различни полета за обновяване
        if 'new_content' in data:
            payload['content'] = data['new_content']
        if 'title' in data:
            payload['title'] = data['title']
        if 'status' in data:
            payload['status'] = data['status']
        if 'slug' in data:
            payload['slug'] = data['slug']
            
        if not payload:
            return jsonify({'error': 'No content to update provided'}), 400
        
        # WordPress REST API URL
        api_url = f"{WP_URL}/wp-json/wp/v2/pages/{page_id}"
        
        logger.info(f"Updating page {page_id} with payload: {json.dumps(payload)}")
        
        # Правим POST заявка (НЕ PUT!)
        response = requests.post(
            api_url,
            json=payload,
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            headers=get_wp_headers(),
            timeout=30
        )
        
        logger.info(f"Update response: {response.status_code}")
        logger.info(f"Response content: {response.text[:200]}...")
        
        # Проверяваме отговора
        if response.status_code == 200:
            updated_page = response.json()
            return jsonify({
                'status': 'success',
                'page_id': page_id,
                'title': updated_page.get('title', {}).get('rendered', ''),
                'modified': updated_page.get('modified', ''),
                'link': updated_page.get('link', '')
            })
        else:
            # Детайлна грешка за дебъгване
            error_details = {
                'status': 'error',
                'code': response.status_code,
                'message': response.text,
                'url': api_url,
                'auth_user': WP_USER
            }
            
            # Специфични съобщения за грешки
            if response.status_code == 401:
                error_details['hint'] = 'Check WordPress credentials and Application Password'
            elif response.status_code == 403:
                error_details['hint'] = 'User lacks permission to edit this page'
            elif response.status_code == 404:
                error_details['hint'] = 'Page not found'
            elif response.status_code == 400:
                error_details['hint'] = 'Invalid data sent to WordPress'
                
            return jsonify(error_details), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'status': 'error', 'error': 'Request timeout'}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({'status': 'error', 'error': 'Connection error to WordPress'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/test-auth', methods=['GET'])
def test_auth():
    """Тестване на WordPress автентикация"""
    try:
        # Опитваме се да вземем информация за потребителя
        api_url = f"{WP_URL}/wp-json/wp/v2/users/me"
        
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(WP_USER, WP_PASS),
            headers=get_wp_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return jsonify({
                'status': 'success',
                'authenticated': True,
                'user': {
                    'id': user_data.get('id'),
                    'username': user_data.get('username'),
                    'roles': user_data.get('roles', []),
                    'capabilities': list(user_data.get('capabilities', {}).keys())[:10]
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'authenticated': False,
                'code': response.status_code,
                'message': response.text
            }), 401
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'authenticated': False,
            'error': str(e)
        }), 500

# За локално тестване
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
