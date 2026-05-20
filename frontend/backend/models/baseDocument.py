from datetime import datetime, timezone
from mongoengine import Document, DateTimeField

class BaseDocument(Document):
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))

    meta = {'abstract': True}  # Prevents this from creating a separate collection

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        return super(BaseDocument, self).save(*args, **kwargs)