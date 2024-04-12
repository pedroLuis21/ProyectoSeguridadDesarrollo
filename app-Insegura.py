from flask import Flask, request, render_template, flash, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(1)

def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Crea la tabla de usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                     )''')

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

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username='{}' AND password='{}'".format(username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        return "Inicio de sesión exitoso como {}".format(username)
        
    else:
        flash("Nombre de usuario o contraseña incorrectos")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
