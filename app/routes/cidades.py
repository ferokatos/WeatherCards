from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, abort
from app.dados import Cidades, CIDADES_SALVAS, buscar_cidade_por_id
from app.services.filtros_cidades import FILTRO_CONDICAO_OPCOES, filtrar_cidades
from app.services.inteligencia_climatica import enriquecer_cidades
from app.services.weather import buscar_clima, WeatherServiceError, normalizar_grupo_condicao
from app.services.previsao_alertas import buscar_previsao_proximo_dia, gerar_alertas_eventos, montar_config_mapa_alerta
from datetime import datetime, timedelta
import io
import random
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
        emoji=dados_clima["emoji"],
        lat=dados_clima["lat"],
        lon=dados_clima["lon"],
    )


def preparar_historico_para_grafico(cidade):
    """Expande um histórico muito curto para uma janela visual mais útil."""
    historico = [registro.copy() for registro in cidade.historico]

    if not historico:
        return []

    historico.sort(key=lambda registro: registro["data"])

    if len(historico) == 1:
        return gerar_historico_simulado(cidade, historico[-1], quantidade=6, intervalo_horas=4)

    intervalo_total = historico[-1]["data"] - historico[0]["data"]
    if len(historico) < 6 or intervalo_total < timedelta(hours=6):
        return gerar_historico_simulado(cidade, historico[-1], quantidade=6, intervalo_horas=4)

    return historico


def gerar_historico_simulado(cidade, referencia, quantidade=6, intervalo_horas=4):
    """Gera pontos auxiliares para o gráfico quando a coleta real ainda é muito recente."""
    base_temperatura = referencia.get("temperatura", cidade.temperatura)
    base_umidade = referencia.get("umidade", cidade.umidade)
    base_vento = referencia.get("vento", cidade.vento)
    momento_final = referencia.get("data", datetime.now())

    historico_simulado = []
    for indice in range(quantidade, 0, -1):
        fator = indice / quantidade
        historico_simulado.append({
            "data": momento_final - timedelta(hours=indice * intervalo_horas),
            "temperatura": round(base_temperatura + random.uniform(-2.4, 2.4) * fator, 1),
            "umidade": round(max(0, min(100, base_umidade + random.uniform(-8, 8) * fator)), 1),
            "vento": round(max(0, base_vento + random.uniform(-2.5, 2.5) * fator), 1),
        })

    historico_simulado.append({
        "data": momento_final,
        "temperatura": base_temperatura,
        "umidade": base_umidade,
        "vento": base_vento,
    })

    return historico_simulado

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
    cidades_dashboard = enriquecer_cidades(cidades_filtradas)

    return render_template(
        "index.html",
        cidades=cidades_dashboard,
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
                lat=dados_clima["lat"],
                lon=dados_clima["lon"],
                adicionado_por_id=session.get("usuario_id"),
                adicionado_por_nome=session.get("usuario_nome")
            )
            CIDADES_SALVAS.append(nova_cidade)
            
            flash(f"Cidade {nova_cidade.nome} adicionada com sucesso!", "sucesso")
            session["pode_avaliar"] = True
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
    session["pode_avaliar"] = True
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
        session["pode_avaliar"] = True   
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


@cidades_bp.route("/cidade/detalhes/<int:id>")
def detalhes(id):
    """Exibe previsão do próximo dia, alertas e área afetada no mapa."""
    if not usuario_logado():
        return redirect(url_for("auth.login"))

    cidade = buscar_cidade_por_id(id)
    if not cidade:
        flash("Cidade não encontrada.", "erro")
        return redirect(url_for("cidades.index"))

    lat = getattr(cidade, "lat", None)
    lon = getattr(cidade, "lon", None)

    try:
        previsao = buscar_previsao_proximo_dia(
            nome_cidade=f"{cidade.nome},{cidade.pais}" if cidade.pais else cidade.nome,
            lat=lat,
            lon=lon,
        )
    except WeatherServiceError:
        previsao = {
            "data_label": "Amanhã",
            "temperatura": cidade.temperatura,
            "temp_min": cidade.temp_min,
            "temp_max": cidade.temp_max,
            "umidade": cidade.umidade,
            "vento": cidade.vento,
            "chuva_prob": 35,
            "condicao": cidade.condicao,
            "grupo_condicao": cidade.grupo_condicao,
            "emoji": cidade.emoji,
            "lat": lat,
            "lon": lon,
        }

    if lat is None:
        lat = previsao.get("lat")
    if lon is None:
        lon = previsao.get("lon")

    alertas, raio_afetado_km = gerar_alertas_eventos(previsao)
    mapa_config = montar_config_mapa_alerta(lat, lon, raio_afetado_km, alertas)

    return render_template(
        "details.html",
        cidade=cidade,
        previsao=previsao,
        alertas=alertas,
        raio_afetado_km=raio_afetado_km,
        mapa_config=mapa_config,
    )

@cidades_bp.route("/cidade/grafico/<int:id>")
def grafico(id):
    """Gera e retorna o gráfico de histórico climático da cidade como PNG."""
    if not usuario_logado():
        abort(403)

    cidade = buscar_cidade_por_id(id)

    if not cidade:
        abort(404)

    historico = preparar_historico_para_grafico(cidade)

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