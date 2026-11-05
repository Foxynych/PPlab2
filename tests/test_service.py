import unittest

from application.ip_service import IPCheckerService
from domain.ip_record import CheckRecord
from domain.repository import CheckRepository


class InMemoryRepository(CheckRepository):
    def __init__(self):
        self.records = []

    def get_all(self) -> list[CheckRecord]:
        return [
            CheckRecord(r.id, r.query, r.kind, list(r.found), r.valid)
            for r in self.records
        ]

    def save_all(self, records: list[CheckRecord]) -> None:
        self.records = [
            CheckRecord(r.id, r.query, r.kind, list(r.found), r.valid)
            for r in records
        ]


class IPCheckerServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = IPCheckerService(InMemoryRepository())

    # --- проверка одного адреса -----------------------------------------

    def test_valid_ips(self):
        for text in ("0.0.0.0", "255.255.255.255", "192.168.1.1", "8.8.8.8"):
            with self.subTest(text=text):
                ip = self.service.check_ip(text)
                self.assertIsNotNone(ip)
                self.assertEqual(ip.value, text)

    def test_invalid_ips(self):
        for text in ("256.1.1.1", "01.2.3.4", "1.2.3", "1.2.3.4.5", "abc"):
            with self.subTest(text=text):
                self.assertIsNone(self.service.check_ip(text))

    def test_empty_check_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.check_ip("   ")

    # --- поиск в тексте -------------------------------------------------

    def test_search_finds_all(self):
        ips = self.service.search_ips(
            "DNS: 8.8.8.8 и 1.1.1.1, шлюз 192.168.0.1,"
        )
        self.assertEqual([ip.value for ip in ips], ["8.8.8.8", "1.1.1.1", "192.168.0.1"])

    def test_search_rejects_partial_matches(self):
        ips = self.service.search_ips("999.1.1.1 и 1.2.3.4.5 и 256.0.0.1")
        self.assertEqual(ips, [])

    def test_search_trailing_dot(self):
        # Точка в конце предложения не должна ломать совпадение.
        ips = self.service.search_ips("Сервер: 10.0.0.1.")
        self.assertEqual([ip.value for ip in ips], ["10.0.0.1"])

    # --- история --------------------------------------------------------

    def test_history_is_saved(self):
        self.service.check_ip("8.8.8.8")
        self.service.search_ips("10.0.0.1, 10.0.0.2")
        records = self.service.list_history()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].kind, "check")
        self.assertTrue(records[0].valid)
        self.assertEqual(records[1].found, ["10.0.0.1", "10.0.0.2"])

    def test_delete_record(self):
        self.service.check_ip("8.8.8.8")
        record_id = self.service.list_history()[0].id
        self.service.delete_record(record_id)
        self.assertEqual(self.service.list_history(), [])

    def test_delete_missing_record(self):
        with self.assertRaises(ValueError):
            self.service.delete_record(42)

    def test_clear_history(self):
        self.service.check_ip("8.8.8.8")
        self.service.clear_history()
        self.assertEqual(self.service.list_history(), [])


if __name__ == "__main__":
    unittest.main()
