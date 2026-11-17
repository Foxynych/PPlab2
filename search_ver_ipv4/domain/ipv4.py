from dataclasses import dataclass


@dataclass(frozen=True)
class IPv4:
    """Синтаксически корректный IPv4-адрес. Создаётся только из проверенной строки."""

    octets: tuple[int, int, int, int]

    @classmethod
    def from_string(cls, value: str) -> "IPv4":
        return cls(tuple(int(part) for part in value.split(".")))

    @property
    def value(self) -> str:
        return ".".join(str(o) for o in self.octets)

    @property
    def ip_class(self) -> str:
        a = self.octets[0]

        if a == 0:
            return "0 (reserved)"
        if 1 <= a <= 126:
            return "A"
        if a == 127:
            return "loopback"
        if 128 <= a <= 191:
            return "B"
        if 192 <= a <= 223:
            return "C"
        if 224 <= a <= 239:
            return "D (multicast)"
        return "E (reserved)"

    @property
    def is_private(self) -> bool:
        a, b = self.octets[0], self.octets[1]
        return (
            a == 10
            or (a == 172 and 16 <= b <= 31)
            or (a == 192 and b == 168)
        )

    @property
    def is_loopback(self) -> bool:
        return self.octets[0] == 127

    @property
    def is_multicast(self) -> bool:
        return 224 <= self.octets[0] <= 239
