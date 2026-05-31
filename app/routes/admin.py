from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.dados import CIDADES_SALVAS, Usuario_padrao
from app.services.inteligencia_climatica import montar_painel_admin

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
def painel():
    """Painel de Controle: Lista os usuários do sistema. Acesso apenas Admin."""
    if session.get("cargo") != "admin":
        flash("Acesso restrito. Você precisa ser administrador para ver esta página.", "erro")
        return redirect(url_for("cidades.index"))
        
    usuarios = Usuario_padrao.USUARIOS
    painel_climatico = montar_painel_admin(CIDADES_SALVAS)
    return render_template("admin.html", usuarios=usuarios, painel_climatico=painel_climatico)
