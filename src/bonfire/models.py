from dataclasses import dataclass
from uuid import UUID


@dataclass
class Session:
    id: UUID
    knight_name: str
    sprite_id: int
    color_index: int
