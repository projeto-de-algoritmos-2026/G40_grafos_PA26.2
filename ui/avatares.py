"""Avatares vetoriais, sem arquivos de imagem externos."""

import tkinter as tk

from simulacao import TipoAdversario
from ui.tema import CORES, FONTE


def cor_avatar(tipo: str | TipoAdversario) -> str:
    valor = tipo.value if isinstance(tipo, TipoAdversario) else tipo
    if valor == TipoAdversario.BFS.value:
        return CORES["bfs"]
    if valor == TipoAdversario.DIJKSTRA.value:
        return CORES["dijkstra"]
    return CORES["jogador"]


class Avatar(tk.Canvas):
    """Retrato de personagem desenhado com formas simples do Canvas."""

    def __init__(
        self,
        parent: tk.Misc,
        tipo: str | TipoAdversario,
        *,
        tamanho: int = 104,
        fundo: str | None = None,
    ) -> None:
        self.tipo = tipo.value if isinstance(tipo, TipoAdversario) else tipo
        self.tamanho = tamanho
        cor_fundo = fundo or CORES["superficie"]
        super().__init__(
            parent,
            width=tamanho,
            height=tamanho,
            bg=cor_fundo,
            highlightthickness=0,
        )
        self._desenhar()

    def _desenhar(self) -> None:
        escala = self.tamanho / 104

        def p(valor: float) -> float:
            return valor * escala

        cor = cor_avatar(self.tipo)
        self.create_oval(p(8), p(8), p(96), p(96), fill="#0E1726", outline=cor, width=max(2, int(p(3))))

        if self.tipo == "Jogador":
            self.create_oval(p(30), p(24), p(74), p(68), fill="#F3C9A5", outline="")
            self.create_arc(p(26), p(15), p(78), p(52), start=0, extent=180, fill=cor, outline=cor)
            self.create_oval(p(39), p(43), p(44), p(48), fill="#27364A", outline="")
            self.create_oval(p(60), p(43), p(65), p(48), fill="#27364A", outline="")
            self.create_arc(p(44), p(48), p(61), p(60), start=195, extent=150, style="arc", outline="#7D4E3A", width=max(1, int(p(2))))
            self.create_rectangle(p(29), p(68), p(75), p(87), fill=cor, outline="")
            sigla = "VOCÊ"
        else:
            estrategista = self.tipo == TipoAdversario.DIJKSTRA.value
            self.create_line(p(52), p(17), p(52), p(27), fill=cor, width=max(2, int(p(3))))
            self.create_oval(p(47), p(11), p(57), p(21), fill=cor, outline="")
            self.create_rectangle(p(25), p(27), p(79), p(71), fill="#EAF2F8", outline=cor, width=max(2, int(p(3))))
            if estrategista:
                self.create_rectangle(p(34), p(39), p(70), p(51), fill="#26374F", outline="")
                self.create_polygon(p(52), p(35), p(58), p(45), p(52), p(55), p(46), p(45), fill=cor, outline="")
            else:
                self.create_oval(p(35), p(40), p(45), p(50), fill=cor, outline="")
                self.create_oval(p(59), p(40), p(69), p(50), fill=cor, outline="")
                self.create_arc(p(40), p(49), p(64), p(63), start=190, extent=160, style="arc", outline="#26374F", width=max(1, int(p(2))))
            self.create_rectangle(p(33), p(72), p(71), p(87), fill=cor, outline="")
            sigla = "DIJ" if estrategista else "BFS"

        self.create_text(p(52), p(79), text=sigla, fill="#FFFFFF", font=(FONTE, max(6, int(p(8))), "bold"))


def desenhar_token(
    canvas: tk.Canvas,
    x: float,
    y: float,
    tipo: str | TipoAdversario,
    etiqueta: str,
) -> None:
    """Desenha a versão compacta do avatar sobre um local do mapa."""
    cor = cor_avatar(tipo)
    canvas.create_oval(x - 16, y - 16, x + 16, y + 16, fill="#10192A", outline="#FFFFFF", width=2)
    canvas.create_oval(x - 10, y - 8, x + 10, y + 8, fill=cor, outline="")
    canvas.create_oval(x - 6, y - 4, x - 2, y, fill="#FFFFFF", outline="")
    canvas.create_oval(x + 2, y - 4, x + 6, y, fill="#FFFFFF", outline="")
    canvas.create_text(x, y + 23, text=etiqueta, fill="#172033", font=(FONTE, 8, "bold"))
