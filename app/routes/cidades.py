from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, abort
from app.dados import Cidades, CIDADES_SALVAS, buscar_cidade_por_id
from app.services.filtros_cidades import FILTRO_CONDICAO_OPCOES, filtrar_cidades
from app.services.weather import buscar_clima, WeatherServiceError, normalizar_grupo_condicao
import io
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # necessário para rodar sem interface gráfica no servidor
import matplotlib.pyplot as plt

cidades_bp = Blueprint("cidades", __name__)

FILTRO_TEMPERATURA_OPCOES = [
    ("todas", "Todas as temperaturas"),
    ("mais-frias", "Mais frias"),
    ("mais-quentes", "Mais quentes"),
]

def usuario_logado():
    """Retorna o ID do usuário logado ou None"""
    return session.get("usuario_id")


def atualizar_cidade_com_dados_api(cidade):
    """Centraliza a atualizacao de uma cidade via OpenWeather."""
    dados_clima = buscar_clima(cidade.nome)
    cidade.atualizar_clima(
        temperatura=dados_clima["temperatura"],
        temp_min=dados_clima["temp_min"],
        temp_max=dados_clima["temp_max"],
        umidade=dados_clima["umidade"],
        vento=dados_clima["vento"],
        condicao=dados_clima["condicao"],
        grupo_condicao=dados_clima["grupo_condicao"],
        emoji=dados_clima["emoji"]
    )

@cidades_bp.route("/")
def index():
    """Lista todas as cidades salvas no Dashboard"""
    if not usuario_logado():
        return redirect(url_for("auth.login"))

    # A rota apenas coordena os filtros solicitados.
    filtro_temperatura = request.args.get("temperatura", "todas")
    filtro_condicao = request.args.get("condicao", "todas")
    
    cidades_filtradas = filtrar_cidades(
        CIDADES_SALVAS,
        filtro_temperatura=filtro_temperatura,
        filtro_condicao=filtro_condicao,
    )

    # Inverte a lista para mostrar da mais nova para a mais antiga
    cidades_filtradas = cidades_filtradas[::-1]

    return render_template(
        "index.html",
        cidades=cidades_filtradas,
        filtro_temperatura=filtro_temperatura,
        filtro_condicao=filtro_condicao,
        filtros_temperatura=FILTRO_TEMPERATURA_OPCOES,
        filtros_condicao=FILTRO_CONDICAO_OPCOES,
    )

@cidades_bp.route("/cidade/adicionar", methods=["GET", "POST"])
def adicionar():
    """Rota para buscar o clima e salvar uma nova cidade (SOLID: Controller)"""
    if not usuario_logado():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome_cidade = request.form.get("cidade")
        try:
            dados_clima = buscar_clima(nome_cidade)
            
            nova_cidade = Cidades(
                nome=dados_clima["nome"],
                pais=dados_clima["pais"],
                temperatura=dados_clima["temperatura"],
                temp_min=dados_clima["temp_min"],
                temp_max=dados_clima["temp_max"],
                umidade=dados_clima["umidade"],
                vento=dados_clima["vento"],
                condicao=dados_clima["condicao"],
                grupo_condicao=dados_clima["grupo_condicao"],
                emoji=dados_clima["emoji"],
                adicionado_por_id=session.get("usuario_id"),
                adicionado_por_nome=session.get("usuario_nome")
            )
            CIDADES_SALVAS.append(nova_cidade)
            
            flash(f"Cidade {nova_cidade.nome} adicionada com sucesso!", "sucesso")
            return redirect(url_for("cidades.index"))
            
        except WeatherServiceError as e:
            flash(str(e), "erro")
        except ValueError as e:
            flash(str(e), "erro")
            
    return render_template("adicionar.html")


@cidades_bp.route("/cidades/refresh", methods=["POST"])
def refresh_cidades():
    """Atualiza as cidades salvas pela API e mantém o contexto do dashboard."""
    if not usuario_logado():
        flash("Faça login para atualizar as cidades.", "erro")
        return redirect(url_for("cidades.index"))

    atualizadas = 0
    falhas = 0

    for cidade in CIDADES_SALVAS:
        try:
            atualizar_cidade_com_dados_api(cidade)
            atualizadas += 1
        except WeatherServiceError:
            falhas += 1

    if atualizadas:
        flash(f"{atualizadas} cidade(s) atualizada(s) pela API.", "sucesso")
    if falhas:
        flash(f"{falhas} cidade(s) não puderam ser atualizadas.", "erro")

    return redirect(url_for(
        "cidades.index",
        temperatura=request.form.get("temperatura", "todas"),
        condicao=request.form.get("condicao", "todas"),
    ))

