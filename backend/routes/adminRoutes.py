from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import re 
from mongoengine.queryset.visitor import Q

from backend.utils.token import generate_token, serialize_doc, token_admin_required

from backend.models.adminModel import Admin
from backend.models.collaboratorModel import Collaborator
from backend.models.workspaceModel import Workspace

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"message": "Name, email, and password are required", "status": 400}), 400

        if Admin.objects(email=email).first():
            return jsonify({"message": "Email already exists", "status": 400}), 400

        hashed_password = generate_password_hash(password)

        admin = Admin(
            name=name,
            email=email,
            password=hashed_password,
        )
        admin.save()

        token = generate_token(admin)
        return jsonify({
            "message": "Signup successful",
            "status": 200,
            "token": token,
            "data": {
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "Error signing up", "status": 500, "error": str(e)}), 500
    
    
@admin_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Email and password required", "status": 400}), 400

        admin = Admin.objects(email=email).first()
        if not admin or not check_password_hash(admin.password, password):
            return jsonify({"message": "Invalid credentials", "status": 401}), 401

        token = generate_token(admin)
        return jsonify({
            "message": "Login successful",
            "status": 200,
            "token": token,
            "data": {
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "Error logging in", "status": 500, "error": str(e)}), 500
    

@admin_bp.route("/create-workspace", methods=["POST"])
@token_admin_required
def create_workspace():
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        if not name or not description:
            return jsonify({"message": "Name and description are required", "status": 400}), 400

        workspace = Workspace(name=name, description=description)
        workspace.save()

        return jsonify({"message": "Workspace created successfully", "status": 200}), 200

    except Exception as e:
        return jsonify({"message": "Error creating workspace", "status": 500, "error": str(e)}), 500
    


@admin_bp.route("/invite-collaborator", methods=["POST"])
@token_admin_required
def invite_collaborator():
    try:
        data = request.get_json()
        email = data.get("email")
        workspace_id = data.get("workspace_id")

        if not email or not workspace_id:
            return jsonify({"message": "Email and workspace ID are required", "status": 400}), 400

        workspace_doc = Workspace.objects(id=workspace_id).first()
        if not workspace_doc:
            return jsonify({"message": "Workspace not found", "status": 404}), 404

        collaborator = Collaborator.objects(email=email).first()
        if not collaborator:
            return jsonify({"message": "Collaborator not found", "status": 404}), 404

        workspace_doc.collaborators.append(collaborator.id)
        collaborator.workspace.append(workspace_doc.id)
        workspace_doc.save()
        collaborator.save()

        return jsonify({"message": "Collaborator invited successfully", "status": 200}), 200

    except Exception as e:
        return jsonify({"message": "Error inviting collaborator", "status": 500, "error": str(e)}), 500
    

@admin_bp.route("/search", methods=["GET"])
def search():
    try:
        data = request.get_json() or {}

        workspace_query = data.get("workspace", "").strip()
        note_query = data.get("note", "").strip()
        tags_query = data.get("tags", "").strip()
        page = int(data.get("page", 1))
        limit = int(data.get("limit", 10))

        query = Q()

        if workspace_query:
            regex = re.compile(workspace_query, re.IGNORECASE)
            query &= (Q(name=regex) | Q(description=regex))

        workspaces = Workspace.objects(query)

        results = []

        for ws in workspaces:
            matched_notes = []

            if note_query:
                regex = re.compile(note_query, re.IGNORECASE)
                matched_notes = [
                    n for n in ws.notes
                    if regex.search(n.title or "") or regex.search(n.content or "")
                ]
            else:
                matched_notes = ws.notes[:]  # all notes

            if tags_query:
                tags = [t.strip().lower() for t in tags_query.split(",") if t.strip()]
                def tag_score(note):
                    return sum(1 for t in note.tags if t.lower() in tags)

                # filter out notes with no matching tags
                matched_notes = [n for n in matched_notes if tag_score(n) > 0]
                # sort by number of matched tags (descending)
                matched_notes.sort(key=tag_score, reverse=True)

            for n in matched_notes:
                results.append({
                    "workspace_id": str(ws.id),
                    "workspace_name": ws.name,
                    "note_id": str(n.id),
                    "title": n.title,
                    "content": n.content,
                    "tags": n.tags,
                    "author": str(n.author) if n.author else None,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                    "updated_at": n.updated_at.isoformat() if n.updated_at else None
                })

        total = len(results)
        start = (page - 1) * limit
        end = start + limit
        paginated = results[start:end]

        return jsonify({
            "status": 200,
            "total": total,
            "page": page,
            "limit": limit,
            "data": paginated
        }), 200

    except Exception as e:
        return jsonify({
            "status": 500,
            "message": "Error performing search",
            "error": str(e)
        }), 500

