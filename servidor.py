import json
import socketserver

from server.repository import UsuarioRepository
from server.json_storage import JsonStorage
from server.service import TelefoniaService


class RequisicaoHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            linha = self.rfile.readline(65537)

            if not linha or len(linha) > 65536 or not linha.endswith(b"\n"):
                resposta = {
                    "sucesso": False,
                    "mensagem": "Requisição inválida ou muito grande."
                }
            else:
                try:
                    requisicao = json.loads(linha.decode("utf-8"))
                    resposta = self.processar(requisicao)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    resposta = {
                        "sucesso": False,
                        "mensagem": "Mensagem JSON inválida."
                    }

        except Exception:
            resposta = {
                "sucesso": False,
                "mensagem": "Erro ao processar a requisição."
            }

        self.wfile.write(
            (json.dumps(resposta, ensure_ascii=False) + "\n").encode("utf-8")
        )

    def processar(self, requisicao):
        if not isinstance(requisicao, dict):
            return {
                "sucesso": False,
                "mensagem": "Formato de requisição inválido."
            }

        operacao = requisicao.get("operacao")
        service = self.server.service

        if operacao == "cadastrar":
            return service.cadastrar(
                requisicao.get("nome"),
                requisicao.get("numero")
            )

        if operacao == "buscar":
            return service.buscar(requisicao.get("numero"))

        if operacao == "listar":
            return service.listar()

        return {
            "sucesso": False,
            "mensagem": "Operação desconhecida."
        }


class ServidorTelefonia(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, endereco, service):
        self.service = service
        super().__init__(endereco, RequisicaoHandler)


def main():
    repository = UsuarioRepository()
    storage = JsonStorage()

    usuarios = storage.carregar()
    repository.carregar(usuarios)

    service = TelefoniaService(repository, storage)

    host = "0.0.0.0"
    porta = 5000

    with ServidorTelefonia((host, porta), service) as servidor:
        print("=" * 40)
        print("SERVIDOR DE TELEFONIA INICIADO")
        print(f"Porta: {porta}")
        print(f"Usuários carregados: {len(usuarios)}")
        print("Aguardando conexões...")
        print("=" * 40)

        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")


if __name__ == "__main__":
    main()