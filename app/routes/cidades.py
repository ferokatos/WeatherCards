<<<<<<< HEAD
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.dados import Cidades, CIDADES_SALVAS, buscar_cidade_por_id
from app.services.weather import buscar_clima, WeatherServiceError

cidades_bp = Blueprint("cidades", __name__)

def usuario_logado():
    """Retorna o ID do usuário logado ou None"""
    return session.get("usuario_id")

@cidades_bp.route("/")
def index():
    """Lista todas as cidades salvas no Dashboard"""
    if not usuario_logado():
        return redirect(url_for("auth.login"))
    
    # Renderiza o dashboard com a lista global de cidades
    return render_template("index.html", cidades=CIDADES_SALVAS)

@cidades_bp.route("/cidade/adicionar", methods=["GET", "POST"])
def adicionar():
    """Rota para buscar o clima e salvar uma nova cidade (SOLID: Controller)"""
    if not usuario_logado():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome_cidade = request.form.get("cidade")
        try:
            # Chama o serviço (SRP)
            dados_clima = buscar_clima(nome_cidade)
            
            # Cria a entidade de dados associando a quem criou
            nova_cidade = Cidades(
                nome=dados_clima["nome"],
                pais=dados_clima["pais"],
                temperatura=dados_clima["temperatura"],
                umidade=dados_clima["umidade"],
                vento=dados_clima["vento"],
                condicao=dados_clima["condicao"],
                emoji=dados_clima["emoji"],
                adicionado_por_id=session.get("usuario_id"),
                adicionado_por_nome=session.get("usuario_nome")
            )
            # Salva no Repositório
            CIDADES_SALVAS.append(nova_cidade)
            
            flash(f"Cidade {nova_cidade.nome} adicionada com sucesso!", "sucesso")
            return redirect(url_for("cidades.index"))
            
        except WeatherServiceError as e:
            flash(str(e), "erro")
        except ValueError as e:
            flash(str(e), "erro")
            
    return render_template("adicionar.html")

@cidades_bp.route("/cidade/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    """Rota para editar a cidade. Valida permissão e atualiza API ou campos."""
    if not usuario_logado():
        return redirect(url_for("auth.login"))
        
    cidade = buscar_cidade_por_id(id)
    if not cidade:
        flash("Cidade não encontrada.", "erro")
        return redirect(url_for("cidades.index"))
        
    # Validar Permissões de Edição (Somente o Dono ou Admin)
    is_dono = session.get("usuario_id") == cidade.adicionado_por_id
    is_admin = session.get("cargo") == "admin"
    
    if not (is_dono or is_admin):
        flash("Acesso Negado! Apenas o dono ou um Administrador pode editar.", "erro")
        return redirect(url_for("cidades.index"))

    if request.method == "POST":
        # Se clicar no botão Refresh da API
        if request.form.get("acao") == "refresh":
            try:
                dados_clima = buscar_clima(cidade.nome)
                cidade.atualizar_clima(
                    temperatura=dados_clima["temperatura"],
                    umidade=dados_clima["umidade"],
                    vento=dados_clima["vento"],
                    condicao=dados_clima["condicao"],
                    emoji=dados_clima["emoji"]
                )
                flash(f"Clima de {cidade.nome} atualizado pela API com sucesso!", "sucesso")
            except WeatherServiceError as e:
                flash(f"Erro ao atualizar: {str(e)}", "erro")
        # Se for preenchimento manual do formulário
        else:
            cidade.temperatura = float(request.form.get("temperatura", cidade.temperatura))
            cidade.umidade = int(request.form.get("umidade", cidade.umidade))
            cidade.vento = float(request.form.get("vento", cidade.vento))
            cidade.condicao = request.form.get("condicao", cidade.condicao)
            flash("Dados da cidade modificados manualmente.", "sucesso")
            
        return redirect(url_for("cidades.index"))
        
    return render_template("editar.html", cidade=cidade)

@cidades_bp.route("/cidade/deletar/<int:id>", methods=["POST"])
def deletar(id):
    """Deleta uma cidade, restrito apenas a Admin."""
    if not usuario_logado() or session.get("cargo") != "admin":
        flash("Acesso Negado! Apenas Administradores podem deletar.", "erro")
        return redirect(url_for("cidades.index"))
        
    cidade = buscar_cidade_por_id(id)
    if cidade:
        CIDADES_SALVAS.remove(cidade)
        flash(f"A cidade {cidade.nome} foi excluída.", "sucesso")
    else:
        flash("Cidade não encontrada para exclusão.", "erro")
        
    return redirect(url_for("cidades.index"))
=======
# Rotas de CRUD de cidades: criar, listar, editar, deletar
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from app import db
from app.models import Cidade
cidade = Blueprint('cidade', __name__)

@cidade.route('/editar/editar/<int:id>', methods=['GET', 'POST'])
@login_required

def editar_cidade(id):
    cidade = Cidade.query.get_or_404(id)

    if not current_user.is_admin and current_user.id != cidade.user_id:
        abort(403) # probir acesso se não for admin ou dono da cidade

        if request.method == 'POST':
            #logica para editar a cidade
            cidade.nome = request.form.get('nome')

            db.session.commit()
            return redirect(url_for('cidade.listar'))
        
    return render_template('editar_cidade.html', cidade=cidade)
>>>>>>> aa6fac7 (Rotas da cidades finalizadas)
