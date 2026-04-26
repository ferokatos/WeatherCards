#Aqui ficarão os dados locais(cache local) para o projeto, como por exemplo os usuários e as cidades, além de métodos para editar as cidades.

#!--------------------------------------------------------------------------------
#!                                  USUÁRIO PADRÃO
#!--------------------------------------------------------------------------------

#? Classe usuário padrão poderá apenas vizualisar as cidades, não poderá criar, deletar ou editar cidades.
class Usuario_padrao:
    USUARIOS = []
    ID_atual = 1
    def __init__(self,nome:str,email:str,senha:str):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.id =Usuario_padrao.ID_atual
        self.cargo = "padrão"
        Usuario_padrao.ID_atual += 1
        Usuario_padrao.USUARIOS.append(self)

#!--------------------------------------------------------------------------------
#!                                  USUÁRIO ADMIN
#!--------------------------------------------------------------------------------

#? Classe usuário admin além de vizualisar as cidades, poderá criar, editar e deletar cidades
class UsuarioAdmin(Usuario_padrao):
    def __init__(self,nome:str,email:str,senha:str):
        super().__init__(nome,email,senha)
        self.cargo = "admin"

#!--------------------------------------------------------------------------------
#!                            CIDADES(descrições)
#!--------------------------------------------------------------------------------

#? Classe de cidades irá receber os dados da API, criando assim um flash_card
class Cidades:
    ID_atual = 1
    def __init__(self, nome:str, pais:str, temperatura:float, umidade:float, vento:float, condicao:str, emoji:str, adicionado_por_id:int, adicionado_por_nome:str):
        self.nome = nome
        self.pais = pais
        self.temperatura = temperatura
        self.umidade = umidade
        self.vento = vento
        self.condicao = condicao
        self.emoji = emoji
        self.adicionado_por_id = adicionado_por_id
        self.adicionado_por_nome = adicionado_por_nome
        self.id = Cidades.ID_atual
        Cidades.ID_atual += 1
    
    def atualizar_clima(self, temperatura:float, umidade:float, vento:float, condicao:str, emoji:str):
        """Atualiza os dados de clima da cidade mantendo quem adicionou intacto"""
        self.temperatura = temperatura
        self.umidade = umidade
        self.vento = vento
        self.condicao = condicao
        self.emoji = emoji

#? Repositório Global em Memória
CIDADES_SALVAS = []

def buscar_cidade_por_id(cidade_id):
    """Busca uma cidade salva pelo ID"""
    for cidade in CIDADES_SALVAS:
        if cidade.id == cidade_id:
            return cidade
    return None

#!--------------------------------------------------------------------------------
#!                      REPOSITÓRIO GLOBAL DE CIDADES
#!--------------------------------------------------------------------------------

#Lista global de cidades, onde todas as cidades serão armazenaddas.
CIDADES_SALVAS = []

#Função que irá adcionar uma cidade se o usuário for admin.
def adicionar_cidade(cidade, cargo=None):
    CIDADES_SALVAS.append(cidade)
    return f"Cidade '{cidade.nome}' adicionada com sucesso!"

#Função que irá remover uma cidade pelo ID da cidade:
def remover_cidade(cidade_id,cargo=None):
    for cidade in CIDADES_SALVAS:
        if cidade.id == cidade_id:
            CIDADES_SALVAS.remove(cidade)
            return f"Cidade '{cidade.nome}' removida com sucesso!"

    return "Cidade não encontrada."

# Função que irá listar todas as cidades salvas
def listar_cidades():
    return CIDADES_SALVAS

if __name__ == "__main__":
    # Criando usuários
    usuario1 = Usuario_padrao("João Silva", "joao@email.com", "senha123")
    usuario2 = UsuarioAdmin("Maria Oliveira", "maria@email.com", "senha456")

    # Criando cidade
    cidade1 = Cidades("Maceió", "Brasil", 30, 80, 10, "Ensolarado")

    # Tentando adicionar com usuário padrão ❌
    print(adicionar_cidade(cidade1, usuario1.cargo))

    # Adicionando com admin ✅
    print(adicionar_cidade(cidade1, usuario2.cargo))

    # Listando cidades
    print("Cidades salvas:", listar_cidades())

    # Editando cidade
    print(cidade1.EditarCidades(temperatura=28, cargo=usuario2.cargo))

    # Removendo cidade
    print(remover_cidade(cidade1.id, usuario2.cargo))

    # Listando novamente
    print("Cidades após remoção:", listar_cidades())