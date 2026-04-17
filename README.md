# 🌦️ WeatherCards Web

Sistema web de gerenciamento de cidades climáticas com CRUD e controle de acesso por cargo.

## ▶️ Como executar

```bash
pip install -r requirements.txt
python run.py
```

Acesse: http://localhost:5000

## 👥 Usuários padrão

| Nome  | Senha     | Cargo   |
|-------|-----------|---------|
| Admin | admin123  | admin   |
| João  | joao123   | usuario |
| Maria | maria123  | usuario |

## 📁 Estrutura
- `app/routes/`   → rotas Flask
- `app/services/` → integração com API
- `app/templates/`→ HTML (Jinja2)
- `app/static/`   → CSS e JS
- `app/dados.py`  → dados em memória
