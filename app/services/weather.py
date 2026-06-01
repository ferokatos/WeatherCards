# Integração com a API OpenWeather
# Responsável: Pessoa 4
import os
from pathlib import Path

from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_UNITS = "metric"
DEFAULT_LANG = "pt_br"

# Mapeia as descricoes oficiais do OpenWeather para grupos internos.
OPENWEATHER_GROUPS = {
    "clear sky": "ceu-limpo",
    "few clouds": "nublado",
    "scattered clouds": "nublado",
    "broken clouds": "nublado",
    "cloud": "nublado",
    "shower rain": "chuva",
    "rain": "chuva",
    "thunderstorm": "tempestade",
    "snow": "neve",
    "mist": "nevoa",
}

# Garante emoji consistente para as descricoes canonicas da API.
OPENWEATHER_EMOJIS = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "🌤️",
    "broken clouds": "☁️",
    "cloud": "☁️",
    "shower rain": "🌧️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
}


class WeatherServiceError(Exception):
    """Erro genérico do serviço de clima."""


class WeatherNotFoundError(WeatherServiceError):
    """Cidade não encontrada pela API de clima."""


class WeatherAPIKeyError(WeatherServiceError):
    """Chave da API do OpenWeather ausente ou inválida."""


def buscar_clima(cidade):
    """Busca dados de clima para uma cidade usando o OpenWeather.

    Retorna um dicionário com campos prontos para consumo pelas rotas.
    """
    if not cidade or not cidade.strip():
        raise ValueError("O nome da cidade não pode ser vazio.")

    if not API_KEY or API_KEY == "INSIRA_SUA_CHAVE_NA_ENV":
        raise WeatherAPIKeyError(
            "A chave da API OpenWeather não está configurada. "
            "Defina OPENWEATHER_API_KEY no ambiente."
        )

    params = {
        "q": cidade,
        "appid": API_KEY,
        "units": DEFAULT_UNITS,
        "lang": DEFAULT_LANG,
    }

    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code == 401:
        raise WeatherAPIKeyError(
            "Chave da API OpenWeather inválida ou sem permissão."
        )

    if response.status_code == 404:
        raise WeatherNotFoundError(
            f"Cidade '{cidade}' não encontrada na API OpenWeather."
        )

    if response.status_code != 200:
        raise WeatherServiceError(
            f"Erro ao consultar OpenWeather: {response.status_code} - {response.text}"
        )

    data = response.json()
    weather_list = data.get("weather") or []
    weather_info = weather_list[0] if weather_list else {}
    main_data = data.get("main", {})

    temperatura = main_data.get("temp")
    temp_min = main_data.get("temp_min")
    temp_max = main_data.get("temp_max")
    umidade = main_data.get("humidity")
    vento = data.get("wind", {}).get("speed")
    condicao = weather_info.get("description") or "" 
    nome = data.get("name") or cidade
    pais = data.get("sys", {}).get("country") or ""
    coord = data.get("coord", {})
    lat = coord.get("lat")
    lon = coord.get("lon")
    grupo_condicao = normalizar_grupo_condicao(condicao)

    return {
        "nome": nome,
        "pais": pais,
        "temperatura": round(temperatura, 1) if isinstance(temperatura, (int, float)) else None,
        "temp_min": round(temp_min, 1) if isinstance(temp_min, (int, float)) else None,
        "temp_max": round(temp_max, 1) if isinstance(temp_max, (int, float)) else None,
        "umidade": int(umidade) if isinstance(umidade, (int, float)) else None,
        "vento": round(vento, 1) if isinstance(vento, (int, float)) else None,
        "condicao": condicao.capitalize(),
        "grupo_condicao": grupo_condicao,
        "emoji": get_emoji(condicao),
        "lat": round(lat, 4) if isinstance(lat, (int, float)) else None,
        "lon": round(lon, 4) if isinstance(lon, (int, float)) else None,
    }


def normalizar_grupo_condicao(condicao):
    """Agrupa descricoes similares para filtros previsiveis."""
    if not condicao:
        return "outros"

    text = condicao.strip().lower()

    if text in OPENWEATHER_GROUPS:
        return OPENWEATHER_GROUPS[text]

    # Mantem o filtro resiliente a variacoes da API.
    if any(k in text for k in ["storm", "thunder", "tempestade", "trovoada", "raio"]):
        return "tempestade"
    if any(k in text for k in ["snow", "neve", "sleet", "ice", "gelo"]):
        return "neve"
    if any(k in text for k in ["rain", "chuva", "drizzle", "chuvisco", "garoa", "shower"]):
        return "chuva"
    if any(k in text for k in ["mist", "fog", "haze", "névoa", "nevoa", "neblina"]):
        return "nevoa"
    if any(k in text for k in ["clear", "sunny", "limpo", "ensolarado", "sol"]):
        return "ceu-limpo"
    if any(k in text for k in ["cloud", "nublado", "overcast", "nuvens", "few", "scattered", "broken", "parcial", "dispersas"]):
        return "nublado"

    return "outros"


def get_emoji(condicao):
    """Retorna um emoji representando a condição do clima."""
    if not condicao:
        return "❔"

    text = condicao.strip().lower()

    if text in OPENWEATHER_EMOJIS:
        return OPENWEATHER_EMOJIS[text]

    # 1. Condições Extremas (Prioridade Máxima)
    if "tornado" in text:
        return "🌪️"
    if any(k in text for k in ["storm", "thunder", "tempestade", "trovoada", "raio"]):
        return "⛈️"
    
    # 2. Neve e Gelo
    if any(k in text for k in ["snow", "neve", "sleet", "ice", "gelo"]):
        return "❄️"

    # 3. Chuva (Diferenciando intensidade se desejar, ou agrupando)
    if any(k in text for k in ["rain", "chuva", "drizzle", "chuvisco", "garoa"]):
        return "🌧️"

    # 4. Atmosfera / Visibilidade
    if any(k in text for k in ["mist", "fog", "haze", "dust", "smoke", "névoa", "neblina", "poeira"]):
        return "🌫️"

    # 5. Vento forte
    if any(k in text for k in ["wind", "ventania", "vento"]):
        return "🌬️"

    # 6. Nuvens (Ordem: Parcialmente -> Nublado total)
    # Verificamos termos de "poucas nuvens" antes de "nublado" total
    if any(k in text for k in ["broken", "scattered", "few", "parcial", "dispersas", "quebradas"]):
        return "🌤️"
    if any(k in text for k in ["cloud", "nublado", "overcast", "nuvens"]):
        return "☁️"

    # 7. Céu Limpo
    if any(k in text for k in ["clear", "sunny", "limpo", "ensolarado", "sol"]):
        return "☀️"

    # Fallback (Arco-íris para condições desconhecidas)
    return "🌈"


if __name__ == "__main__":
    teste_cidades = ["São Paulo", "Londres", "Maceió", "Groenlandia"]

    for cidade in teste_cidades:
        try:
            resultado = buscar_clima(cidade)
            print(f"\nCidade: {resultado['nome']}, {resultado['pais']}")
            print(f"Temperatura: {resultado['temperatura']} °C")
            print(f"Umidade: {resultado['umidade']} %")
            print(f"Vento: {resultado['vento']} m/s")
            print(f"Condição: {resultado['condicao']} {resultado['emoji']}")
        except WeatherServiceError as exc:
            print(f"Erro ao buscar clima para '{cidade}': {exc}")
        except Exception as exc:
            print(f"Erro inesperado para '{cidade}': {exc}")
