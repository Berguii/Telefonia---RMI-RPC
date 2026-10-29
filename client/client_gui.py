import sys

from client.controller import TelefoniaController
from client.gui import JanelaTelefonia


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

    controller = TelefoniaController(host=host)
    JanelaTelefonia(controller).mainloop()


if __name__ == "__main__":
    main()