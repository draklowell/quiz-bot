from typing import Optional

from babel import Locale

from .. import Repository, User


class UserService:
    repo: Repository

    def __init__(self, repository: Repository) -> None:
        self.repo = repository

    async def resolve_user(
        self,
        telegram_id: int,
        language: Locale,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> User:
        """
        Resolve user

        :param telegram_id:
        :param language:
        :param first_name:
        :param last_name:
        :param username:
        :return: created or updated user
        """
        async with self.repo.transaction():
            user = await self.repo.get_user_by_telegram_id(telegram_id=telegram_id)
            if not user:
                user = await self.repo.create_user(
                    telegram_id,
                    language=language,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                )
            else:
                await self.repo.update_user(
                    user_id=user.id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    language=language,
                )

            return User(
                id=user.id,
                telegram_id=user.telegram_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                language=language,
            )
