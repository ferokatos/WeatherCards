from datetime import datetime, timedelta
import requests

from app.services.weather import API_KEY, DEFAULT_LANG, DEFAULT_UNITS, WeatherServiceError, normalizar_grupo_condicao, get_emoji

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def _selecionar_janela_previsao(lista_previsoes):
    """Seleciona a melhor leitura para o próximo dia perto do horário de almoço."""
    if not lista_previsoes:
        raise WeatherServiceError("Sem dados de previsão disponíveis no momento.")

    amanha = datetime.now().date() + timedelta(days=1)

    candidatos = []
    for item in lista_previsoes:
        timestamp = item.get("dt")
        if not timestamp:
            continue
        data_item = datetime.fromtimestamp(timestamp)
        if data_item.date() == amanha:
            candidatos.append(item)

    if not candidatos:
        candidatos = lista_previsoes[:8]

    return min(
        candidatos,
        key=lambda item: abs(datetime.fromtimestamp(item["dt"]).hour - 12)
    )


def buscar_previsao_proximo_dia(nome_cidade=None, lat=None, lon=None):
    """Busca a previsão climática mais representativa para o próximo dia."""
    params = {
        "appid": API_KEY,
        "units": DEFAULT_UNITS,
        "lang": DEFAULT_LANG,
    }

    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        params["lat"] = lat
        params["lon"] = lon
    elif nome_cidade:
        params["q"] = nome_cidade
    else:
        raise WeatherServiceError("Cidade inválida para consultar previsão.")

    response = requests.get(FORECAST_URL, params=params, timeout=10)

    if response.status_code != 200:
        raise WeatherServiceError(
            f"Erro ao consultar previsão: {response.status_code} - {response.text}"
        )

    payload = response.json()
    leitura = _selecionar_janela_previsao(payload.get("list", []))

    weather_info = (leitura.get("weather") or [{}])[0]
    main = leitura.get("main", {})
    wind = leitura.get("wind", {})
    chuva_prob = leitura.get("pop", 0) or 0

    condicao_raw = weather_info.get("description") or "Condição indisponível"
    data_leitura = datetime.fromtimestamp(leitura.get("dt", 0))

    coords = payload.get("city", {}).get("coord", {})
    lat_final = coords.get("lat", lat)
    lon_final = coords.get("lon", lon)

    return {
        "data": data_leitura,
        "data_label": data_leitura.strftime("%d/%m às %Hh"),
        "temperatura": round(main.get("temp"), 1) if isinstance(main.get("temp"), (int, float)) else None,
        "temp_min": round(main.get("temp_min"), 1) if isinstance(main.get("temp_min"), (int, float)) else None,
        "temp_max": round(main.get("temp_max"), 1) if isinstance(main.get("temp_max"), (int, float)) else None,
        "umidade": int(main.get("humidity")) if isinstance(main.get("humidity"), (int, float)) else None,
        "vento": round(wind.get("speed"), 1) if isinstance(wind.get("speed"), (int, float)) else None,
        "chuva_prob": int(round(chuva_prob * 100)),
        "condicao": condicao_raw.capitalize(),
        "grupo_condicao": normalizar_grupo_condicao(condicao_raw),
        "emoji": get_emoji(condicao_raw),
        "lat": round(lat_final, 4) if isinstance(lat_final, (int, float)) else None,
        "lon": round(lon_final, 4) if isinstance(lon_final, (int, float)) else None,
    }


def gerar_alertas_eventos(previsao):
    """Gera alertas de eventos climáticos com severidade operacional."""
    alertas = []
    raio_base = 14

    chuva_prob = previsao.get("chuva_prob") or 0
    vento = previsao.get("vento") or 0
    temp_max = previsao.get("temp_max")
    temp_min = previsao.get("temp_min")
    grupo = previsao.get("grupo_condicao") or "outros"

    if grupo == "tempestade" or chuva_prob >= 70:
        alertas.append({
            "nivel": "alto",
            "titulo": "Risco de tempestade localizada",
            "descricao": "Alta chance de pancadas intensas, rajadas e baixa visibilidade em pontos da cidade.",
            "impacto": "Reforçar monitoramento de drenagem e deslocamentos no período crítico.",
        })
        raio_base = max(raio_base, 40)
    elif grupo == "chuva" or chuva_prob >= 45:
        alertas.append({
            "nivel": "moderado",
            "titulo": "Evento de chuva em evolução",
            "descricao": "Há sinal de chuva intermitente para o próximo dia, com impacto em horários de pico.",
            "impacto": "Planejar rotas com alternativa e atenção a pontos de alagamento leve.",
        })
        raio_base = max(raio_base, 28)

    if vento >= 12:
        nivel = "alto" if vento >= 18 else "moderado"
        alertas.append({
            "nivel": nivel,
            "titulo": "Rajadas de vento previstas",
            "descricao": f"Ventos estimados em até {vento} km/h podem ampliar sensação térmica e espalhar chuva.",
            "impacto": "Evitar estruturas temporárias e redobrar cuidado em áreas abertas.",
        })
        raio_base = max(raio_base, 32 if nivel == "alto" else 24)

    if isinstance(temp_max, (int, float)) and temp_max >= 33:
        alertas.append({
            "nivel": "moderado",
            "titulo": "Estresse térmico no período da tarde",
            "descricao": f"Temperatura máxima prevista de {temp_max}°C com potencial de desconforto térmico.",
            "impacto": "Hidratação e pausas em locais sombreados para atividades externas.",
        })
        raio_base = max(raio_base, 22)

    if isinstance(temp_min, (int, float)) and temp_min <= 8:
        alertas.append({
            "nivel": "moderado",
            "titulo": "Queda térmica no amanhecer",
            "descricao": f"Temperatura mínima prevista de {temp_min}°C no início do dia.",
            "impacto": "Atenção com população vulnerável e exposição prolongada ao frio.",
        })
        raio_base = max(raio_base, 22)

    if not alertas:
        alertas.append({
            "nivel": "baixo",
            "titulo": "Sem eventos críticos relevantes",
            "descricao": "A tendência é de estabilidade, sem indicação de fenômenos extremos na janela analisada.",
            "impacto": "Manter monitoramento de rotina e atualização periódica do painel.",
        })

    return alertas, raio_base


def montar_config_mapa_alerta(lat, lon, raio_km, alertas):
    """Monta configuração do mapa para desenhar a área do evento climático."""
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None

    nivel_maximo = "baixo"
    if any(alerta.get("nivel") == "alto" for alerta in alertas):
        nivel_maximo = "alto"
    elif any(alerta.get("nivel") == "moderado" for alerta in alertas):
        nivel_maximo = "moderado"

    estilos = {
        "alto": {
            "cor_linha": "#dc2626",
            "cor_preenchimento": "#fca5a5",
            "opacidade_preenchimento": 0.25,
        },
        "moderado": {
            "cor_linha": "#d97706",
            "cor_preenchimento": "#fcd34d",
            "opacidade_preenchimento": 0.22,
        },
        "baixo": {
            "cor_linha": "#16a34a",
            "cor_preenchimento": "#86efac",
            "opacidade_preenchimento": 0.2,
        },
    }

    estilo = estilos[nivel_maximo]

    return {
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "raio_metros": int(max(6000, (raio_km or 12) * 1000)),
        "nivel": nivel_maximo,
        "cor_linha": estilo["cor_linha"],
        "cor_preenchimento": estilo["cor_preenchimento"],
        "opacidade_preenchimento": estilo["opacidade_preenchimento"],
    }
