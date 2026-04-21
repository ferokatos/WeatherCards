# Inicialização do Flask
# Aqui o app é criado e as rotas são registradas
from flask import Flask

def criar_app():
    app = Flask(__name__)
    app.secret_key = "weathercards_secret"

    # Registrar rotas aqui (quando forem criadas)
    from app.routes.auth    import auth_bp
    # from app.routes.cidades import cidades_bp
    # from app.routes.admin   import admin_bp

    app.register_blueprint(auth_bp)
    # app.register_blueprint(cidades_bp)
    # app.register_blueprint(admin_bp)

    return app