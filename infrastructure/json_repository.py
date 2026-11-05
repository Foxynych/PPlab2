import json
from pathlib import Path

from domain.ip_record import CheckIP
from domain.repository import CheckRepository


class JsonCheckRepository(CheckRepository):
    """Хранение истории в JSON-файле."""

    def __init__(self, path: Path):
        self.path = path

    def get_all(self) -> list[CheckIP]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        
        return [
            CheckIP(
                id=item["id"],
                ip=str(item["ip"]),
                valid=bool(item["valid"]),
            )
            for item in data
        ]

    def save_all(self, ips: list[CheckIP]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        data = [
            dict(
                id=i.id,
                ip=i.ip,
                valid=i.valid,
            )
            for i in ips
        ]

        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
