from flask import Flask, request, render_template, make_response
app = Flask(__name__)
app.debug = False




@app.route('/register', methods=['POST'])
def register():
    return 'OK'



users = {
    'chaberb': {'fisrtname': 'Bartosz', 'lastname': 'Chaber'}
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

@app.route('/sender/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    # Listen to every interface
    app.run(host='127.0.0.1', port=5000)