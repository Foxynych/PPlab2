# Проверка и поиск IPv4 — пример слоистой архитектуры на Python

Минимальный консольный проект на Python 3.10+, без сторонних зависимостей.
Адреса проверяются и ищутся регулярными выражениями.

## Запуск в PyCharm

1. Распакуйте архив.
2. В PyCharm выберите **File → Open** и папку `layered_ipcheck`.
3. Укажите Python 3.10 или новее как интерпретатор проекта.
4. Откройте `main.py` и нажмите **Run**.
5. История проверок сохраняется в `history.json` рядом с `main.py`.

## Слои

```text
main.py                            Сборка зависимостей (composition root)
presentation/console.py            UI: input/print, меню и обработка ошибок
application/ip_service.py          Бизнес-логика: регулярки, проверка, поиск, история
domain/ipv4.py                     Value object корректного адреса + классификация
domain/ip_record.py                Сущность записи истории
domain/repository.py               Абстракция хранилища (контракт)
infrastructure/json_repository.py  Работа с JSON-файлом
tests/test_service.py              Unit-тесты сервиса с подменным репозиторием