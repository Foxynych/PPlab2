import re

from domain.ip_record import CheckRecord
from domain.ipv4 import IPv4
from domain.repository import CheckRepository

# Октет: 0–255, без ведущих нулей.
#   25[0-5]    -> 250..255
#   2[0-4]\d   -> 200..249
#   1\d{2}     -> 100..199
#   [1-9]?\d   -> 0..99 без "01"
_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)"

# Для проверки одной строки целиком.
IPV4_FULL = re.compile(rf"^{_OCTET}(?:\.{_OCTET}){{3}}$")

# Для поиска внутри текста.
#   (?<![\d.])   — слева не цифра и не точка (чтобы не матчить хвосты чисел);
#   (?!\.?\d)    — справа не «.цифра» (чтобы "1.2.3.4.5" не дало "1.2.3.4",
#                  но "10.0.0.1." в конце предложения — дало).
IPV4_SEARCH = re.compile(
    rf"(?<![\d.])(?:{_OCTET}\.){{3}}{_OCTET}(?!\.?\d)"
)


class IPCheckerService:
    """Бизнес-правила: проверка, поиск и ведение истории."""

    def __init__(self, repository: CheckRepository):
        self.repository = repository

    # --- публичный API --------------------------------------------------

    def list_history(self) -> list[CheckRecord]:
        return self.repository.get_all()

    def check_ip(self, text: str) -> IPv4 | None:
        query = text.strip()
        if not query:
            raise ValueError("Строка для проверки не может быть пустой")

        ip = IPv4.from_string(query) if IPV4_FULL.match(query) else None
        self._append(
            CheckRecord(
                id=self._next_id(),
                query=query,
                kind="check",
                found=[ip.value] if ip else [],
                valid=ip is not None,
            )
        )
        return ip

    def search_ips(self, text: str) -> list[IPv4]:
        query = text.strip()
        if not query:
            raise ValueError("Текст для поиска не может быть пустым")

        found = [IPv4.from_string(m) for m in IPV4_SEARCH.findall(query)]
        self._append(
            CheckRecord(
                id=self._next_id(),
                query=query,
                kind="search",
                found=[ip.value for ip in found],
                valid=bool(found),
            )
        )
        return found

    def delete_record(self, record_id: int) -> None:
        records = self.repository.get_all()
        remaining = [r for r in records if r.id != record_id]
        if len(remaining) == len(records):
            raise ValueError(f"Запись с ID {record_id} не найдена")
        self.repository.save_all(remaining)

    def clear_history(self) -> None:
        self.repository.save_all([])

    # --- внутренние помощники ------------------------------------------

    def _append(self, record: CheckRecord) -> None:
        records = self.repository.get_all()
        records.append(record)
        self.repository.save_all(records)

    def _next_id(self) -> int:
        records = self.repository.get_all()
        return max((r.id for r in records), default=0) + 1
