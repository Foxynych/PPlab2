from pathlib import Path

from application.ip_service import IPCheckerService
from infrastructure.json_repository import JsonCheckRepository
from presentation.console import ConsoleApp


def main() -> None:
    repository = JsonCheckRepository(Path(__file__).parent / "history.json")
    service = IPCheckerService(repository)
    app = ConsoleApp(service)
    app.run()


if __name__ == "__main__":
    main()
