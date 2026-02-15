from dataclasses import dataclass
from uuid import UUID


@dataclass
class VersionAuthor:
    user_id: UUID
    email: str
