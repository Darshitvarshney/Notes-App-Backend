from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime, timezone

from backend.utils.token import generate_token, serialize_doc, token_user_required

from backend.models.adminModel import Admin
from backend.models.collaboratorModel import Collaborator
from backend.models.workspaceModel import Workspace, Notes

colab_bp = Blueprint('colab_bp', __name__)

@colab_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"message": "Name, email, and password are required", "status": 400}), 400

        if Collaborator.objects(email=email).first():
            return jsonify({"message": "Email already exists", "status": 400}), 400

        hashed_password = generate_password_hash(password)

        colab = Collaborator(
            name=name,
            email=email,
            password=hashed_password,
        )
        colab.save()

        token = generate_token(colab)
        return jsonify({
            "message": "Signup successful",
            "status": 200,
            "token": token,
            "data": {
                "id": str(colab.id),
                "name": colab.name,
                "email": colab.email
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "Error signing up", "status": 500, "error": str(e)}), 500
    
    
@colab_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Email and password required", "status": 400}), 400

        colab = Collaborator.objects(email=email).first()
        if not colab or not check_password_hash(colab.password, password):
            return jsonify({"message": "Invalid credentials", "status": 401}), 401

        token = generate_token(colab)
        return jsonify({
            "message": "Login successful",
            "status": 200,
            "token": token,
            "data": {
                "id": str(colab.id),
                "name": colab.name,
                "email": colab.email
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "Error logging in", "status": 500, "error": str(e)}), 500
    

@colab_bp.route("/create-notes", methods=["POST"])
@token_user_required
def create_notes(user):
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        tags = data.get("tags")
        author = user["_id"]
        workspace_id = data.get("workspace_id")

        if not title or not content or not workspace_id:
            return jsonify({"message": "Title, content, and workspace ID are required", "status": 400}), 400

        workspace_doc = Workspace.objects(id=workspace_id).first()
        if not workspace_doc:
            return jsonify({"message": "Workspace not found", "status": 404}), 404
        
        tags = [tag.strip() for tag in tags.split(",")]
        workspace = Workspace.objects(id=workspace_id).first()
        if not workspace:
            return jsonify({"message": "Workspace not found", "status": 404}), 404
        
        collaborator = Collaborator.objects(id=author).first()
        if not collaborator:
            return jsonify({"message": "Collaborator not found", "status": 404}), 404
        
        if ObjectId(workspace_id) not in collaborator.workspace:
            return jsonify({"message": "You are not a member of this workspace", "status": 401}), 401

        note = Notes(title=title, content=content, tags=tags, author=author)
        workspace.notes.append(note)
        collaborator.notesId.append(note.id)
        workspace.save()
        collaborator.save()

        return jsonify({"message": "Note created successfully", "status": 201}), 201

    except Exception as e:
        return jsonify({"message": "Error creating note", "status": 500, "error": str(e)}), 500
    

@colab_bp.route("/edit-notes", methods=["PUT"])
@token_user_required
def edit_notes(user):
    try:
        data = request.get_json()
        workspace_id = data.get("workspace_id")
        note_id = data.get("note_id")
        title = data.get("title")
        content = data.get("content")
        tags = data.get("tags")
        tags = [tag.strip() for tag in tags.split(",")]

        if not note_id or not title or not content:
            return jsonify({"message": "Note ID, title, and content are required", "status": 400}), 400

        workspace_doc = Workspace.objects(id=workspace_id).first()
        if not workspace_doc:
            return jsonify({"message": "Workspace not found", "status": 404}), 404
        
        collaborator = Collaborator.objects(id=user["_id"]).first()
        if not collaborator:
            return jsonify({"message": "Collaborator not found", "status": 404}), 404
        
        if ObjectId(workspace_id) not in collaborator.workspace:
            return jsonify({"message": "You are not a member of this workspace", "status": 401}), 401
        
        note = None
        for n in workspace_doc.notes:
            if str(n.id) == str(note_id):
                note = n
                break

        if not note:
            return jsonify({
                "message": "Note not found in this workspace", 
                "status": 404
            }), 404

        # update fields
        note.title = title
        note.content = content
        note.tags = tags
        note.updated_at = datetime.now(timezone.utc)

        # save parent document
        workspace_doc.save()

        return jsonify({
            "message": "Note updated successfully", 
            "status": 200
        }), 200

    except Exception as e:
        return jsonify({"message": "Error updating note", "status": 500, "error": str(e)}), 500
    

@colab_bp.route("/all-notes", methods=["GET"])
@token_user_required
def all_notes(user):
    try:
        data = request.get_json()
        workspace_id = data.get("workspace_id")

        if not workspace_id:
            return jsonify({"message": "Workspace ID is required", "status": 400}), 400

        workspace_doc = Workspace.objects(id=workspace_id).first()
        if not workspace_doc:
            return jsonify({"message": "Workspace not found", "status": 404}), 404
        
        collaborator = Collaborator.objects(id=user["_id"]).first()
        if not collaborator:
            return jsonify({"message": "Collaborator not found", "status": 404}), 404
        
        if ObjectId(workspace_id) not in collaborator.workspace:
            return jsonify({"message": "You are not a member of this workspace", "status": 401}), 401

        notes = workspace_doc.notes

        return jsonify({"message": "Notes retrieved successfully", "status": 200, "data": serialize_doc(notes)}), 200

    except Exception as e:
        return jsonify({"message": "Error retrieving notes", "status": 500, "error": str(e)}), 500
    

@colab_bp.route("/all-workspaces", methods=["GET"])
@token_user_required
def all_workspaces(user):
    try:
        collaborator_id = user["_id"]
        collaborator = Collaborator.objects(id=collaborator_id).first()
        if not collaborator:
            return jsonify({
                "message": "Collaborator not found",
                "status": 404
            }), 404

        workspace_ids = collaborator.workspace  
        workspaces_data = []

        for ws_id in workspace_ids:
            workspace = Workspace.objects(id=ws_id).first()
            if workspace:
                ws_dict = serialize_doc(workspace)
                workspaces_data.append(ws_dict)

        return jsonify({
            "message": "Workspaces retrieved successfully",
            "status": 200,
            "data": workspaces_data
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Error retrieving workspaces",
            "status": 500,
            "error": str(e)
        }), 500