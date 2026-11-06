import unittest

from application.ip_service import IPCheckerService
from domain.ip_record import CheckIP
from domain.repository import CheckRepository


class InMemoryRepository(CheckRepository):
    """Подменный репозиторий: копирует записи, чтобы имитировать JSON."""

    def __init__(self):
        self.ips: list[CheckIP] = []

    def get_all(self) -> list[CheckIP]:
        return [
            CheckIP(id=i.id, ip=i.ip, describe=i.describe, valid=i.valid)
            for i in self.ips
        ]

    def save_all(self, ips: list[CheckIP]) -> None:
        self.records = [
            CheckIP(id=i.id, ip=i.ip, describe=i.describe, valid=i.valid)
            for i in ips
        ]


class IPCheckerServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = IPCheckerService(InMemoryRepository())

    def test_search_finds_all(self):
        ips = self.service.search_and_check_ips(
            "DNS: 8.8.8.8 и 1.1.1.1, шлюз 192.168.0.1,"
        )
        self.assertEqual(
            [ip.value for ip in ips],
            ["8.8.8.8", "1.1.1.1", "192.168.0.1"],
        )

    def test_search_rejects_partial_matches(self):
        ips = self.service.search_and_check_ips(
            "999.1.1.1 и 1.2.3.4.5 и 256.0.0.1"
        )
        self.assertEqual(ips, [])

    def test_search_trailing_dot(self):
        ips = self.service.search_and_check_ips("Сервер: 10.0.0.1.")
        self.assertEqual([ip.value for ip in ips], ["10.0.0.1"])

    def test_search_ignores_leading_zeros(self):
        self.assertEqual(self.service.search_and_check_ips("01.2.3.4"), [])

    def test_search_empty_text_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search_and_check_ips("   ")

    def test_empty_search_does_not_save_history(self):
        ips = self.service.search_and_check_ips("тут нет адресов")
        self.assertEqual(ips, [])
        self.assertEqual(self.service.list_history(), [])

    def test_clear_history(self):
        self.service.search_and_check_ips("8.8.8.8, 1.1.1.1")
        self.service.clear_history()
        self.assertEqual(self.service.list_history(), [])

    def test_clear_empty_history_is_safe(self):
        self.service.clear_history()
        self.assertEqual(self.service.list_history(), [])


if __name__ == "__main__":
    unittest.main()
