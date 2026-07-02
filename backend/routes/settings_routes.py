from fastapi import APIRouter

from backend.schemas.settings_schema import SettingsRequest
from backend.services.settings_service import (
    get_settings,
    save_settings,
)

router = APIRouter(tags=["Settings"])


@router.get("/settings")
def read_settings():
    return get_settings()


@router.post("/settings")
def update_settings(settings: SettingsRequest):
    save_settings(settings.model_dump())

    return {
        "message": "Settings saved successfully."
    }