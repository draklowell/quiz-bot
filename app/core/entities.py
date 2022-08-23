from dataclasses import dataclass
from typing import List, Optional

from babel import Locale


@dataclass(frozen=True)
class User:
    id: int

    telegram_id: int

    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    language: Locale


@dataclass(frozen=True)
class QuizAnswer:
    id: int

    value: str
    right: bool


@dataclass(frozen=True)
class QuizQuestion:
    id: int

    question: str

    answers: List[QuizAnswer]


@dataclass(frozen=True)
class Quiz:
    id: int

    description: str
    language: Locale

    questions: Optional[List[QuizQuestion]]


@dataclass(frozen=True)
class QuizSessionAnswer:
    id: int

    question: str
    answer: str
    right: bool


@dataclass(frozen=True)
class QuizSession:
    id: int

    description: str
    language: Locale

    quiz: Optional[Quiz]
    answers: List[QuizSessionAnswer]
    user: User
