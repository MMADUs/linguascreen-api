from typing import Optional
from sqlmodel import Field, SQLModel


class WordsBase(SQLModel):
    """Base model for saved words"""

    original: str
    original_lang: str
    translation: str
    translation_lang: str
    description: Optional[str] = None
    user_id: Optional[int] = None


class Words(WordsBase, table=True):
    """Database model for saved words"""

    id: Optional[int] = Field(default=None, primary_key=True)


# Words schema
class WordsPayload(WordsBase):
    """Schema for item creation"""

    pass


class WordsResponse(WordsBase):
    """Schema for item response"""

    id: int
