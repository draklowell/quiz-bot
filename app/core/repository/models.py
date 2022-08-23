from dataclasses import dataclass
from typing import Optional

from babel import Locale


@dataclass(frozen=True)
class QuizAnswerModel:
    id: int
    question_id: int

    right: bool
    value: str


@dataclass(frozen=True)
class QuizQuestionModel:
    id: int
    quiz_id: int

    question: str


@dataclass(frozen=True)
class QuizModel:
    id: int

    description: str
    language: Locale


@dataclass(frozen=True)
class QuizSessionModel:
    id: int
    quiz_id: Optional[int]
    user_id: int


@dataclass(frozen=True)
class QuizSessionAnswerModel:
    id: int
    answer_id: int
    session_id: int


@dataclass(frozen=True)
class UserModel:
    id: int

    telegram_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    language: Locale
