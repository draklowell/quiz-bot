from itertools import islice
from typing import List, Optional, Union

from babel import Locale

from app.core import Repository
from app.core.repository.models import (
    QuizAnswerModel,
    QuizModel,
    QuizQuestionModel,
    QuizSessionAnswerModel,
    QuizSessionModel,
    UserModel,
)


class MemoryRepository(Repository):
    def __init__(self) -> None:
        self.tables = {
            "quiz": {"data": [], "seq": 0},
            "quiz_answer": {"data": [], "seq": 0},
            "quiz_question": {"data": [], "seq": 0},
            "quiz_session": {"data": [], "seq": 0},
            "quiz_session_answer": {"data": [], "seq": 0},
            "user": {"data": [], "seq": 0},
        }

    async def begin_transaction(self):
        pass

    async def cancel_transaction(self):
        pass

    async def commit_transaction(self):
        pass

    def _table(self, table: str) -> list:
        return self.tables[table]["data"]

    def _seq(self, table: str) -> int:
        self.tables[table]["seq"] += 1
        return self.tables[table]["seq"]

    async def get_user(self, id: int) -> Optional[UserModel]:
        try:
            return next(
                filter(
                    lambda user: user.id == id,
                    self._table("user"),
                )
            )
        except StopIteration:
            return None

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserModel]:
        try:
            return next(
                filter(
                    lambda user: user.telegram_id == telegram_id,
                    self._table("user"),
                )
            )
        except StopIteration:
            return None

    async def create_user(
        self,
        telegram_id: int,
        language: Locale,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> UserModel:
        model = UserModel(
            id=self._seq("user"),
            telegram_id=telegram_id,
            language=language,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        self._table("user").append(model)
        return model

    def _update_user(
        self,
        user: UserModel,
        language: Locale = object,
        first_name: str = object,
        last_name: Union[str, None] = object,
        username: Union[str, None] = object,
    ) -> UserModel:
        new_language = user.language
        new_first_name = user.first_name
        new_last_name = user.last_name
        new_username = user.username

        if language is not object:
            new_language = language
        if first_name is not object:
            new_first_name = first_name
        if last_name is not object:
            new_last_name = last_name
        if username is not object:
            new_username = username

        model = UserModel(
            id=user.id,
            telegram_id=user.telegram_id,
            first_name=new_first_name,
            last_name=new_last_name,
            username=new_username,
            language=new_language,
        )

        try:
            index = next(
                filter(
                    lambda item: item[1].id == model.id,
                    enumerate(self._table("user")),
                )
            )[0]
        except StopIteration:
            raise KeyError()

        self._table("user")[index] = model

        return model

    async def set_user_first_name(self, user: UserModel, first_name: str) -> UserModel:
        return self._update_user(user, first_name=first_name)

    async def set_user_last_name(
        self, user: UserModel, last_name: Union[str, None]
    ) -> UserModel:
        return self._update_user(user, last_name=last_name)

    async def set_user_username(
        self, user: UserModel, username: Union[str, None]
    ) -> UserModel:
        return self._update_user(user, username=username)

    async def set_user_language(self, user: UserModel, language: Locale) -> UserModel:
        return self._update_user(user, language=language)

    async def get_quiz(self, quiz_id: int) -> Optional[QuizModel]:
        try:
            return next(
                filter(
                    lambda quiz: quiz.id == quiz_id,
                    self._table("quiz"),
                )
            )
        except StopIteration:
            return None

    async def list_quizzes_by_language(
        self,
        language: Locale,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
    ) -> List[QuizModel]:
        start = offset
        stop = limit and offset + limit
        return list(
            islice(
                filter(
                    lambda quiz: quiz.language == language,
                    self._table("quiz"),
                ),
                start,
                stop,
            )
        )

    async def count_quizzes_by_language(self, language: Locale) -> int:
        return len(
            list(
                filter(
                    lambda quiz: quiz.language == language,
                    self._table("quiz"),
                )
            )
        )

    async def get_quiz_question(self, question_id: int) -> Optional[QuizQuestionModel]:
        try:
            return next(
                filter(
                    lambda question: question.id == question_id,
                    self._table("quiz_question"),
                )
            )
        except StopIteration:
            return None

    async def get_quiz_answer(self, answer_id: int) -> Optional[QuizAnswerModel]:
        try:
            return next(
                filter(
                    lambda answer: answer.id == answer_id,
                    self._table("quiz_answer"),
                )
            )
        except StopIteration:
            return None

    async def create_quiz(self, description: str, language: Locale) -> QuizModel:
        model = QuizModel(
            id=self._seq("quiz"),
            description=description,
            language=language,
        )
        self._table("quiz").append(model)
        return model

    async def create_quiz_question(
        self, quiz: QuizModel, question: str
    ) -> QuizQuestionModel:
        model = QuizQuestionModel(
            id=self._seq("quiz_question"),
            quiz_id=quiz.id,
            question=question,
        )
        self._table("quiz_question").append(model)
        return model

    async def create_quiz_answer(
        self, question: QuizQuestionModel, value: str, right: bool
    ) -> QuizAnswerModel:
        model = QuizAnswerModel(
            id=self._seq("quiz_answer"),
            question_id=question.id,
            right=right,
            value=value,
        )
        self._table("quiz_answer").append(model)
        return model

    async def create_quiz_session(
        self, user: UserModel, quiz: QuizModel
    ) -> QuizSessionModel:
        model = QuizSessionModel(
            id=self._seq("quiz_session"),
            quiz_id=quiz.id,
            user_id=user.id,
        )
        self._table("quiz_session").append(model)
        return model

    async def create_quiz_session_answer(
        self, session: QuizSessionModel, answer: QuizAnswerModel
    ) -> QuizSessionAnswerModel:
        model = QuizSessionAnswerModel(
            id=self._seq("quiz_session_answer"),
            answer_id=answer.id,
            session_id=session.id,
        )
        self._table("quiz_session_answer").append(model)
        return model