@cidades_bp.route("/cidade/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    """Rota para editar a cidade. Valida permissão e atualiza API ou campos."""
    if not usuario_logado():
        return redirect(url_for("auth.login"))
        
    cidade = buscar_cidade_por_id(id)
    if not cidade:
        flash("Cidade não encontrada.", "erro")
        return redirect(url_for("cidades.index"))
        
    is_dono = session.get("usuario_id") == cidade.adicionado_por_id
    is_admin = session.get("cargo") == "admin"
    
    if not (is_dono or is_admin):
        flash("Acesso Negado! Apenas o dono ou um Administrador pode editar.", "erro")
        return redirect(url_for("cidades.index"))

    if request.method == "POST":
        if request.form.get("acao") == "refresh":
            try:
                atualizar_cidade_com_dados_api(cidade)
                flash(f"Clima de {cidade.nome} atualizado pela API com sucesso!", "sucesso")
            except WeatherServiceError as e:
                flash(f"Erro ao atualizar: {str(e)}", "erro")
        else:
            cidade.temperatura = float(request.form.get("temperatura", cidade.temperatura))
            cidade.temp_min = float(request.form.get("temp_min", cidade.temp_min or cidade.temperatura))
            cidade.temp_max = float(request.form.get("temp_max", cidade.temp_max or cidade.temperatura))
            cidade.umidade = int(request.form.get("umidade", cidade.umidade))
            cidade.vento = float(request.form.get("vento", cidade.vento))
            cidade.condicao = request.form.get("condicao", cidade.condicao)
            cidade.grupo_condicao = normalizar_grupo_condicao(cidade.condicao)
            cidade._registrar_historico()  # registra edição manual no histórico também
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

@cidades_bp.route("/cidade/grafico/<int:id>")
def grafico(id):
    """Gera e retorna o gráfico de histórico climático da cidade como PNG."""
    if not usuario_logado():
        abort(403)

    cidade = buscar_cidade_por_id(id)

    if not cidade:
        abort(404)

    # Se ainda não tem histórico suficiente, simula os últimos 10 minutos
    from datetime import datetime, timedelta
    import random

    historico = cidade.historico.copy()

    if len(historico) < 2:
        agora = datetime.now()
        # Gera 6 pontos nos últimos 10 minutos com pequenas variações
        for i in range(5, 0, -1):
            momento = agora - timedelta(minutes=i * 2)
            historico.insert(0, {
                "data": momento,
                "temperatura": round(cidade.temperatura + random.uniform(-1.5, 1.5), 1),
                "umidade":     round(cidade.umidade     + random.uniform(-3, 3), 1),
                "vento":       round(max(0, cidade.vento + random.uniform(-1, 1)), 1),
            })

    # Monta o DataFrame com o histórico (real ou simulado)
    df = pd.DataFrame(historico)
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')

    # Cria o gráfico
    fig, ax1 = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor('#ffffff')
    ax1.set_facecolor('#f8fafc')

    cor_temp  = '#ef4444'
    cor_umid  = '#3b82f6'
    cor_vento = '#10b981'

    datas = df['data'].dt.strftime('%d/%m %H:%M')

    # Temperatura no eixo esquerdo
    ax1.plot(datas, df['temperatura'], color=cor_temp, marker='o', linewidth=2, label='Temp (°C)', markersize=4)
    ax1.set_ylabel('Temp (°C)', color=cor_temp, fontsize=8)
    ax1.tick_params(axis='y', labelcolor=cor_temp)
    ax1.tick_params(axis='x', labelsize=6, rotation=30)

    # Umidade e Vento no eixo direito
    ax2 = ax1.twinx()
    ax2.plot(datas, df['umidade'],  color=cor_umid,  marker='s', linewidth=2, label='Umidade (%)',  markersize=4, linestyle='--')
    ax2.plot(datas, df['vento'],    color=cor_vento, marker='^', linewidth=2, label='Vento (km/h)', markersize=4, linestyle=':')
    ax2.set_ylabel('Umidade / Vento', fontsize=8)
    ax2.tick_params(axis='y', labelsize=7)

    # Legenda unificada
    linhas1, labels1 = ax1.get_legend_handles_labels()
    linhas2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(linhas1 + linhas2, labels1 + labels2, fontsize=7, loc='upper left')

    ax1.set_title(f'Histórico — {cidade.nome}', fontsize=9, fontweight='bold', color='#0f172a')
    fig.tight_layout()

    # Converte para PNG em memória e retorna
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return send_file(buf, mimetype='image/png')