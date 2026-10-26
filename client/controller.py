import json
import socket


class TelefoniaController:
    def __init__(self, host="127.0.0.1", porta=5000):
        self.host = host
        self.porta = porta

    def _enviar(self, requisicao):
        with socket.create_connection(
            (self.host, self.porta),
            timeout=5
        ) as conexao:
            conexao.settimeout(5)

            mensagem = (
                json.dumps(requisicao, ensure_ascii=False) + "\n"
            ).encode("utf-8")

            conexao.sendall(mensagem)

            with conexao.makefile("rb") as resposta:
                linha = resposta.readline(65537)

            if not linha or len(linha) > 65536:
                raise ConnectionError("Resposta inválida do servidor.")

            return json.loads(linha.decode("utf-8"))

    def cadastrar(self, nome, numero):
        return self._enviar({
            "operacao": "cadastrar",
            "nome": nome,
            "numero": numero
        })

    def buscar(self, numero):
        return self._enviar({
            "operacao": "buscar",
            "numero": numero
        })

    def listar(self):
        return self._enviar({
            "operacao": "listar"
        })