from mongoengine import StringField, EmailField, ListField, EmbeddedDocumentField, EmbeddedDocument, ObjectIdField
from backend.models.baseDocument import BaseDocument

class Invitation(EmbeddedDocument):
    email = EmailField(required=True)
    workspaceId = ObjectIdField(required=True)

class Admin(BaseDocument):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    invitation = ListField(EmbeddedDocumentField(Invitation))