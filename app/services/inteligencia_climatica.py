from statistics import mean


CONDITION_SCORES = {
    "ceu-limpo": 94,
    "nublado": 84,
    "nevoa": 66,
    "chuva": 58,
    "neve": 42,
    "tempestade": 18,
    "outros": 72,
}


def _clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def _score_temperatura(temperatura):
    if temperatura is None:
        return 60

    distancia_ideal = abs(float(temperatura) - 23)
    return round(_clamp(100 - (distancia_ideal * 7)))


def _score_umidade(umidade):
    if umidade is None:
        return 60

    distancia_ideal = abs(float(umidade) - 52)
    return round(_clamp(100 - (distancia_ideal * 2.1)))


def _score_vento(vento):
    if vento is None:
        return 65

    vento = float(vento)
    if vento <= 1:
        return 88
    if vento <= 7:
        return 100

    excesso = vento - 7
    return round(_clamp(100 - (excesso * 8)))


def _score_condicao(grupo_condicao):
    return CONDITION_SCORES.get(grupo_condicao or "outros", CONDITION_SCORES["outros"])


def _snapshot_climatico(origem):
    if isinstance(origem, dict):
        return {
            "temperatura": origem.get("temperatura"),
            "umidade": origem.get("umidade"),
            "vento": origem.get("vento"),
            "grupo_condicao": origem.get("grupo_condicao"),
            "condicao": origem.get("condicao"),
        }

    return {
        "temperatura": getattr(origem, "temperatura", None),
        "umidade": getattr(origem, "umidade", None),
        "vento": getattr(origem, "vento", None),
        "grupo_condicao": getattr(origem, "grupo_condicao", None),
        "condicao": getattr(origem, "condicao", None),
    }


def calcular_indice_conforto(origem):
    snapshot = _snapshot_climatico(origem)
    score_temperatura = _score_temperatura(snapshot["temperatura"])
    score_umidade = _score_umidade(snapshot["umidade"])
    score_vento = _score_vento(snapshot["vento"])
    score_condicao = _score_condicao(snapshot["grupo_condicao"])

    indice = round(
        (score_temperatura * 0.45)
        + (score_umidade * 0.30)
        + (score_vento * 0.15)
        + (score_condicao * 0.10)
    )

    return _clamp(indice)


def classificar_risco(origem, indice_conforto=None):
    snapshot = _snapshot_climatico(origem)
    temperatura = snapshot["temperatura"]
    umidade = snapshot["umidade"]
    vento = snapshot["vento"]
    grupo_condicao = snapshot["grupo_condicao"] or "outros"

    if indice_conforto is None:
        indice_conforto = calcular_indice_conforto(snapshot)

    severidade = 0

    if temperatura is not None:
        if temperatura >= 35 or temperatura <= 6:
            severidade += 2
        elif temperatura >= 30 or temperatura <= 10:
            severidade += 1

    if umidade is not None:
        if umidade >= 85 and (temperatura or 0) >= 28:
            severidade += 2
        elif umidade >= 75 or umidade <= 25:
            severidade += 1

    if vento is not None:
        if vento >= 12:
            severidade += 2
        elif vento >= 8:
            severidade += 1

    if grupo_condicao in {"tempestade", "neve"}:
        severidade += 2
    elif grupo_condicao in {"chuva", "nevoa"}:
        severidade += 1

    if indice_conforto <= 40:
        severidade += 2
    elif indice_conforto <= 65:
        severidade += 1

    if severidade >= 4:
        return {
            "label": "Alto",
            "classe": "risco-alto",
            "ordem": 3,
            "score": severidade,
        }
    if severidade >= 2:
        return {
            "label": "Moderado",
            "classe": "risco-moderado",
            "ordem": 2,
            "score": severidade,
        }

    return {
        "label": "Baixo",
        "classe": "risco-baixo",
        "ordem": 1,
        "score": severidade,
    }


def calcular_tendencia(cidade):
    historico = getattr(cidade, "historico", [])
    if len(historico) < 2:
        return {
            "label": "Estável",
            "classe": "tendencia-estavel",
            "seta": "→",
            "delta": 0,
        }

    leituras_recentes = historico[-4:]
    pontuacoes = [calcular_indice_conforto(leitura) for leitura in leituras_recentes]

    referencia = mean(pontuacoes[:-1]) if len(pontuacoes) > 2 else pontuacoes[-2]
    delta = round(pontuacoes[-1] - referencia, 1)

    if delta >= 5:
        return {
            "label": "Melhorando",
            "classe": "tendencia-melhorando",
            "seta": "↑",
            "delta": delta,
        }
    if delta <= -5:
        return {
            "label": "Piorando",
            "classe": "tendencia-piorando",
            "seta": "↓",
            "delta": delta,
        }

    return {
        "label": "Estável",
        "classe": "tendencia-estavel",
        "seta": "→",
        "delta": delta,
    }


