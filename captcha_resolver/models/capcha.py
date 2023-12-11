from __future__ import annotations

from pydantic import BaseModel


class RequestModel(BaseModel):
    method: str
    coordinatescaptcha: int
    key: str
    body: str
    imginstructions: str
    textinstructions: str
    sobel_filter: int



