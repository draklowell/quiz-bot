from typing import Iterable, List, Optional, Tuple, TypeVar, Union

import aiosqlite
from babel import Locale

from ...core.repository import (
    QuizAnswerModel,
    QuizModel,
    QuizQuestionModel,
    QuizSessionAnswerModel,
    QuizSessionModel,
    Repository,
    UserModel,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS "quiz" (
	"id"	INTEGER,
	"description"	TEXT NOT NULL,
	"language"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "quiz_answer" (
	"id"	INTEGER,
	"question_id"	INTEGER NOT NULL,
	"right"	INTEGER NOT NULL,
	"value"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("question_id") REFERENCES "quiz_question"("id") ON DELETE CASCADE,
	UNIQUE("question_id","value")
);
CREATE TABLE IF NOT EXISTS "quiz_question" (
	"id"	INTEGER,
	"quiz_id"	INTEGER NOT NULL,
	"question"	TEXT NOT NULL,
	FOREIGN KEY("quiz_id") REFERENCES "quiz"("id") ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "quiz_session" (
	"id"	INTEGER,
	"quiz_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	"language"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("quiz_id") REFERENCES "quiz"("id") ON DELETE SET NULL,
	FOREIGN KEY("user_id") REFERENCES "user"("id") ON DELETE CASCADE,
	UNIQUE("quiz_id","user_id")
);
CREATE TABLE IF NOT EXISTS "quiz_session_answer" (
	"id"	INTEGER,
	"answer_id"	INTEGER,
	"session_id"	INTEGER NOT NULL,
	"question"	TEXT NOT NULL,
	"answer"	TEXT NOT NULL,
	"right"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("answer_id") REFERENCES "quiz_answer"("id") ON DELETE SET NULL,
	FOREIGN KEY("session_id") REFERENCES "quiz_session"("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER,
	"telegram_id"	INTEGER NOT NULL UNIQUE,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT,
	"username"	TEXT,
	"language"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("telegram_id")
);
CREATE INDEX IF NOT EXISTS "quiz_answer_question_id_idx" ON "quiz_answer" (
	"question_id"	ASC
);
CREATE INDEX IF NOT EXISTS "quiz_language_idx" ON "quiz" (
	LOWER("language")
);
CREATE INDEX IF NOT EXISTS "quiz_question_quiz_id_idx" ON "quiz_question" (
	"quiz_id"	ASC
);
CREATE INDEX IF NOT EXISTS "quiz_session_answer_session_id_idx" ON "quiz_session_answer" (
	"session_id"	ASC
);
CREATE INDEX IF NOT EXISTS "quiz_session_user_id_idx" ON "quiz_session" (
	"user_id"	ASC
);
CREATE UNIQUE INDEX IF NOT EXISTS "user_telegram_id_idx" ON "user" (
	"telegram_id"	ASC
);
"""


T = TypeVar("T")


class MemoryRepository(Repository):
    path: str
    connection: Optional[aiosqlite.Connection] = None

    def __init__(self, path: str) -> None:
        self.path = path

    async def generate_schema(self):
        async with self.transaction():
            await self.connection.executescript(SCHEMA)

    async def connect(self):
        self.connection = await aiosqlite.connect(self.path)
        self.connection.row_factory = aiosqlite.Row

    async def close(self):
        await self.connection.close()

    async def begin_transaction(self):
        # Clean journal
        await self.connection.commit()

    async def cancel_transaction(self):
        await self.connection.rollback()

    async def commit_transaction(self):
        await self.connection.commit()

    @staticmethod
    def _generate_constraints(**kwargs: T) -> Tuple[List[str], List[T]]:
        constraints = []
        values = []

        for name, value in kwargs.items():
            name = name.replace("`", "\\`")
            if value is object:
                constraints.append(f"`{name}`")
            else:
                constraints.append("?")
                values.append(value)

        return constraints, values

    def _build_user(self, row: Union[aiosqlite.Row, None]) -> Optional[UserModel]:
        return row and UserModel(
            id=row["id"],
            telegram_id=row["telegram_id"],
            language=Locale.parse(row["language"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            username=row["username"],
        )

    def _build_quiz(self, row: Union[aiosqlite.Row, None]) -> Optional[QuizModel]:
        return row and QuizModel(
            id=row["id"],
            description=row["description"],
            language=Locale.parse(row["language"]),
        )

    def _build_quiz_answer(
        self, row: Union[aiosqlite.Row, None]
    ) -> Optional[QuizAnswerModel]:
        return row and QuizAnswerModel(
            id=row["id"],
            question_id=row["question_id"],
            right=row["right"],
            value=row["value"],
        )

    def _build_quiz_question(
        self, row: Union[aiosqlite.Row, None]
    ) -> Optional[QuizQuestionModel]:
        return row and QuizQuestionModel(
            id=row["id"],
            quiz_id=row["quiz_id"],
            question=row["question"],
        )

    def _build_quiz_session(
        self, row: Union[aiosqlite.Row, None]
    ) -> Optional[QuizSessionModel]:
        return row and QuizSessionModel(
            id=row["id"],
            quiz_id=row["quiz_id"],
            user_id=row["user_id"],
            description=row["description"],
            language=Locale.parse(row["language"]),
        )

    def _build_quiz_session_answer(
        self, row: Union[aiosqlite.Row, None]
    ) -> Optional[QuizSessionAnswerModel]:
        return row and QuizSessionAnswerModel(
            id=row["id"],
            answer_id=row["answer_id"],
            session_id=row["session_id"],
            question=row["question"],
            answer=row["answer"],
            right=bool(row["right"]),
        )

    async def get_user(self, user_id: int) -> Optional[UserModel]:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "SELECT * FROM user WHERE id=?",
                (user_id,),
            )
            return self._build_user(await cur.fetchone())

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserModel]:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "SELECT * FROM user WHERE telegram_id=?",
                (telegram_id,),
            )
            return self._build_user(await cur.fetchone())

    async def get_quiz(self, quiz_id: int) -> Optional[QuizModel]:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "SELECT * FROM quiz WHERE id=?",
                (quiz_id,),
            )
            return self._build_quiz(await cur.fetchone())

    async def get_quiz_answer(self, answer_id: int) -> Optional[QuizAnswerModel]:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "SELECT * FROM quiz_answer WHERE id=?",
                (answer_id,),
            )
            return self._build_quiz_answer(await cur.fetchone())

    async def get_quiz_question(self, question_id: int) -> Optional[QuizQuestionModel]:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "SELECT * FROM quiz_question WHERE id=?",
                (question_id,),
            )
            return self._build_quiz_question(await cur.fetchone())

    async def create_user(
        self,
        telegram_id: int,
        language: Locale,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> UserModel:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "INSERT INTO user(telegram_id, language, first_name, last_name, username) VALUES (?, ?, ?, ?, ?)",
                (telegram_id, str(language), first_name, last_name, username),
            )
            id = cur.lastrowid
            return UserModel(
                id=id,
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                language=language,
            )

    async def create_quiz(self, description: str, language: Locale) -> QuizModel:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "INSERT INTO quiz(description, language) VALUES (?, ?)",
                (description, str(language)),
            )
            id = cur.lastrowid
            return QuizModel(
                id=id,
                description=description,
                language=language,
            )

    async def create_quiz_question(
        self, quiz_id: int, question: str
    ) -> QuizQuestionModel:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "INSERT INTO quiz_question(quiz_id, question) VALUES (?, ?)",
                (quiz_id, question),
            )
            id = cur.lastrowid
            return QuizQuestionModel(
                id=id,
                quiz_id=quiz_id,
                question=question,
            )

    async def create_quiz_answer(
        self, question_id: int, value: str, right: bool
    ) -> QuizAnswerModel:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "INSERT INTO quiz_answer(question_id, value, right) VALUES (?, ?, ?)",
                (question_id, value, right),
            )
            id = cur.lastrowid
            return QuizAnswerModel(
                id=id,
                question_id=question_id,
                value=value,
                right=right,
            )

    async def create_quiz_session(
        self, user_id: int, quiz_id: int, description: str, language: Locale
    ) -> QuizSessionModel:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "INSERT INTO quiz_session(user_id, quiz_id, description, language) VALUES (?, ?, ?, ?)",
                (user_id, quiz_id, description, str(language)),
            )
            id = cur.lastrowid
            return QuizSessionModel(
                id=id,
                user_id=user_id,
                quiz_id=quiz_id,
                description=description,
                language=language,
            )

    async def create_quiz_session_answer(
        self, session_id: int, answer_id: int, question: str, answer: str, right: bool
    ) -> QuizSessionAnswerModel:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "INSERT INTO quiz_session_answer(session_id, answer_id, question, answer, right) VALUES (?, ?, ?, ?, ?)",
                (session_id, answer_id, question, answer, right),
            )
            id = cur.lastrowid
            return QuizSessionAnswerModel(
                id=id,
                session_id=session_id,
                answer_id=answer_id,
                question=question,
                answer=answer,
                right=right,
            )

    async def update_user(
        self,
        user_id: int,
        language: Union[Locale, object] = ...,
        first_name: Union[str, object] = ...,
        last_name: Union[str, None, object] = ...,
        username: Union[str, None, object] = ...,
    ):
        async with self.connection.cursor() as cur:
            constraints, values = self._generate_constraints(
                language=str(language),
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
            await cur.execute(
                "UPDATE user SET language={}, first_name={}, last_name={}, username = {} WHERE id=?".format(
                    *constraints
                ),
                (*values, user_id),
            )

    async def list_quizzes_by_language(
        self, language: Locale, offset: Optional[int] = 0, limit: Optional[int] = 100
    ) -> Iterable[QuizModel]:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "SELECT * FROM quiz WHERE LOWER(language) = LOWER(?) LIMIT ?, ?",
                (str(language), offset, limit),
            )
            result = []
            async for row in cur:
                result.append(self._build_quiz(row))
            return result

    async def count_quizzes_by_language(self, language: Locale) -> int:
        async with self.connection.cursor() as cur:
            await cur.execute(
                "SELECT COUNT(id) AS `count` FROM quiz WHERE LOWER(language) = LOWER(?)",
                (str(language),),
            )
            return (await cur.fetchone())["count"]
