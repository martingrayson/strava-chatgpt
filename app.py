from flask import Flask
from config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN
from routes import home

app = Flask(__name__)
app.add_url_rule('/', 'home', home, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True, port=3000)