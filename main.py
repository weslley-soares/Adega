from flask import Flask, request, jsonify
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
from flask_cors import CORS
import traceback
from datetime import timedelta

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = '123abc'  # para uso futuro com JWT
jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30) 

def conectar():
    return pymysql.connect(
        host='localhost',
        user='root',
        passwd='',
        database='adega',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()

    if not all(k in dados for k in ('nome', 'email', 'senha')):
        return jsonify({'Mensagem': 'Dados incompletos'}), 400

    nome = dados['nome']
    email = dados['email']
    hash_senha = generate_password_hash(dados['senha'])

    try:
        banco = conectar()
        cursor = banco.cursor()

        # Verificar duplicidade de email
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        if cursor.fetchone():
            return jsonify({'Mensagem': 'E-mail já cadastrado'}), 409

        cursor.execute(
            'INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)',
            (nome, email, hash_senha)
        )
        banco.commit()

        return jsonify({'Mensagem': 'Usuário cadastrado com sucesso'}), 201

    except Exception as e:
        print("Erro ao cadastrar:", e)
        traceback.print_exc()
        return jsonify({'Mensagem': 'Erro ao cadastrar dados'}), 500

    finally:
        banco.close()


#Login
@app.route('/login', methods=['POST'])
def login():

    dados = request.get_json()
    email = dados['email']
    senha = dados['senha']
    print(f"Dados recebidos Email={email}, Senha={senha}")

    banco = conectar()
    cursor = banco.cursor()
    cursor.execute('SELECT user_id, email, senha FROM usuario WHERE email = %s', (email,))
    usuario = cursor.fetchone()
    banco.close()

    if usuario and check_password_hash(usuario['senha'], senha):
        identit_data = {
            'user_id': usuario['user_id'],
            'email': usuario['email']
        }
        token = create_access_token(identity=identit_data)
        return jsonify({'token': token})
    else:
        return jsonify({'Mensagem': 'Erro ao fazer login'})
    

#Perfil
@app.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():

    user = get_jwt_identity()
    id = user['user_id']
    
    banco = conectar()
    cursor = banco.cursor()
    cursor.execute('SELECT user_id, nome, email FROM usuario WHERE user_id = %s', (id,))
    usuario = cursor.fetchone()
    banco.close()

    return jsonify(usuario)


#Cadastro de Produtos
@app.route('/cadProduto', methods=['POST'])
@jwt_required()
def cadProduto():
    user = get_jwt_identity()
    id = user['user_id']

    dados = request.get_json()
    nome =  dados['nome']
    quantidade = dados['quantidade']
    descricao = dados['descricao']
    validade = dados['validade']
    print(f"Dados Nome={nome}, Quantidade={quantidade}, Descrição={descricao}, Validade={validade}")

    try:
        banco = conectar()
        cursor = banco.cursor()
        cursor.execute('INSERT INTO produtos (fk_user_id, nome, quantidade, descricao, dt_validade) VALUES (%s, %s, %s, %s, %s)', (id, nome, quantidade, descricao, validade))
        banco.commit()
        return jsonify({'Mensagem': 'Produto cadastrado com sucesso'})
    except:
        return jsonify({'Mensagem': 'Erro ao cadastrar produto'})
    finally:
        banco.close()


#Produtos
@app.route('/produto', methods=['GET'])
@jwt_required()
def produto():
    #Pegando o ID do usuário
    user = get_jwt_identity()
    id = user['user_id']

    banco = conectar()
    cursor = banco.cursor()
    cursor.execute('SELECT produtos_id, fk_user_id, nome, descricao, dt_validade, dt_adicionado FROM produtos WHERE fk_user_id = %s', (id,))
    produto = cursor.fetchall()
    banco.close()

    return jsonify(produto)

if __name__ == '__main__':
    app.run(debug=True)