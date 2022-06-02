from typing import Optional

from pydantic import BaseModel, Field


class TitleLocalized(BaseModel):
    en: str
    jp: Optional[str]
    kr: Optional[str]
    zh_Hans: Optional[str]
    zh_Hant: Optional[str]


class SourceLocalized(BaseModel):
    en: str
    ja: Optional[str]
    kr: Optional[str]
    zh_Hans: Optional[str] = Field(..., alias='zh-Hans')
    zh_Hant: Optional[str] = Field(..., alias='zh-Hant')


class Difficulty(BaseModel):
    ratingClass: int
    chartDesigner: str
    jacketDesigner: str
    jacketOverride: Optional[bool]
    rating: int
    ratingPlus: Optional[bool]


class Song(BaseModel):
    idx: int
    id: str
    title_localized: TitleLocalized
    source_localized: Optional[SourceLocalized]
    source_copyright: Optional[str]
    artist: str
    bpm: str
    bpm_base: float
    set: str
    purchase: str
    audioPreview: int
    audioPreviewEnd: int
    side: int
    bg: str
    date: int
    version: str
    difficulties: list[Difficulty]
