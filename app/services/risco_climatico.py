# Serviço de classificação de risco climático para a Área Alvo da Mudança Climática

NIVEIS_RISCO = {
    "critico":  {"label": "Crítico",  "emoji": "🔴", "ordem": 4},
    "alto":     {"label": "Alto",     "emoji": "🟠", "ordem": 3},
    "moderado": {"label": "Moderado", "emoji": "🟡", "ordem": 2},
    "baixo":    {"label": "Baixo",    "emoji": "🟢", "ordem": 1},
}


def classificar_risco(cidade):
    """Classifica o nível de risco climático de uma cidade.

    Leva em conta temperatura máxima, mínima, umidade e condição do céu
    para atribuir um dos quatro níveis: critico, alto, moderado ou baixo.

    Retorna um dicionário com as chaves 'nivel', 'label', 'emoji' e 'motivos'.
    """
    motivos = []
    nivel = "baixo"

    temp_max = cidade.temp_max if cidade.temp_max is not None else cidade.temperatura
    temp_min = cidade.temp_min if cidade.temp_min is not None else cidade.temperatura
    umidade = cidade.umidade or 0
    grupo = getattr(cidade, "grupo_condicao", "") or ""

    # ── Risco Crítico ────────────────────────────────────────────
    if temp_max is not None and temp_max >= 38:
        nivel = "critico"
        motivos.append(f"Calor extremo: máxima de {temp_max}°C")

    if temp_min is not None and temp_min <= -20:
        nivel = "critico"
        motivos.append(f"Frio extremo: mínima de {temp_min}°C")

    if grupo == "tempestade":
        if nivel != "critico":
            nivel = "alto"
        motivos.append("Condição de tempestade")

    # ── Risco Alto ───────────────────────────────────────────────
    if nivel not in ("critico",):
        if temp_max is not None and temp_max >= 33:
            if nivel == "baixo":
                nivel = "alto"
            motivos.append(f"Calor intenso: máxima de {temp_max}°C")

        if temp_min is not None and temp_min <= -5:
            if nivel == "baixo":
                nivel = "alto"
            motivos.append(f"Frio intenso: mínima de {temp_min}°C")

        if umidade >= 90:
            if nivel == "baixo":
                nivel = "alto"
            motivos.append(f"Umidade muito alta: {umidade}%")

    # ── Risco Moderado ───────────────────────────────────────────
    if nivel == "baixo":
        if temp_max is not None and temp_max >= 28:
            nivel = "moderado"
            motivos.append(f"Temperatura elevada: máxima de {temp_max}°C")

        if temp_min is not None and temp_min <= 0:
            nivel = "moderado"
            motivos.append(f"Temperatura baixa: mínima de {temp_min}°C")

        if umidade >= 80:
            nivel = "moderado"
            motivos.append(f"Umidade elevada: {umidade}%")

        if grupo in ("neve", "nevoa"):
            nivel = "moderado"
            motivos.append("Condição de neve ou névoa")

    if not motivos:
        motivos.append("Condições climáticas dentro dos parâmetros normais")

    return {
        "nivel": nivel,
        "label": NIVEIS_RISCO[nivel]["label"],
        "emoji": NIVEIS_RISCO[nivel]["emoji"],
        "ordem": NIVEIS_RISCO[nivel]["ordem"],
        "motivos": motivos,
    }


def agrupar_cidades_por_risco(cidades):
    """Retorna uma lista de tuplas (cidade, risco) ordenada do maior ao menor risco."""
    resultado = []
    for cidade in cidades:
        risco = classificar_risco(cidade)
        resultado.append((cidade, risco))

    resultado.sort(key=lambda x: x[1]["ordem"], reverse=True)
    return resultado
