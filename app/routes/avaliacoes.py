#Rota para salvar avaliação
from flask import Blueprint, request, session, redirect,flash,url_for
from app.dados import Formulario,Usuario_padrao
from types import SimpleNamespace

formulario_bp = Blueprint('formulario', __name__)

@formulario_bp.route('/avaliar', methods=['POST'])
def avaliar():
    #verifica se tem algum usuário logado(caso não, vai para a sessão de login)
    if not session.get('usuario_id'):
        flash('Faça login para enviar uma avaliação.')
        return redirect('/login')
    #verifica se o usuário já enviou uma avaliação antes - bloqueando caso já tenha enviado
    if session.get("ja_avaliou"):
        flash('Você já enviou uma avaliação. Obrigado!')
        return redirect('/')
    
    #coleta os dados do formulário(se não tiver, atribui os valores 0 e "Nada")
    estrelas = int(request.form.get('estrelas', 0))
    comentario = request.form.get('comentario', 'Nada')

    #O SimpleNamespace cria um objeto rápido(não precisamos de uma classe para isso)
    usuario = SimpleNamespace(id = session.get('usuario_id'),
    nome = session.get('usuario_nome'))

    #Cria e salva o formulário enviado
    Formulario(estrelas=estrelas,comentario=comentario,usuario=usuario)
    
    # Marca no objeto do usuário que já avaliou
    usuario_obj = next((u for u in Usuario_padrao.USUARIOS if u.id == session.get('usuario_id')), None)
    if usuario_obj:
        usuario_obj.ja_avaliou = True

    #Marca na sessão que "ja_avaliou" como True
    session['ja_avaliou'] = True

    flash('Avaliação enviada com sucesso! Obrigado por contribuir.')
    return redirect(url_for('cidades.index'))