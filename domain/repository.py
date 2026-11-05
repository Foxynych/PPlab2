from abc import ABC, abstractmethod

from domain.ip_record import CheckRecord


class CheckRepository(ABC):
    """Контракт хранения истории. Бизнес-логика не знает о JSON."""

    @abstractmethod
    def get_all(self) -> list[CheckRecord]:
        pass

    @abstractmethod
    def save_all(self, records: list[CheckRecord]) -> None:
        pass
