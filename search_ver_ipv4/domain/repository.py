from abc import ABC, abstractmethod

from domain.ip_record import CheckIP


class CheckRepository(ABC):
    """Контракт хранения истории. Бизнес-логика не знает о JSON."""

    @abstractmethod
    def get_all(self) -> list[CheckIP]:
        pass

    @abstractmethod
    def save_all(self, ips: list[CheckIP]) -> None:
        pass
