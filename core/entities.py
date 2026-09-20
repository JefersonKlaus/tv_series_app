from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Episode:
    id: int
    name: str
    season: int
    number: int
    summary: Optional[str] = None
    watched: bool = False
    comment: Optional[str] = None


@dataclass
class Series:
    id: int
    name: str
    genres: List[str]
    poster_url: Optional[str] = None
    summary: Optional[str] = None
    premiered_year: Optional[int] = None
    episodes: List[Episode] = field(default_factory=list)
    comment: Optional[str] = None
    status: str = "not_started"
