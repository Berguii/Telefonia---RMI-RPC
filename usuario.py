class Usuario:
    def __init__(self, nome: str, numero_celular: str):
        self.nome = nome
        self.numero_celular = numero_celular

    def to_dict(self):
        return {
            "nome": self.nome,
            "numeroCelular": self.numero_celular
        }

    @staticmethod
    def from_dict(dados):
        return Usuario(
            dados["nome"],
            dados["numeroCelular"]
        )

    def __str__(self):
        return (
            f"Nome: {self.nome} | "
            f"Telefone: {self.numero_celular}"
        )