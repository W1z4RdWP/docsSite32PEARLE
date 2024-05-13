from flask import Flask, render_template, url_for, redirect, request, session # type: ignore
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, hashlib
#from flask_login import LoginManager

# Запуск фреймворка сохраняется в переменной app
app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

##login_manager = LoginManager(app)


# Конфигурация БД
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "registred_users_db"
# Для работы БД, нужно запустить Apache и MySQL в XAMPP Control Panel
mysql = MySQL(app)


# Маршруты к страницам
# Основной маршрут (Начальная страница)
@app.route('/')
def index():
    
    return render_template('index.html') # название функции служит переменной в Jinja2 в HTML шаблонах
# все шаблоны строго в папке templates

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form['username']
        password = request.form['password']
        repeatPassword = request.form['repeatPassword']
        if password == repeatPassword and len(password) > 5:

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password:
                msg = 'Please fill out the form!'
            else:
                    # Хэширования паролей
                hash = password + str(app.secret_key)
                hash = hashlib.sha1(hash.encode())
                password = hash.hexdigest()

                cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s)', (username,password,))
                mysql.connection.commit()
                msg = 'Успешно зарегистрировано'
        else:
            return render_template('registerPassFail.html')
    elif request.method == 'POST':
        msg = 'Пожалуйста, заполните форму регистрации!'
    return render_template('register.html', msg=msg)

# Страница авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():

    msg = ''
    # Если пользователь авторизован - переадресуем его в профиль
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profilePage.html', account=account)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Хэширование паролей
        hash = password + str(app.secret_key)
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return the result
        account = cursor.fetchone()

         # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('welcome_page'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('loginPage.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/welcome')
def welcome_page():
    return render_template('WelcomePage.html')

@app.route('/Mikrotik')
def mikrotik_page():
    return render_template('Mikrotik.html')

@app.route('/Zabbix')
def zabbix_page():
    if 'loggedin' in session:
        return render_template('ZabbixPage.html')
    return redirect(url_for('login'))

@app.route('/Dent')
def dent_page():
    if 'loggedin' in session:
        return render_template('DentPage.html')
    return redirect(url_for('login'))

@app.route('/CT')
def ct_page():
    return render_template('CtPage.html')

@app.route('/Xray')
def xray_page():
    return render_template('RentgenPage.html')

# Прочее (Для паролей, заметок и т.д. и т.п.)
@app.route('/etc')
def etc_page():
    return render_template('etc.html')


# Выполняется запуск Flask сервера если запущен родительский файл.
if __name__ == '__main__':
    app.run(host="0.0.0.0")