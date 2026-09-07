"""Telas do fluxo do jogo educacional."""

import tkinter as tk
import time
from collections.abc import Callable

from mapas import MAPAS, Mapa
from partida import Partida
from simulacao import TipoAdversario
from ui.avatares import Avatar, cor_avatar
from ui.componentes import Botao, CardMapa
from ui.componentes_jogo import CardAdversario
from ui.hud_jogo import ControlesMovimento, HUDCompacto, ResultadoTempo
from ui.mapa_jogo import MapaJogo
from ui.tema import CORES, FONTE


class TelaBase(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=CORES["fundo"])


class TelaMenu(TelaBase):
    def __init__(self, parent: tk.Misc, iniciar: Callable[[], None]) -> None:
        super().__init__(parent)
        conteudo = tk.Frame(self, bg=CORES["fundo"], padx=35, pady=25)
        conteudo.place(relx=0.5, rely=0.49, anchor="center", relwidth=0.94)

        tk.Label(
            conteudo, text="UM JOGO DE CAMINHOS E ESTRATÉGIA",
            bg=CORES["fundo"], fg=CORES["caminho"],
            font=(FONTE, 9, "bold"),
        ).pack()
        tk.Label(
            conteudo, text="Corrida de Algoritmos", bg=CORES["fundo"],
            fg=CORES["texto"], font=(FONTE, 32, "bold"),
        ).pack(pady=(8, 4))
        tk.Label(
            conteudo, text="Trace sua rota. Enfrente o algoritmo. Chegue ao destino.",
            bg=CORES["fundo"], fg=CORES["texto_suave"],
            font=(FONTE, 14),
        ).pack()

        personagens = tk.Frame(conteudo, bg=CORES["fundo"])
        personagens.pack(pady=24)
        self._personagem(personagens, "Jogador", "VOCÊ", 0)
        tk.Label(
            personagens, text="VS", bg=CORES["fundo"], fg=CORES["texto_suave"],
            font=(FONTE, 13, "bold"),
        ).grid(row=0, column=1, padx=18)
        self._personagem(personagens, TipoAdversario.BFS, "BFS", 2)
        tk.Label(
            personagens, text="OU", bg=CORES["fundo"], fg=CORES["texto_suave"],
            font=(FONTE, 9, "bold"),
        ).grid(row=0, column=3, padx=12)
        self._personagem(personagens, TipoAdversario.DIJKSTRA, "DIJKSTRA", 4)

        tk.Label(
            conteudo,
            text="Escolha uma cidade e um adversário. Cada movimento acontece pelas conexões reais do grafo.",
            bg=CORES["fundo"], fg=CORES["texto_suave"],
            font=(FONTE, 10), wraplength=690, justify="center",
        ).pack(pady=(0, 18))
        Botao(conteudo, "Jogar agora  →", iniciar, destaque=True, width=20).pack()

    @staticmethod
    def _personagem(
        parent: tk.Misc, tipo: str | TipoAdversario, nome: str, coluna: int
    ) -> None:
        frame = tk.Frame(parent, bg=CORES["fundo"])
        frame.grid(row=0, column=coluna)
        Avatar(frame, tipo, tamanho=92, fundo=CORES["fundo"]).pack()
        tk.Label(
            frame, text=nome, bg=CORES["fundo"], fg=cor_avatar(tipo),
            font=(FONTE, 9, "bold"),
        ).pack(pady=(3, 0))


