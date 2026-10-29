import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk


class JanelaTelefonia(tk.Tk):
    """Interface gráfica do cliente. Usa o mesmo TelefoniaController do terminal."""

    INTERVALO_AUTO_MS = 3000

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Resultados das chamadas de rede chegam por esta fila e são
        # tratados na thread principal (o Tkinter não é thread-safe).
        self.fila = queue.Queue()
        self.auto_var = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Conectando ao servidor...")
        self._auto_id = None

        self.title("Sistema de Telefonia")
        self.geometry("580x540")
        self.minsize(500, 480)

        self._montar_tela()
        self._processar_fila()
        self.atualizar_lista()

    # ------------------------------------------------------------------
    # Montagem da tela
    # ------------------------------------------------------------------
    def _montar_tela(self):
        corpo = ttk.Frame(self, padding=12)
        corpo.pack(fill="both", expand=True)

        # --- Cadastro ---
        cadastro = ttk.LabelFrame(corpo, text="Cadastrar usuário", padding=10)
        cadastro.pack(fill="x")
        cadastro.columnconfigure(1, weight=1)

        ttk.Label(cadastro, text="Nome:").grid(row=0, column=0, sticky="w", pady=3)
        self.entrada_nome = ttk.Entry(cadastro)
        self.entrada_nome.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=3)

        ttk.Label(cadastro, text="Celular:").grid(row=1, column=0, sticky="w", pady=3)
        self.entrada_numero = ttk.Entry(cadastro)
        self.entrada_numero.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=3)

        ttk.Button(cadastro, text="Cadastrar", command=self.cadastrar).grid(
            row=2, column=1, sticky="e", pady=(6, 0)
        )

        self.entrada_nome.bind("<Return>", lambda _e: self.entrada_numero.focus())
        self.entrada_numero.bind("<Return>", lambda _e: self.cadastrar())

        # --- Busca ---
        busca = ttk.LabelFrame(corpo, text="Buscar por telefone", padding=10)
        busca.pack(fill="x", pady=(10, 0))
        busca.columnconfigure(0, weight=1)

        self.entrada_busca = ttk.Entry(busca)
        self.entrada_busca.grid(row=0, column=0, sticky="ew")
        ttk.Button(busca, text="Buscar", command=self.buscar).grid(
            row=0, column=1, padx=(8, 0)
        )
        self.entrada_busca.bind("<Return>", lambda _e: self.buscar())

        self.resultado_busca = ttk.Label(busca, text="", wraplength=500)
        self.resultado_busca.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # --- Lista ---
        lista = ttk.LabelFrame(corpo, text="Usuários cadastrados", padding=10)
        lista.pack(fill="both", expand=True, pady=(10, 0))
        lista.columnconfigure(0, weight=1)
        lista.rowconfigure(0, weight=1)

        self.tabela = ttk.Treeview(
            lista, columns=("nome", "celular"), show="headings", height=8
        )
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("celular", text="Celular")
        self.tabela.column("nome", width=300)
        self.tabela.column("celular", width=160)
        self.tabela.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(lista, orient="vertical", command=self.tabela.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=barra.set)

        rodape = ttk.Frame(lista)
        rodape.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(rodape, text="Atualizar", command=self.atualizar_lista).pack(side="left")
        ttk.Checkbutton(
            rodape,
            text="Atualizar sozinho (a cada 3 s)",
            variable=self.auto_var,
            command=self._alternar_auto,
        ).pack(side="left", padx=(12, 0))

        ttk.Label(corpo, textvariable=self.status, foreground="gray").pack(
            anchor="w", pady=(8, 0)
        )

        self.entrada_nome.focus()

    # ------------------------------------------------------------------
    # Rede em segundo plano (a janela não congela se o servidor demorar)
    # ------------------------------------------------------------------
    def _executar(self, funcao, ao_concluir, *args):
        def tarefa():
            try:
                self.fila.put((ao_concluir, funcao(*args), None))
            except (OSError, ValueError) as erro:
                self.fila.put((ao_concluir, None, erro))

        threading.Thread(target=tarefa, daemon=True).start()

    def _processar_fila(self):
        try:
            while True:
                ao_concluir, resultado, erro = self.fila.get_nowait()
                ao_concluir(resultado, erro)
        except queue.Empty:
            pass
        self.after(100, self._processar_fila)

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def cadastrar(self):
        nome = self.entrada_nome.get().strip()
        numero = self.entrada_numero.get().strip()
        self._executar(self.controller.cadastrar, self._cadastro_concluido, nome, numero)

    def _cadastro_concluido(self, resposta, erro):
        if erro:
            self._mostrar_erro_conexao(erro)
            return

        mensagem = resposta.get("mensagem", "Resposta desconhecida.")

        if resposta.get("sucesso"):
            messagebox.showinfo("Cadastro", mensagem)
            self.entrada_nome.delete(0, "end")
            self.entrada_numero.delete(0, "end")
            self.entrada_nome.focus()
            self.atualizar_lista()
        else:
            messagebox.showwarning("Cadastro", mensagem)

    def buscar(self):
        numero = self.entrada_busca.get().strip()
        self._executar(self.controller.buscar, self._busca_concluida, numero)

    def _busca_concluida(self, resposta, erro):
        if erro:
            self._mostrar_erro_conexao(erro)
            return

        if resposta.get("sucesso"):
            usuario = resposta["usuario"]
            self.resultado_busca.config(
                text=f"Encontrado: {usuario['nome']}  |  {usuario['numeroCelular']}"
            )
        else:
            self.resultado_busca.config(
                text=resposta.get("mensagem", "Contato não encontrado.")
            )

    def atualizar_lista(self):
        self._executar(self.controller.listar, self._lista_atualizada)

    def _lista_atualizada(self, resposta, erro):
        if erro:
            self.status.set(f"Servidor indisponível: {erro}")
            return

        usuarios = resposta.get("usuarios", [])

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for usuario in usuarios:
            self.tabela.insert(
                "", "end", values=(usuario["nome"], usuario["numeroCelular"])
            )

        self.status.set(f"Conectado | {len(usuarios)} usuário(s) cadastrado(s)")

    def _alternar_auto(self):
        if self._auto_id is not None:
            self.after_cancel(self._auto_id)
            self._auto_id = None

        if self.auto_var.get():
            self._ciclo_auto()

    def _ciclo_auto(self):
        self.atualizar_lista()
        self._auto_id = self.after(self.INTERVALO_AUTO_MS, self._ciclo_auto)

    def _mostrar_erro_conexao(self, erro):
        self.status.set(f"Servidor indisponível: {erro}")
        messagebox.showerror(
            "Erro de conexão",
            f"Não foi possível falar com o servidor:\n{erro}",
        )