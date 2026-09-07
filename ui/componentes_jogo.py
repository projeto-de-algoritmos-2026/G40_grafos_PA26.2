"""Componentes do fluxo e HUD da partida."""

import tkinter as tk
from collections.abc import Callable

from mapas import Mapa, TERRENOS
from partida import Partida
from simulacao import TipoAdversario
from ui.avatares import Avatar, cor_avatar
from ui.componentes import Botao
from ui.tema import CORES, FONTE


APRESENTACAO_ADVERSARIOS = {
    TipoAdversario.BFS: (
        "O Explorador",
        "Busca o caminho com menor número de passos, sem considerar o custo dos terrenos.",
    ),
    TipoAdversario.DIJKSTRA: (
        "O Estrategista",
        "Analisa o custo dos caminhos e procura a rota com menor custo total.",
    ),
}


class CardAdversario(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        adversario: TipoAdversario,
        comando: Callable[[], None],
    ) -> None:
        cor = cor_avatar(adversario)
        super().__init__(
            parent, bg=CORES["superficie"], padx=28, pady=24,
            highlightbackground=cor, highlightthickness=2,
        )
        titulo, descricao = APRESENTACAO_ADVERSARIOS[adversario]
        Avatar(self, adversario, tamanho=118).pack(pady=(0, 12))
        tk.Label(
            self, text=adversario.value, bg=CORES["superficie"], fg=cor,
            font=(FONTE, 20, "bold"),
        ).pack()
        tk.Label(
            self, text=titulo, bg=CORES["superficie"], fg=CORES["texto"],
            font=(FONTE, 12, "bold"),
        ).pack(pady=(2, 12))
        tk.Label(
            self, text=descricao, bg=CORES["superficie"],
            fg=CORES["texto_suave"], font=(FONTE, 10),
            wraplength=310, justify="center",
        ).pack(fill="x", expand=True)
        Botao(
            self, f"Competir contra {adversario.value}", comando, destaque=True
        ).pack(fill="x", pady=(22, 0))


