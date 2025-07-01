from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! Server is working!"

# Премахваме if __name__ == '__main__' частта
# Railway ще използва Gunicorn вместо Flask dev server
