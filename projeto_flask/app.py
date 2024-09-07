from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Inicializando o Flask e configurando o banco de dados SQLite
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meudb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'minhachave'  # Chave secreta para gerenciamento de sessões

# Inicializando o SQLAlchemy
db = SQLAlchemy(app)

# Configurando o gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Página de login

# Modelo de usuário para autenticação
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Carregando usuário
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modelo de mensagens
class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de cadastro
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verifica se o usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe!')
            return redirect(url_for('signup'))
        
        # Cria o novo usuário
        novo_usuario = User(username=username, password=password)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário criado com sucesso! Faça login.')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Busca o usuário no banco de dados
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            flash('Login realizado com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas. Tente novamente.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Rota para logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.')
    return redirect(url_for('index'))

# Rota protegida, acessível apenas para usuários autenticados
@app.route('/dashboard')
@login_required
def dashboard():
    return f'Bem-vindo, {current_user.username}! Esta é sua área exclusiva.'

# Rota de contato com envio de mensagem
@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form['nome']
        mensagem = request.form['mensagem']
        nova_mensagem = Mensagem(nome=nome, mensagem=mensagem)
        
        try:
            db.session.add(nova_mensagem)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return "Houve um erro ao salvar sua mensagem."
    
    return render_template('contact.html')

# Rota para exibir as mensagens salvas
@app.route('/mensagens')
def mensagens():
    todas_as_mensagens = Mensagem.query.all()  # Busca todas as mensagens no banco
    return render_template('messages.html', mensagens=todas_as_mensagens)

# Inicializando o banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
