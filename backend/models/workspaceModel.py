from mongoengine import StringField, EmailField, ListField, EmbeddedDocumentField, EmbeddedDocument, ObjectIdField, DateTimeField
from datetime import datetime, timezone
from bson import ObjectId

from backend.models.baseDocument import BaseDocument

class Notes(EmbeddedDocument):
    id = ObjectIdField(default=ObjectId, primary_key=True)
    title = StringField(required=True)
    content = StringField()
    tags = ListField(StringField())
    author = ObjectIdField()
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))

class Workspace(BaseDocument):
    name = StringField(required=True)
    description = StringField()
    collaborators = ListField(ObjectIdField())
    notes = ListField(EmbeddedDocumentField(Notes))
