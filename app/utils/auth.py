import logging

from fastapi_users.authentication import JWTStrategy
from fastapi_users import models

from app.models.token import InvalidTokenModel


logger = logging.getLogger(__name__)


class JWTWithLogout(JWTStrategy):
    async def destroy_token(self, token: str, user: models.UP) -> None:
        invalid_token = await InvalidTokenModel.objects.get_or_create(token=token, user_id=user.id)
        logger.debug(f'invalidated token: <{invalid_token}>')
