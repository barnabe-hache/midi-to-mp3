from pydantic import BaseModel, Field
from typing import List

class SoundfontInfo(BaseModel):
    id: str
    name: str

class SoundfontListResponse(BaseModel):
    soundfonts: List[SoundfontInfo]


class EffectsParams(BaseModel):
    room_size: float = Field(0.5, ge=0.0, le=1.0)
    damping: float = Field(0.5, ge=0.0, le=1.0)
    wet_level: float = Field(0.3, ge=0.0, le=1.0)
    dry_level: float = Field(0.7, ge=0.0, le=1.0)
    highpass_freq: float | None = Field(None, ge=20.0, le=2000.0)
    lowpass_freq: float | None = Field(None, ge=1000.0, le=20000.0)
    target_lufs: float = Field(-14.0, ge=-30.0, le=-6.0)