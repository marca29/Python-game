from pydantic import BaseModel
from typing import List, Optional

class Player(BaseModel):
    name: str

class Move(BaseModel):
    match_id: int
    position: int
    player: str

class Match(BaseModel):
    id: int
    board: List[str]
    current_player: str
    players: List[str]
    winner: Optional[str] = None
    is_draw: bool = False
