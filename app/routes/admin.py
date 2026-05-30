from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.dados import Usuario_padrao

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
def painel():
    """Painel de Controle: Lista os usuários do sistema. Acesso apenas Admin."""
    if session.get("cargo") != "admin":
        flash("Acesso restrito. Você precisa ser administrador para ver esta página.", "erro")
        return redirect(url_for("cidades.index"))
        
    usuarios = Usuario_padrao.USUARIOS
    return render_template("admin.html", usuarios=usuarios)
from app.dados import Usuario_padrao, Formulario

@admin_bp.route("/admin")
def painel():
    if session.get("cargo") != "admin":
        flash("Acesso restrito.", "erro")
        return redirect(url_for("cidades.index"))

    usuarios = Usuario_padrao.USUARIOS
    avaliacoes = Formulario.Lista_de_formularios  # ← adiciona isso!
    return render_template("admin.html", usuarios=usuarios, avaliacoes=avaliacoes)
