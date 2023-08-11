
from decimal import Decimal
from flask import render_template
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
        
        if user:
            # Recupere a lista de produtos do banco de dados
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            
            return render_template('dashboard.html', current_user=user, products=products)
    
    flash('Faça login para acessar o dashboard.', 'warning')
    return redirect(url_for('login'))


# Rota do Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout bem-sucedido.', 'info')
    return redirect(url_for('index'))


# Rota para listar produtos
@app.route('/products')
def products():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return render_template('products.html', products=products)


# Dentro do arquivo app.py


# Rota para adicionar produto
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        product_price = Decimal(request.form['product_price'].replace(',', '.'))  # Converter formato

        cursor = db.cursor()
        cursor.execute("INSERT INTO products (name, description, price) VALUES (%s, %s, %s)",
                       (product_name, product_description, product_price))
        db.commit()
        cursor.close()

        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_product.html')



# Rota para editar produto
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if product:
        if request.method == 'POST':
            # Código para atualizar o produto, igual ao anterior
            product_name = request.form['product_name']
            product_description = request.form['product_description']
            product_price = Decimal(request.form['product_price'].replace(',', '.'))  # Converter formato

            cursor.execute("UPDATE products SET name = %s, description = %s, price = %s WHERE id = %s",
                           (product_name, product_description, product_price, product_id))
            db.commit()

            flash('Alterações salvas com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('edit_product.html', product=product)

    flash('Produto não encontrado.', 'danger')
    return redirect(url_for('dashboard'))


# Rota para deletar produto
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    db.commit()

    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('dashboard'))






if __name__ == '__main__':
    app.run(debug=True)
