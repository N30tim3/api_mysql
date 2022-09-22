# pip install flask
# pip install PyMySQL
# from app import app
# from db import mysql
#pip install -U flask-cors
#pip install cryptography
#pip install -U Werkzeug
#pip install Flask-MySQL
#pip install dotenv
from flask import Flask, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS
from datetime import timedelta
import re
from flaskext.mysql import MySQL
import pymysql

from dotenv import load_dotenv
import os

load_dotenv('.env')
user = os.environ.get("MYSQL_DATABASE_USER")
password= os.environ.get("MYSQL_DATABASE_PASSWORD")
db = os.environ.get("MYSQL_DATABASE_DB")
host = os.environ.get("MYSQL_DATABASE_HOST")
app = Flask(__name__)
app.secret_key = "secret key"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
CORS(app)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = user
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = db
app.config['MYSQL_DATABASE_HOST'] = host
mysql.init_app(app)


@app.route('/')
def home():
	if 'username' in session:
		username = session['username']
		return jsonify({'message': 'Tu haz sido logueado con ', 'Usuario': username})
	else:
		resp = jsonify({'message': 'No haz sido autorizado'})
		resp.status_code = 401
		return resp


@app.route('/login', methods=['POST'])
def login():
	conn = None;
	cursor = None;
    #session.clear()
	try:
		_json = request.json
		_username = _json['username']
		_password = _json['password']
		_email = _json['email']

		# validate the received values
		if _username and _password:
			# check user exists
			conn = mysql.connect()
			cursor = conn.cursor()

			sql = "SELECT * FROM user WHERE username=%s"
			sql_where = (_username,)

			cursor.execute(sql, sql_where)
			row = cursor.fetchone()

			if row:
				if check_password_hash(row[2], _password):
					session['username'] = row[1]
					# cursor.close()
					# conn.close()
					return jsonify({'message': 'Has iniciado sesión correctamente'})
				else:
					resp = jsonify({'message': 'Solicitud incorrecta: contraseña no válida'})
					resp.status_code = 400
					return resp
		else:
			resp = jsonify({'message': 'Solicitud incorrecta: credenciales no válidas'})
			resp.status_code = 400
			return resp

	except Exception as e:
		print(e)

	finally:
		if cursor and conn:
			cursor.close()
			conn.close()

@app.route('/register', methods=['POST', 'GET'])
def register():
    conn = None;
    cursor = None;
    
    try:
        _json = request.json
        _username = _json['username']
        _password = _json['password']
        _email = _json['email']
        
        if _username and _password and _email:
            
            conn = mysql.connect()
            cursor = conn.cursor()
            
            sql = "SELECT * FROM user WHERE username=%s" 
            sql_where = (_username,)
            
            cursor.execute(sql, sql_where)
            row = cursor.fetchone()
            
            if row:
                resp = jsonify({'message': 'La cuenta ya existe'})
                resp.status_code = 400
                return resp
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', _email):
                resp = jsonify({'message': '¡Dirección de correo electrónico no válida!'})
                resp.status_code = 400
                return resp
            elif not re.match(r'[A-Za-z0-9]+', _username):
                resp = jsonify({'message': '¡El nombre de usuario debe contener solo caracteres y números!'})
                resp.status_code = 400
                return resp
            elif not _username or not _password or not _email:
                resp = jsonify({'message': 'Por favor rellena el formulario !'})
                resp.status_code = 400
                return resp
            else:
                _hashed_password = generate_password_hash(_password)
                list_of_values = [_username, _password, _hashed_password, _email]
                print (list_of_values)
                conn = mysql.connect()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                sqlQuery = "INSERT INTO user(username, password, email) VALUES(%s, %s, %s)"
                bindData = (_username, _hashed_password, _email)
                cursor.execute(sqlQuery, bindData)
                conn.commit()
                resp = jsonify({'message': 'Se ha registrado exitosamente !'})
                return resp
                
        else:
            resp = jsonify({'message': 'Por favor rellena el formulario !'})
            resp.status_code = 400
            return resp

        
    except Exception as e:
        print(e)
        
    finally:
        if cursor and conn:
            cursor.close()
            conn.close()



@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username', None)
	return jsonify({'message' : 'Has cerrado sesión con éxito'})

		
if __name__ == "__main__":
    app.run(debug=True)