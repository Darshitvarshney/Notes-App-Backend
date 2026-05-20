from mongoengine import StringField, EmailField, ListField, EmbeddedDocumentField, EmbeddedDocument, ObjectIdField
from backend.models.baseDocument import BaseDocument

class Collaborator(BaseDocument):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    workspace = ListField(ObjectIdField())
    notesId = ListField(ObjectIdField())