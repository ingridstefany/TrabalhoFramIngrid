from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ingrid:1234@localhost:3307/trabalho1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'rel'  

db = SQLAlchemy(app)


class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    end = db.Column('usu_end', db.String(256))

    def __init__(self, nome, email, senha, end):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.end = end

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__(self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))
    

    perguntas = db.relationship('Pergunta', backref='anuncio', lazy=True)

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id


class Venda(db.Model):
    __tablename__ = "ven"
    id = db.Column('ven_id', db.Integer, primary_key=True)
    nome = db.Column('ven_nome', db.String(256))
    qtd = db.Column('ven_qtd', db.Integer)
    preco = db.Column('ven_preco', db.Float)
    total = db.Column('ven_total', db.Float)
    data = db.Column('ven_data', db.Date)
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, nome, qtd, preco, total, data, usu_id):
        self.nome = nome
        self.qtd = qtd
        self.preco = preco
        self.total = total
        self.data = data
        self.usu_id = usu_id

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255))
    desc = db.Column(db.String(255))
    qtd = db.Column(db.Integer)
    preco = db.Column(db.Float)
    ven_codigo = db.Column(db.String(255))  # Nova coluna para armazenar 'Venda-1'
    total_id = db.Column(db.Float)
    usu_id = db.Column(db.Integer)

    def __init__(self, nome, desc, qtd, preco, ven_codigo, total_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.ven_codigo = ven_codigo
        self.total_id = total_id
        self.usu_id = usu_id




def buscar_anuncio_por_id(id):
    try:
        anuncio = Anuncio.query.get(id)
        return anuncio
    except Exception as e:
        print(f"Erro ao buscar anúncio por ID {id}: {str(e)}")
        return None

class Pergunta(db.Model):
    __tablename__ = 'perguntas'
    id = db.Column(db.Integer, primary_key=True)
    pergunta_texto = db.Column(db.String(255))
    resposta_texto = db.Column(db.String(255))
    
    
    anuncio_id = db.Column(db.Integer, db.ForeignKey('anuncio.anu_id'), nullable=False)


@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('pagnaoencontrada.html')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cad/usuario")
def usuario():
    usuarios = Usuario.query.all()
    return render_template('usuario.html', usuarios=usuarios, titulo="Usuario")

@app.route("/usuario/criar", methods=['POST'])
def criarusuario():
    nome = request.form.get('user')
    email = request.form.get('email')
    senha = request.form.get('passwd')
    end = request.form.get('end')
    
    usuario = Usuario(nome=nome, email=email, senha=senha, end=end)
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET', 'POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('user')
        usuario.email = request.form.get('email')
        usuario.senha = request.form.get('passwd')
        usuario.end = request.form.get('end')
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('eusuario.html', usuario=usuario, titulo="Usuario")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cad/anuncio")
def anuncio():
    anuncios = Anuncio.query.all()
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template('anuncio.html', anuncios=anuncios, categorias=categorias, usuarios=usuarios, titulo="Anuncio")




@app.route("/anuncio/criar", methods=['POST'])
def criaranuncio():
    nome = request.form.get('nome')
    desc = request.form.get('desc')
    qtd = request.form.get('qtd')
    preco = request.form.get('preco')
    cat_id = request.form.get('cat')
    usu_id = request.form.get('uso')
    
    anuncio = Anuncio(nome=nome, desc=desc, qtd=qtd, preco=preco, cat_id=cat_id, usu_id=usu_id)
    db.session.add(anuncio

)
    db.session.commit()
    return redirect(url_for('anuncio'))


@app.route("/anuncios")
def listar_anuncios():
    anuncios = Anuncio.query.all()

    for anuncio in anuncios:
        anuncio.perguntas = Pergunta.query.filter_by(anuncio_id=anuncio.id).all()

    return render_template('lista_anuncios.html', anuncios=anuncios)


@app.route("/comprar/<int:id>", methods=['GET', 'POST'])
def comprar_anuncio(id):
    if request.method == 'POST':
        anuncio = buscar_anuncio_por_id(id)
        if anuncio:
            nome = anuncio.nome
            desc = anuncio.desc
            qtd = request.form.get('quantity')
            preco = anuncio.preco

            if qtd is not None and preco is not None:
                try:
                    qtd = float(qtd)
                    preco = float(preco)
                    total_id = qtd * preco
                except ValueError as e:
                    print(f"Erro ao converter valores para float: {e}")
                    return redirect(url_for('index'))

                ven_id = id 
                ven_codigo = f"Venda-{id}" 
                usu_id = 1

                compra_info = {
                    'nome': nome,
                    'desc': desc,
                    'qtd': qtd,
                    'preco': preco,
                    'ven_codigo': ven_codigo,
                    'total_id': total_id,
                    'usu_id': usu_id
                }

                db.session.add(Compra(**compra_info))
                db.session.commit()

                anuncios = Anuncio.query.all()
                return render_template('lista_anuncios.html', anuncios=anuncios, compra_info=compra_info)

    return redirect(url_for('index'))


@app.route("/compra_sucesso")
def compra_sucesso():
    compra_info = session.pop('compra_info', None)
    if compra_info:
        return render_template('compra_sucesso.html', **compra_info)
    else:
        return "Informações de compra não encontradas"


@app.route("/anuncios/compra")
def compra():
    print("anuncio comprado")
    return ""

@app.route("/config/categoria")
def categoria():
    categorias = Categoria.query.all()
    return render_template('categoria.html', categorias=categorias, titulo='Categoria')

@app.route("/categoria/criar", methods=['POST'])
def criarcategoria():
    nome = request.form.get('nome')
    desc = request.form.get('desc')
    
    categoria = Categoria(nome=nome, desc=desc)
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/relatorios/vendas")
def relVendas():
    vendas = Venda.query.all()
    return render_template('rel_vendas.html', vendas=vendas, titulo="Venda")

@app.route("/vendas/criar", methods=['POST'])
def criarvenda():
    nome = request.form.get('nome')
    qtd = request.form.get('qtd')
    preco = request.form.get('preco')
    total = request.form.get('total')
    data = request.form.get('data')
    usu_id = request.form.get('uso')
    
    venda = Venda(nome=nome, qtd=qtd, preco=preco, total=total, data=data, usu_id=usu_id)
    db.session.add(venda)
    db.session.commit()
    return redirect(url_for('relVendas'))

@app.route("/rel_compras")
def rel_compras():
    compras = Compra.query.all()

    return render_template('rel_compras.html', compras=compras)

@app.route('/detalhesCompra/<int:id>')
def detalhesCompra(id):
    anuncio = buscar_anuncio_por_id(id)

    if anuncio:
        return render_template('detalhes_compra.html', anuncio=anuncio)
    else:
        return "Anúncio não encontrado"

@app.route("/anuncio/<int:id>/perguntas", methods=['GET', 'POST'])
def perguntas_respostas(id):
    anuncio = buscar_anuncio_por_id(id)

    if request.method == 'POST':
        pergunta_texto = request.form.get('pergunta')
        pergunta = Pergunta(pergunta_texto=pergunta_texto, anuncio_id=id)
        db.session.add(pergunta)
        db.session.commit()

    perguntas = Pergunta.query.filter_by(anuncio_id=id).all()

    return render_template('perguntas_respostas.html', anuncio=anuncio, perguntas=perguntas)


@app.route("/fazer_pergunta/<int:anuncio_id>", methods=['POST'])
def fazer_pergunta(anuncio_id):
    pergunta_texto = request.form.get('pergunta')

    pergunta = Pergunta(pergunta_texto=pergunta_texto, resposta_texto=None, anuncio_id=anuncio_id)
    db.session.add(pergunta)
    db.session.commit()

    
    anuncio = buscar_anuncio_por_id(anuncio_id)

    
    return render_template('lista_anuncios.html', anuncios=[anuncio])



def criar_tabelas():
    with app.app_context():
        db.create_all()

criar_tabelas()

if __name__ == "__main__":
    app.run(debug=True)