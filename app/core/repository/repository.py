from abc import ABC, abstractmethod
from typing import Iterable, Optional, Union

from babel import Locale

from .models import (
    QuizAnswerModel,
    QuizModel,
    QuizQuestionModel,
    QuizSessionAnswerModel,
    QuizSessionModel,
    UserModel,
)


class Repository(ABC):
    """
    Generic repository class
    """

    # Transaction sugar
    def transaction(self) -> "Repository":
        """
        Get transaction context
        """
        return self

    async def __aenter__(self):
        await self.begin_transaction()
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        if exception_type:
            await self.cancel_transaction()
        else:
            await self.commit_transaction()

    # Methods without implementation
    @abstractmethod
    async def begin_transaction(self):
        """
        Begin transaction
        """
        pass

    @abstractmethod
    async def cancel_transaction(self):
        """
        Cancel all changes made in transaction
        """
        pass

    @abstractmethod
    async def commit_transaction(self):
        """
        Commit all changes made in transaction to database
        """
        pass

    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[UserModel]:
        """
        Get user by id

        :param user_id: user id ( not telegram id )
        :return: user or None if not found
        """
        pass

    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserModel]:
        """
        Get user by telegram id

        :param telegram_id:
        :return: user or None if not found
        """
        pass

    @abstractmethod
    async def create_user(
        self,
        telegram_id: int,
        language: Locale,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> UserModel:
        """
        Create user

        :param telegram_id:
        :param language:
        :param first_name:
        :param last_name:
        :param username:
        :return: created user
        """
        pass

    @abstractmethod
    async def update_user(
        self,
        user_id: int,
        language: Union[Locale, object] = object,
        first_name: Union[str, object] = object,
        last_name: Union[str, None, object] = object,
        username: Union[str, None, object] = object,
    ):
        """
        Update user ( use :class:`object` if not used )

        :param user_id:
        :param language:
        :param first_name:
        :param last_name:
        :param username:
        :return:
        """
        pass

    @abstractmethod
    async def get_quiz(self, quiz_id: int) -> Optional[QuizModel]:
        """
        Get quiz

        :param quiz_id:
        :return: quiz or None if not found
        """
        pass

    @abstractmethod
    async def list_quizzes_by_language(
        self,
        language: Locale,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
    ) -> Iterable[QuizModel]:
        """
        List quizzes by supported language

        :param language:
        :param offset: number of quizzes to skip
        :param limit:
        :return: list of quizzes
        """
        pass

    @abstractmethod
    async def count_quizzes_by_language(self, language: Locale) -> int:
        """
        Get count of quizzes by supported language

        :param language:
        :return: count of quizzes
        """
        pass

    @abstractmethod
    async def get_quiz_question(self, question_id: int) -> Optional[QuizQuestionModel]:
        """
        Get quiz question

        :param question_id:
        :return: quiz question or None if not found
        """
        pass

    @abstractmethod
    async def get_quiz_answer(self, answer_id: int) -> Optional[QuizAnswerModel]:
        """
        Get quiz answer

        :param answer_id:
        :return: quiz answer or None if not found
        """
        pass

    @abstractmethod
    async def create_quiz(self, description: str, language: Locale) -> QuizModel:
        """
        Create quiz

        :param description:
        :param language:
        :return: created quiz
        """
        pass

    @abstractmethod
    async def create_quiz_question(
        self, quiz_id: int, question: str
    ) -> QuizQuestionModel:
        """
        Create quiz question

        :param quiz_id:
        :param question:
        :return: created quiz question
        """
        pass

    @abstractmethod
    async def create_quiz_answer(
        self, question_id: int, value: str, right: bool
    ) -> QuizAnswerModel:
        """
        Create quiz answer

        :param question_id:
        :param value:
        :param right:
        :return: created quiz answer
        """
        pass

    @abstractmethod
    async def create_quiz_session(
        self, user_id: int, quiz_id: int, description: str, language: Locale
    ) -> QuizSessionModel:
        """
        Create quiz session

        :param user_id:
        :param quiz_id:
        :description:
        :language:
        :return: created quiz session
        """
        pass

    @abstractmethod
    async def create_quiz_session_answer(
        self, session_id: int, answer_id: int, question: str, answer: str, right: bool
    ) -> QuizSessionAnswerModel:
        """
        Add answer to quiz session

        :param session_id:
        :param answer_id:
        :param question:
        :param answer:
        :param right:
        :return: created quiz session answer
        """
        pass
