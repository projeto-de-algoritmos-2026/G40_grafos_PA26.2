"""Adapta os algoritmos do grafo para eventos visuais do jogo."""

from dataclasses import dataclass
from enum import StrEnum

from grafo import GrafoPonderado


class TipoEventoBusca(StrEnum):
    DESCOBRIU = "descobriu"
    PROCESSOU = "processou"
    ATUALIZOU_CUSTO = "atualizou-custo"
    CONCLUIU = "concluiu"


@dataclass(frozen=True)
class EventoBusca:
    tipo: TipoEventoBusca
    vertice: int
    origem: int | None = None
    custo: int | None = None


@dataclass(frozen=True)
class ResultadoBusca:
    caminho: tuple[int, ...]
    ordem_exploracao: tuple[int, ...]
    custo_total: int
    eventos: tuple[EventoBusca, ...] = ()

    @property
    def distancia(self) -> int:
        return max(len(self.caminho) - 1, 0)


def executar_bfs(
    grafo: GrafoPonderado, origem: int, destino: int
) -> ResultadoBusca:
    ordem: list[int] = []
    eventos: list[EventoBusca] = []

    def registrar_descoberta(vertice: int) -> None:
        ordem.append(vertice)
        eventos.append(EventoBusca(TipoEventoBusca.DESCOBRIU, vertice))

    caminho = grafo.busca_em_largura(
        origem, destino, ao_descobrir=registrar_descoberta
    )
    if caminho:
        eventos.append(EventoBusca(TipoEventoBusca.CONCLUIU, destino))
    return ResultadoBusca(
        caminho=tuple(caminho),
        ordem_exploracao=tuple(ordem),
        custo_total=_calcular_custo(grafo, caminho),
        eventos=tuple(eventos),
    )


def executar_dijkstra(
    grafo: GrafoPonderado,
    vertices: list[int] | tuple[int, ...],
    origem: int,
    destino: int,
) -> ResultadoBusca:
    """Usa o Dijkstra e a heap do grafo, coletando decisões para a animação."""
    del vertices  # Mantido no contrato para compatibilidade com os chamadores.
    ordem: list[int] = []
    eventos: list[EventoBusca] = []

    def registrar_processamento(vertice: int, custo: int) -> None:
        ordem.append(vertice)
        eventos.append(
            EventoBusca(TipoEventoBusca.PROCESSOU, vertice, custo=custo)
        )

    def registrar_atualizacao(origem_evento: int, vertice: int, custo: int) -> None:
        eventos.append(
            EventoBusca(
                TipoEventoBusca.ATUALIZOU_CUSTO,
                vertice,
                origem=origem_evento,
                custo=custo,
            )
        )

    caminho, custo = grafo.dijkstra(
        origem,
        destino,
        ao_processar=registrar_processamento,
        ao_atualizar=registrar_atualizacao,
    )
    if caminho:
        eventos.append(
            EventoBusca(TipoEventoBusca.CONCLUIU, destino, custo=int(custo))
        )
    return ResultadoBusca(
        caminho=tuple(caminho),
        ordem_exploracao=tuple(ordem),
        custo_total=0 if not caminho else int(custo),
        eventos=tuple(eventos),
    )


def _calcular_custo(grafo: GrafoPonderado, caminho: list[int]) -> int:
    return sum(
        grafo.obter_vizinhos(origem)[destino]
        for origem, destino in zip(caminho, caminho[1:])
    )
