from typing import List, Optional, Set, Tuple

from babel import Locale

from .. import (
    Quiz,
    QuizAnswerNotFoundError,
    QuizNotFoundError,
    QuizSession,
    QuizSessionAnswer,
    Repository,
    User,
    UserNotFoundError,
)


class QuizService:
    repo: Repository

    def __init__(self, repository: Repository) -> None:
        self.repo = repository

    async def submit_answers(
        self, user_id: int, quiz_id: int, answer_ids: Set[int]
    ) -> Tuple[User, QuizSession]:
        """
        Submit answers

        :param user_id:
        :param quiz_id:
        :param answers_id: list of answers
        :return: updated user and created session
        """
        async with self.repo.transaction():
            user = await self.repo.get_user(user_id)
            if user is None:
                raise UserNotFoundError(id=user_id)

            quiz = await self.repo.get_quiz(quiz_id)
            if quiz is None:
                raise QuizNotFoundError(id=quiz_id)

            quiz_session = await self.repo.create_quiz_session(user, quiz)

            answers = []

            for answer_id in answer_ids:
                quiz_answer = await self.repo.get_quiz_answer(answer_id)
                if quiz_answer is None:
                    raise QuizAnswerNotFoundError(id=answer_id)

                quiz_question = await self.repo.get_quiz_question(
                    quiz_answer.question_id
                )
                if quiz_question is None:
                    raise QuizAnswerNotFoundError(id=answer_id)

                quiz_session_answer = await self.repo.create_quiz_session_answer(
                    quiz_session, quiz_answer
                )

                answers.append(
                    QuizSessionAnswer(
                        id=quiz_session_answer.id,
                        question=quiz_question.question,
                        answer=quiz_answer.value,
                        right=quiz_answer.right,
                    )
                )

            user = await self.repo.get_user(user.id)

            return user, QuizSession(
                id=quiz_session.id,
                description=quiz.description,
                language=quiz.language,
                answers=answers,
                user=user,
                quiz=quiz,
            )

    async def list_quizzes(
        self,
        language: Optional[Locale] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
    ) -> Tuple[int, List[Quiz]]:
        """
        List quizzes for specific region

        :param language:
        :param offset: number of quizzes to skip
        :param limit:
        :return: list of quizzes ( without questions )
        """
        async with self.repo.transaction():
            quizzes = []

            for quiz in await self.repo.list_quizzes_by_language(
                language=language, offset=offset, limit=limit
            ):
                quizzes.append(
                    Quiz(
                        id=quiz.id,
                        description=quiz.description,
                        language=quiz.language,
                        questions=None,
                    )
                )

            return (
                await self.repo.count_quizzes_by_language(language),
                quizzes,
            )
