class TerminalView:
    def __init__(self, controller):
        self.controller = controller

    def iniciar(self):
        while True:
            print("\n===== SISTEMA DE TELEFONIA =====")
            print("1 - Cadastrar usuário")
            print("2 - Buscar por telefone")
            print("3 - Listar usuários")
            print("0 - Sair")

            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    self.cadastrar()

                elif opcao == "2":
                    self.buscar()

                elif opcao == "3":
                    self.listar()

                elif opcao == "0":
                    print("Encerrando o cliente.")
                    break

                else:
                    print("Opção inválida.")

            except (OSError, ValueError) as erro:
                print(f"Erro de comunicação ou resposta: {erro}")

    def cadastrar(self):
        nome = input("Digite o nome: ").strip()
        numero = input("Digite o celular (somente números): ").strip()

        resposta = self.controller.cadastrar(nome, numero)
        print(resposta.get("mensagem", "Resposta desconhecida."))

    def buscar(self):
        numero = input("Digite o celular que deseja pesquisar: ").strip()

        resposta = self.controller.buscar(numero)

        if resposta.get("sucesso"):
            usuario = resposta["usuario"]
            print("\nContato encontrado!")
            print(f"Nome: {usuario['nome']}")
            print(f"Celular: {usuario['numeroCelular']}")
        else:
            print(resposta.get("mensagem", "Contato não encontrado."))

    def listar(self):
        resposta = self.controller.listar()

        usuarios = resposta.get("usuarios", [])

        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return

        print("\n===== USUÁRIOS CADASTRADOS =====")

        for usuario in usuarios:
            print(
                f"Nome: {usuario['nome']} | "
                f"Celular: {usuario['numeroCelular']}"
            )