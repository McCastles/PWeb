
from bcrypt import hashpw, gensalt, checkpw
from dotenv import load_dotenv
from os import getenv

from flask import Flask, request, render_template, make_response, session


load_dotenv()

app = Flask(__name__)
app.debug = False

app.secret_key = getenv("SECRET_KEY")



@app.route('/register', methods=['POST'])
def register():
    
    
    return f'''
    {request.form.get("login")}
    {request.form.get("password")}
    {request.form.get("password2")}
    {request.form.get("firstname")}
    {request.form.get("lastname")}
    {request.form.get("sex")}
    {request.form.get("photo")}
    '''



users = {
    'Bartosz Chaber': {
        'fisrtname': 'Bartosz',
        'lastname': 'Chaber',
        'password': hashpw( "testtest".encode('utf8'), gensalt(4) )
    }
}

allowed_origins = ['http://localhost:5000']

# <> yields method argument
@app.route('/check/<username>', methods=['GET'])
def check(username):
    
    origin = request.headers.get('Origin')
    result = {username: 'available'}

    print(f'Got a request from {origin}')

    if username in users.keys():
        result = {username: 'taken'}
    response = make_response(result, 200)
    
    if origin:
        if origin in allowed_origins or origin.endswith(".herokuapp.com"):
            response.headers['Access-Control-Allow-Origin'] = origin
    return response


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sender/signup', methods=["GET"])
def signup_form():
    return render_template('signup.html')


@app.route('/sender/signup', methods=["POST"])
def signup():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    password = request.form.get("password")

    if firstname is None:
        return "No firstname provided", 400
    if lastname is None:
        return "No lastname provided", 400
    if password is None:
        return "No password provided", 400

    username = f'{firstname} {lastname}'
    if username in users:
        return "User exists", 409 # conflict
    else:
        users[username] = {
            'firstname': firstname,
            'lastname': lastname,
            'password': hashpw( password.encode('utf8'), gensalt(4) ),
        }
        
        print("User registered succesfully")
        response = make_response("", 301)
        response.headers["Location"] = "http://localhost:5000/sender/login"
        
        return response



@app.route('/sender/login', methods=["GET"])
def login_form():
    return render_template('login.html')


@app.route('/sender/login', methods=["POST"])
def login():
    username = request.form.get("login")
    password = request.form.get("password")

    

    if username not in users:
        return "Incorrect username or password", 401


    # print( password, password.encode('utf-8'), users[username]["password"],
        checkpw( password.encode('utf8'), users[username]["password"] ) 
    if not checkpw( password.encode('utf8'), users[username]["password"] ):

        return "Incorrect username or passworddd", 401

    session[username] = "logged-in"

    response = make_response("", 301)
    response.headers["Location"] = "http://localhost:5000/"

    return response

if __name__ == '__main__':
    # Listen to every interface
    app.run(host='127.0.0.1', port=5000)