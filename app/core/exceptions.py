from typing import Any


class CoreError(Exception):
    """Base core error"""

    text: str = "Unknown core error"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(self.text.format(kwargs))


class ServiceError(CoreError):
    text = "Unknown service error"


class QuizNotFoundError(ServiceError):
    text = "Quiz with id {id} not found"


class QuizAnswerNotFoundError(ServiceError):
    text = "Quiz answer with id {id} not found"


class UserNotFoundError(ServiceError):
    text = "User with id {id} not found"
