from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship

from .words import Words


class SentencesBase(SQLModel):
    """Base model for saved sentences"""

    original: str
    original_lang: str
    translation: str
    translation_lang: str
    explanation: Optional[str] = None
    user_id: Optional[int] = None


class Sentences(SentencesBase, table=True):
    """Database model for saved sentences"""

    id: Optional[int] = Field(default=None, primary_key=True)

    # relationship to words
    words: List[Words] = Relationship(back_populates="sentences")

