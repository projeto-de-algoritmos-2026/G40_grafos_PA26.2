"""Componentes visuais reutilizáveis da aplicação."""

import tkinter as tk
from collections.abc import Callable, Mapping

from mapas import Mapa
from simulacao import EstadoAlgoritmo, EstadoVertice
from ui.tema import CORES, FONTE


class Botao(tk.Button):
    def __init__(
        self,
        parent: tk.Misc,
        texto: str,
        comando: Callable[[], None] | None = None,
        *,
        destaque: bool = False,
        **kwargs: object,
    ) -> None:
        fundo = CORES["primaria"] if destaque else CORES["superficie_clara"]
        ativo = CORES["primaria_hover"] if destaque else CORES["borda"]
        padx = kwargs.pop("padx", 20)
        pady = kwargs.pop("pady", 11)
        fonte = kwargs.pop("font", (FONTE, 10, "bold"))
        super().__init__(
            parent,
            text=texto,
            command=comando,
            bg=fundo,
            fg=CORES["texto"],
            activebackground=ativo,
            activeforeground=CORES["texto"],
            disabledforeground=CORES["texto_suave"],
            relief="flat",
            bd=0,
            padx=padx,
            pady=pady,
            cursor="hand2",
            font=fonte,
            **kwargs,
        )


class CardMapa(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        mapa: Mapa,
        comando: Callable[[], None],
    ) -> None:
        super().__init__(
            parent,
            bg=CORES["superficie"],
            highlightbackground=CORES["borda"],
            highlightthickness=1,
            padx=12,
            pady=10,
        )
        preview = tk.Canvas(
            self, width=240, height=68, bg="#DCE9D6", highlightthickness=0
        )
        preview.pack(fill="x", pady=(0, 7))
        self._desenhar_preview(preview, mapa)
        tk.Label(
            self, text=mapa.nome, bg=CORES["superficie"], fg=CORES["texto"],
            font=(FONTE, 13, "bold"), anchor="w",
        ).pack(fill="x")
        estrelas = "★" * mapa.dificuldade + "☆" * (6 - mapa.dificuldade)
        tk.Label(
            self, text=f"NÍVEL {mapa.dificuldade}  {estrelas}",
            bg=CORES["superficie"], fg=CORES["caminho"],
            font=(FONTE, 8, "bold"), anchor="w",
        ).pack(fill="x", pady=(3, 0))
        tk.Label(
            self, text=mapa.descricao, bg=CORES["superficie"],
            fg=CORES["texto_suave"], font=(FONTE, 9), anchor="nw",
            justify="left", wraplength=260,
        ).pack(fill="both", expand=True, pady=(5, 7))
        botao = Botao(
            self,
            "Selecionar" if mapa.disponivel else "Em breve",
            comando,
            destaque=mapa.disponivel,
            pady=7,
        )
        if not mapa.disponivel:
            botao.configure(state="disabled", cursor="arrow")
        botao.pack(fill="x")

    @staticmethod
    def _desenhar_preview(canvas: tk.Canvas, mapa: Mapa) -> None:
        canvas.create_rectangle(6, 5, 234, 63, fill="#C8DDBF", outline="")
        if not mapa.disponivel:
            canvas.create_text(
                120, 34, text="＋  NOVA CIDADE", fill="#62725E",
                font=(FONTE, 12, "bold"),
            )
            return
        caminhos = (
            (20, 52, 72, 35), (72, 35, 124, 48),
            (72, 35, 122, 14), (124, 48, 182, 36),
            (122, 14, 218, 26), (182, 36, 218, 26),
        )
        cores = ("#CBD5E1", "#71C98B", "#E8C36A", "#A56A4B")
        for indice, (x1, y1, x2, y2) in enumerate(caminhos):
            cor = "#CBD5E1" if not mapa.ponderado else cores[indice % len(cores)]
            canvas.create_line(x1, y1, x2, y2, fill="#718096", width=9)
            canvas.create_line(x1, y1, x2, y2, fill=cor, width=5)
        pontos = ((20, 52), (72, 35), (124, 48), (122, 14), (182, 36), (218, 26))
        for indice, (x, y) in enumerate(pontos):
            cor = CORES["inicio"] if indice == 0 else CORES["destino"] if indice == 5 else "#FFFFFF"
            canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=cor, outline="#526174", width=2)


