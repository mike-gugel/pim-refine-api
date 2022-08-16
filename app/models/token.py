from ormar.models import Model
from ormar import String, DateTime, UUID

from app.db import metadata, database

from sqlalchemy import func


class InvalidTokenModel(Model):
    class Meta:
        tablename = 'invalid_token'
        metadata = metadata
        database = database

    token = String(
        primary_key=True, index=True,
        unique=True, nullable=False, max_length=256
        )
    user_id = UUID()
    invalidated_at = DateTime(server_default=func.current_timestamp())
