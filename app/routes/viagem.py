import math
import requests
from flask import Blueprint, render_template, request, flash

from app.services.weather import (
    API_KEY, DEFAULT_UNITS, DEFAULT_LANG,
    WeatherServiceError, normalizar_grupo_condicao, get_emoji
)

viagem_bp = Blueprint('viagem', __name__)

# --- ROTA DO FLASK ---
@viagem_bp.route('/planejar-viagem', methods=['GET', 'POST'])
def planejar():
    # Puxa diretamente a lista real de objetos que está no seu app/dados.py
    try:
        from app.dados import CIDADES_SALVAS
        cidades_usuario = CIDADES_SALVAS
    except Exception:
        cidades_usuario = []

    if request.method == 'POST':
        origem = request.form.get('origem')
        destino = request.form.get('destino')
        
        if not origem or not destino:
            flash("Por favor, selecione a origem e o destino.", "perigo")
            return render_template('viagem.html', cidades=cidades_usuario)
            
        try:
            # Chama a função de planejamento que está logo abaixo
            dados_viagem = planejar_viagem(origem, destino)
            return render_template('viagem_resultado.html', viagem=dados_viagem)
        except Exception as e:
            flash(f"Erro ao planejar rota: {str(e)}", "perigo")
            
    return render_template('viagem.html', cidades=cidades_usuario)


# --- FUNÇÕES DE LÓGICA E APIS ---
FIND_URL = "https://api.openweathermap.org/data/2.5/find"
GEO_URL  = "https://api.openweathermap.org/geo/1.0/direct"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def geocodificar(nome_cidade: str) -> dict:
    """Converte nome de cidade em coordenadas usando a API de geocodificação."""
    if not nome_cidade or not nome_cidade.strip():
        raise ValueError("O nome da cidade não pode ser vazio.")

    params = {"q": nome_cidade, "limit": 1, "appid": API_KEY}
    try:
        resp = requests.get(GEO_URL, params=params, timeout=10)
    except requests.RequestException:
        raise WeatherServiceError("Falha de conexão ao geocodificar a cidade.")

    if resp.status_code == 401:
        raise WeatherServiceError("Chave da API OpenWeather inválida.")
    if resp.status_code != 200:
        raise WeatherServiceError(f"Erro na geocodificação: {resp.status_code}")

    resultados = resp.json()
    if not resultados:
        raise WeatherServiceError(f"Cidade '{nome_cidade}' não encontrada. Tente adicionar o país (Ex: Maceió, BR).")

    r = resultados[0]
    return {
        "lat": round(r["lat"], 4),
        "lon": round(r["lon"], 4),
        "nome": r.get("local_names", {}).get("pt") or r.get("name", nome_cidade),
        "pais": r.get("country", ""),
    }


