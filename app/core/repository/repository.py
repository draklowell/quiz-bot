from abc import ABC, abstractmethod
from typing import List, Optional, Union

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
    async def get_user(self, id: int) -> Optional[UserModel]:
        """
        Get user by id

        :param id: user id ( not telegram id)
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
        :return: user
        """
        pass

    @abstractmethod
    async def set_user_language(self, user: UserModel, language: Locale) -> UserModel:
        """
        Update user language

        :param user: old user
        :param language:
        :return: updated user
        """
        pass

    @abstractmethod
    async def set_user_first_name(self, user: UserModel, first_name: str) -> UserModel:
        """
        Update user first name

        :param user: old user
        :param first_name:
        :return: updated user
        """
        pass

    @abstractmethod
    async def set_user_last_name(
        self, user: UserModel, last_name: Union[str, None]
    ) -> UserModel:
        """
        Update user last name

        :param user: old user
        :param last_name:
        :return: updated user
        """
        pass

    @abstractmethod
    async def set_user_username(
        self, user: UserModel, username: Union[str, None]
    ) -> UserModel:
        """
        Update user username

        :param user: old user
        :param username:
        :return: updated user
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
        limit: Optional[int] = None,
    ) -> List[QuizModel]:
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
        self, quiz: QuizModel, question: str
    ) -> QuizQuestionModel:
        """
        Create quiz question

        :param quiz:
        :param question:
        :return: created quiz question
        """
        pass

    @abstractmethod
    async def create_quiz_answer(
        self, question: QuizQuestionModel, value: str, right: bool
    ) -> QuizAnswerModel:
        """
        Create quiz answer

        :param question:
        :param value:
        :param right:
        :return: created quiz answer
        """
        pass

    @abstractmethod
    async def create_quiz_session(
        self, user: UserModel, quiz: QuizModel
    ) -> QuizSessionModel:
        """
        Create quiz session

        :param user:
        :param quiz:
        :return: created quiz session
        """
        pass

    @abstractmethod
    async def create_quiz_session_answer(
        self, session: QuizSessionModel, answer: QuizAnswerModel
    ) -> QuizSessionAnswerModel:
        """
        Add answer to quiz session

        :param quiz:
        :return: created quiz session answer
        """
        pass
