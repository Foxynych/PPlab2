import json
from pathlib import Path

from domain.ip_record import CheckRecord
from domain.repository import CheckRepository


class JsonCheckRepository(CheckRepository):
    """Хранение истории в JSON-файле."""

    def __init__(self, path: Path):
        self.path = path

    def get_all(self) -> list[CheckRecord]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            CheckRecord(
                id=item["id"],
                query=item["query"],
                kind=item["kind"],
                found=list(item["found"]),
                valid=bool(item["valid"]),
            )
            for item in data
        ]

    def save_all(self, records: list[CheckRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [
            dict(
                id=r.id,
                query=r.query,
                kind=r.kind,
                found=list(r.found),
                valid=r.valid,
            )
            for r in records
        ]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