class IndicadorDestino(tk.Frame):
    def __init__(self, parent: tk.Misc, mapa: Mapa) -> None:
        super().__init__(
            parent, bg="#2A1D36", padx=14, pady=11,
            highlightbackground=CORES["destino"], highlightthickness=1,
        )
        destino = mapa.obter_vertice(mapa.destino)
        tk.Label(
            self, text="MISSÃO", bg="#2A1D36", fg=CORES["destino"],
            font=(FONTE, 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            self, text=f"Chegue a {destino.nome}", bg="#2A1D36",
            fg=CORES["texto"], font=(FONTE, 11, "bold"), wraplength=255,
        ).pack(anchor="w", pady=(2, 0))
        tk.Label(
            self, text=f"Destino · Nó {destino.identificador}", bg="#2A1D36",
            fg=CORES["texto_suave"], font=(FONTE, 8),
        ).pack(anchor="w", pady=(2, 0))


class GameHUD(tk.Frame):
    def __init__(self, parent: tk.Misc, partida: Partida) -> None:
        super().__init__(
            parent, bg=CORES["superficie"], padx=13, pady=12,
            highlightbackground=CORES["borda"], highlightthickness=1,
        )
        self._partida = partida
        topo = tk.Frame(self, bg=CORES["superficie"])
        topo.pack(fill="x", pady=(0, 9))
        tk.Label(
            topo, text="PLACAR DA ROTA", bg=CORES["superficie"],
            fg=CORES["texto_suave"], font=(FONTE, 8, "bold"),
        ).pack(side="left")
        self._turno = tk.Label(
            topo, bg=CORES["superficie"], fg=CORES["caminho"],
            font=(FONTE, 8, "bold"),
        )
        self._turno.pack(side="right")

        disputa = tk.Frame(self, bg=CORES["superficie"])
        disputa.pack(fill="x")
        disputa.columnconfigure((0, 2), weight=1, uniform="hud")
        self._jogador = self._criar_competidor(disputa, "VOCÊ", CORES["jogador"], 0)
        tk.Label(
            disputa, text="VS", bg=CORES["superficie"], fg=CORES["texto_suave"],
            font=(FONTE, 9, "bold"),
        ).grid(row=0, column=1, padx=5)
        self._algoritmo = self._criar_competidor(
            disputa, partida.adversario.value.upper(), cor_avatar(partida.adversario), 2
        )
        self.atualizar(partida)

    @staticmethod
    def _criar_competidor(
        parent: tk.Misc, nome: str, cor: str, coluna: int
    ) -> dict[str, tk.Label]:
        frame = tk.Frame(parent, bg=CORES["superficie_clara"], padx=8, pady=8)
        frame.grid(row=0, column=coluna, sticky="nsew")
        tk.Label(
            frame, text=nome, bg=CORES["superficie_clara"], fg=cor,
            font=(FONTE, 9, "bold"),
        ).pack(anchor="w")
        local = tk.Label(
            frame, bg=CORES["superficie_clara"], fg=CORES["texto"],
            font=(FONTE, 8, "bold"), wraplength=105, justify="left",
        )
        local.pack(anchor="w", pady=(5, 2))
        numeros = tk.Label(
            frame, bg=CORES["superficie_clara"], fg=CORES["texto_suave"],
            font=(FONTE, 7), justify="left",
        )
        numeros.pack(anchor="w")
        return {"local": local, "numeros": numeros}

    def atualizar(self, partida: Partida) -> None:
        self._partida = partida
        estado = partida.estado
        jogador_local = partida.mapa.obter_vertice(estado.jogador.local_atual)
        algoritmo_local = partida.mapa.obter_vertice(estado.algoritmo.local_atual)
        self._turno.configure(text=f"TURNO {estado.turno}")
        self._jogador["local"].configure(text=jogador_local.nome)
        self._jogador["numeros"].configure(
            text=f"Movimentos: {estado.jogador.movimentos}\nCusto: {estado.jogador.custo}"
        )
        self._algoritmo["local"].configure(text=algoritmo_local.nome)
        self._algoritmo["numeros"].configure(
            text=(
                f"Movimentos: {estado.algoritmo.movimentos}\n"
                f"Nós analisados: {partida.estado.exploracao_revelada}/"
                f"{estado.algoritmo.nos_analisados}\n"  
                f"Custo atual: {estado.algoritmo.custo}"
            )
        )


class PainelMovimento(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        partida: Partida,
        mover: Callable[[int], None],
    ) -> None:
        super().__init__(
            parent, bg=CORES["superficie"], padx=13, pady=11,
            highlightbackground=CORES["borda"], highlightthickness=1,
        )
        self._mover = mover
        self._titulo = tk.Label(
            self, bg=CORES["superficie"], fg=CORES["texto"],
            font=(FONTE, 10, "bold"), wraplength=260, justify="left",
        )
        self._titulo.pack(anchor="w")
        tk.Label(
            self, text="Escolha uma conexão direta:", bg=CORES["superficie"],
            fg=CORES["texto_suave"], font=(FONTE, 8),
        ).pack(anchor="w", pady=(5, 7))
        self._opcoes = tk.Frame(self, bg=CORES["superficie"])
        self._opcoes.pack(fill="x")
        self.atualizar(partida)

    def atualizar(self, partida: Partida) -> None:
        for filho in self._opcoes.winfo_children():
            filho.destroy()
        atual = partida.mapa.obter_vertice(partida.estado.jogador.local_atual)
        self._titulo.configure(text=f"Você está em {atual.nome} · Nó {atual.identificador}")
        destinos = partida.destinos_disponiveis()
        if not destinos:
            tk.Label(
                self._opcoes, text="Partida concluída", bg=CORES["superficie"],
                fg=CORES["caminho"], font=(FONTE, 9, "bold"),
            ).pack(anchor="w")
            return
        for destino in destinos:
            aresta = partida.mapa.obter_aresta(atual.identificador, destino.identificador)
            texto = f"→ {destino.nome}   {aresta.terreno.nome} · {aresta.peso}"
            Botao(
                self._opcoes,
                texto,
                lambda item=destino.identificador: self._mover(item),
                anchor="w",
                padx=11,
                pady=7,
                font=(FONTE, 8, "bold"),
            ).pack(fill="x", pady=2)


class LegendaTerrenos(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(
            parent, bg=CORES["superficie"], padx=12, pady=9,
            highlightbackground=CORES["borda"], highlightthickness=1,
        )
        self._aberta = False
        self._botao = tk.Button(
            self, text="Terrenos  ▸", command=self._alternar,
            bg=CORES["superficie"], fg=CORES["texto"],
            activebackground=CORES["superficie"], activeforeground=CORES["texto"],
            font=(FONTE, 9, "bold"), relief="flat", bd=0, cursor="hand2",
        )
        self._botao.pack(fill="x")
        self._conteudo = tk.Frame(self, bg=CORES["superficie"])
        for linha, terreno in enumerate(TERRENOS.values()):
            amostra = tk.Canvas(
                self._conteudo, width=28, height=12, bg=CORES["superficie"],
                highlightthickness=0,
            )
            amostra.grid(row=linha, column=0, padx=(0, 6), pady=2)
            amostra.create_line(2, 6, 26, 6, fill=terreno.cor, width=5, dash=terreno.tracejado or ())
            tk.Label(
                self._conteudo, text=terreno.nome, bg=CORES["superficie"],
                fg=CORES["texto_suave"], font=(FONTE, 8),
            ).grid(row=linha, column=1, sticky="w")
            tk.Label(
                self._conteudo, text=f"custo {terreno.custo}",
                bg=CORES["superficie"], fg=CORES["texto_suave"],
                font=(FONTE, 8, "bold"),
            ).grid(row=linha, column=2, sticky="e", padx=(10, 0))
        self._conteudo.columnconfigure(1, weight=1)

    def _alternar(self) -> None:
        self._aberta = not self._aberta
        self._botao.configure(text=f"Terrenos  {'▾' if self._aberta else '▸'}")
        if self._aberta:
            self._conteudo.pack(fill="x", pady=(8, 0))
        else:
            self._conteudo.pack_forget()


class ResultadoJogo(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        jogar_novamente: Callable[[], None],
        escolher_adversario: Callable[[], None],
    ) -> None:
        super().__init__(
            parent, bg="#17243A", padx=30, pady=24,
            highlightbackground=CORES["caminho"], highlightthickness=3,
        )
        self._titulo = tk.Label(
            self, bg="#17243A", fg=CORES["caminho"],
            font=(FONTE, 20, "bold"),
        )
        self._titulo.pack()
        self._placar = tk.Label(
            self, bg="#17243A", fg=CORES["texto"],
            font=(FONTE, 10), justify="left",
        )
        self._placar.pack(fill="x", pady=(16, 12))
        self._conclusao = tk.Label(
            self, bg="#17243A", fg=CORES["texto_suave"],
            font=(FONTE, 10, "bold"), wraplength=560, justify="center",
        )
        self._conclusao.pack()
        self._explicacao = tk.Label(
            self, bg=CORES["superficie_clara"], fg=CORES["texto_suave"],
            font=(FONTE, 9), wraplength=540, justify="left", padx=14, pady=11,
        )
        self._explicacao.pack(fill="x", pady=(15, 18))
        botoes = tk.Frame(self, bg="#17243A")
        botoes.pack()
        Botao(botoes, "Jogar novamente", jogar_novamente, destaque=True).pack(side="left", padx=4)
        Botao(botoes, "Trocar adversário", escolher_adversario).pack(side="left", padx=4)

    def mostrar(self, partida: Partida) -> None:
        estado = partida.estado
        
        if estado.vencedor == "jogador":
            titulo = "Você venceu!"
        elif estado.vencedor == "algoritmo":
            titulo = f"{partida.adversario.value} venceu!"
        elif estado.vencedor == "empate":
            titulo = "Empate!"
        else:
            titulo = "Partida encerrada."

        rota = partida.resultado_algoritmo
        self._titulo.configure(text=titulo)
        self._placar.configure(
            text=(
                f"JOGADOR\nMovimentos: {estado.jogador.movimentos}   •   "
                f"Custo total: {estado.jogador.custo}\n\n"
                f"{partida.adversario.value.upper()} · ROTA CALCULADA\n"
                f"Movimentos: {rota.distancia}   •   Custo total: {rota.custo_total}   •   "
                f"Nós analisados: {len(rota.ordem_exploracao)}"
            )
        )
        self._conclusao.configure(text=partida.conclusao_tecnica())
        self._explicacao.configure(text=partida.explicacao_educacional())
        self.place(relx=0.5, rely=0.51, anchor="center", relwidth=0.62)
        self.lift()

    def ocultar(self) -> None:
        self.place_forget()
