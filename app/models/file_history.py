from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FileHistory(BaseModel):
    """Schema for file history records."""
    session_id: str = Field(..., description="Unique identifier for the user session")
    file_name: str = Field(..., description="Original name of the uploaded file")
    translated_file: Optional[str] = Field(None, description="Path to the translated file")
    language: str = Field(..., description="Target language for translation")
    result: Optional[str] = Field(None, description="Translated text or error message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the record was created")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123",
                "file_name": "example.txt",
                "translated_file": "example_translated.txt",
                "language": "fr",
                "result": "Translated content here",
                "created_at": "2024-11-18T12:34:56.789Z",
            }
        }
