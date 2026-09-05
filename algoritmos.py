"""Adaptadores dos algoritmos para o estado de uma partida.

O BFS continua sendo executado por ``GrafoPonderado.busca_em_largura``. Este
módulo apenas coleta seus detalhes. Dijkstra é implementado aqui porque ainda
não existia no projeto.
"""

import heapq
import math
from dataclasses import dataclass

from grafo import GrafoPonderado


@dataclass(frozen=True)
class ResultadoBusca:
    caminho: tuple[int, ...]
    ordem_exploracao: tuple[int, ...]
    custo_total: int

    @property
    def distancia(self) -> int:
        return max(len(self.caminho) - 1, 0)


def executar_bfs(
    grafo: GrafoPonderado, origem: int, destino: int
) -> ResultadoBusca:
    ordem: list[int] = []
    caminho = grafo.busca_em_largura(origem, destino, ao_descobrir=ordem.append)
    return ResultadoBusca(
        caminho=tuple(caminho),
        ordem_exploracao=tuple(ordem),
        custo_total=_calcular_custo(grafo, caminho),
    )


def executar_dijkstra(
    grafo: GrafoPonderado,
    vertices: list[int] | tuple[int, ...],
    origem: int,
    destino: int,
) -> ResultadoBusca:
    """Encontra o caminho de menor custo usando somente a API pública do grafo."""
    distancias = {vertice: math.inf for vertice in vertices}
    distancias[origem] = 0
    antecessores: dict[int, int] = {}
    fila: list[tuple[int, int]] = [(0, origem)]
    ordem: list[int] = []
    finalizados: set[int] = set()

    while fila:
        distancia_atual, atual = heapq.heappop(fila)
        if atual in finalizados:
            continue
        finalizados.add(atual)
        ordem.append(atual)
        if atual == destino:
            break

        for vizinho, peso in grafo.obter_vizinhos(atual).items():
            if peso == 0:
                continue
            nova_distancia = distancia_atual + peso
            if nova_distancia < distancias[vizinho]:
                distancias[vizinho] = nova_distancia
                antecessores[vizinho] = atual
                heapq.heappush(fila, (nova_distancia, vizinho))

    if math.isinf(distancias[destino]):
        return ResultadoBusca((), tuple(ordem), 0)

    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(antecessores[caminho[-1]])
    caminho.reverse()
    return ResultadoBusca(tuple(caminho), tuple(ordem), int(distancias[destino]))


def _calcular_custo(grafo: GrafoPonderado, caminho: list[int]) -> int:
    return sum(
        grafo.obter_vizinhos(origem)[destino]
        for origem, destino in zip(caminho, caminho[1:])
    )
