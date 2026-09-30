from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    selected_paper_id: int | None = None
