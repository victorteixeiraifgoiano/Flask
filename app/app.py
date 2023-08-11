
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configurações do MySQL
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="DB_FLASK_LOGIN"
)

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]  # Armazena o ID do usuário na sessão
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        cursor.close()

        flash('Registro realizado com sucesso.', 'success')

        # Realiza o login automaticamente após o registro
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]  # Armazena o ID do usuário na sessão

        return redirect(url_for('dashboard'))

    return render_template('register.html')



# Rota do Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            return render_template('dashboard.html', current_user=user)
    
    flash('Faça login para acessar o dashboard.', 'warning')
    return redirect(url_for('login'))

# Rota do Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout bem-sucedido.', 'info')
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)
