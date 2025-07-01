import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "WordPress MCP Server is running!"

@app.route('/env')
def check_env():
    return {
        "WP_URL": os.environ.get('WP_URL', 'NOT_SET'),
        "WP_USER": os.environ.get('WP_USER', 'NOT_SET'),
        "WP_APP_PASSWORD": "SET" if os.environ.get('WP_APP_PASSWORD') else "NOT_SET"
    }
