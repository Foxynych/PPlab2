from dataclasses import dataclass


@dataclass
class CheckRecord:
    id: int
    query: str          # что ввёл пользователь
    kind: str           # "check" | "search"
    found: list[str]    # найденные/подтверждённые корректные IP
    valid: bool         # для "check" — корректен ли; для "search" — найдено ли хоть что-то
