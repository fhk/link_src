from flask import Flask

app = Flask(__name__, static_url_path='/static')

from link.views import main
