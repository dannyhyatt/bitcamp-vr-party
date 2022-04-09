from flask import Flask

app = Flask(__name__,
            static_url_path='', 
            static_folder='')

app.run(ssl_context=('cert.pem', 'key.pem'))