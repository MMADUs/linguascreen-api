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
import json


class BoundingPolygon(BaseModel):
    """Bounding Polygon Model"""

    x: float
    y: float

class OcrWord(BaseModel):
    """OCR Word Model"""

    text: str
    bounding_polygon: List[BoundingPolygon]
    confidence: float = 0.0  # Confidence score of the OCR word, default to 0.0

class OcrLine(BaseModel):
    """Line Model"""

    text: str
    bounding_polygon: List[BoundingPolygon]
    words: List[OcrWord]

class OcrData(BaseModel):
    """OCR Data Model"""

    lines: List[OcrLine]


class OcrExtractedText(BaseModel):
    """OCR Extracted Text Model"""

    text: str


def llm_ocr_selection_postprocessing_service(ocr_data: OcrData) -> str:
    """LLM OCR Postprocessing Service"""

    ocr_data_json = json.dumps(ocr_data.model_dump(mode="json"), ensure_ascii=False)

    prompt = """
You are an expert in OCR post-processing. Your primary goal is to reconstruct the text from the provided OCR data in its natural reading order.

Extract the text make sure it sounds natural and coherent in its language. Read from right to left, left to right, top to bottom, or bottom to top depending on the language and context of the text.

You will receive OCR data in JSON format, which includes lines of text and their bounding polygons. 
Your task is to process this data and return a single string that represents the reconstructed text in its correct reading order.
    """

    response = llm_client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": ocr_data_json,
            }
        ],
        max_tokens=4096,
        response_format=OcrExtractedText,
        model="gpt-4o-mini-2",
        temperature=1.0,
    )

    choice = response.choices[0]
    base = choice.message.parsed
    if base is None:
        raise ValueError("LLM response parsing failed, no data returned")

    return base.text


class WordsExplanation(BaseModel):
    """Words Explanation Response"""

    original_word: str
    translated_word: str
    explanation: str
    romanization: str = ""


class FormatResponse(BaseModel):
    """LLM Format Response"""

    words_explanation: List[WordsExplanation]
    entire_explanation: str


class LLMResponse(FormatResponse):
    """LLM Response Schema"""

    original_sentence: str
    translated_sentence: str
    prompt_tokens: int
    completion_tokens: int


def llm_explaination_service(
    original_sentence: str,
    translated_sentence: str,
    original_lang: str,
    target_lang: str,
):
    prompt = f"""
              You are a language expert, and your task is to explain the meaning of the given sentences in {target_lang.upper()} language.
              The original sentence is: {original_sentence}.
              The original sentence language is: {original_lang.upper()}.
              The translated sentence is: {translated_sentence}.
              Please provide a simple and easy-to-understand explanation for both sentences.
              Provide an explanation for each word in the original sentence based on the context, and do not explain duplicated words.
              You may merge words or kanjis or letters depending on the context when it comes to words_explanation.
              Provide romanization/pinyin/romaji/romaja as necessary.
              """

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

    choice = response.choices[0]
    base = choice.message.parsed
    if base is None:
        raise ValueError("LLM response parsing failed, no data returned")

    return LLMResponse(
        words_explanation=base.words_explanation,
        entire_explanation=base.entire_explanation,
        original_sentence=original_sentence,
        translated_sentence=translated_sentence,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
    )


# I'll put this on the backlog for now
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
        original_sentence=data.original,
        translated_sentence=data.translation,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
    )
