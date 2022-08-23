import pytest
from babel import Locale

from app.core.repository.models import (
    QuizAnswerModel,
    QuizModel,
    QuizQuestionModel,
    QuizSessionModel,
    UserModel,
)

from .memory import MemoryRepository

pytestmark = pytest.mark.asyncio

TEST_USER = {
    "telegram_id": 42,
    "first_name": "John",
    "last_name": "Pink",
    "username": "johnpink42",
    "language": Locale("en", "AU"),
}
TEST_QUIZ = {
    "description": "Capitals quiz",
    "language": Locale("en", "AU"),
}
TEST_QUESTION = {"question": "Which city is the capital of Britain?"}
TEST_ANSWER = {
    "value": "London",
    "right": True,
}


async def test_get_user():
    repo = MemoryRepository()
    user = UserModel(id=1, **TEST_USER)

    repo.tables["user"]["data"].append(user)

    assert await repo.get_user(user.id) == user
    assert await repo.get_user(0) is None


async def test_get_user_by_telegram_id():
    repo = MemoryRepository()
    user = UserModel(id=1, **TEST_USER)

    repo.tables["user"]["data"].append(user)

    assert await repo.get_user_by_telegram_id(user.telegram_id) == user
    assert await repo.get_user_by_telegram_id(1) is None


async def test_create_user():
    repo = MemoryRepository()
    user = UserModel(id=1, **TEST_USER)

    assert (
        await repo.create_user(
            user.telegram_id,
            user.language,
            user.first_name,
            user.last_name,
            user.username,
        )
        == user
    )
    assert repo.tables["user"]["data"][0] == user
    assert repo.tables["user"]["seq"] == 1


async def test_update_user():
    repo = MemoryRepository()
    user = UserModel(id=1, **TEST_USER)

    repo.tables["user"]["data"].append(user)

    received_user = await repo.set_user_first_name(user, "Jack")

    assert received_user.id == user.id
    assert received_user.telegram_id == user.telegram_id
    assert received_user.first_name == "Jack"
    assert received_user.last_name == user.last_name
    assert received_user.username == user.username
    assert received_user.language == user.language

    user = received_user
    received_user = await repo.set_user_last_name(user, "White")

    assert received_user.id == user.id
    assert received_user.telegram_id == user.telegram_id
    assert received_user.first_name == "Jack"
    assert received_user.last_name == "White"
    assert received_user.username == user.username
    assert received_user.language == user.language

    user = received_user
    received_user = await repo.set_user_username(user, "jackwhite20")

    assert received_user.id == user.id
    assert received_user.telegram_id == user.telegram_id
    assert received_user.first_name == "Jack"
    assert received_user.last_name == "White"
    assert received_user.username == "jackwhite20"
    assert received_user.language == user.language

    user = received_user
    received_user = await repo.set_user_language(user, Locale("en", "GB"))

    assert received_user.id == user.id
    assert received_user.telegram_id == user.telegram_id
    assert received_user.first_name == "Jack"
    assert received_user.last_name == "White"
    assert received_user.username == "jackwhite20"
    assert received_user.language == Locale("en", "GB")


async def test_get_quiz():
    repo = MemoryRepository()
    quiz = QuizModel(id=1, description="Capitals quiz", language=Locale("en", "AU"))

    repo.tables["quiz"]["data"].append(quiz)

    assert await repo.get_quiz(quiz.id) == quiz

    assert await repo.get_quiz(0) is None


