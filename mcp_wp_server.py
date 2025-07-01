import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# WordPress конфигурация – взима от Environment Variables или с зададени стойности по подразбиране
WP_URL = os.environ.get('WP_URL', 'https://your-wordpress-site.com')  # Базов URL на WordPress сайта
WP_USER = os.environ.get('WP_USER', 'your_wp_username')               # WordPress потребител с Application Password
WP_PASS = os.environ.get('WP_PASS', 'your_application_password')      # Application Password за горния потребител

@app.route('/update', methods=['POST'])
def update_page():
    data = request.get_json()
    if not data or 'page_id' not in data or 'new_content' not in data:
        return jsonify({'error': 'Expected JSON with "page_id" and "new_content"'}), 400

    page_id = data['page_id']
    new_content = data['new_content']

    # Изграждаме URL за WordPress REST API за съответната страница
    api_url = f"{WP_URL}/wp-json/wp/v2/pages/{page_id}"
    payload = {'content': new_content}

    try:
        # Изпращаме POST заявка за обновяване на страницата с Basic Authentication
        response = requests.post(api_url, json=payload, auth=(WP_USER, WP_PASS))
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

    # Проверяваме отговора от WordPress
    if response.status_code == 200:
        return jsonify({'status': 'success', 'page_id': page_id})
    else:
        # Връщаме детайли при неуспех (напр. грешни креденшъли или несъществуваща страница)
        return jsonify({
            'status': 'error',
            'code': response.status_code,
            'response': response.text
        }), 500

# Опционално: начална страница или здравен чек
@app.route('/', methods=['GET'])
def hello():
    return "Flask server is running!", 200

# Локално стартиране на сървъра за тест (в Railway се стартира с Gunicorn, виж по-долу)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
