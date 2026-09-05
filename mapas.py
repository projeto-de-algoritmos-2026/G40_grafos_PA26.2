"""Definições dos mapas, locais e terrenos do jogo.

Nomes, ícones e coordenadas pertencem à apresentação. Os algoritmos recebem
somente os identificadores e conexões do :class:`grafo.GrafoPonderado`.
"""

from dataclasses import dataclass
from enum import StrEnum

from grafo import GrafoPonderado


class TipoLocal(StrEnum):
    CASA = "casa"
    HOSPITAL = "hospital"
    ESCOLA = "escola"
    MERCADO = "mercado"
    PRACA = "praça"
    UNIVERSIDADE = "universidade"
    ESTACAO = "estação"
    PREDIO = "prédio"
    RESTAURANTE = "restaurante"
    DELEGACIA = "delegacia"


@dataclass(frozen=True)
class Terreno:
    custo: int
    nome: str
    descricao: str
    cor: str
    tracejado: tuple[int, ...] | None = None

    @property
    def bloqueado(self) -> bool:
        return self.custo == 0


TERRENOS: dict[int, Terreno] = {
    0: Terreno(0, "Bloqueado", "Não pode atravessar", "#E35D6A", (8, 6)),
    1: Terreno(1, "Estrada", "Custo mínimo", "#CBD5E1"),
    2: Terreno(2, "Grama", "Custo baixo", "#71C98B", (12, 5)),
    5: Terreno(5, "Areia", "Custo médio", "#E8C36A", (6, 4)),
    10: Terreno(10, "Lama", "Custo alto", "#A56A4B", (3, 5)),
}


@dataclass(frozen=True)
class VerticeVisual:
    identificador: int
    nome: str
    tipo: TipoLocal
    x: float
    y: float

    @property
    def rotulo(self) -> str:
        """Compatibilidade com a primeira interface visual."""
        return str(self.identificador)


@dataclass(frozen=True)
class ArestaVisual:
    origem: int
    destino: int
    peso: int = 1

    def __post_init__(self) -> None:
        if self.peso not in TERRENOS:
            custos = ", ".join(map(str, TERRENOS))
            raise ValueError(f"Custo de terreno inválido. Use: {custos}.")

    @property
    def terreno(self) -> Terreno:
        return TERRENOS[self.peso]


@dataclass(frozen=True)
class Mapa:
    identificador: str
    nome: str
    descricao: str
    vertices: tuple[VerticeVisual, ...]
    arestas: tuple[ArestaVisual, ...]
    inicio: int
    destino: int
    ponderado: bool
    disponivel: bool = True

    def criar_grafo(self) -> GrafoPonderado:
        """Cria o grafo lógico, omitindo caminhos visualmente bloqueados."""
        grafo = GrafoPonderado()
        for vertice in self.vertices:
            grafo.adicionar_vertice(vertice.identificador)
        for aresta in self.arestas:
            if not aresta.terreno.bloqueado:
                grafo.adicionar_aresta(aresta.origem, aresta.destino, aresta.peso)
        return grafo

    def obter_vertice(self, identificador: int) -> VerticeVisual:
        for vertice in self.vertices:
            if vertice.identificador == identificador:
                return vertice
        raise ValueError(f"Vértice inexistente no mapa: {identificador}.")

    def obter_aresta(self, origem: int, destino: int) -> ArestaVisual:
        procurada = frozenset((origem, destino))
        for aresta in self.arestas:
            if frozenset((aresta.origem, aresta.destino)) == procurada:
                return aresta
        raise ValueError(f"Não existe caminho entre os nós {origem} e {destino}.")

    def vizinhos_validos(self, identificador: int) -> tuple[VerticeVisual, ...]:
        ids: list[int] = []
        for aresta in self.arestas:
            if aresta.terreno.bloqueado:
                continue
            if aresta.origem == identificador:
                ids.append(aresta.destino)
            elif aresta.destino == identificador:
                ids.append(aresta.origem)
        return tuple(self.obter_vertice(item) for item in ids)

    def custo_caminho(self, caminho: list[int] | tuple[int, ...]) -> int:
        return sum(
            self.obter_aresta(origem, destino).peso
            for origem, destino in zip(caminho, caminho[1:])
        )


def _locais() -> tuple[VerticeVisual, ...]:
    return (
        VerticeVisual(1, "Casa do Jogador", TipoLocal.CASA, 0.08, 0.55),
        VerticeVisual(2, "Mercado Norte", TipoLocal.MERCADO, 0.23, 0.18),
        VerticeVisual(3, "Escola Municipal", TipoLocal.ESCOLA, 0.46, 0.16),
        VerticeVisual(4, "Praça Central", TipoLocal.PRACA, 0.38, 0.53),
        VerticeVisual(5, "Estação Leste", TipoLocal.ESTACAO, 0.61, 0.82),
        VerticeVisual(6, "Universidade", TipoLocal.UNIVERSIDADE, 0.72, 0.20),
        VerticeVisual(7, "Restaurante da Vila", TipoLocal.RESTAURANTE, 0.72, 0.55),
        VerticeVisual(8, "Hospital Central", TipoLocal.HOSPITAL, 0.93, 0.42),
    )


# Cenários temporários, isolados da UI e dos algoritmos. No mapa ponderado,
# BFS tende à rota curta 1-4-8 (custo 20), enquanto Dijkstra encontra a rota
# 1-2-3-6-8 (custo 6), deixando clara a diferença acadêmica.
MAPAS: tuple[Mapa, ...] = (
    Mapa(
        identificador="sem-pesos",
        nome="Bairro das Rotas",
        descricao="Todas as ruas têm o mesmo custo. Passos e custo apontam para a mesma rota.",
        vertices=_locais(),
        arestas=(
            ArestaVisual(1, 4), ArestaVisual(4, 8),
            ArestaVisual(1, 2), ArestaVisual(2, 3),
            ArestaVisual(3, 6), ArestaVisual(6, 8),
            ArestaVisual(3, 4), ArestaVisual(4, 5),
            ArestaVisual(5, 7), ArestaVisual(7, 8),
        ),
        inicio=1,
        destino=8,
        ponderado=False,
    ),
    Mapa(
        identificador="ponderado",
        nome="Cidade dos Terrenos",
        descricao="Estradas, grama, areia e lama mudam o custo de cada rota.",
        vertices=_locais(),
        arestas=(
            ArestaVisual(1, 4, 10), ArestaVisual(4, 8, 10),
            ArestaVisual(1, 2, 1), ArestaVisual(2, 3, 2),
            ArestaVisual(3, 6, 1), ArestaVisual(6, 8, 2),
            ArestaVisual(3, 4, 5), ArestaVisual(4, 5, 5),
            ArestaVisual(5, 7, 2), ArestaVisual(7, 8, 5),
            ArestaVisual(1, 5, 0),
        ),
        inicio=1,
        destino=8,
        ponderado=True,
    ),
    Mapa(
        identificador="personalizado",
        nome="Sua própria cidade",
        descricao="Crie e configure os locais e terrenos do seu mapa.",
        vertices=(),
        arestas=(),
        inicio=0,
        destino=0,
        ponderado=True,
        disponivel=False,
    ),
)


def obter_mapa(identificador: str) -> Mapa:
    for mapa in MAPAS:
        if mapa.identificador == identificador:
            return mapa
    raise ValueError(f"Mapa inexistente: {identificador}.")
