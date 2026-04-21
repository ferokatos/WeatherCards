# app/routes/auth.py
# Sessões de login/cadastro de usuário

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..dados import Usuario_padrao, UsuarioAdmin

# Registra esse arquivo como um grupo de rotas
auth_bp = Blueprint("auth", __name__)


# ── Função auxiliar de busca ────────────────────────────────
def buscar_usuario(email, senha):
    """
    Percorre a lista USUARIOS buscando email e senha.
    Retorna o usuário se encontrar, ou None se não encontrar.
    """
    for user in Usuario_padrao.USUARIOS:
        if user.email == email and user.senha == senha:
            return user
    return None  # não encontrou ninguém


# ── Login ───────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # GET  → só exibe o formulário
    # POST → processa os dados digitados
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = buscar_usuario(email, senha)

        if usuario:
            # Salva os dados na sessão
            session["usuario_id"]   = usuario.id
            session["usuario_nome"] = usuario.nome
            session["cargo"]        = usuario.cargo
            return redirect(url_for("cidades.index"))  # vai pro dashboard

        # Se não encontrou, volta pro login com mensagem de erro
        flash("Email ou senha incorretos.", "erro")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ── Cadastro ────────────────────────────────────────────────
@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome              = request.form["nome"].capitalize()
        email             = request.form["email"]
        senha             = request.form["senha"]
        confirmacao_senha = request.form["confirmacao_senha"]
        tipo_usuario      = request.form["tipo_usuario"].lower()

        # Validação da senha
        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.", "erro")
            return redirect(url_for("auth.cadastro"))

        # Validação de confirmação de senha
        if senha != confirmacao_senha:
            flash("As senhas não coincidem, tente novamente.", "erro")
            return redirect(url_for("auth.cadastro"))

        # Cria o usuário conforme o tipo escolhido
        if tipo_usuario == "admin":
            novo_usuario = UsuarioAdmin(nome, email, senha)
        elif tipo_usuario == "padrão":
            novo_usuario = Usuario_padrao(nome, email, senha)
        else:
            flash("Tipo de usuário inválido.", "erro")
            return redirect(url_for("auth.cadastro"))

        flash("Cadastro realizado com sucesso!", "sucesso")
        return redirect(url_for("auth.login"))

    return render_template("cadastro.html")


# ── Logout ──────────────────────────────────────────────────
@auth_bp.route("/logout")
def logout():
    session.clear()  # apaga tudo da sessão
    return redirect(url_for("auth.login"))