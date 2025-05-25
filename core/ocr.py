from typing import List, Optional

from azure.core.exceptions import HttpResponseError
from azure.ai.vision.imageanalysis.models import VisualFeatures

from .client import ocr_client


class ImageOcrResponse:
    """Image Analysis Response Schema"""

    sentences: Optional[str]
    width: Optional[int]
    height: Optional[int]

    def __init__(
        self, sentences: Optional[str], width: Optional[int], height: Optional[int]
    ):
        self.sentences = sentences
        self.width = width
        self.height = height

    def __repr__(self):
        return (
            f"ImageResponse(sentences={self.sentences}, "
            f"Metadata(width={self.width}, height={self.height})"
        )


def ocr_service(image_buffer: bytes) -> ImageOcrResponse:
    """OCR Image to text api service"""
    try:
        # hit api client
        response = ocr_client.analyze(
            image_data=image_buffer, visual_features=[VisualFeatures.READ]
        )
        # prepare for raw line of texts
        merged_lines: List[str] = []
        # merge
        if response.read and response.read.blocks:
            for block in response.read.blocks:
                for line in block.lines:
                    merged_lines.append(line.text)
        # structured response
        metadata = response.metadata if response else None
        return ImageOcrResponse(
            sentences=" ".join(merged_lines) if merged_lines else None,
            width=metadata.width if metadata else None,
            height=metadata.height if metadata else None,
        )
    # catch api errors
    except HttpResponseError as exception:
        print(f"raw error: {exception}")
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
