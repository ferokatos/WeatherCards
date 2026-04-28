from app.services.weather import normalizar_grupo_condicao


FILTRO_CONDICAO_OPCOES = [
    ("todas", "Todas as condições"),
    ("ceu-limpo", "Só céu limpo"),
    ("nublado", "Só nublados"),
    ("chuva", "Só chuva"),
    ("tempestade", "Só tempestade"),
    ("neve", "Só neve"),
    ("nevoa", "Só névoa"),
    ("outros", "Outras condições"),
]


FILTROS_TEMPERATURA = {
    "mais-frias": lambda cidade: (
        cidade.temp_min if cidade.temp_min is not None else float("inf"),
        cidade.temperatura if cidade.temperatura is not None else float("inf"),
    ),
    "mais-quentes": lambda cidade: (
        cidade.temp_max if cidade.temp_max is not None else float("-inf"),
        cidade.temperatura if cidade.temperatura is not None else float("-inf"),
    ),
}


def filtrar_cidades(cidades, filtro_temperatura="todas", filtro_condicao="todas"):
    """Aplica filtros do dashboard sem acoplar a rota a regras."""
    cidades_filtradas = list(cidades)

    if filtro_condicao != "todas":
        cidades_filtradas = [
            cidade for cidade in cidades_filtradas
            if obter_grupo_condicao(cidade) == filtro_condicao
        ]

    if filtro_temperatura == "mais-quentes":
        cidades_filtradas.sort(key=FILTROS_TEMPERATURA[filtro_temperatura])
    elif filtro_temperatura == "mais-frias":
        cidades_filtradas.sort(
            key=FILTROS_TEMPERATURA[filtro_temperatura],
            reverse=True,
        )

    return cidades_filtradas


def obter_grupo_condicao(cidade):
    """Usa o grupo salvo e faz fallback para dados antigos."""
    if getattr(cidade, "grupo_condicao", None):
        return cidade.grupo_condicao

    return normalizar_grupo_condicao(getattr(cidade, "condicao", ""))