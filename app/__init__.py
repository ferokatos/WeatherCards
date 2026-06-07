# Inicialização do Flask
from flask import Flask

def criar_app():
    app = Flask(__name__)
    app.secret_key = "weathercards_secret"
    
    # Importando as rotas dos arquivos corretos
    from app.routes.viagem import viagem_bp 
    from app.routes.auth    import auth_bp
    from app.routes.cidades import cidades_bp
    from app.routes.admin   import admin_bp
    from app.routes.avaliacoes import formulario_bp
    
    # Registrando os Blueprints no Flask
    app.register_blueprint(auth_bp)
    app.register_blueprint(cidades_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(formulario_bp)
    app.register_blueprint(viagem_bp)

    # Popula as cidades padrão ao iniciar o app
    with app.app_context():
        from app.dados import popular_cidades_padrao, popular_usuarios_padrao
        popular_usuarios_padrao()
        popular_cidades_padrao()

    return app