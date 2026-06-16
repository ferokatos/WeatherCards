# 🌦️ WeatherCards Web

Sistema web de gerenciamento de cidades climáticas com CRUD e controle de acesso por cargo.

## ▶️ Como executar

```bash
pip install -r requirements.txt
python run.py
```

Acesse: http://127.0.0.1:5001 || https://weather-cards-web.onrender.com/

> Crie um arquivo `.env` na raiz do projeto com a chave OpenWeather em `OPENWEATHER_API_KEY` (veja a seção [API Utilizada](#-api-utilizada)).

## 👥 Usuários padrão

| Nome    | Email                      | Senha      | Cargo   |
|---------|----------------------------|------------|---------|
| Admin   | admin@weathercards.local   | admin1234  | admin   |
| Usuario | usuario@weathercards.local | usuario123 | padrão  |

## 🌐 API Utilizada

Este projeto consome a [OpenWeather API](https://openweathermap.org/api) (plano gratuito) para obter dados climáticos em tempo real.

### Autenticação

A OpenWeather autentica as requisições através de uma **API Key enviada como parâmetro na URL** (`appid`). Não há tokens, headers de autorização ou OAuth — basta incluir a chave em cada chamada.

```python
params = {
    "q": cidade,
    "appid": API_KEY,   # ← autenticação
    "units": "metric",
    "lang": "pt_br"
}
```

### Como obter sua chave de acesso

1. Crie uma conta gratuita em [openweathermap.org](https://openweathermap.org)
2. Após confirmar o e-mail, acesse **"My API Keys"** no seu perfil
3. Copie a chave gerada e adicione no arquivo `.env`:

```
OPENWEATHER_API_KEY=sua_chave_aqui
```

> ⚠️ A chave pode levar até 2 horas para ser ativada após a criação da conta.
> ⚠️ Sem a chave configurada, o sistema simula dados de histórico para manter os gráficos funcionando.

### Endpoints consumidos

| Endpoint | Usado em | Finalidade |
|---|---|---|
| `https://api.openweathermap.org/data/2.5/weather` | `app/services/weather.py` | Dados climáticos atuais de uma cidade (temperatura, umidade, vento, condição) |
| `https://api.openweathermap.org/data/2.5/forecast` | `app/services/previsao_alertas.py` | Previsão climática, usada para gerar alertas e histórico |

### Parâmetros enviados nas requisições

| Parâmetro | Descrição |
|---|---|
| `q` | Nome da cidade (ex: `Maceio,BR`) |
| `appid` | Chave de acesso (autenticação) |
| `units` | Unidade de medida (`metric` = Celsius) |
| `lang` | Idioma da resposta (`pt_br`) |

### Dados retornados e utilizados pelo sistema

- Nome da cidade e país
- Temperatura atual, mínima e máxima
- Umidade (%)
- Velocidade do vento (km/h)
- Condição climática (ex: "céu limpo", "chuva")
- Ícone/emoji correspondente à condição
- Previsão futura para geração de alertas climáticos

## 📁 Estrutura
- `app/routes/`   → rotas Flask
- `app/services/` → integração com API
- `app/templates/`→ HTML (Jinja2)
- `app/static/`   → CSS e JS
- `app/dados.py`  → dados em memória
