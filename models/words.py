from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .sentences import Sentences


class WordsBase(SQLModel):
    """Base model for saved words"""

    word: str
    desc: str
    sentences_id: Optional[int] = Field(default=None, foreign_key="sentences.id")


class Words(WordsBase, table=True):
    """Database model for saved words"""

    id: Optional[int] = Field(default=None, primary_key=True)

    sentences: Optional["Sentences"] = Relationship(back_populates="words")
