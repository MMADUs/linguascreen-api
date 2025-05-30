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

from fastapi import APIRouter, Depends, status, Form, UploadFile, File, HTTPException
from sqlmodel import Session, select

from db import get_session

from core.translation import translation_service, TranslationResponse
from core.ocr import raw_ocr_service, ocr_service, ImageOcrResponse
from core.llm import llm_service, LLMResponse

from models.sentences import Sentences
from models.words import Words
from models.user import User

from security.jwt import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/ocr", status_code=status.HTTP_200_OK)
async def ocr(image: UploadFile = File(...)):
    img_buf: bytes = await image.read()

    ocr_result = raw_ocr_service(img_buf)

    return {"result": ocr_result}


@router.post("/image", status_code=status.HTTP_200_OK)
async def image_to_text(
    to_language: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """API for translating the image content"""
    # read image content
    img_buf: bytes = await image.read()
    # scan image to text
    ocr_result: ImageOcrResponse = ocr_service(img_buf)
    # translate text sentences
    translation_result: TranslationResponse = translation_service(
        to_language, ocr_result.sentences
    )
    # save to db
    data: Sentences = Sentences(
        original=translation_result.input_text,
        original_lang=translation_result.detected_language,
        translation=translation_result.translation,
        translation_lang=to_language,
        description=None,
        user_id=user.id,
    )
    # query
    db.add(data)
    db.commit()
    db.refresh(data)
    # return response
    return {
        "message": "successful image translation",
        "metadata": {
            "width": ocr_result.width,
            "height": ocr_result.height,
        },
        "result": {
            "raw": translation_result.input_text,
            "result": translation_result.translation,
            "from_language": translation_result.detected_language,
            "to_language": to_language,
            "score": translation_result.score,
        },
    }


@router.patch("/llm/{id}", status_code=status.HTTP_200_OK)
async def describe_by_llm(
    id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """API for explaining saved sentences in disctionary with LLM"""
    # get sentence from dictionary
    sentences: Sentences = db.exec(
        select(Sentences).where(Sentences.id == id, Sentences.user_id == user.id)
    ).first()
    # check if exist
    if not sentences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sentences not found in dictionary",
        )
    # generate llm response
    response: LLMResponse = llm_service(sentences)
    # update new explanation to dictionary
    sentences.explanation = response.entire_explanation
    db.add(sentences)
    # check if there is words explained for this sentences
    existing_word: Words = db.exec(
        select(Words).where(Words.sentences_id == sentences.id)
    ).first()
    # check if exist
    if not existing_word:
        words: List[Words] = [
            Words(
                word=word_explanation.each_word,
                desc=word_explanation.explanation,
                sentences_id=sentences.id,
            )
            for word_explanation in response.words_explanation
        ]
        # bulk insert
        db.add_all(words)
    # commit changes
    db.commit()
    db.refresh(sentences)
    # return response
    return {
        "message": "successful llm explanation",
        "metadata": {
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
        },
        "result": {
            "dictionary": {
                "original": sentences.original,
                "original_lang": sentences.original_lang,
                "translation": sentences.translation,
                "translation_lang": sentences.translation_lang,
            },
            "explanation": {
                "each_word": response.words_explanation,
                "entire_explanation": response.entire_explanation,
            },
        },
    }
