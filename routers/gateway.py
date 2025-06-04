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

from typing import List, Optional
import random

from fastapi import APIRouter, Depends, status, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy import func

from db import get_session

from core.translation import translation_service, TranslationResponse
from core.ocr import raw_ocr_service, ocr_service, ImageOcrResponse
from core.llm import (
    llm_service,
    llm_explaination_service,
    llm_ocr_selection_postprocessing_service,
    LLMResponse,
    WordsExplanation,
    OcrData
)

from models.sentences import Sentences, TranslationReqBody
from models.words import Words
from models.user import User

from security.jwt import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])


class TranslateResponseModel(BaseModel):
    """Response model for translation API"""

    class ResultModel(BaseModel):
        """Result model for translation response"""

        raw: str
        result: str
        from_language: str
        to_language: str
        score: float

    message: str
    result: ResultModel


@router.post(
    "/translate", status_code=status.HTTP_200_OK, response_model=TranslateResponseModel
)
async def translate(req_body: TranslationReqBody):
    """API for text translation only"""
    # translate
    translation_result: TranslationResponse = translation_service(
        req_body.to_language, req_body.sentences
    )
    # return response
    return JSONResponse(
        content={
            "message": "successful text translation",
            "result": {
                "raw": translation_result.input_text,
                "result": translation_result.translation,
                "from_language": translation_result.detected_language,
                "to_language": req_body.to_language,
                "score": translation_result.score,
            },
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/ocr", status_code=status.HTTP_200_OK)
async def ocr(image: UploadFile = File(...)):
    """API for image analysis only"""
    # read image content
    img_buf: bytes = await image.read()
    # scan image
    ocr_result = raw_ocr_service(img_buf)
    # return response
    return {"message": "successful image analysis", "result": ocr_result}

# TODO: clean up context for pydantic models

class OcrSelectionPostprocessRequestBody(BaseModel):
    """Request body for OCR selection postprocess"""

    ocr_data: OcrData

class OcrSelectionPostprocessResponse(BaseModel):
    """Response model for OCR selection postprocess"""

    message: str
    result: str
    
@router.post("/ocr/selection/postprocess", status_code=status.HTTP_200_OK, response_model=OcrSelectionPostprocessResponse)
async def ocr_selection_postprocess(
    req_body: OcrSelectionPostprocessRequestBody,
):
    """API for OCR selection postprocess"""
    text = llm_ocr_selection_postprocessing_service(
        ocr_data=req_body.ocr_data,
    )
    return {
        "message": "successful OCR selection postprocess",
        "result": text,
    }

class ExplainRequestBody(BaseModel):
    """Request body for LLM explanation"""

    original_sentence: str
    translated_sentence: str
    original_lang: str
    target_lang: str


class ExplainResponseModel(BaseModel):
    """Response model for LLM explanation"""

    message: str
    result: LLMResponse


@router.post(
    "/explain", status_code=status.HTTP_200_OK, response_model=ExplainResponseModel
)
async def explain(req_body: ExplainRequestBody):
    """API for LLM explanation"""
    result = llm_explaination_service(
        req_body.original_sentence,
        req_body.translated_sentence,
        req_body.original_lang,
        req_body.target_lang,
    )
    return {
        "message": "successful LLM explanation",
        "result": {
            "words_explanation": result.words_explanation,
            "entire_explanation": result.entire_explanation,
            "original_sentence": result.original_sentence,
            "translated_sentence": result.translated_sentence,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
        },
    }


class LLMExplanationResponse(BaseModel):
    """Response model for LLM explanation API"""

    class MetadataModel(BaseModel):
        """Metadata model for LLM explanation response"""

        prompt_tokens: int
        completion_tokens: int

    class ResultModel(BaseModel):
        """Result model for LLM explanation response"""

        class DictionaryModel(BaseModel):
            """Dictionary model for LLM explanation response"""

            original: str
            original_lang: str
            translation: str
            translation_lang: str

        class ExplanationModel(BaseModel):
            """Explanation model for LLM explanation response"""

            each_word: List[WordsExplanation]
            entire_explanation: str
            romanization: str = ""

        dictionary: DictionaryModel
        explanation: ExplanationModel

    message: str
    metadata: MetadataModel
    result: ResultModel


class WordSavingResponse(BaseModel):
    """Response model for Word Saving /save"""
    message: str = "successfully saved to dictionary"

@router.post("/save", status_code=status.HTTP_200_OK, response_model=WordSavingResponse)
async def explain_and_save(
    req_body: ExplainRequestBody,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """API for LLM explanation and save"""
    result = llm_explaination_service(
        req_body.original_sentence,
        req_body.translated_sentence,
        req_body.original_lang,
        req_body.target_lang,
    )
    # save to db
    sentence: Sentences = Sentences(
        original=req_body.original_sentence,
        original_lang=req_body.original_lang,
        translation=req_body.translated_sentence,
        translation_lang=req_body.target_lang,
        explanation=result.entire_explanation,
        user_id=user.id,
    )
    # query
    db.add(sentence)
    db.commit()
    db.refresh(sentence)
    # save words
    words: List[Words] = [
        Words(
            original_word=word_explanation.original_word,
            translated_word=word_explanation.translated_word,
            explanation=word_explanation.explanation,
            romanization=word_explanation.romanization,
            sentences_id=sentence.id,
        )
        for word_explanation in result.words_explanation
    ]
    # bulk insert
    db.add_all(words)
    # commit changes
    db.commit()
    # return response
    return {"message": "successfully saved to dictionary"}


# Alternative simpler response format if you prefer
class SimpleQuizWord(BaseModel):
    original_word: str
    translated_word: str
    explanation: str
    romanization: Optional[str]
    is_correct_for_question: str  # The word being asked about


class SimpleQuizResponse(BaseModel):
    sentence_id: int
    original_sentence: str
    translation: str
    question_word: str  # The word being asked about
    options: List[SimpleQuizWord]  # 5 words with one being the correct answer
    correct_answer_index: int


@router.get("/quiz", status_code=status.HTTP_200_OK, response_model=SimpleQuizResponse)
async def get_simple_randomized_quiz(
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Generate a simpler quiz format - guess the meaning of one word from 5 options"""

    # Get sentences with at least 5 words
    sentences_with_enough_words = (
        db.query(Sentences)
        .join(Words)
        .filter(Sentences.user_id == user.id)
        .group_by(Sentences.id)
        .having(func.count(Words.id) >= 5)
        .all()
    )

    if not sentences_with_enough_words:
        raise HTTPException(
            status_code=404,
            detail="You need to learn more words in one sentence",
        )

    # Select random sentence
    selected_sentence = random.choice(sentences_with_enough_words)

    # Get words from the sentence
    sentence_words = (
        db.query(Words).filter(Words.sentences_id == selected_sentence.id).all()
    )

    # Select 5 random words
    selected_words = random.sample(sentence_words, 5)

    # Pick one word to be the question
    question_word_data = random.choice(selected_words)

    # Shuffle the options
    random.shuffle(selected_words)

    # Find the new index of the correct answer after shuffling
    new_correct_index = selected_words.index(question_word_data)

    quiz_options = []
    for word in selected_words:
        quiz_options.append(
            SimpleQuizWord(
                original_word=word.original_word,
                translated_word=word.translated_word,
                explanation=word.explanation,
                romanization=word.romanization,
                is_correct_for_question=question_word_data.original_word,
            )
        )

    return SimpleQuizResponse(
        sentence_id=selected_sentence.id,
        original_sentence=selected_sentence.original,
        translation=selected_sentence.translation,
        question_word=question_word_data.original_word,
        options=quiz_options,
        correct_answer_index=new_correct_index,
    )
