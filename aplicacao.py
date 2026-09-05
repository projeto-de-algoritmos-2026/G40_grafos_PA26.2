"""Controlador de navegação da aplicação desktop."""

import tkinter as tk

from mapas import Mapa
from simulacao import TipoAdversario
from ui.telas import (
    TelaCorrida,
    TelaEscolhaAdversario,
    TelaMenu,
    TelaSelecaoMapa,
)
from ui.tema import CORES


class AplicacaoCorrida(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Corrida de Algoritmos")
        self.geometry("1280x800")
        self.minsize(1000, 700)
        self.configure(bg=CORES["fundo"])
        self._tela_atual: tk.Frame | None = None
        self.mapa_selecionado: Mapa | None = None
        self.adversario_selecionado: TipoAdversario | None = None
        self.mostrar_menu()

    def _mostrar(self, tela: tk.Frame) -> None:
        if self._tela_atual is not None:
            self._tela_atual.destroy()
        self._tela_atual = tela
        self._tela_atual.pack(fill="both", expand=True)

    def mostrar_menu(self) -> None:
        self._mostrar(TelaMenu(self, self.mostrar_selecao))

    def mostrar_selecao(self) -> None:
        self._mostrar(
            TelaSelecaoMapa(self, self.mostrar_adversarios, self.mostrar_menu)
        )

    def mostrar_adversarios(self, mapa: Mapa) -> None:
        if not mapa.disponivel:
            return
        self.mapa_selecionado = mapa
        self._mostrar(
            TelaEscolhaAdversario(
                self,
                mapa,
                lambda adversario: self.mostrar_corrida(mapa, adversario),
                self.mostrar_selecao,
            )
        )

    def mostrar_corrida(
        self, mapa: Mapa, adversario: TipoAdversario
    ) -> None:
        self.mapa_selecionado = mapa
        self.adversario_selecionado = adversario
        self._mostrar(
            TelaCorrida(
                self,
                mapa,
                adversario,
                lambda: self.mostrar_adversarios(mapa),
            )
        )


def executar() -> None:
    AplicacaoCorrida().mainloop()
