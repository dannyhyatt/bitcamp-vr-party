from email.policy import default
from flask import Flask
from flask import request
import psycopg2

print(1)
conn = psycopg2.connect(
    host="free-tier14.aws-us-east-1.cockroachlabs.cloud",
    database="bitcamp-hack-1163.defaultdb",
    user="danny",
    password="bfoniXZ9evI3uRqe4R2vVw",
    port="26257")

print(1)
cur = conn.cursor()
print(1)
cur.execute('SELECT version()')
db_version = cur.fetchone()
print(db_version)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "testing"

@app.route('/user', methods=['GET', 'POST'])
def user():
    print(query := "SELECT * from users WHERE username='{}';".format(request.args.get('username')))
    cur.execute(query)
    return '{}'.format(cur.fetchone())

@app.route('/signup', methods=['POST'])
def signup():
    query = "INSERT INTO users (username, password, profile_img, display_name) VALUES ('{}', '{}', '{}', '{}');".format(
        request.form.get('username'),
        request.form.get('password'),
        request.form.get('profile_img'),
        request.form.get('display_name')
    )
    # print(query)
    success = cur.execute(query)
    return 'success: {}'.format(success)

app.run(debug=True)