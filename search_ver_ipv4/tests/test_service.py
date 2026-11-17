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

    def test_validate_url_accepts_ip_host(self):
        for url in (
            "http://192.168.1.1",
            "https://8.8.8.8:8080",
            "http://10.0.0.1/path?q=1#frag",
        ):
            with self.subTest(url=url):
                self.assertTrue(self.service.validate_url(url))

    def test_validate_url_accepts_domain_host(self):
        for url in (
            "http://example.com",
            "https://sub.example.co.uk/path",
            "http://my-site.org:8443/",
        ):
            with self.subTest(url=url):
                self.assertTrue(self.service.validate_url(url))

    def test_validate_url_rejects_bad_urls(self):
        for url in (
            "",
            "   ",
            "example.com",               # нет схемы
            "ftp://example.com",         # схема не http(s)
            "http://256.1.1.1",          # плохой IP и плохой домен
            "http://1.2.3.4.5",          # лишний октет
            "http://",                   # нет хоста
            "http://-bad.com",           # метка начинается с дефиса
            "http://bad-.com",           # метка кончается дефисом
        ):
            with self.subTest(url=url):
                if url.strip() == "":
                    with self.assertRaises(ValueError):
                        self.service.validate_url(url)
                else:
                    self.assertFalse(self.service.validate_url(url))

    def test_extract_ip_from_url_returns_ip(self):
        ip = self.service.extract_ip_from_url("https://10.0.0.1:443/admin")
        self.assertIsNotNone(ip)
        self.assertEqual(ip.value, "10.0.0.1")

    def test_extract_ip_from_url_returns_none_for_domain(self):
        self.assertIsNone(
            self.service.extract_ip_from_url("https://example.com/path")
        )

    def test_extract_ip_from_url_raises_on_bad_url(self):
        with self.assertRaises(ValueError):
            self.service.extract_ip_from_url("ftp://example.com")
        with self.assertRaises(ValueError):
            self.service.extract_ip_from_url("http://256.1.1.1")

    def test_check_url_combined(self):
        self.assertEqual(
            self.service.check_url("http://8.8.8.8")[0].__class__, bool
        )
        valid, ip = self.service.check_url("http://8.8.8.8:8080/x")
        self.assertTrue(valid)
        self.assertEqual(ip.value, "8.8.8.8")

        valid, ip = self.service.check_url("https://example.com")
        self.assertTrue(valid)
        self.assertIsNone(ip)

        valid, ip = self.service.check_url("not a url")
        self.assertFalse(valid)
        self.assertIsNone(ip)

if __name__ == "__main__":
    unittest.main()
