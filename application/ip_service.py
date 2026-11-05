import re

from domain.ip_record import CheckIP
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

    def list_history(self) -> list[CheckIP]:
        return self.repository.get_all()
    
    def search_and_check_ips(self, text: str) -> list[IPv4]:
        t = text.strip()
        if not t:
            raise ValueError("Текст для поиска не может быть пустым")

        found = []
        for i in IPV4_SEARCH.findall(t):
            ip = IPv4.from_string(i)
            found.append(ip)

            self._append(
                CheckIP(
                    id=self._next_id(),
                    ip=ip.value,
                    valid=ip is not None,
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

    def _append(self, ip: CheckIP) -> None:
        ips = self.repository.get_all()
        ips.append(ip)
        self.repository.save_all(ips)

    def _next_id(self) -> int:
        records = self.repository.get_all()
        return max((r.id for r in records), default=0) + 1
