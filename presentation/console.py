from application.ip_service import IPCheckerService
from domain.ipv4 import IPv4


class ConsoleApp:
    """Ввод и вывод: здесь нет бизнес-правил и работы с JSON."""

    def __init__(self, service: IPCheckerService):
        self.service = service

    def run(self) -> None:
        while True:
            print("\n=== ПРОВЕРКА И ПОИСК IPv4 ===")
            print("1. Найти и проверить IP-адрес")
            print("2. Выбрать IP-адрес из истории")
            print("3. Очистить историю")
            print("0. Выход")
            choice = input("Выберите действие: ").strip()
            try:
                if choice == "1":
                    self.search_and_check()
                elif choice == "2":
                    self._cmd_search()
                elif choice == "3":
                    self._cmd_show_history()
                elif choice == "0":
                    print("До свидания!")
                    return
                else:
                    print("Неизвестная команда")
            except ValueError as error:
                print(f"Ошибка: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nВыход")
                return

    def search_and_check(self) -> None:
        text = input("Текст: ")
        ips = self.service.search_and_check_ips(text)
        if not ips:
            print("Корректных IPv4-адресов не найдено")
            return
        
        for ip in ips:
            if ip is not None:
                print(f"OK: {ip.value}  ({self._describe(ip)})")
            else:
                print(f"Not OK: {ip.value}  ({self._describe(ip)})")

    def _cmd_show_history(self) -> None:
        records = self.service.list_history()
        if not records:
            print("История пуста")
            return
        for r in records:
            mark = "✓" if r.valid else "✗"
            found = ", ".join(r.found) if r.found else "—"
            print(f"{r.id}. [{mark}] {r.kind:6} | {r.query!r} → {found}")

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
