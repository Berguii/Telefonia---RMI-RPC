class UsuarioRepository:
    def __init__(self):
        self.usuarios = {}

    def cadastrar(self, usuario):
        numero = usuario.numero_celular

        if numero in self.usuarios:
            return False

        self.usuarios[numero] = usuario
        return True

    def buscar(self, numero):
        return self.usuarios.get(numero)

    def listar(self):
        return list(self.usuarios.values())

    def carregar(self, usuarios):
        self.usuarios.clear()

        for usuario in usuarios:
            self.usuarios[usuario.numero_celular] = usuario

    def remover(self, numero):
        return self.usuarios.pop(numero, None)