from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass
class CustomerDao:
    id: int
    username: str
    password: str
    name: str | None
    role: str
    created_at: datetime
    updated_at: datetime