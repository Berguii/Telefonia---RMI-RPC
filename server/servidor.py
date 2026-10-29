
import json
import socketserver

from .logs import logger
from server.repository import UsuarioRepository
from server.json_storage import JsonStorage
from server.service import TelefoniaService


class RequisicaoHandler(socketserver.StreamRequestHandler):
    def handle(self):
        cliente = f"{self.client_address[0]}:{self.client_address[1]}"

        logger.info("Conexão recebida de %s", cliente)

        try:
            linha = self.rfile.readline(65537)

            if not linha:
                logger.warning("Conexão encerrada sem requisição: %s", cliente)
                return

            if len(linha) > 65536 or not linha.endswith(b"\n"):
                logger.warning("Requisição inválida ou muito grande: %s", cliente)

                resposta = {
                    "sucesso": False,
                    "mensagem": "Requisição inválida ou muito grande."
                }

            else:
                try:
                    requisicao = json.loads(linha.decode("utf-8"))
                    resposta = self.processar(requisicao, cliente)

                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.warning("JSON inválido recebido de %s", cliente)

                    resposta = {
                        "sucesso": False,
                        "mensagem": "Mensagem JSON inválida."
                    }

        except Exception:
            logger.exception("Erro ao processar requisição de %s", cliente)

            resposta = {
                "sucesso": False,
                "mensagem": "Erro ao processar a requisição."
            }

        try:
            self.wfile.write(
                (json.dumps(resposta, ensure_ascii=False) + "\n").encode("utf-8")
            )
            logger.debug("Resposta enviada para %s", cliente)

        except Exception:
            logger.exception("Erro ao enviar resposta para %s", cliente)

    def processar(self, requisicao, cliente):
        if not isinstance(requisicao, dict):
            logger.warning("Formato de requisição inválido: %s", cliente)

            return {
                "sucesso": False,
                "mensagem": "Formato de requisição inválido."
            }

        operacao = requisicao.get("operacao")
        service = self.server.service

        logger.info(
            "Operação recebida: %s | Cliente: %s",
            operacao,
            cliente
        )

        try:
            if operacao == "cadastrar":
                resposta = service.cadastrar(
                    requisicao.get("nome"),
                    requisicao.get("numero")
                )

            elif operacao == "buscar":
                resposta = service.buscar(requisicao.get("numero"))

            elif operacao == "listar":
                resposta = service.listar()

            else:
                logger.warning(
                    "Operação desconhecida: %s | Cliente: %s",
                    operacao,
                    cliente
                )

                return {
                    "sucesso": False,
                    "mensagem": "Operação desconhecida."
                }

            if isinstance(resposta, dict) and resposta.get("sucesso") is False:
                logger.warning(
                    "Operação %s não concluída com sucesso | Cliente: %s",
                    operacao,
                    cliente
                )
            else:
                logger.info(
                    "Operação %s processada | Cliente: %s",
                    operacao,
                    cliente
                )

            return resposta

        except Exception:
            logger.exception(
                "Erro na operação %s | Cliente: %s",
                operacao,
                cliente
            )

            return {
                "sucesso": False,
                "mensagem": "Erro interno ao executar a operação."
            }


class ServidorTelefonia(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, endereco, service):
        self.service = service
        super().__init__(endereco, RequisicaoHandler)


def main():
    logger.info("Inicializando servidor de telefonia")

    try:
        repository = UsuarioRepository()
        storage = JsonStorage()

        usuarios = storage.carregar()
        repository.carregar(usuarios)

        service = TelefoniaService(repository, storage)

        host = "0.0.0.0"
        porta = 5000

        with ServidorTelefonia((host, porta), service) as servidor:
            logger.info(
                "Servidor iniciado | Porta: %d | Usuários carregados: %d",
                porta,
                len(usuarios)
            )

            print("=" * 40)
            print("SERVIDOR DE TELEFONIA INICIADO")
            print(f"Porta: {porta}")
            print(f"Usuários carregados: {len(usuarios)}")
            print("Aguardando conexões...")
            print("=" * 40)

            try:
                servidor.serve_forever()

            except KeyboardInterrupt:
                logger.info("Servidor encerrado pelo usuário")
                print("\nServidor encerrado.")

    except Exception:
        logger.exception("Falha ao iniciar ou executar o servidor")
        raise


if __name__ == "__main__":
    main()
