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

from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .sentences import Sentences


class WordsBase(SQLModel):
    """Base model for saved words"""

    original_word: str
    translated_word: str
    explanation: str
    romanization: str = ""
    sentences_id: Optional[int] = Field(default=None, foreign_key="sentences.id")


class Words(WordsBase, table=True):
    """Database model for saved words"""

    id: Optional[int] = Field(default=None, primary_key=True)

    sentences: Optional["Sentences"] = Relationship(back_populates="words")
