import json

from google import genai

from app.config import settings
from app.models.schemas import ExtractedDocument


# uses google-genai SDK style: genai.Client(api_key=...), not google-generativeai
class GeminiClient:
    """Wraps the Google Gemini API to extract structured data from document text."""

    def __init__(self) -> None:
        # one client instance reused for all calls
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model
        # pre-compute schema once; injected into every prompt
        self._schema_json = json.dumps(
            ExtractedDocument.model_json_schema(), indent=2
        )

    async def extract_document(self, document_text: str) -> ExtractedDocument:
        """Send document text to Gemini and return a validated ExtractedDocument."""
        prompt = (
            "You are a document inntelligence API. Extract structured data from "
            "the following document text.\n\n"
            "Return ONLY valid JSON matching this exact schema -- no markdown, "
            "no explanation, no code fences:\n"
            f"{self._schema_json}\n\n"
            "If a field cannot be determined from the text, use null.\n"
            "Set raw_confidence to a float between 0.0 and 1.0 indicating "
            "how complete and clear the document data was.\n\n"
            f"DOCUMENT TEXT:\n{document_text}"
        )
        # .aio = async I/O namespace of the SDK
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
        )
        # response.text is the raw JSON string Gemini returned
        data = json.loads(response.text)
        # raises ValidationError if Gemini returned wrong shape
        return ExtractedDocument.model_validate(data)
