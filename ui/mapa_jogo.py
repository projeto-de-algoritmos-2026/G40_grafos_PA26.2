"""Canvas do mapa urbano e seus elementos interativos."""

import tkinter as tk
from collections.abc import Callable

from mapas import Mapa, TipoLocal
from partida import Partida
from simulacao import FaseRobo
from ui.avatares import cor_avatar, desenhar_token
from ui.tema import CORES, FONTE, FONTE_ICONE


ICONES_LOCAL: dict[TipoLocal, str] = {
    TipoLocal.CASA: "⌂",
    TipoLocal.HOSPITAL: "✚",
    TipoLocal.ESCOLA: "▤",
    TipoLocal.MERCADO: "▣",
    TipoLocal.PRACA: "♧",
    TipoLocal.UNIVERSIDADE: "◆",
    TipoLocal.ESTACAO: "▥",
    TipoLocal.PREDIO: "▦",
    TipoLocal.RESTAURANTE: "●",
    TipoLocal.DELEGACIA: "★",
}


class MapaJogo(tk.Canvas):
    """Representa o grafo como cidade, mantendo IDs apenas no modelo lógico."""

    def __init__(
        self,
        parent: tk.Misc,
        mapa: Mapa,
        ao_escolher_destino: Callable[[int], None],
    ) -> None:
        super().__init__(
            parent, bg=CORES["mapa"], highlightthickness=0, cursor="arrow"
        )
        self.mapa = mapa
        self._ao_escolher_destino = ao_escolher_destino
        self._partida: Partida | None = None
        self.bind("<Configure>", lambda _evento: self.redesenhar())

    def atualizar(self, partida: Partida) -> None:
        self._partida = partida
        self.redesenhar()

    def _coordenada(self, x: float, y: float) -> tuple[float, float]:
        margem_x, margem_y = 76, 65
        largura = max(self.winfo_width() - 2 * margem_x, 1)
        altura = max(self.winfo_height() - 2 * margem_y, 1)
        return margem_x + x * largura, margem_y + y * altura

    def redesenhar(self) -> None:
        self.delete("all")
        if self.winfo_width() < 120:
            return
        self._desenhar_cidade()
        coordenadas = {
            vertice.identificador: self._coordenada(vertice.x, vertice.y)
            for vertice in self.mapa.vertices
        }
        for aresta in self.mapa.arestas:
            self._desenhar_terreno(aresta, coordenadas)
        if self._partida is not None:
            self._desenhar_trilhas(coordenadas)

        vizinhos = set()
        if self._partida is not None:
            vizinhos = {
                vertice.identificador
                for vertice in self._partida.destinos_disponiveis()
            }

        explorados = set()
        if self._partida is not None: 
            explorados = set(self._partida.nos_explorados_visiveis())

        
        for vertice in self.mapa.vertices:
            self._desenhar_local(
                vertice,
                *coordenadas[vertice.identificador],
                disponivel=vertice.identificador in vizinhos,
                explorado=vertice.identificador in explorados,
                analisando=(
                    self._partida is not None
                    and vertice.identificador == self._partida.estado.no_em_analise
                ),
            )

        if self._partida is not None:
            self._desenhar_competidores(coordenadas)

    def _desenhar_cidade(self) -> None:
        largura, altura = self.winfo_width(), self.winfo_height()
        blocos = (
            (0.02, 0.04, 0.28, 0.32), (0.38, 0.02, 0.64, 0.28),
            (0.73, 0.03, 0.97, 0.27), (0.04, 0.68, 0.29, 0.96),
            (0.39, 0.72, 0.64, 0.97), (0.76, 0.72, 0.97, 0.96),
        )
        for x1, y1, x2, y2 in blocos:
            self.create_rectangle(
                x1 * largura, y1 * altura, x2 * largura, y2 * altura,
                fill=CORES["mapa_bloco"], outline="#B7D0AC", width=1,
            )
        self.create_text(
            18, 18, anchor="nw", text="CIDADE DAS ROTAS",
            fill="#708269", font=(FONTE, 9, "bold"),
        )

    def _desenhar_terreno(self, aresta, coordenadas: dict[int, tuple[float, float]]) -> None:
        x1, y1 = coordenadas[aresta.origem]
        x2, y2 = coordenadas[aresta.destino]
        terreno = aresta.terreno
        self.create_line(x1, y1, x2, y2, fill="#718096", width=14, capstyle="round")
        self.create_line(
            x1, y1, x2, y2, fill=terreno.cor, width=8,
            dash=terreno.tracejado or (), capstyle="round",
        )
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        texto = terreno.nome if not self.mapa.ponderado else f"{terreno.nome} · {terreno.custo}"
        largura = max(56, 7 * len(texto))
        self.create_rectangle(
            mx - largura / 2, my - 10, mx + largura / 2, my + 10,
            fill="#F7FAF5", outline=terreno.cor, width=1,
        )
        self.create_text(mx, my, text=texto, fill="#35445A", font=(FONTE, 7, "bold"))
        if terreno.bloqueado:
            for deslocamento in (-18, 0, 18):
                self.create_line(
                    mx + deslocamento - 5, my - 5,
                    mx + deslocamento + 5, my + 5,
                    fill="#8F2634", width=3,
                )

    def _desenhar_local(
        self,
        vertice,
        x: float,
        y: float,
        *,
        disponivel: bool,
        explorado: bool,
        analisando: bool,
    ) -> None:
        tag = f"local-{vertice.identificador}"
        contorno = CORES["caminho"] if disponivel else "#7B8A9A"
        largura = 4 if disponivel else 2

        if explorado and vertice.identificador not in (self.mapa.inicio, self.mapa.destino):
            contorno = (cor_avatar(self._partida.adversario) if self._partida else CORES["caminho"])
            largura = 4

        if analisando:
            contorno = cor_avatar(self._partida.adversario) if self._partida else CORES["caminho"]
            largura = 6

        if vertice.identificador == self.mapa.inicio:
            contorno = CORES["inicio"]
        elif vertice.identificador == self.mapa.destino:
            contorno = CORES["destino"]

        self.create_rectangle(
            x - 64, y - 28, x + 64, y + 30,
            fill="#FFFFFF", outline=contorno, width=largura,
            tags=(tag, "local"),
        )
        self.create_oval(
            x - 57, y - 19, x - 27, y + 11,
            fill=contorno, outline="", tags=(tag, "local"),
        )
        self.create_text(
            x - 42, y - 4, text=ICONES_LOCAL[vertice.tipo],
            fill="#FFFFFF", font=(FONTE_ICONE, 16, "bold"), tags=(tag, "local"),
        )
        nome = vertice.nome if len(vertice.nome) <= 18 else f"{vertice.nome[:16]}…"
        self.create_text(
            x - 20, y - 9, anchor="w", text=nome,
            fill=CORES["mapa_texto"], font=(FONTE, 8, "bold"), tags=(tag, "local"),
        )
        self.create_text(
            x - 20, y + 9, anchor="w", text=f"Nó {vertice.identificador}",
            fill="#718096", font=(FONTE, 7), tags=(tag, "local"),
        )
        if (
            self._partida is not None
            and vertice.identificador in self._partida.estado.custos_estimados
        ):
            custo = self._partida.estado.custos_estimados[vertice.identificador]
            self.create_oval(
                x + 42, y - 38, x + 68, y - 14,
                fill=cor_avatar(self._partida.adversario), outline="#FFFFFF", width=2,
            )
            self.create_text(
                x + 55, y - 26, text=str(custo), fill="#10192A",
                font=(FONTE, 8, "bold"),
            )
        if vertice.identificador in (self.mapa.inicio, self.mapa.destino):
            etiqueta = "ORIGEM" if vertice.identificador == self.mapa.inicio else "DESTINO"
            self.create_text(
                x, y + 42, text=etiqueta, fill=contorno,
                font=(FONTE, 8, "bold"), tags=(tag, "local"),
            )
        if disponivel:
            self.tag_bind(tag, "<Button-1>", lambda _evento, item=vertice.identificador: self._ao_escolher_destino(item))
            self.tag_bind(tag, "<Enter>", lambda _evento: self.configure(cursor="hand2"))
            self.tag_bind(tag, "<Leave>", lambda _evento: self.configure(cursor="arrow"))

    def _desenhar_trilhas(self, coordenadas: dict[int, tuple[float, float]]) -> None:
        assert self._partida is not None

        def trilha(caminho: list[int] | tuple[int, ...], cor: str, tracejado=()) -> None:
            for origem, destino in zip(caminho, caminho[1:]):
                x1, y1 = coordenadas[origem]
                x2, y2 = coordenadas[destino]
                self.create_line(
                    x1, y1, x2, y2, fill=cor, width=4,
                    dash=tracejado, capstyle="round",
                )

        trilha(self._partida.estado.jogador.caminho_percorrido, CORES["jogador"])
        rota_visivel = self._partida.estado.algoritmo.caminho_percorrido
        if self._partida.estado.fase_robo != FaseRobo.ANALISANDO:
            rota_visivel = list(self._partida.estado.rota_algoritmo)
        trilha(rota_visivel, cor_avatar(self._partida.adversario), (8, 4))

        for competidor, cor in (
            (self._partida.estado.jogador, CORES["jogador"]),
            (self._partida.estado.algoritmo, cor_avatar(self._partida.adversario)),
        ):
            if competidor.movimento is None:
                continue
            inicio = coordenadas[competidor.movimento.origem]
            atual = self._posicao_competidor(competidor, coordenadas)
            self.create_line(
                *inicio, *atual, fill=cor, width=4, capstyle="round"
            )

    def _desenhar_competidores(self, coordenadas: dict[int, tuple[float, float]]) -> None:
        assert self._partida is not None
        jogador = self._partida.estado.jogador
        algoritmo = self._partida.estado.algoritmo
        jx, jy = self._posicao_competidor(jogador, coordenadas)
        ax, ay = self._posicao_competidor(algoritmo, coordenadas)
        mesmo_local = (
            jogador.local_atual == algoritmo.local_atual
            and jogador.movimento is None
            and algoritmo.movimento is None
        )
        desenhar_token(self, jx - (19 if mesmo_local else 0), jy - 45, "Jogador", "VOCÊ")
        desenhar_token(
            self, ax + (19 if mesmo_local else 0), ay - 45,
            self._partida.adversario, self._partida.adversario.value.upper(),
        )
        self._desenhar_pensamento(ax + (19 if mesmo_local else 0), ay - 45, coordenadas)

    def _posicao_competidor(self, competidor, coordenadas) -> tuple[float, float]:
        movimento = competidor.movimento
        if movimento is None:
            return coordenadas[competidor.local_atual]
        x1, y1 = coordenadas[movimento.origem]
        x2, y2 = coordenadas[movimento.destino]
        progresso = movimento.progresso
        return x1 + (x2 - x1) * progresso, y1 + (y2 - y1) * progresso

    def _desenhar_pensamento(
        self,
        robo_x: float,
        robo_y: float,
        coordenadas: dict[int, tuple[float, float]],
    ) -> None:
        assert self._partida is not None
        estado = self._partida.estado
        cor = cor_avatar(self._partida.adversario)
        largura_balao = 224
        x = min(max(robo_x, largura_balao / 2 + 8), self.winfo_width() - largura_balao / 2 - 8)
        y = max(robo_y - 72, 48)

        if estado.no_em_analise in coordenadas:
            alvo_x, alvo_y = coordenadas[estado.no_em_analise]
            self.create_line(
                robo_x, robo_y, alvo_x, alvo_y,
                fill=cor, width=2, dash=(4, 5), arrow="last",
            )

        self.create_oval(robo_x - 8, robo_y - 30, robo_x, robo_y - 22, fill="#FFFFFF", outline=cor)
        self.create_oval(robo_x - 16, robo_y - 43, robo_x - 5, robo_y - 32, fill="#FFFFFF", outline=cor)
        self.create_rectangle(
            x - largura_balao / 2, y - 28,
            x + largura_balao / 2, y + 28,
            fill="#FFFFFF", outline=cor, width=2,
        )
        self.create_text(
            x, y, text=estado.mensagem_robo, fill="#243447",
            font=(FONTE, 8, "bold"), width=largura_balao - 16, justify="center",
        )
