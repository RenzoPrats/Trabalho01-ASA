#Aluno : Renzo Prats Silva Souza    11921ECP004
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import json
import os
from sender import RabbitMq

#Configurando a aplicação flask e o banco de dados
app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{os.path.abspath("")}/alunos.db'


db = SQLAlchemy(app)

#iniciando servidor de mensageria
server = RabbitMq(queue='alunos')
        

#Criando o objeto Aluno
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True)
    matricula = db.Column(db.String(20), unique=True)
    
    #metodo que converte os campos do objeto em json
    def to_json(self):
        return {"id": self.id, "nome": self.nome, "email": self.email, "matricula": self.matricula}


db.drop_all()
db.create_all()


#funcao que gera o response
def generate_response(status, content_name, content, mensagem=False):
    body = {}
    body[content_name] = content
     
    if mensagem:
        body["mensagem"] = mensagem
        
    return Response(json.dumps(body), status=status, mimetype="application/json")


#Routes

#route /alunos retorna todos alunos
@app.route("/alunos", methods=["GET"])
def select_alunos():
    try:
        alunos_objects = Aluno.query.all()
        alunos_json = [aluno.to_json() for aluno in alunos_objects]
        
        server.publish(payload={"Alunos":alunos_json})

        return generate_response(200, "alunos", alunos_json, "OK")
    
    except:
        return generate_response(400, "alunos", {}, "Erro ao filtrar")


#route /aluno/<id> retorna o aluno pelo id
@app.route("/aluno/<id>", methods=["GET"])
def select_aluno(id):
    aluno_object = Aluno.query.filter_by(id=id).first()
    
    try:
        aluno_json = aluno_object.to_json()
        
        server.publish(payload={"Aluno":aluno_json})
        
        return generate_response(200, "aluno", aluno_json, "OK")
    
    except:
        return generate_response(400, "aluno", {}, "Erro ao filtrar")
    


#route /aluno cria um aluno pelo metodo HTTP POST
@app.route("/aluno", methods=["POST"])
def create_aluno():
    body = request.get_json()
    
    try:
        aluno = Aluno(nome=body["nome"], email=body["email"], matricula=body["matricula"])
        db.session.add(aluno)
        db.session.commit()
        
        server.publish(payload={"Criado":{"Aluno":aluno.to_json()}})
        
        return generate_response(201, "aluno", aluno.to_json(), "Criado com sucesso")
    
    except:
        return generate_response(400, "aluno", {}, "Erro ao criar")


#route /aluno/<id> atualiza um aluno pelo metodo HTTP PUT
@app.route("/aluno/<id>", methods=["PUT"])
def update_aluno(id):
    aluno_object = Aluno.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if('nome' in body):
            aluno_object.nome = body['nome']
        if('email' in body):
            aluno_object.email = body['email']
        if('matricula' in body):
            aluno_object.matricula = body['matricula']
        
        db.session.add(aluno_object)
        db.session.commit()
        
        server.publish(payload={"Atualizado":{"Aluno":aluno_object.to_json()}})
        
        return generate_response(200, "aluno", aluno_object.to_json(), "Atualizado com sucesso")
    
    except:
        return generate_response(400, "aluno", {}, "Erro ao atualizar")


#route /aluno/<id> deleta um aluno pelo metodo HTTP DELETE
@app.route("/aluno/<id>", methods=["DELETE"])
def delete_aluno(id):
    aluno_object = Aluno.query.filter_by(id=id).first()
    
    try:
        db.session.delete(aluno_object)
        db.session.commit()
        
        server.publish(payload={"Deletado":{"Aluno":aluno_object.to_json()}})
        
        return generate_response(200, "aluno", aluno_object.to_json(), "Sucesso ao deletar")
    
    except:
        return generate_response(400, "aluno", {}, "Erro ao deletar")
    
#roda o app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')