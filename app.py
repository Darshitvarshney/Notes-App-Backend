from flask import Flask, jsonify
from flask_cors import CORS
from mongoengine import connect


from backend.routes.adminRoutes import admin_bp
from backend.routes.collaboratorRoutes import colab_bp

app = Flask(__name__)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

connect(db='notesDB', host='mongodb+srv://darshit2412062:nniC4O40bFUYSvpm@notesapp.gcgatmg.mongodb.net/')

app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(colab_bp, url_prefix="/api/collaborator")


@app.route("/api/health", methods=["GET"])
def index():
    return jsonify({"message": "Backend Running Successfully!!!", "status": 200, "data": ""}), 200

if __name__ == "__main__":
    app.run(debug=True,port=5050,use_reloader=True)