class TelaSelecaoMapa(TelaBase):
    def __init__(
        self,
        parent: tk.Misc,
        selecionar: Callable[[Mapa], None],
        voltar: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._cabecalho(
            "Escolha sua cidade",
            "Cada cenário tem ruas e terrenos que mudam a estratégia.",
            voltar,
        )
        cards = tk.Frame(self, bg=CORES["fundo"], padx=24, pady=10)
        cards.pack(fill="both", expand=True)
        total_colunas = 3
        for indice, mapa in enumerate(MAPAS):
            linha, coluna = divmod(indice, total_colunas)
            card = CardMapa(cards, mapa, lambda item=mapa: selecionar(item))
            card.grid(row=linha, column=coluna, padx=6, pady=6, sticky="nsew")
            cards.columnconfigure(coluna, weight=1, uniform="mapas")
            cards.rowconfigure(linha, weight=1, uniform="mapas")

    def _cabecalho(self, titulo: str, subtitulo: str, voltar: Callable[[], None]) -> None:
        cabecalho = tk.Frame(self, bg=CORES["fundo"], padx=30, pady=18)
        cabecalho.pack(fill="x")
        Botao(cabecalho, "← Voltar", voltar).pack(side="left")
        textos = tk.Frame(cabecalho, bg=CORES["fundo"])
        textos.pack(side="left", padx=24)
        tk.Label(
            textos, text=titulo, bg=CORES["fundo"], fg=CORES["texto"],
            font=(FONTE, 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            textos, text=subtitulo, bg=CORES["fundo"],
            fg=CORES["texto_suave"], font=(FONTE, 10),
        ).pack(anchor="w", pady=(3, 0))


class TelaEscolhaAdversario(TelaBase):
    def __init__(
        self,
        parent: tk.Misc,
        mapa: Mapa,
        selecionar: Callable[[TipoAdversario], None],
        voltar: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        cabecalho = tk.Frame(self, bg=CORES["fundo"], padx=38, pady=24)
        cabecalho.pack(fill="x")
        Botao(cabecalho, "← Trocar cidade", voltar).pack(side="left")
        textos = tk.Frame(cabecalho, bg=CORES["fundo"])
        textos.pack(side="left", padx=24)
        tk.Label(
            textos, text="Escolha seu adversário", bg=CORES["fundo"],
            fg=CORES["texto"], font=(FONTE, 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            textos, text=f"Partida em {mapa.nome}", bg=CORES["fundo"],
            fg=CORES["texto_suave"], font=(FONTE, 10),
        ).pack(anchor="w", pady=(3, 0))

        cards = tk.Frame(self, bg=CORES["fundo"], padx=90, pady=12)
        cards.pack(fill="both", expand=True)
        for coluna, adversario in enumerate(TipoAdversario):
            card = CardAdversario(
                cards, adversario, lambda item=adversario: selecionar(item)
            )
            card.grid(row=0, column=coluna, padx=14, sticky="nsew")
            cards.columnconfigure(coluna, weight=1, uniform="adversarios")
        cards.rowconfigure(0, weight=1)


class TelaCorrida(TelaBase):
    def __init__(
        self,
        parent: tk.Misc,
        mapa: Mapa,
        adversario: TipoAdversario,
        voltar: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.partida = Partida(mapa, adversario)
        self._voltar = voltar
        self._tick_id: str | None = None
        self._ultimo_tick = time.perf_counter()
        self._resultado_mostrado = False
        self._montar_cabecalho()

        self.hud = HUDCompacto(self, self.partida)
        self.hud.pack(fill="x", padx=18, pady=(0, 10))

        moldura_mapa = tk.Frame(
            self, bg="#F4F8F1", padx=5, pady=5,
            highlightbackground="#5D7257", highlightthickness=2,
        )
        moldura_mapa.pack(fill="both", expand=True, padx=18)
        self.mapa_jogo = MapaJogo(moldura_mapa, mapa, self._mover_jogador)
        self.mapa_jogo.pack(fill="both", expand=True)

        self.movimentos = ControlesMovimento(
            self, self.partida, self._mover_jogador
        )
        self.movimentos.pack(fill="x", padx=18, pady=10)

        self.resultado = ResultadoTempo(self, self._reiniciar, self._voltar)
        self._atualizar_interface()
        self._agendar_tick()

    def _montar_cabecalho(self) -> None:
        cabecalho = tk.Frame(self, bg=CORES["fundo"], padx=18, pady=13)
        cabecalho.pack(fill="x")
        Botao(cabecalho, "← Sair da partida", self._voltar, padx=13, pady=8).pack(side="left")
        titulo = tk.Frame(cabecalho, bg=CORES["fundo"])
        titulo.pack(side="left", padx=18)
        tk.Label(
            titulo, text="CORRIDA DE ALGORITMOS", bg=CORES["fundo"],
            fg=CORES["texto"], font=(FONTE, 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            titulo, text=self.partida.mapa.nome, bg=CORES["fundo"],
            fg=CORES["texto_suave"], font=(FONTE, 8),
        ).pack(anchor="w")
        badge = tk.Label(
            cabecalho, text=f"VOCÊ  VS  {self.partida.adversario.value.upper()}",
            bg=cor_avatar(self.partida.adversario), fg="#10192A",
            font=(FONTE, 9, "bold"), padx=13, pady=7,
        )
        badge.pack(side="right")
        Botao(
            cabecalho, "Reiniciar", self._reiniciar, padx=12, pady=7
        ).pack(side="right", padx=(0, 9))

    def _mover_jogador(self, destino: int) -> None:
        if self.partida.estado.concluida:
            return
        self.partida.mover_jogador(destino)
        self._atualizar_interface()

    def _agendar_tick(self) -> None:
        if self._tick_id is None and not self.partida.estado.concluida:
            self._tick_id = self.after(33, self._tick)

    def _tick(self) -> None:
        self._tick_id = None
        agora = time.perf_counter()
        delta_ms = (agora - self._ultimo_tick) * 1000
        self._ultimo_tick = agora
        self.partida.atualizar(delta_ms)
        self._atualizar_interface()
        if self.partida.estado.concluida:
            if not self._resultado_mostrado:
                self._resultado_mostrado = True
                self.resultado.mostrar(self.partida)
            return
        self._agendar_tick()

    def _atualizar_interface(self) -> None:
        self.mapa_jogo.atualizar(self.partida)
        self.hud.atualizar(self.partida)
        self.movimentos.atualizar(self.partida)

    def _reiniciar(self) -> None:
        self.partida.reiniciar()
        self.resultado.ocultar()
        self._resultado_mostrado = False
        self._ultimo_tick = time.perf_counter()
        self._atualizar_interface()
        self._agendar_tick()

    def destroy(self) -> None:
        if self._tick_id is not None:
            try:
                self.after_cancel(self._tick_id)
            except tk.TclError:
                pass
            self._tick_id = None
        super().destroy()
