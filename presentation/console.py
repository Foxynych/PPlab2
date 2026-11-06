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
                    self.pick_and_check_ip_form_history()
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
                print(f"✓: {ip.value}  ({self.service._describe(ip)})")
            else:
                print(f"✗: {ip.value}  ({self.service._describe(ip)})")

    def pick_and_check_ip_form_history(self) -> None:
        ips = self.service.list_history()
        if not ips:
            print("История пуста")
            return

        try:
            id = int(input("Введите id: "))
            if id > ips[-1].id or id < 1:
                raise ValueError("Введённый id не соответствует истории")

        except ValueError as error:
            print(f"Ошибка {error}")
            return
            

        for ip in ips:
            if ip.id == id:
                if ip.valid:
                    print(f"✓: {ip.ip}  ({ip.describe})")
                else:
                    print(f"✗: {ip.ip}  ({ip.describe})")