def gerar_recomendacoes(cidade, risco, tendencia):
    snapshot = _snapshot_climatico(cidade)
    temperatura = snapshot["temperatura"]
    umidade = snapshot["umidade"]
    vento = snapshot["vento"]
    grupo_condicao = snapshot["grupo_condicao"] or "outros"

    recomendacoes = []

    if temperatura is not None and temperatura >= 32:
        recomendacoes.append("Reforce a hidratação e reduza a exposição ao sol nas horas mais quentes.")
    elif temperatura is not None and temperatura <= 10:
        recomendacoes.append("Use camadas extras e priorize ambientes protegidos do frio.")

    if umidade is not None and umidade >= 80 and (temperatura or 0) >= 28:
        recomendacoes.append("Procure locais ventilados para evitar sensação térmica abafada.")
    elif umidade is not None and umidade <= 30:
        recomendacoes.append("Mantenha hidratação frequente e atenção ao ressecamento do ar.")

    if vento is not None and vento >= 12:
        recomendacoes.append("Evite áreas abertas e proteja objetos leves por causa dos ventos fortes.")

    if grupo_condicao == "tempestade":
        recomendacoes.append("Adie deslocamentos ao ar livre até a instabilidade perder força.")
    elif grupo_condicao == "chuva":
        recomendacoes.append("Saia com proteção extra contra chuva e reserve mais tempo para deslocamentos.")
    elif grupo_condicao == "nevoa":
        recomendacoes.append("Redobre a atenção em trajetos com baixa visibilidade.")
    elif grupo_condicao == "neve":
        recomendacoes.append("Evite superfícies escorregadias e revise o vestuário térmico antes de sair.")

    if tendencia["label"] == "Piorando":
        recomendacoes.append("As últimas leituras mostram piora; reavalie atividades externas ao longo do dia.")
    elif tendencia["label"] == "Melhorando":
        recomendacoes.append("O cenário está melhorando, mas siga monitorando novas atualizações.")

    if risco["label"] == "Alto" and not recomendacoes:
        recomendacoes.append("Condições exigem cautela extra nas próximas horas.")
    elif not recomendacoes:
        recomendacoes.append("Condições relativamente equilibradas para atividades ao ar livre.")

    return recomendacoes[:3]


def enriquecer_cidade(cidade):
    indice_conforto = calcular_indice_conforto(cidade)
    risco = classificar_risco(cidade, indice_conforto)
    tendencia = calcular_tendencia(cidade)
    recomendacoes = gerar_recomendacoes(cidade, risco, tendencia)

    dados_cidade = vars(cidade).copy()
    dados_cidade["insights"] = {
        "indice_conforto": indice_conforto,
        "risco": risco,
        "tendencia": tendencia,
        "recomendacoes": recomendacoes,
    }
    return dados_cidade


def enriquecer_cidades(cidades):
    return [enriquecer_cidade(cidade) for cidade in cidades]


def _gerar_pontos_sparkline(valores):
    if not valores:
        return []

    menor = min(valores)
    maior = max(valores)
    amplitude = max(maior - menor, 1)
    largura = 100
    altura = 42

    pontos = []
    total = max(len(valores) - 1, 1)
    for indice, valor in enumerate(valores):
        eixo_x = round((indice / total) * largura, 2)
        eixo_y = round(altura - (((valor - menor) / amplitude) * altura), 2)
        pontos.append(f"{eixo_x},{eixo_y}")

    return pontos


def calcular_evolucao_media(cidades, limite=6):
    historicos = [getattr(cidade, "historico", []) for cidade in cidades if getattr(cidade, "historico", None)]
    if not historicos:
        return {
            "valores": [],
            "media_atual": None,
            "variacao": 0,
            "sparkline_points": [],
        }

    maior_historico = max(len(historico) for historico in historicos)
    janela = min(limite, maior_historico)
    medias = []

    for indice_inverso in range(janela - 1, -1, -1):
        leituras = []
        for historico in historicos:
            if len(historico) > indice_inverso:
                leituras.append(calcular_indice_conforto(historico[-(indice_inverso + 1)]))

        if leituras:
            medias.append(round(mean(leituras), 1))

    variacao = round(medias[-1] - medias[0], 1) if len(medias) > 1 else 0

    return {
        "valores": medias,
        "media_atual": medias[-1] if medias else None,
        "variacao": variacao,
        "sparkline_points": _gerar_pontos_sparkline(medias),
    }


def montar_painel_admin(cidades, limite=5):
    cidades_enriquecidas = enriquecer_cidades(cidades)

    mais_confortaveis = sorted(
        cidades_enriquecidas,
        key=lambda cidade: cidade["insights"]["indice_conforto"],
        reverse=True,
    )[:limite]

    maior_risco = sorted(
        cidades_enriquecidas,
        key=lambda cidade: (
            cidade["insights"]["risco"]["ordem"],
            cidade["insights"]["risco"]["score"],
            100 - cidade["insights"]["indice_conforto"],
        ),
        reverse=True,
    )[:limite]

    return {
        "mais_confortaveis": mais_confortaveis,
        "maior_risco": maior_risco,
        "evolucao_media": calcular_evolucao_media(cidades),
    }