
import datetime
import uuid
import re
from os import getenv

from flask import (Flask, flash, make_response, render_template, request,
                   session, url_for)

from bcrypt import checkpw, gensalt, hashpw
from dotenv import load_dotenv
from flask_session import Session
from redis import StrictRedis
from redis.exceptions import ConnectionError
from jwt import encode, decode


# CONFIGS


# for bach: P2.5 Wczytywanie sekretów z .env
load_dotenv()
SESSION_TYPE='redis'
JWT_SECRET = getenv( 'JWT_SECRET' )
REDIS_HOST = getenv('REDIS_HOST')
REDIS_PASS = getenv('REDIS_PASS')

# for bach: P2.9 Obsługuje błędy związany z brakiem bazy danych
try:
    db = StrictRedis(host=REDIS_HOST, db=0, password=REDIS_PASS) #decode_responses=True
except ConnectionError:
    print( 'Could not connect to Redis' )

SESSION_REDIS=db


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
app.debug = False

# ses = Session(app)


fields = [
    'login',
    'firstname',
    'password',
    'lastname',
    'sex',
    'password2',
    'email'
]


regexps = {
    # 'address': '[a-z]{3,12}$',
    'recipient': '[a-z]{3,12}$',
    'weight': '^[-+]?[1-9]\d*$'
}



# ADDITIONAL FUNCTIONS

def generate_tracking_token( login, package ):
    payload = {
        'iss': "ponczkomat auth server",
        'sub': package,
        'usr': login,
        'aud': "ponczkomat tracking service",
    }
    token = encode( payload, JWT_SECRET,
        algorithm='HS256')
    return token



def is_user( login ):
    return db.hexists( f'user:{login}', 'password' )



def save_user( email, login, password ):
    salt = gensalt(5)
    password = password.encode()
    hashed = hashpw( password, salt )
    db.hset( f'user:{login}', 'password', hashed )
    return True



def verify_user( login, password ):
    password = password.encode()
    hashed = db.hget( f"user:{login}", "password" )
    if not hashed:
        print( f'ERROR: No password for {login}' )
        return False
    return checkpw( password, hashed )


def redirect( url, status=301 ):
    response = make_response('', status)
    response.headers['Location'] = url
    return response 








# ROOT ENDPOINT
@app.route('/')
def index():
    # TODO: g.user instead of render_template parameter
    return render_template('index.html', loggedin=session.get('loggedin'))



# SENDER REGISTER GET
@app.route('/sender/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html', loggedin=session.get('loggedin'))



# SENDER REGISTER POST
@app.route('/sender/signup', methods=['POST'])
def signup():

    # for bach: P2.7 Poprawna walidacja danych do redis
    ok = True

    # TODO: Additional validations (JS is not enough?)
    for field in fields:
        value = request.form.get( field )
        if value is None:
            flash( f'{field} is missing' )
            ok = False
    
    if request.form.get('password') != request.form.get('password2'):
        flash('Passwords have to match')
        ok = False
    login = request.form.get( 'login' )
    if is_user(login):
        flash(f'User {login} already exists')
        ok = False
    
    if not ok:
        return redirect(url_for('signup_form'))
    
    success = save_user(
        request.form.get('email'),
        request.form.get('login'),
        request.form.get('password'),
    )

    if not success:
        flash( 'Error while saving user' )
        return redirect(url_for('signup_form'))

    flash( f'User registered: {login}' )
    return redirect(url_for('login_form'))
    





# SENDER LOGIN GET
@app.route('/sender/login', methods=['GET'])
def login_form():
    return render_template('login.html', loggedin=session.get('loggedin'))



