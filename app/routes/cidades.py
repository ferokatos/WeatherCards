# Rotas de CRUD de cidades: criar, listar, editar, deletar
class Cidades:
    CIDADES = []  # lista de todas as cidades
    ID_atual = 1

    def __init__(self, nome: str, pais: str, temperatura: float,
                 umidade: float, vento: float, condicao: str):
        self.nome = nome
        self.pais = pais
        self.temperatura = temperatura
        self.umidade = umidade
        self.vento = vento
        self.condicao = condicao
        self.id = Cidades.ID_atual
        Cidades.ID_atual += 1
        Cidades.CIDADES.append(self)  # ← registra na lista ao criar

    # ✅ Criar cidade (verifica cargo)
    @classmethod
    def CriarCidade(cls, nome, pais, temperatura, umidade, vento, condicao, usuario):
        if not isinstance(usuario, "UsuarioAdmin"):
            return "Acesso negado! Apenas admins podem criar cidades."
        nova = cls(nome, pais, temperatura, umidade, vento, condicao)
        return nova

    # ✅ Listar todas as cidades
    @classmethod
    def ListarCidades(cls):
        if not cls.CIDADES:
            return "Nenhuma cidade cadastrada."
        return [
            {
                "id": c.id,
                "nome": c.nome,
                "pais": c.pais,
                "temperatura": c.temperatura,
                "umidade": c.umidade,
                "vento": c.vento,
                "condicao": c.condicao,
            }
            for c in cls.CIDADES
        ]

    # ✅ Buscar cidade por ID
    @classmethod
    def BuscarPorId(cls, id: int):
        for cidade in cls.CIDADES:
            if cidade.id == id:
                return cidade
        return None

    # ✅ Deletar cidade (verifica cargo)
    @classmethod
    def DeletarCidade(cls, id: int, usuario):
        if not isinstance(usuario, "UsuarioAdmin"):
            return "Acesso negado! Apenas admins podem deletar cidades."
        cidade = cls.BuscarPorId(id)
        if cidade is None:
            return "Cidade não encontrada."
        cls.CIDADES.remove(cidade)
        return f"Cidade '{cidade.nome}' deletada com sucesso!"

    def EditarCidades(self, usuario, nome=None, pais=None,
                      temperatura=None, umidade=None, vento=None, condicao=None):
        if not isinstance(usuario, "UsuarioAdmin"):  # ← agora recebe objeto, não string
            return "Acesso negado!"
        if nome: self.nome = nome
        if pais: self.pais = pais
        if temperatura: self.temperatura = temperatura
        if umidade: self.umidade = umidade
        if vento: self.vento = vento
        if condicao: self.condicao = condicao
        return "Cidade atualizada com sucesso!"