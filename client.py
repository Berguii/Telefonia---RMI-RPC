import sys

from client.controller import TelefoniaController
from client.view import TerminalView


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

    controller = TelefoniaController(host=host)
    view = TerminalView(controller)

    try:
        view.iniciar()
    except (OSError, ValueError) as erro:
        print(f"Não foi possível comunicar com o servidor: {erro}")


if __name__ == "__main__":
    main()