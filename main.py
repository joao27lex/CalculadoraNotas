from flask import Flask, render_template, request
import pymongo

#Pymongo
cluster = pymongo.MongoClient("mongodb+srv://joaocampanella:batatademp5@cluster0.wzgc7wv.mongodb.net/")  # Conecta ao servidor local na porta padrão
db = cluster.get_database('calculadora')
collection = db.get_collection('dados')

#Variáveis Globais
email = None
senha = None
notat1 = None
notat2 = None
notaListas = None
notaParcial = None

#Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/goto', methods = ["GET","POST"])
def goto():
    global email, senha
    if request.method == "POST":
        email = request.form.get('email')
        senha = request.form.get('senha')

        resultado = collection.find({})

        #Itera sobre o Banco de Dados e busca se o cadastro existe
        for l in resultado:
            if email == l['email']:
                return '<h1>Já existe um cadastro com esse email!</h1>'
        
        #Caso os campos de input não tenham sido preenchidos
        if email == '' or senha == '':
            return '<h1>Você precisa preencher todos os campos!</h1>'

        #Caso não seja um poli-mail
        elif senha != ''  and ('@poli.ufrj') not in email:
            return '<h1>Você precisa se cadastrar com um Poli-Mail!</h1>'
        
        #Caso a senha não tenha letra maíuscula ou caracteres especiais
        elif email != '' and senha != '' and (not(any(x.isupper() for x in senha)) or not(any('@#$%&' for x in senha))):
            return '<h1>Sua senha precisa conter ao menos um caracter especial e uma letra maiúscula.</h1>'
        
        #Caso o cadastro seja de um poli-mail e a senha contenha letras maiúsculas + caracteres especiais, ir para login
        elif ('@poli.ufrj' in email) and any(x.isupper() for x in senha) and any('@#$%&' for x in senha):
            registro = {
                'email' : email,
                'senha' : senha
            }
            #Insere email e senha no Banco de Dados
            collection.insert_one(registro)
            return render_template('login.html')
        
@app.route('/menu', methods=["POST", "GET"])
def menu():
    global email, senha

    if request.method == "POST":
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        #Busca pelo email e senha no banco de dados
        resultado = collection.find({})

        for l in resultado:
            if email == l['email'] and senha == l['senha']:
                return render_template('menu.html', email=email)
        
        else:
            return '<h1>Seu login não foi encontrado.</h1>'

@app.route('/inserir', methods=["POST", "GET"])
def inserir():
    return render_template('inserir.html')

@app.route('/consultar', methods=["POST", "GET"])
def consultar():
    global email 

    if request.method == "POST" or request.method == "GET":
        busca = collection.find({'email': email})

        for l in busca:
            if email == l['email']:
                notaFinal = l['notaParcial']
                return render_template('consultar.html', notaFinal=notaFinal)

    return '<h1>E-mail não encontrado.</h1>'

@app.route('/resultado', methods=["POST", "GET"])
def resultado():
    global email, senha, notat1, notat2, notaListas, notaParcial  # Indique que você está usando as variáveis globais 'email' e 'senha'
    if request.method == "POST":
        notat1 = float(request.form.get('notat1'))
        notat2 = float(request.form.get('notat2'))
        notaListas = request.form.get('notaListas')

        notaListas = [float(nota.strip()) for nota in notaListas.split(',')]

        somaLista = 0
        for i in notaListas:
            somaLista += i

        mediaListas = (somaLista / len(notaListas))

        #Checa se os valores fornecidos para as notas estão entre os intervalos de 0 a 10
        if (0 <= notat1 <= 10) and (0 <= notat2 <= 10) and all(0 <= n <= 10 for n in notaListas):
            notaParcial = round(((notat1 + notat2) / 2 * 0.8) + (mediaListas * 0.2), 2)
            collection.update_one(
                {'email': email,
                 'senha': senha},
                {'$set':
                {'notat1': notat1,
                'notat2': notat2,
                'notaLista': notaListas,
                'notaParcial': notaParcial}})
            return render_template('resultado.html', notaParcial = notaParcial)
        
        else:
            return '<h1>Por favor, insira valores válidos (0 a 10)</h1>'
    
if __name__ == '__main__':
    app.run()

