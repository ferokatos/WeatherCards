#Aqui ficarão os dados locais(cache local) para o projeto, como por exemplo os usuários e as cidades, além de métodos para editar as cidades.

#!--------------------------------------------------------------------------------
#!                                   USUÁRIO PADRÃO
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
        self.ja_avaliou = False
        Usuario_padrao.ID_atual += 1
        Usuario_padrao.USUARIOS.append(self)

#!--------------------------------------------------------------------------------
#!                                   USUÁRIO ADMIN
#!--------------------------------------------------------------------------------

#? Classe usuário admin além de vizualisar as cidades, poderá criar, editar e deletar cidades
class UsuarioAdmin(Usuario_padrao):
    def __init__(self,nome:str,email:str,senha:str):
        super().__init__(nome,email,senha)
        self.cargo = "admin"


def buscar_usuario_por_email(email):
    """Retorna um usuário já cadastrado pelo email."""
    for usuario in Usuario_padrao.USUARIOS:
        if usuario.email == email:
            return usuario
    return None


def popular_usuarios_padrao():
    """Cria usuários padrão em memória sem duplicar registros existentes."""
    usuarios_iniciais = [
        {
            "nome": "Admin",
            "email": "admin@weathercards.local",
            "senha": "admin1234",
            "classe": UsuarioAdmin,
        },
        {
            "nome": "Usuario",
            "email": "usuario@weathercards.local",
            "senha": "usuario123",
            "classe": Usuario_padrao,
        },
    ]

    for dados_usuario in usuarios_iniciais:
        if buscar_usuario_por_email(dados_usuario["email"]):
            continue

        dados_usuario["classe"](
            dados_usuario["nome"],
            dados_usuario["email"],
            dados_usuario["senha"],
        )

#!--------------------------------------------------------------------------------
#!                              CIDADES(descrições)
#!--------------------------------------------------------------------------------

#? Classe de cidades irá receber os dados da API, criando assim um flash_card
class Cidades:
    ID_atual = 1
    def __init__(self, nome:str, pais:str, temperatura:float, temp_min:float, temp_max:float, umidade:float, vento:float, condicao:str, grupo_condicao:str, emoji:str, adicionado_por_id:int, adicionado_por_nome:str):
        self.nome = nome
        self.pais = pais
        self.temperatura = temperatura
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.umidade = umidade
        self.vento = vento
        self.condicao = condicao
        self.grupo_condicao = grupo_condicao
        self.emoji = emoji
        self.adicionado_por_id = adicionado_por_id
        self.adicionado_por_nome = adicionado_por_nome
        self.id = Cidades.ID_atual
        Cidades.ID_atual += 1

        # Histórico de leituras climáticas para o gráfico
        self.historico = []
        self._registrar_historico()

    def _registrar_historico(self):
        """Registra a leitura atual no histórico."""
        from datetime import datetime
        self.historico.append({
            "data": datetime.now(),
            "temperatura": self.temperatura,
            "temp_min": self.temp_min,
            "temp_max": self.temp_max,
            "umidade": self.umidade,
            "vento": self.vento,
            "condicao": self.condicao,
            "grupo_condicao": self.grupo_condicao,
        })

    def atualizar_clima(self, temperatura:float, temp_min:float, temp_max:float, umidade:float, vento:float, condicao:str, grupo_condicao:str, emoji:str):
        """Atualiza os dados de clima da cidade mantendo quem adicionou intacto"""
        self.temperatura = temperatura
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.umidade = umidade
        self.vento = vento
        self.condicao = condicao
        self.grupo_condicao = grupo_condicao
        self.emoji = emoji
        self._registrar_historico()  # registra cada atualização no histórico

def buscar_cidade_por_id(cidade_id):
    """Busca uma cidade salva pelo ID"""
    for cidade in CIDADES_SALVAS:
        if cidade.id == cidade_id:
            return cidade
    return None

#!--------------------------------------------------------------------------------
#!                       REPOSITÓRIO GLOBAL DE CIDADES
#!--------------------------------------------------------------------------------

#Lista global de cidades, onde todas as cidades serão armazenaddas.
CIDADES_SALVAS = []

#Função que irá adcionar uma cidade se o usuário for admin.
def adicionar_cidade(cidade):
    CIDADES_SALVAS.append(cidade)
    return f"Cidade '{cidade.nome}' adicionada com sucesso!"

#Função que irá remover uma cidade pelo ID da cidade:
def remover_cidade(cidade_id):
    for cidade in CIDADES_SALVAS:
        if cidade.id == cidade_id:
            CIDADES_SALVAS.remove(cidade)
            return f"Cidade '{cidade.nome}' removida com sucesso!"

    return "Cidade não encontrada."

# Função que irá listar todas as cidades salvas (Ordenadas do mais novo para o mais antigo)
def listar_cidades():
    return CIDADES_SALVAS[::-1]

