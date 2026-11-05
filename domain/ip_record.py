from dataclasses import dataclass


@dataclass
class CheckIP:
    id: int
    ip: str
    valid: bool
