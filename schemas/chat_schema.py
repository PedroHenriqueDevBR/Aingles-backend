from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    title: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My New Chat",
            }
        }
