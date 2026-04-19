# 💡 Ideias e Organização — WeatherCards Web (CRUD + Cargos)

---

## 🎯 Visão Geral

Sistema web de gerenciamento de cidades climáticas.
O usuário faz login, pesquisa cidades, salva no sistema e visualiza dados do clima.
Cada cargo tem permissões diferentes na interface.

---

## 👥 Cargos e Permissões

| Ação              | Admin             | Usuário Comum        |
| ------------------- | ----------------- | --------------------- |
| Ver cidades salvas  | ✅                | ✅                    |
| Adicionar cidade    | ✅                | ✅                    |
| Editar cidade       | ✅ (qualquer uma) | ✅ (só as próprias) |
| Deletar cidade      | ✅                | ❌                    |
| Gerenciar usuários | ✅                | ❌                    |

---

## 🔐 Login em Memória

Sem banco de dados — os usuários ficam numa lista em memória:

```python
USUARIOS = [
    {"id": 1, "nome": "Admin",  "senha": "admin123", "cargo": "admin"},
    {"id": 2, "nome": "João",   "senha": "joao123",  "cargo": "usuario"},
    {"id": 3, "nome": "Maria",  "senha": "maria123", "cargo": "usuario"},
]
```

---

## 🗃️ CRUD de Cidades

Cada cidade salva no sistema terá:

```python
{
    "id": 1,
    "nome": "Maceió",
    "pais": "BR",
    "temperatura": 32,
    "umidade": 80,
    "vento": 15.0,
    "condicao": "Céu limpo",
    "adicionado_por": "João"  # quem salvou
}
```

### Operações:

- **Criar** → buscar cidade na API e salvar na lista
- **Listar** → mostrar todas as cidades salvas
- **Editar** → atualizar dados da cidade (busca novamente na API)
- **Deletar** → remover da lista (só Admin)

---

## 🗺️ Páginas do Site

```
/login              → Tela de login
/                   → Dashboard (lista de cidades) — requer login
/cidade/adicionar   → Formulário para adicionar cidade
/cidade/editar/<id> → Formulário para editar cidade
/cidade/deletar/<id>→ Deletar cidade (só Admin)
/admin/usuarios     → Gerenciar usuários (só Admin)
```

---

## 🔥 Funcionalidades

### 1. Login com cargos

- Tela de login simples
- Ao logar, salva o usuário e cargo na sessão
- Rotas bloqueadas por cargo

### 2. Dashboard de cidades

- Lista todas as cidades salvas
- Mostra temperatura, condição e emoji do clima
- Botões de editar/deletar aparecem conforme o cargo

### 3. Adicionar cidade

- Campo de busca com nome da cidade
- Busca dados na OpenWeather API
- Salva na lista em memória

### 4. Editar cidade

- Admin edita qualquer cidade
- Usuário comum edita só as que ele adicionou
- Botão de editar some para cidades de outros usuários

### 5. Deletar cidade

- Só o Admin vê o botão de deletar
- Usuário comum não tem esse botão

### 6. Painel Admin

- Lista todos os usuários cadastrados
- Mostra cargo de cada um
- Só acessível pelo Admin

---

## 📁 Estrutura do Projeto

```
weathercards_web/
│
├── app/
│   ├── routes/
│   │   ├── auth.py         # login e logout
│   │   ├── cidades.py      # CRUD de cidades
│   │   └── admin.py        # painel admin
│   │
│   ├── services/
│   │   └── weather.py      # consumo da API OpenWeather
│   │
│   ├── templates/
│   │   ├── base.html       # template base (navbar)
│   │   ├── login.html      # tela de login
│   │   ├── index.html      # dashboard
│   │   ├── adicionar.html  # form adicionar cidade
│   │   ├── editar.html     # form editar cidade
│   │   └── admin.html      # painel admin
│   │
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   ├── dados.py            # listas em memória (usuários + cidades)
│   └── __init__.py         # inicialização do Flask
│
├── run.py                  # ponto de entrada
├── requirements.txt
└── README.md
```

---

## 👥 Divisão do Grupo (5 pessoas)

| Pessoa   | Responsabilidade                     | Branch                   |
| -------- | ------------------------------------ | ------------------------ |
| Pessoa 1 | Login + sessão + controle de cargos | `feature/auth`         |
| Pessoa 2 | CRUD de cidades (criar + listar)     | `feature/crud-cidades` |
| Pessoa 3 | CRUD de cidades (editar + deletar)   | `feature/crud-editar`  |
| Pessoa 4 | Integração com API OpenWeather     | `feature/api-weather`  |
| Pessoa 5 | Painel Admin + templates base        | `feature/admin`        |

---

## ⚠️ Regras do Grupo

- Cada um trabalha na própria branch
- Nada de commitar direto na `main`
- Toda contribuição via Pull Request
- PR com título e descrição claros
- Código revisado antes de mergear
