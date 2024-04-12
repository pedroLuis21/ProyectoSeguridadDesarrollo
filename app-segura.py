from flask import Flask, request, render_template, flash, redirect, url_for
import sqlite3
import os
from passlib.hash import bcrypt
import re

app = Flask(__name__)
app.secret_key = os.urandom(32)

# Configuración para límites de intentos de inicio de sesión
MAX_LOGIN_ATTEMPTS = 5
BLOCK_TIME_MINUTES = 10

def create_db():
    conn = sqlite3.connect('users-segura.db')
    cursor = conn.cursor()

    # Crea la tabla de usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                     )''')

    # Verifica si la columna login_attempts
    cursor.execute('''PRAGMA table_info(users)''')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    if 'login_attempts' not in column_names:
        cursor.execute('''ALTER TABLE users
                          ADD COLUMN login_attempts INTEGER DEFAULT 0''')

    conn.commit()
    conn.close()

create_db()

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el proceso de inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Validación de entrada
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        flash("Nombre de usuario no válido")
        return redirect(url_for('index'))

    # Verifica si el usuario está bloqueado 
    conn = sqlite3.connect('users-segura.db')
    cursor = conn.cursor()
    cursor.execute("SELECT login_attempts FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result and result[0] >= MAX_LOGIN_ATTEMPTS:
        flash("Tu cuenta está bloqueada. Inténtalo de nuevo más tarde.")
        return redirect(url_for('index'))

    # Verifica las credenciales del usuario
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user and bcrypt.verify(password, user[2]):
        # Restablece el contador de intentos de inicio de sesión al iniciar sesión con éxito
        cursor.execute("UPDATE users SET login_attempts=0 WHERE username=?", (username,))
        conn.commit()
        conn.close()
        return "Inicio de sesión exitoso como {}".format(username)
    else:
        # Incrementa el contador de intentos de inicio de sesión fallidos
        if result:
            cursor.execute("UPDATE users SET login_attempts=login_attempts+1 WHERE username=?", (username,))
        else:
            cursor.execute("INSERT INTO users (username, password, login_attempts) VALUES (?, ?, 1)", (username, bcrypt.hash(password)))
        conn.commit()
        conn.close()
        flash("Nombre de usuario o contraseña incorrectos")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

