from pydantic import BaseModel, Field


class PaperUpdate(BaseModel):
    name: str | None = None
    roll_width: float = Field(..., gt=0)
    note: str | None = None
