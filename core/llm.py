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
