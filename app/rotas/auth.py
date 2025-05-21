from flask import Blueprint, request, jsonify
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import pymysql

auth_bp = Blueprint('auth', __name__)
CORS(auth_bp)

def conectar():
    return pymysql.connect(
        host = 'localhost',
        user = 'root',
        passwd = '',
        database = 'adega',
        cursorclass = pymysql.cursors.DictCursor
    )

@auth_bp.route('cadastro', methods=['POST'])
def cadastro():
    
    dados = request.get_json()
    nome = dados['nome']
    email = dados['email']
    hash_senha = generate_password_hash(dados['senha'])
    print(f"Dados recebidos Nome={nome}, Email={email}, Senha={hash_senha}")

    try:
        banco = conectar()
        cursor = banco.cursor()
        cursor.execute('INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)',(nome, email, hash_senha))
        banco.commit()

        return jsonify({'Mensagem': 'Dados recebidos com sucesso'})
    except:
        return jsonify({'Mensagem': 'Erro ao cadastrar dados'})
    finally:
        banco.close()