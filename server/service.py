import re
from threading import RLock

from model.usuario import Usuario


class TelefoniaService:
    def __init__(self, repository, storage):
        self.repository = repository
        self.storage = storage
        self.lock = RLock()

    def cadastrar(self, nome, numero):
        nome = nome.strip() if isinstance(nome, str) else ""
        numero = numero.strip() if isinstance(numero, str) else ""

        if not nome:
            return {
                "sucesso": False,
                "mensagem": "O nome é obrigatório."
            }

        if not re.fullmatch(r"\d{10,13}", numero):
            return {
                "sucesso": False,
                "mensagem": "Informe um celular com 10 a 13 dígitos."
            }

        with self.lock:
            usuario = Usuario(nome, numero)

            if not self.repository.cadastrar(usuario):
                return {
                    "sucesso": False,
                    "mensagem": "Este número já está cadastrado."
                }

            try:
                self.storage.salvar(self.repository.listar())
            except OSError:
                self.repository.remover(numero)

                return {
                    "sucesso": False,
                    "mensagem": "Erro ao salvar os dados."
                }

            return {
                "sucesso": True,
                "mensagem": "Cadastro realizado com sucesso."
            }

    def buscar(self, numero):
        if not isinstance(numero, str):
            numero = ""

        numero = numero.strip()

        if not re.fullmatch(r"\d{10,13}", numero):
            return {
                "sucesso": False,
                "mensagem": "Número de celular inválido."
            }

        with self.lock:
            usuario = self.repository.buscar(numero)

            if usuario is None:
                return {
                    "sucesso": False,
                    "mensagem": "Número não cadastrado."
                }

            return {
                "sucesso": True,
                "usuario": usuario.to_dict()
            }

    def listar(self):
        with self.lock:
            return {
                "sucesso": True,
                "usuarios": [
                    usuario.to_dict()
                    for usuario in self.repository.listar()
                ]
            }