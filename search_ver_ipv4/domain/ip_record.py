from dataclasses import dataclass


@dataclass
class CheckIP:
    id: int
    ip: str
    describe: str
    valid: bool