#Função que com o nome da cidade busca os dados na API
def popular_cidades_padrao():
    """Busca e salva cidades padrão ao iniciar o app."""

    # Evita duplicar se já foram carregadas
    if CIDADES_SALVAS:
        return

    from app.services.weather import buscar_clima, WeatherServiceError

    # Espalha as cidades por faixas climaticas diferentes.
    cidades_padrao = [
        "Maceió,BR", "Manaus,BR", "Curitiba,BR",
        "Porto Alegre,BR", "Londres,GB","Nuuk,GL", "Reykjavik,IS",
        "Moscou,RU", "Cairo,EG", "Tokyo,JP", "Vancouver,CA"
    ]

    for nome in cidades_padrao:
        try:
            dados = buscar_clima(nome)
            cidade = Cidades(
                nome=dados["nome"],
                pais=dados["pais"],
                temperatura=dados["temperatura"],
                temp_min=dados["temp_min"],
                temp_max=dados["temp_max"],
                umidade=dados["umidade"],
                vento=dados["vento"],
                condicao=dados["condicao"],
                grupo_condicao=dados["grupo_condicao"],
                emoji=dados["emoji"],
                adicionado_por_id=0,           # 0 = sistema
                adicionado_por_nome="Sistema"
            )
            CIDADES_SALVAS.append(cidade)
            print(f"✅ {nome} carregada!")
        except WeatherServiceError:
            print(f"❌ Erro ao carregar {nome}")
        except Exception as e:
            print(f"❌ Erro inesperado em {nome}: {e}")


#!------------------------------------------------------------------
#!                          Classe de formulário
#!------------------------------------------------------------------

class Formulario:
    numero_do_formulario = 1
    Lista_de_formularios = []
    def __init__(self,estrelas:int =None,comentario:str ="Nada",usuario=None):
        self.estrelas = estrelas
        self.comentario = comentario
        self.usuario_nome = usuario.nome
        self.usuario_id = usuario.id
        self.id = self.numero_do_formulario
        Formulario.numero_do_formulario +=1
        Formulario.Lista_de_formularios.append(self)



#!Teste local
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 TESTANDO O SISTEMA")
    print("=" * 50)

    # ── Criando usuários ──────────────────────────────
    print("\n👥 Criando usuários...")
    usuario_comum = Usuario_padrao("João Silva", "joao@email.com", "senha123")
    usuario_admin = UsuarioAdmin("Maria Oliveira", "maria@email.com", "senha456")

    print(f"✅ Usuário criado: {usuario_comum.nome} | cargo: {usuario_comum.cargo}")
    print(f"✅ Usuário criado: {usuario_admin.nome} | cargo: {usuario_admin.cargo}")

    # ── Criando cidades ───────────────────────────────
    print("\n🌍 Criando cidades...")
    cidade1 = Cidades(
        nome="Maceió",
        pais="Brasil",
        temperatura=30,
        temp_min=28,
        temp_max=31,
        umidade=80,
        vento=10,
        condicao="Ensolarado",
        grupo_condicao="ceu-limpo",
        emoji="☀️",
        adicionado_por_id=usuario_admin.id,
        adicionado_por_nome=usuario_admin.nome
    )

    cidade2 = Cidades(
        nome="Recife",
        pais="Brasil",
        temperatura=28,
        temp_min=26,
        temp_max=29,
        umidade=85,
        vento=15,
        condicao="Nublado",
        grupo_condicao="nublado",
        emoji="☁️",
        adicionado_por_id=usuario_comum.id,
        adicionado_por_nome=usuario_comum.nome
    )

    # ── Testando adicionar ────────────────────────────
    print("\n➕ Adicionando cidades...")
    print(adicionar_cidade(cidade1))
    print(adicionar_cidade(cidade2))

    # ── Testando listar ───────────────────────────────
    print("\n📋 Listando cidades salvas (Deve mostrar a mais nova primeiro):")
    for cidade in listar_cidades():
        print(f"  [{cidade.id}] {cidade.emoji} {cidade.nome} — {cidade.temperatura}°C — adicionado por: {cidade.adicionado_por_nome}")

    # ── Testando buscar por ID ────────────────────────
    print("\n🔍 Buscando cidade com ID 1...")
    encontrada = buscar_cidade_por_id(1)
    if encontrada:
        print(f"  ✅ Encontrada: {encontrada.nome}")
    else:
        print("  ❌ Não encontrada!")

    # ── Testando atualizar clima ──────────────────────
    print("\n✏️ Atualizando clima de Maceió...")
    cidade1.atualizar_clima(25, 23, 27, 70, 12, "Chuvoso", "outros", "🌧️")
    print(f"  ✅ Novo clima: {cidade1.emoji} {cidade1.condicao} — {cidade1.temperatura}°C")
    print(f"  ✅ Adicionado por continua: {cidade1.adicionado_por_nome}")
    print(f"  ✅ Histórico tem {len(cidade1.historico)} registros")

    # ── Testando remover ──────────────────────────────
    print("\n🗑️ Removendo Recife...")
    print(f"  {remover_cidade(cidade2.id)}")

    # ── Listando após remoção ─────────────────────────
    print("\n📋 Cidades após remoção:")
    for cidade in listar_cidades():
        print(f"  [{cidade.id}] {cidade.emoji} {cidade.nome}")

    # ── Testando buscar ID inexistente ────────────────
    print("\n🔍 Buscando cidade com ID 99 (inexistente)...")
    nao_encontrada = buscar_cidade_por_id(99)
    if nao_encontrada:
        print("  ✅ Encontrada!")
    else:
        print("  ✅ Retornou None corretamente!")

    print("\n" + "=" * 50)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 50)