import os
import sys

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.barbeiros import barbeiros_bp
from src.routes.servicos import servicos_bp
from src.routes.agendamentos import agendamentos_bp
from src.routes.produtos import produtos_bp
from src.routes.webhooks import webhooks_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config["SECRET_KEY"] = "asdf#FGSgvasgf$5$WGT"
app.config["JWT_SECRET_KEY"] = "jwt-secret-string-change-in-production"

# Configurar CORS para permitir requisições de qualquer origem
CORS(app)

# Configurar JWT
jwt = JWTManager(app)

# Configurar Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://", # Usar Redis em produção: "redis://localhost:6379"
)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(barbeiros_bp, url_prefix="/api/barbeiros")
app.register_blueprint(servicos_bp, url_prefix="/api/servicos")
app.register_blueprint(agendamentos_bp, url_prefix="/api/agendamentos")
app.register_blueprint(produtos_bp, url_prefix="/api/produtos")
app.register_blueprint(webhooks_bp, url_prefix="/webhooks")

# Configurar banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