# SENDER LOGIN POST
@app.route('/sender/login', methods=['POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        flash( 'Please enter your login and password' )
        return redirect(url_for('login_form'))

    if not verify_user( login, password ):
        flash( 'Invalid login and/or password' )
        return redirect(url_for('login_form'))

    flash( f'Welcome, {login}!' )
    
    
    # for bach: P2.1 Unikalny identyfikator w ciasteczku?
    session[ "login" ] = login
    session[ "loggedin" ] = True
    session[ "login-time" ] = str(datetime.datetime.now())
    
    return redirect(url_for('index'))
    
    

# for bach: P2.2 Usuwane dane przy wylogowaniu
# TODO: Sometimes have to toggle 'Disable Cache' flag to make it work
# SENDER LOGOUT
@app.route('/sender/logout', methods=['GET'])
def logout():
    
    # print('logout triggered')
    session.clear()
    flash( "Logged out successfully" )
    return redirect(url_for('login_form'))




# for bach: P2.6 Pozwala na wczytywanie listy etykiet
# DASHBOARD: CREATE PACKAGE
@app.route('/sender/dashboard', methods = ['POST'])
def create_package():

    username = session.get( 'login' )
    pkg_id = str(uuid.uuid4())

    pkg_model = [
        "pkg_id",
        "pkg_sender",
        "pkg_weight",
        "pkg_address",
        "pkg_recipient",
        "pkg_sent_date",
        "pkg_delivered_date",
        "pkg_status"
    ]


    # for bach: P2.7 Poprawna walidacja danych do redis
    ok = True

    address = request.form.get('address')
    if (address == '' or address is None):
        flash('Address: must be non-empty')
        ok = False


    recipient = request.form.get('recipient')
    if (recipient == '' or recipient is None):
        flash('Recipient: must be non-empty')
        ok = False
    elif not re.search( regexps['recipient'], recipient ):
        flash('Recipient: small Latin letters, length between 3 and 12')
        ok = False

        
    weight = request.form.get('weight')
    if (weight == '' or weight is None):
        flash('Weight: must be non-empty')
        ok = False
    elif not re.search( regexps['weight'], weight ):
        flash('Weight: positive integer (kg)')
        ok = False

    if not ok:
        return redirect(url_for('dashboard'))

    row = {
        field: value for field, value in zip(
            pkg_model,
            [
                pkg_id,
                username,
                address,
                recipient,
                weight,
                str(datetime.datetime.now()),
                '-',
                'Sent'
            ]
        )
    }


    for field, value in row.items():
        db.hset( f'{username}:{pkg_id}', field, value.encode() )

    db.lpush(f"{username}:packages", pkg_id.encode())

    flash('Package sent successfully')
    
    return redirect(url_for('dashboard'))



# DASHBOARD: SHOW PACKAGES
@app.route('/sender/dashboard', methods=['GET'])
def dashboard():

    # TODO: Some better way?
    if not session.get('loggedin'):
        flash('Please log in to see packages')
        return redirect(url_for('login_form'))

    username = session.get('login')


    pids = [
        item.decode() for item in db.lrange(
            f'{username}:packages', 0, db.llen(f'{username}:packages')
        )
    ]

    # print(pids)

    tokens = {}
    for pid in pids:
        tokens[ pid ] = generate_tracking_token( username, pid ).decode()

    

    return render_template(
        'dashboard.html',
        loggedin=session.get('loggedin'),
        tokens=tokens,
        haspackages=( len(pids)>0 )
    )



# GET PACKAGE BY ID
@app.route('/package/<pid>', methods=['GET'])
def get_package( pid ):
    token = request.args.get('token')
    if token is None:
        return 'No access token', 401
    try:
        payload = decode(token, key=JWT_SECRET, algorithm=['HS256'], audience='ponczkomat tracking service')
    except jwt.InvalidTokenError as error:
        print('Invalid token error' + str(error))
        return 'Invalid access token' , 401
    if pid != payload.get('sub'):
        return 'Not aurhotized', 401

    username = session.get('login')

    package = [
        item.decode() for item in db.hvals(f'{username}:{pid}')
    ]

    # print(package)
    return render_template(
        'package.html',
        loggedin=session.get('loggedin'),
        package=package
    )



# for bach: P2.8 Pozwala na dodawanie/usuwanie etykiet
# DELETE PACKAGE
# TODO: methods=['DELETE']?
@app.route('/sender/delete_package/<pid>', methods=['POST'])
def delete_package( pid ):
    
    username = session.get('login')

    db.delete(f'{username}:{pid}')
    db.lrem(f'{username}:packages', 0, pid.encode())

    # flash('Package deleted (not really)')
    flash('Package deleted (really)')

    return redirect(url_for('dashboard'))




















if __name__ == '__main__':
    # Listen to every interface
    app.run(host='127.0.0.1', port=5000)
