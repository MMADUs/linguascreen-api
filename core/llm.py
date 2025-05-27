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

from typing import List
from pydantic import BaseModel

from .client import llm_client

from models.words import WordsBase


class WordsExplanation(BaseModel):
    """Words Explanation Response"""

    each_word: str
    explanation: str


class FormatResponse(BaseModel):
    """LLM Format Response"""

    words_explanation: List[WordsExplanation]
    entire_explanation: str


class LLMResponse(FormatResponse):
    """LLM Response Schema"""

    raw: str
    translated: str
    prompt_tokens: int
    completion_tokens: int


def llm_service(data: WordsBase) -> LLMResponse:
    """LLM api service"""
    # prepare prompt
    prompt = (
        f"Imagine you are a language expert, and analyze the given data:\n"
        f"the original sentences is: {data.original}\n"
        f"the original sentences language is: {data.original_lang.upper()}\n"
        f"the translated sentences is: {data.translation}\n"
        f"the translated sentences language is: {data.translation_lang.upper()}\n"
        f"now explain the meaning of the original and translated sentences in {data.original_lang.upper()} language\n"
        f"make the explanation simple and easy to understand based on the given format\n"
        f"for each word explanation, do not explain duplicated word"
    )
    # hit api client
    response = llm_client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
        ],
        max_tokens=4096,
        response_format=FormatResponse,
        model="gpt-4o-mini-2",
    )
    # structured response
    choice = response.choices[0]
    base: FormatResponse = choice.message.parsed
    return LLMResponse(
        words_explanation=base.words_explanation,
        entire_explanation=base.entire_explanation,
        raw=data.original,
        translated=data.translation,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
    )