class GrafoCanvas(tk.Canvas):
    """Desenha mapas e traduz estados da simulação em estilos visuais."""

    RAIO = 21

    def __init__(self, parent: tk.Misc, **kwargs: object) -> None:
        super().__init__(
            parent,
            bg=CORES["superficie"],
            highlightthickness=0,
            **kwargs,
        )
        self._mapa: Mapa | None = None
        self._estados: Mapping[int, set[EstadoVertice]] = {}
        self._caminho_final: tuple[int, ...] = ()
        self.bind("<Configure>", lambda _evento: self.redesenhar())

    def definir_mapa(
        self, mapa: Mapa, estados: Mapping[int, set[EstadoVertice]]
    ) -> None:
        self._mapa = mapa
        self._estados = estados
        self.redesenhar()

    def atualizar_estados(
        self,
        estados: Mapping[int, set[EstadoVertice]],
        caminho_final: list[int] | tuple[int, ...] = (),
    ) -> None:
        self._estados = estados
        self._caminho_final = tuple(caminho_final)
        self.redesenhar()

    def _coordenada(self, x: float, y: float) -> tuple[float, float]:
        margem_x, margem_y = 55, 38
        largura = max(self.winfo_width() - 2 * margem_x, 1)
        altura = max(self.winfo_height() - 2 * margem_y, 1)
        return margem_x + x * largura, margem_y + y * altura

    def redesenhar(self) -> None:
        self.delete("all")
        if self._mapa is None or self.winfo_width() < 80:
            return

        coordenadas = {
            vertice.identificador: self._coordenada(vertice.x, vertice.y)
            for vertice in self._mapa.vertices
        }
        caminho = self._arestas_do_caminho_final()

        for aresta in self._mapa.arestas:
            x1, y1 = coordenadas[aresta.origem]
            x2, y2 = coordenadas[aresta.destino]
            final = frozenset((aresta.origem, aresta.destino)) in caminho
            self.create_line(
                x1, y1, x2, y2,
                fill=CORES["caminho"] if final else CORES["aresta"],
                width=5 if final else 3,
            )
            if self._mapa.ponderado:
                self._desenhar_peso((x1 + x2) / 2, (y1 + y2) / 2, aresta.peso)

        for vertice in self._mapa.vertices:
            self._desenhar_vertice(
                *coordenadas[vertice.identificador],
                vertice.rotulo,
                self._estados.get(vertice.identificador, {EstadoVertice.NORMAL}),
            )

        self.create_text(
            18, 18, text="INÍCIO", anchor="w", fill=CORES["inicio"],
            font=(FONTE, 9, "bold"),
        )
        self.create_text(
            self.winfo_width() - 18, 18, text="DESTINO", anchor="e",
            fill=CORES["destino"], font=(FONTE, 9, "bold"),
        )

    def _arestas_do_caminho_final(self) -> set[frozenset[int]]:
        return {frozenset(par) for par in zip(self._caminho_final, self._caminho_final[1:])}

    def _desenhar_peso(self, x: float, y: float, peso: int) -> None:
        self.create_oval(x - 13, y - 13, x + 13, y + 13, fill=CORES["fundo"], outline="")
        self.create_text(x, y, text=str(peso), fill=CORES["texto"], font=(FONTE, 9, "bold"))

    def _desenhar_vertice(
        self, x: float, y: float, rotulo: str, estados: set[EstadoVertice]
    ) -> None:
        preenchimento, contorno, largura = self._estilo_vertice(estados)
        r = self.RAIO
        self.create_oval(
            x - r, y - r, x + r, y + r,
            fill=preenchimento, outline=contorno, width=largura,
        )
        self.create_text(x, y, text=rotulo, fill=CORES["fundo"], font=(FONTE, 11, "bold"))

    @staticmethod
    def _estilo_vertice(estados: set[EstadoVertice]) -> tuple[str, str, int]:
        if EstadoVertice.INICIO in estados:
            return CORES["inicio"], "#B8F7D2", 3
        if EstadoVertice.DESTINO in estados:
            return CORES["destino"], "#FFC0CB", 3
        if EstadoVertice.ATUAL_BFS in estados:
            return CORES["bfs_clara"], CORES["bfs"], 4
        if EstadoVertice.ATUAL_DIJKSTRA in estados:
            return CORES["dijkstra_clara"], CORES["dijkstra"], 4
        if EstadoVertice.CAMINHO_FINAL in estados:
            return CORES["caminho"], "#FFF0A8", 3
        if EstadoVertice.VISITADO_BFS in estados:
            return CORES["bfs"], CORES["bfs_clara"], 2
        if EstadoVertice.VISITADO_DIJKSTRA in estados:
            return CORES["dijkstra"], CORES["dijkstra_clara"], 2
        return CORES["texto_suave"], CORES["texto"], 2


