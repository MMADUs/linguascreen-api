from openai import AzureOpenAI

from azure.ai.translation.text import TextTranslationClient
from azure.ai.vision.imageanalysis import ImageAnalysisClient

from azure.core.credentials import AzureKeyCredential

from config import settings


def new_azure_text_translation_client():
    """Make new instance of azure text translation client"""
    # get credentials from settings
    api_key = settings.AZURE_TEXT_TRANSLATION_API_KEY
    region = settings.AZURE_TEXT_TRANSLATION_REGION
    # generate credential and client
    credential = AzureKeyCredential(api_key)
    client = TextTranslationClient(credential=credential, region=region)
    print("Azure text-translator client connected")
    # connection established
    return client


def new_azure_image_analysis_client():
    """Make new instance of azure image analysis client"""
    # get credentials from settings
    endpoint = settings.AZURE_IMAGE_ANALYSIS_ENDPOINT
    api_key = settings.AZURE_IMAGE_ANALYSIS_API_KEY
    # generate client
    credential = AzureKeyCredential(api_key)
    client = ImageAnalysisClient(endpoint=endpoint, credential=credential)
    print("Azure image-analysis client connected")
    # connection established
    return client


def new_azure_llm_openai_client():
    """Make new instance of azure llm open-ai client"""
    # get credentials from settings
    api_version = settings.AZURE_LLM_OPENAI_API_VERSION
    endpoint = settings.AZURE_LLM_OPENAI_ENDPOINT
    api_key = settings.AZURE_LLM_OPENAI_API_KEY
    # generate client
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    print("Azure llm open AI client connected")
    # connection established
    return client


translator_client: TextTranslationClient = new_azure_text_translation_client()
ocr_client: ImageAnalysisClient = new_azure_image_analysis_client()
llm_client: AzureOpenAI = new_azure_llm_openai_client()
