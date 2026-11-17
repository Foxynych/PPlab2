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

# Хост URL — либо корректный IPv4, либо доменное имя.
# Домен: метки 1–63 символа, начинаются/кончаются буквой-цифрой,
# дефис — только внутри; TLD — минимум 2 буквы.
_URL_DOMAIN = (
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}"
)
_URL_HOST = rf"(?:{_OCTET}(?:\.{_OCTET}){{3}}|{_URL_DOMAIN})"

# Полный URL: схема http/https, хост (IP или домен), опциональный порт
# (1–5 цифр) и опциональные путь/запрос/фрагмент.
URL_RE = re.compile(
    rf"^https?://(?P<host>{_URL_HOST})(?::\d{{1,5}})?(?:[/?#]\S*)?$"
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
                    describe=self._describe(ip),
                    valid=ip is not None,
                )
            )

        return found
    
    def validate_url(self, url: str) -> bool:
        url = url.strip()
        if not url:
            raise ValueError("URL не может быть пустым")
        
        return URL_RE.match(url) is not None

    def extract_ip_from_url(self, url: str) -> IPv4 | None:
        url = url.strip()
        if not url:
            raise ValueError("URL не может быть пустым")
        
        m = URL_RE.match(url)
        if not m:
            raise ValueError(f"Некорректный URL: {url}")
        
        host = m.group("host")

        return IPv4.from_string(host) if IPV4_FULL.match(host) else None

    def check_url(self, url: str) -> tuple[bool, IPv4 | None]:
        url = url.strip()
        if not url:
            raise ValueError("URL не может быть пустым")
        
        m = URL_RE.match(url)
        if not m:
            return False, None
        
        host = m.group("host")
        ip = IPv4.from_string(host) if IPV4_FULL.match(host) else None

        return True, ip
    
    def clear_history(self) -> None:
        self.repository.save_all([])

    def _append(self, ip: CheckIP) -> None:
        ips = self.repository.get_all()
        ips.append(ip)
        self.repository.save_all(ips)

    def _next_id(self) -> int:
        ips = self.repository.get_all()
        return max((i.id for i in ips), default=0) + 1

    @staticmethod
    def _describe(ip: IPv4) -> str:
        flags = [f"class {ip.ip_class}"]

        if ip.is_private:
            flags.append("private")
        if ip.is_loopback:
            flags.append("loopback")
        if ip.is_multicast:
            flags.append("multicast")

        return ", ".join(flags)