def buscar_clima_por_coords(lat: float, lon: float) -> dict:
    """Busca dados climáticos atuais usando lat/lon."""
    params = {
        "lat": lat, "lon": lon,
        "appid": API_KEY,
        "units": DEFAULT_UNITS,
        "lang": DEFAULT_LANG,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException:
        raise WeatherServiceError("Falha de rede ao buscar dados climáticos.")

    if resp.status_code == 401:
        raise WeatherServiceError("Chave da API OpenWeather inválida.")
    if resp.status_code != 200:
        raise WeatherServiceError(f"Erro ao buscar clima ({resp.status_code}).")

    data = resp.json()
    weather_info = (data.get("weather") or [{}])[0]
    main = data.get("main", {})
    condicao_raw = weather_info.get("description") or ""

    return {
        "nome": data.get("name", "Ponto da rota"),
        "pais": data.get("sys", {}).get("country", ""),
        "lat": round(data.get("coord", {}).get("lat", lat), 4),
        "lon": round(data.get("coord", {}).get("lon", lon), 4),
        "temperatura": round(main.get("temp"), 1) if isinstance(main.get("temp"), (int, float)) else None,
        "temp_min":   round(main.get("temp_min"), 1) if isinstance(main.get("temp_min"), (int, float)) else None,
        "temp_max":   round(main.get("temp_max"), 1) if isinstance(main.get("temp_max"), (int, float)) else None,
        "umidade":    int(main.get("humidity")) if isinstance(main.get("humidity"), (int, float)) else None,
        "vento":       round(data.get("wind", {}).get("speed", 0), 1),
        "condicao":    condicao_raw.capitalize(),
        "grupo_condicao": normalizar_grupo_condicao(condicao_raw),
        "emoji":       get_emoji(condicao_raw),
    }


def _ponto_interpolado(lat1, lon1, lat2, lon2, frac: float) -> tuple[float, float]:
    return (
        round(lat1 + (lat2 - lat1) * frac, 4),
        round(lon1 + (lon2 - lon1) * frac, 4),
    )


def _distancia_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _frações_intermediárias(distancia_km: float) -> list[float]:
    if distancia_km < 150:
        return [0.5]
    if distancia_km < 500:
        return [1/3, 2/3]
    return [0.25, 0.5, 0.75]


ALERTAS_VIAGEM = {
    "tempestade": {
        "nivel": "alto",
        "titulo": "Tempestade no trajeto",
        "mensagem": "⚡ Há risco de tempestade nesta região. Considere adiar a viagem ou reforçar equipamentos de proteção.",
        "cor": "#dc2626",
        "bg": "rgba(220,38,38,0.10)",
    },
    "chuva": {
        "nivel": "moderado",
        "titulo": "Chuva no trajeto",
        "mensagem": "🌧️ Chuva prevista nesta área. Reduza a velocidade e aumente a distância de segurança.",
        "cor": "#d97706",
        "bg": "rgba(217,119,6,0.10)",
    },
    "neve": {
        "nivel": "alto",
        "titulo": "Neve ou gelo na estrada",
        "mensagem": "❄️ Condições de neve ou gelo detectadas. Verifique pneus e evite estradas de serra.",
        "cor": "#2563eb",
        "bg": "rgba(37,99,235,0.10)",
    },
    "nevoa": {
        "nivel": "moderado",
        "titulo": "Névoa ou neblina",
        "mensagem": "🌫️ Visibilidade reduzida por névoa. Use faróis baixos e diminua a velocidade.",
        "cor": "#7c3aed",
        "bg": "rgba(124,58,237,0.10)",
    },
}


def gerar_alerta_parada(parada: dict) -> dict | None:
    grupo = parada.get("grupo_condicao", "outros")
    return ALERTAS_VIAGEM.get(grupo)


def gerar_resumo_rota(paradas: list[dict]) -> dict:
    grupos = [p.get("grupo_condicao", "outros") for p in paradas]
    temps = [p["temperatura"] for p in paradas if isinstance(p.get("temperatura"), (int, float))]

    if "tempestade" in grupos or "neve" in grupos:
        severidade = "alto"
        icone = "⚠️"
        titulo = "Atenção: condições adversas no percurso"
        texto  = "Há pelo menos um trecho com risco elevado (tempestade ou neve). Avalie a viagem com cautela."
    elif "chuva" in grupos or "nevoa" in grupos:
        severidade = "moderado"
        icone = "🌦️"
        titulo = "Viagem com trechos chuvosos"
        texto  = "Parte do trajeto apresenta chuva ou névoa. Planeje paradas estratégicas e mantenha atenção redobrada."
    else:
        severidade = "baixo"
        icone = "✅"
        titulo = "Rota com clima favorável"
        texto  = "O percurso apresenta condições climáticas estáveis. Boa viagem!"

    variacao = (max(temps) - min(temps)) if len(temps) >= 2 else 0
    dica_termica = ""
    if variacao >= 8:
        dica_termica = f"A temperatura varia até {variacao:.0f}°C ao longo do trajeto — tenha roupas para diferentes climas na mala de mão."
    elif variacao >= 4:
        dica_termica = f"Variação de {variacao:.0f}°C entre os trechos. Um casaco leve pode ser útil."

    return {
        "severidade": severidade,
        "icone": icone,
        "titulo": titulo,
        "texto": texto,
        "dica_termica": dica_termica,
    }


def planejar_viagem(nome_origem: str, nome_destino: str) -> dict:
    geo_origem  = geocodificar(nome_origem)
    geo_destino = geocodificar(nome_destino)

    lat_o, lon_o = geo_origem["lat"], geo_origem["lon"]
    lat_d, lon_d = geo_destino["lat"], geo_destino["lon"]

    distancia = _distancia_km(lat_o, lon_o, lat_d, lon_d)

    try:
        clima_origem  = buscar_clima_por_coords(lat_o, lon_o)
        clima_destino = buscar_clima_por_coords(lat_d, lon_d)
    except WeatherServiceError as e:
        raise WeatherServiceError(f"Falha ao obter dados meteorológicos dos pontos principais: {str(e)}")

    fracoes = _frações_intermediárias(distancia)
    paradas_intermediarias = []
    
    for i, frac in enumerate(fracoes):
        lat_m, lon_m = _ponto_interpolado(lat_o, lon_o, lat_d, lon_d, frac)
        try:
            clima = buscar_clima_por_coords(lat_m, lon_m)
            clima["papel"] = f"parada_{i + 1}"
            clima["label"] = f"Parada {i + 1}" if len(fracoes) > 1 else "Ponto médio"
            clima["alerta"] = gerar_alerta_parada(clima)
            paradas_intermediarias.append(clima)
        except WeatherServiceError:
            continue

    clima_origem["papel"]  = "origem"
    clima_origem["label"]  = "Origem"
    clima_origem["alerta"] = gerar_alerta_parada(clima_origem)

    clima_destino["papel"]  = "destino"
    clima_destino["label"]  = "Destino"
    clima_destino["alerta"] = gerar_alerta_parada(clima_destino)

    paradas = [clima_origem, *paradas_intermediarias, clima_destino]
    resumo = gerar_resumo_rota(paradas)

    return {
        "paradas":       paradas,
        "distancia_km":  round(distancia),
        "resumo":        resumo,
        "nome_origem":   clima_origem["nome"],
        "nome_destino":  clima_destino["nome"],
    }