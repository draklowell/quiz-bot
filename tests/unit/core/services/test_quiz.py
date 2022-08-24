import pytest
from babel import Locale

from app.core import Quiz, QuizService, Repository

pytestmark = pytest.mark.asyncio

TEST_QUIZ = {
    "description": "Capitals quiz",
    "language": Locale("en", "AU"),
}

TEST_USER = {
    "telegram_id": 42,
    "first_name": "John",
    "last_name": "Pink",
    "username": "johnpink42",
    "language": Locale("en", "AU"),
}


async def test_list_quizzes(repo: Repository):
    service = QuizService(repo)

    quizzes_au = set()
    quizzes_gb = set()
    for quiz in [
        {"description": "Quiz1", "language": Locale("en", "GB")},
        {"description": "Quiz2", "language": Locale("en", "AU")},
        {"description": "Quiz3", "language": Locale("en", "AU")},
        {"description": "Quiz4", "language": Locale("en", "AU")},
    ]:
        if quiz["language"] == Locale("en", "AU"):
            quizzes = quizzes_au
        elif quiz["language"] == Locale("en", "GB"):
            quizzes = quizzes_gb
        else:
            quizzes = set()

        quiz = await repo.create_quiz(**quiz)
        quizzes.add(
            Quiz(
                id=quiz.id,
                description=quiz.description,
                language=quiz.language,
                questions=None,
            )
        )

    count, received_quizzes = await service.list_quizzes(Locale("en", "AU"))
    assert count == 3
    assert set(received_quizzes) == quizzes_au

    count, received_quizzes = await service.list_quizzes(Locale("en", "GB"))
    assert count == 1
    assert set(received_quizzes) == quizzes_gb

    count, received_quizzes = await service.list_quizzes(Locale("en", "US"))
    assert count == 0
    assert len(received_quizzes) == 0

    count, received_quizzes = await service.list_quizzes(Locale("en", "AU"), 1, 1)
    assert count == 3
    assert set(received_quizzes).issubset(quizzes_au)

    count, received_quizzes = await service.list_quizzes(Locale("en", "AU"), 0, 5)
    assert count == 3
    assert set(received_quizzes) == quizzes_au

    _, received_quizzes_a = await service.list_quizzes(Locale("en", "AU"), 0, 1)
    _, received_quizzes_b = await service.list_quizzes(Locale("en", "AU"), 1, 1)
    assert len(set(received_quizzes_a + received_quizzes_b)) == 2


async def test_submit_answers(repo: Repository):
    service = QuizService(repo)

    user = await repo.create_user(**TEST_USER)
    quiz = await repo.create_quiz(**TEST_QUIZ)

    question1 = await repo.create_quiz_question(
        quiz.id, "Which city is the capital of Great Britain?"
    )
    answer1 = await repo.create_quiz_answer(question1.id, "London", True)
    question2 = await repo.create_quiz_question(
        quiz.id, "Which city is the capital of Japan?"
    )
    answer2 = await repo.create_quiz_answer(question2.id, "Rome", False)

    user, session = await service.submit_answers(
        user.id, quiz.id, [answer1.id, answer2.id]
    )

    assert session.quiz.id == quiz.id
    assert session.quiz.description == quiz.description
    assert session.quiz.language == quiz.language
    assert session.description == quiz.description
    assert session.language == quiz.language
    assert session.user.id == user.id
    assert session.user.telegram_id == user.telegram_id
    assert session.user.first_name == user.first_name
    assert session.user.last_name == user.last_name
    assert session.user.username == user.username
    assert session.user.language == user.language
    assert session.answers[0].question == question1.question
    assert session.answers[0].answer == answer1.value
    assert session.answers[0].right == answer1.right
    assert session.answers[1].question == question2.question
    assert session.answers[1].answer == answer2.value
    assert session.answers[1].right == answer2.right
