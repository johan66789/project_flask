from flask import Flask, render_template, redirect, url_for,session,flash
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)

# secret key
app.config['SECRET_KEY'] = "1234chien"

csrf = CSRFProtect(app)

# mysql configuration
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "database_flask"

# Initialize MySQL
mysql = MySQL(app)

# RegisterForm
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


# LoginForm
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("password",validators=[DataRequired()])
    submit = SubmitField("Register")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form_register = RegisterForm()
    if form_register.validate_on_submit():
        name = form_register.name.data
        email = form_register.email.data
        password = form_register.password.data
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Add data to the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO utilisateur(name, email, mdp) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html', form_register=form_register)

@app.route('/login', methods=['GET','POST'])
def login():
    form_login = LoginForm()
    if form_login.validate_on_submit():
        email = form_login.email.data
        password = form_login.password.data

        req_login = mysql.connection.cursor()
        req_login.execute("SELECT * FROM utilisateur WHERE email=%s",(email,))
        user = req_login.fetchone()
        req_login.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Connexion échouée")
            return redirect(url_for('login'))

    return render_template('login.html',form_login=form_login)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
