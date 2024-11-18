import httpx
import os

API_URL = "https://api.example.com/translate"
API_KEY = os.getenv("LLM_API_KEY")


async def translate_text(content: str, target_language: str) -> str:
    """Translate text using an external LLM API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_URL,
            json={"text": content, "target_language": target_language},
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        response.raise_for_status()
        return response.json()["translated_text"]
