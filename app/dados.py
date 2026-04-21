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
    def __init__(self,nome:str,pais:str,temperatura:float,umidade:float,vento:float,condicao:str):
        self.nome = nome
        self.pais = pais
        self.temperatura = temperatura
        self.umidade = umidade
        self.vento = vento
        self.condicao = condicao
        self.id = Cidades.ID_atual
        Cidades.ID_atual += 1
    
    #? Metódo que irá atualizar os dados da Cidade, e verificará o cargo de quem está tentando fazer essa alteração, caso Usuário padrão = Negado❌, caso Admin = permitido✅
    def EditarCidades(self,nome=None,pais=None,temperatura=None,umidade=None,vento=None,condicao=None,cargo=None):
        if cargo != "admin":
            return "Acesso negado! Apenas usuários admin podem editar as cidades."
        else:
            if nome is not None:
                self.nome = nome
            if pais is not None:
                self.pais = pais
            if temperatura is not None:
                self.temperatura = temperatura
            if umidade is not None:
                self.umidade = umidade
            if vento is not None:
                self.vento = vento
            if condicao is not None:
                self.condicao = condicao
            return "Cidade atualizada com sucesso!"

if __name__ == "__main__":
    #? Criando usuários para teste
    usuario1 = Usuario_padrao("João Silva", "joao@email.com","senha123")
    usuario2 = UsuarioAdmin("Maria Oliveira", "maria@email.com","senha456")
