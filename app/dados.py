# Persistência em memória — sem banco de dados!
# Aqui ficam os usuários e as cidades salvas

# Lista de usuários do sistema
USUARIOS = [
    {"id": 1, "nome": "Admin", "senha": "admin123", "cargo": "admin"},
    {"id": 2, "nome": "João",  "senha": "joao123",  "cargo": "usuario"},
    {"id": 3, "nome": "Maria", "senha": "maria123", "cargo": "usuario"},
]

# Lista de cidades salvas
CIDADES = []

# Controle de IDs
_contador_id = 0

def proxima_id():
    global _contador_id
    _contador_id += 1
    return _contador_id
