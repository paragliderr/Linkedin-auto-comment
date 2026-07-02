from pydantic import BaseModel


class SettingsRequest(BaseModel):
    api_key: str
    base_url: str
    model: str