class PainelAlgoritmo(tk.Frame):
    def __init__(self, parent: tk.Misc, nome: str, cor: str, metrica: str) -> None:
        super().__init__(
            parent, bg=CORES["superficie"],
            highlightbackground=CORES["borda"], highlightthickness=1,
            padx=18, pady=13,
        )
        self._metrica = metrica
        self._valores: dict[str, tk.Label] = {}
        tk.Label(
            self, text=nome, bg=CORES["superficie"], fg=cor,
            font=(FONTE, 14, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 7))
        for linha, chave in enumerate(("Status", "Nós explorados", metrica, "Caminho"), start=1):
            tk.Label(
                self, text=f"{chave}:", bg=CORES["superficie"],
                fg=CORES["texto_suave"], font=(FONTE, 9),
            ).grid(row=linha, column=0, sticky="w", padx=(0, 8), pady=2)
            valor = tk.Label(
                self, text="--", bg=CORES["superficie"], fg=CORES["texto"],
                font=(FONTE, 9, "bold"), anchor="w",
            )
            valor.grid(row=linha, column=1, sticky="w", pady=2)
            self._valores[chave] = valor
        self.columnconfigure(1, weight=1)

    def atualizar(self, estado: EstadoAlgoritmo) -> None:
        self._valores["Status"].configure(text=estado.status)
        self._valores["Nós explorados"].configure(text=str(estado.nos_explorados))
        metrica = estado.distancia if self._metrica == "Distância" else estado.custo
        self._valores[self._metrica].configure(text="--" if metrica is None else str(metrica))
        caminho = " → ".join(map(str, estado.caminho)) if estado.caminho else "--"
        self._valores["Caminho"].configure(text=caminho)


class ResultadoCorrida(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(
            parent, bg=CORES["superficie_clara"],
            highlightbackground=CORES["caminho"], highlightthickness=1,
            padx=18, pady=14,
        )
        self._titulo = tk.Label(
            self, text="Comparação concluída", bg=CORES["superficie_clara"],
            fg=CORES["texto"], font=(FONTE, 13, "bold"),
        )
        self._titulo.pack(anchor="w")
        self._conteudo = tk.Label(
            self, bg=CORES["superficie_clara"], fg=CORES["texto_suave"],
            font=(FONTE, 9), justify="left", anchor="w",
        )
        self._conteudo.pack(fill="x", pady=(7, 0))

    def mostrar(
        self,
        bfs: EstadoAlgoritmo,
        dijkstra: EstadoAlgoritmo,
        conclusao: str,
    ) -> None:
        def linha(estado: EstadoAlgoritmo) -> str:
            distancia = "--" if estado.distancia is None else estado.distancia
            custo = "--" if estado.custo is None else estado.custo
            return (
                f"{estado.nome}  •  Nós explorados: {estado.nos_explorados}  "
                f"•  Distância: {distancia}  •  Custo do caminho: {custo}"
            )

        self._conteudo.configure(
            text=f"{linha(bfs)}\n{linha(dijkstra)}\n\n{conclusao}"
        )
        self.grid()

    def ocultar(self) -> None:
        self.grid_remove()
