from application.ip_service import IPCheckerService
from domain.ipv4 import IPv4


class ConsoleApp:
    """Ввод и вывод: здесь нет бизнес-правил и работы с JSON."""

    def __init__(self, service: IPCheckerService):
        self.service = service

    def run(self) -> None:
        while True:
            print("\n=== ПРОВЕРКА И ПОИСК IPv4 ===")
            print("1. Проверить один IP-адрес")
            print("2. Найти IP-адреса в тексте")
            print("3. Показать историю")
            print("4. Удалить запись из истории")
            print("5. Очистить историю")
            print("0. Выход")
            choice = input("Выберите действие: ").strip()
            try:
                if choice == "1":
                    self._cmd_check()
                elif choice == "2":
                    self._cmd_search()
                elif choice == "3":
                    self._cmd_show_history()
                elif choice == "4":
                    self.service.delete_record(int(input("ID записи: ")))
                    print("Запись удалена")
                elif choice == "5":
                    self.service.clear_history()
                    print("История очищена")
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

    def _cmd_check(self) -> None:
        ip = self.service.check_ip(input("IP-адрес: "))
        if ip is None:
            print("Некорректный IPv4-адрес")
        else:
            print(f"OK: {ip.value}  ({self._describe(ip)})")

    def _cmd_search(self) -> None:
        text = input("Текст: ")
        ips = self.service.search_ips(text)
        if not ips:
            print("Корректных IPv4-адресов не найдено")
            return
        print(f"Найдено: {len(ips)}")
        for ip in ips:
            print(f"  • {ip.value}  ({self._describe(ip)})")

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
