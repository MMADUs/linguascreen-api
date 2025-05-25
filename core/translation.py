from typing import Optional

from azure.core.exceptions import HttpResponseError

from .client import translator_client


class TranslationResponse:
    """Translation Response Schema"""

    input_text: str
    translation: Optional[str]
    detected_language: Optional[str]
    score: Optional[float]

    def __init__(
        self,
        input_text: str,
        translation: Optional[str],
        detected: Optional[str],
        score: Optional[float],
    ):
        self.input_text = input_text
        self.translation = translation
        self.detected_language = detected
        self.score = score

    def __repr__(self):
        return (
            f"TranslationResponse(translation={self.translation}, "
            f"detected_language={self.detected_language}, score={self.score})"
        )


def translation_service(to_language: str, input_text: str) -> TranslationResponse:
    """Translation api service"""
    # prepare
    to_language = [to_language]
    input_text_elements = [input_text]
    # try catch
    try:
        # hit api client
        response = translator_client.translate(
            body=input_text_elements, to_language=to_language
        )
        # extract response
        translation = response[0] if response else None
        # structured response
        detected = translation.detected_language if translation else None
        return TranslationResponse(
            input_text,
            translation=translation.translations[0].text
            if translation.translations
            else None,
            detected=detected.language if detected else None,
            score=detected.score if detected else None,
        )
    # catch api errors
    except HttpResponseError as exception:
        print(f"raw error: {exception}")
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
