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
            print("2. Посмотреть историю запросов")
            print("3. Очистить историю")
            print("0. Выход")
            choice = input("Выберите действие: ").strip()

            try:
                if choice == "1":
                    self.search_and_check()
                elif choice == "2":
                    self.pick_and_check_ip_form_history()
                elif choice == "3":
                    answer = input("Вы уверены, что хотите очистить историю? (y/n) ")

                    if answer == 'y':
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

    def search_and_check(self) -> None:
        text = input("Текст: ")
        ips = self.service.search_and_check_ips(text)
        if not ips:
            print("Корректных IPv4-адресов не найдено")
            return
        
        for ip in ips:
            if ip is not None:
                print(f"[✓] {ip.value}  ({self.service._describe(ip)})")
            else:
                print(f"[✗] {ip.value}  ({self.service._describe(ip)})")

    def pick_and_check_ip_form_history(self) -> None:
        ips = self.service.list_history()
        if not ips:
            print("История пуста")
            return
        
        for ip in ips:
            mark = "✓" if ip.valid else "✗"
            print(f"{ip.id}. [{mark}] {ip.ip} ({ip.describe})")

        input("Нажмите Enter для выхода в меню...")