async def test_list_count_quizzes_by_language():
    repo = MemoryRepository()
    quizzes_gb = [
        QuizModel(id=1, description="Quiz1", language=Locale("en", "GB")),
    ]
    quizzes_au = [
        QuizModel(id=2, description="Quiz2", language=Locale("en", "AU")),
        QuizModel(id=3, description="Quiz3", language=Locale("en", "AU")),
        QuizModel(id=4, description="Quiz4", language=Locale("en", "AU")),
        QuizModel(id=5, description="Quiz5", language=Locale("en", "AU")),
        QuizModel(id=6, description="Quiz6", language=Locale("en", "AU")),
        QuizModel(id=7, description="Quiz7", language=Locale("en", "AU")),
    ]
    quizzes = quizzes_gb + quizzes_au

    repo.tables["quiz"]["data"] += quizzes

    assert await repo.count_quizzes_by_language(Locale("en", "AU")) == 6
    assert await repo.count_quizzes_by_language(Locale("en", "GB")) == 1
    assert await repo.count_quizzes_by_language(Locale("en", "US")) == 0

    assert (await repo.list_quizzes_by_language(Locale("en", "AU"), 1, 1))[
        0
    ] == quizzes_au[1]
    assert await repo.list_quizzes_by_language(Locale("en", "AU")) == quizzes_au
    assert (
        await repo.list_quizzes_by_language(Locale("en", "AU"), 0, 5)
    ) == quizzes_au[:5]
    assert await repo.list_quizzes_by_language(Locale("en", "GB")) == quizzes_gb
    assert len(await repo.list_quizzes_by_language(Locale("en", "US"))) == 0


async def test_create_quiz():
    repo = MemoryRepository()
    quiz = QuizModel(id=1, description="Capitals quiz", language=Locale("en", "AU"))

    assert await repo.create_quiz(quiz.description, quiz.language) == quiz
    assert repo.tables["quiz"]["data"][0] == quiz
    assert repo.tables["quiz"]["seq"] == 1


async def test_create_quiz_question():
    repo = MemoryRepository()
    quiz = QuizModel(id=1, **TEST_QUIZ)
    question = QuizQuestionModel(id=1, quiz_id=quiz.id, **TEST_QUESTION)

    repo.tables["quiz"]["data"].append(quiz)

    assert await repo.create_quiz_question(quiz, question.question) == question
    assert repo.tables["quiz_question"]["data"][0] == question
    assert repo.tables["quiz_question"]["seq"] == 1


async def test_create_quiz_answer():
    repo = MemoryRepository()
    question = QuizQuestionModel(id=1, quiz_id=1, **TEST_QUESTION)
    answer = QuizAnswerModel(id=1, question_id=question.id, **TEST_ANSWER)

    repo.tables["quiz_question"]["data"].append(question)

    assert await repo.create_quiz_answer(question, answer.value, answer.right) == answer
    assert repo.tables["quiz_answer"]["data"][0] == answer
    assert repo.tables["quiz_answer"]["seq"] == 1


async def test_create_quiz_session():
    repo = MemoryRepository()
    user = UserModel(id=1, **TEST_USER)
    quiz = QuizModel(id=1, **TEST_QUIZ)

    repo.tables["quiz"]["data"].append(quiz)
    repo.tables["user"]["data"].append(user)

    session = await repo.create_quiz_session(user, quiz)

    assert repo.tables["quiz_session"]["data"][0] == session
    assert repo.tables["quiz_session"]["seq"] == 1
    assert session.id == 1
    assert session.quiz_id == quiz.id
    assert session.user_id == user.id


async def test_create_quiz_session_answer():
    repo = MemoryRepository()
    user = UserModel(id=1, **TEST_USER)
    quiz = QuizModel(id=1, **TEST_QUIZ)
    question = QuizQuestionModel(id=1, quiz_id=quiz.id, **TEST_QUESTION)
    answer = QuizAnswerModel(id=1, question_id=question.id, **TEST_ANSWER)
    session = QuizSessionModel(id=1, quiz_id=quiz.id, user_id=user.id)

    repo.tables["quiz"]["data"].append(quiz)
    repo.tables["user"]["data"].append(user)
    repo.tables["quiz_question"]["data"].append(question)
    repo.tables["quiz_answer"]["data"].append(answer)
    repo.tables["quiz_session"]["data"].append(session)

    session_answer = await repo.create_quiz_session_answer(session, answer)

    assert repo.tables["quiz_session_answer"]["data"][0] == session_answer
    assert repo.tables["quiz_session_answer"]["seq"] == 1
    assert session_answer.id == 1
    assert session_answer.answer_id == answer.id
    assert session_answer.session_id == session.id
