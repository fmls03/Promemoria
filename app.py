import os 
from flask import Flask, render_template, redirect, request, session, flash
from passlib.hash import sha256_crypt
from datetime import date
import sqlite3
from werkzeug.utils import secure_filename


key = os.urandom(32)
key = str(key)


UPLOAD_FOLDER = 'ImageProfiles/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__) # Modulo flask
app.config['SECRET_KEY'] = key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

email = ""
id_acc = ""
username = ""
passw = ""


@app.route('/')
def session_clear():
    logout()
    return Home()


@app.route('/Home')
def Home():
    if not session.get('logged_in'):
        return redirect('/signup')
    else:
        return redirect('/Promemoria')


@app.route('/signup', methods=('GET', 'POST'))
def signin():
    alert = "" 
    logout()
    if request.method == 'POST':
        global email
        global id_acc
        global username
        global passw
        username = str(request.form['username'])
        email = str(request.form['email'])
        passw= str(request.form['passw'])
        confirm_passw = str(request.form['confirm_passw'])
        connection = sqlite3.connect('database.db') 
        connection.row_factory = sqlite3.Row 
        signin = connection.execute('SELECT * FROM accounts WHERE email = ?', (email, )).fetchall()
        username_used = connection.execute('SELECT * FROM accounts WHERE username = ?', (username, )).fetchall()
        if (len(signin) > 0) :
            alert = ("*ACCOUNT ALREADY EXISTS*")
        elif (len(username_used) > 0):
            alert = ("*USERNAME ALREADY USED*")
        elif (passw != confirm_passw):
            alert = ("*CONFIRM THE RIGHT PASSWORD*")
        else:           
            session['logged_in'] = True 
            passw = sha256_crypt.hash(passw)  
            connection.execute('INSERT INTO accounts (email, username, passw) VALUES (?, ?, ?)', (email, username, passw))
            id_acc = connection.execute('SELECT * FROM accounts WHERE email = ?', (email, )).fetchone()[3]
            connection.commit()
            connection.close()
            return Home()


    return render_template('signup.html', alert = alert, session=session)


@app.route('/login', methods=('GET', 'POST'))
def login():
    alert=""
    account = False
    global id_acc
    global email
    global username
    global passw
    if request.method == 'POST':
        username = str(request.form['username'])
        passw = str(request.form['passw'])
        connection = sqlite3.connect('database.db') 
        connection.row_factory = sqlite3.Row 
        login = connection.execute("SELECT * FROM accounts WHERE username=?", (username, )).fetchone()[2]
        email = connection.execute("SELECT * FROM accounts WHERE username = ?", (username, )).fetchone()[0]
        if sha256_crypt.verify(passw,login):
            account=True
        if account:
            session['logged_in'] = True  
            id_acc = connection.execute('SELECT * FROM accounts WHERE email = ?', (email, )).fetchone()[3]
            connection.close()
            return Home()
        else:
            alert = "*WRONG CREDENTIALS*"

                               
    return render_template('login.html', alert=alert, session=session)


@app.route("/forgotten_credential", methods=("GET", "POST"))
def reset_password():
    global email
    alert =""
    if not session.get("logged_in"):
        if request.method == "POST":
            email = str(request.form['email'])
            connection = sqlite3.connect('database.db')
            connection.row_factory = sqlite3.Row
            check_email = connection.execute("SELECT * FROM accounts WHERE email = ?", (email, )).fetchone()[0]
            if (len(check_email) > 0) :
                print(check_email)
            else:
                alert = ("*THIS EMAIL IS NOT REGISTERED*")

    else:
        return redirect("/Promemoria")

    return render_template ("forgotten_credential.html", alert=alert)

     
@app.route('/Promemoria') # Home page della web app
def index():
    if not session.get('logged_in'):
        return Home()
    else: 
        posts= ""
        connection = sqlite3.connect('database.db') # Connessione al database
        connection.row_factory = sqlite3.Row # Organizzazione in righe
        posts = connection.execute('SELECT * FROM posts WHERE id_acc = ?', (id_acc, )).fetchall() # Selezioniamo dal db le righe e memoriziamole nella lista di promemoria 'posts'   
        connection.commit()
        connection.close()
    return render_template('index.html', posts=posts, username=username)


@app.route('/<int:idx>/delete', methods=('POST',))
def delete(idx): #usiamo 'idx' perchè 'id' darebbe problemi
    if session.get('logged_in'):
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        connection.execute('DELETE FROM posts WHERE id=?', (idx, ))
        connection.execute('UPDATE posts SET id = id - 1 WHERE id > ?', (idx, ))
        connection.commit()
        connection.close()
    else:
        return Home()
    return redirect('/Promemoria')


@app.route('/logout', methods=("POST", ))
def logout():
    global username
    global email
    global passw
    global id_acc
    username = ""
    email = ""
    passw = ""
    id_acc = "" 
    session['logged_in'] = False
    session.clear()
    return Home()


@app.route('/profile', methods = ('GET', 'POST'))
def profile():
    if session.get("logged_in"):
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
    else:
        return Home()
    return render_template('profile.html', username=username, email=email) 


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/changeImageProfile', methods = ('POST', ))
def changeImageProfile():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect('/profile')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/profile', filename=filename) 


@app.route('/create', methods=('GET', 'POST'))
def create():
    if session.get('logged_in'):
        if request.method == 'POST':
            today = date.today()
            title = request.form['title']
            info = request.form['info']
            connection = sqlite3.connect('database.db')
            connection.row_factory = sqlite3.Row
            connection.execute('INSERT INTO posts (title, info, today, id_acc) VALUES (?, ?, ?, ?)', (title, info, today, id_acc))
            connection.commit()
            connection.close()
            return redirect('/Promemoria')
    else:
        return Home()
    return render_template('create.html')

if __name__ == "__main__":
    app.run("localhost", 5000, debug=True)
