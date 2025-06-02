# Copyright (c) 2024-2025 LinguaScreen, Inc.
#
# This file is part of LinguaScreen Server
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel

from .words import Words


class SentencesBase(SQLModel, BaseModel):
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


# schema
class TranslationReqBody(BaseModel):
    """Api translation request body schema"""

    to_language: str
    sentences: str

class SentenceResponse(SentencesBase):
    """Model for sentence when sent as a response body"""

    id: int

class GetSentencesResponse(BaseModel):
    """Model for GET /sentence/ response body"""

    message: str
    result: List[SentenceResponse]