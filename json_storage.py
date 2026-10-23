import json
from pathlib import Path

from model.usuario import Usuario


class JsonStorage:
    def __init__(self):
        raiz_projeto = Path(__file__).resolve().parent.parent
        self.arquivo = raiz_projeto / "data" / "usuarios.json"

        self.arquivo.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.arquivo.exists():
            self.salvar([])

    def carregar(self):
        with self.arquivo.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        return [Usuario.from_dict(item) for item in dados]

    def salvar(self, usuarios):
        dados = [usuario.to_dict() for usuario in usuarios]

        temporario = self.arquivo.with_suffix(".tmp")

        with temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        temporario.replace(self.arquivo)