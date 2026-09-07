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
    dificuldade: int = 1
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


def _locais_parque() -> tuple[VerticeVisual, ...]:
    return (
        VerticeVisual(1, "Casa do Jogador", TipoLocal.CASA, 0.06, 0.50),
        VerticeVisual(2, "Mercado das Flores", TipoLocal.MERCADO, 0.28, 0.14),
        VerticeVisual(3, "Praça das Fontes", TipoLocal.PRACA, 0.28, 0.50),
        VerticeVisual(4, "Escola do Parque", TipoLocal.ESCOLA, 0.28, 0.86),
        VerticeVisual(5, "Delegacia Norte", TipoLocal.DELEGACIA, 0.55, 0.14),
        VerticeVisual(6, "Estação Parque", TipoLocal.ESTACAO, 0.55, 0.50),
        VerticeVisual(7, "Restaurante do Lago", TipoLocal.RESTAURANTE, 0.55, 0.86),
        VerticeVisual(8, "Universidade Verde", TipoLocal.UNIVERSIDADE, 0.79, 0.22),
        VerticeVisual(9, "Hospital do Parque", TipoLocal.HOSPITAL, 0.94, 0.52),
    )


def _locais_pontes() -> tuple[VerticeVisual, ...]:
    return (
        VerticeVisual(1, "Casa da Colina", TipoLocal.CASA, 0.05, 0.50),
        VerticeVisual(2, "Mercado da Ponte", TipoLocal.MERCADO, 0.23, 0.13),
        VerticeVisual(3, "Praça do Rio", TipoLocal.PRACA, 0.23, 0.50),
        VerticeVisual(4, "Escola das Águas", TipoLocal.ESCOLA, 0.23, 0.87),
        VerticeVisual(5, "Estação Oeste", TipoLocal.ESTACAO, 0.48, 0.13),
        VerticeVisual(6, "Delegacia Central", TipoLocal.DELEGACIA, 0.48, 0.50),
        VerticeVisual(7, "Restaurante da Orla", TipoLocal.RESTAURANTE, 0.48, 0.87),
        VerticeVisual(8, "Universidade das Pontes", TipoLocal.UNIVERSIDADE, 0.73, 0.16),
        VerticeVisual(9, "Estação Leste", TipoLocal.ESTACAO, 0.73, 0.72),
        VerticeVisual(10, "Hospital das Águas", TipoLocal.HOSPITAL, 0.95, 0.45),
    )


def _locais_obras() -> tuple[VerticeVisual, ...]:
    return (
        VerticeVisual(1, "Casa do Jogador", TipoLocal.CASA, 0.04, 0.50),
        VerticeVisual(2, "Mercado Antigo", TipoLocal.MERCADO, 0.21, 0.12),
        VerticeVisual(3, "Praça das Obras", TipoLocal.PRACA, 0.21, 0.50),
        VerticeVisual(4, "Escola Técnica", TipoLocal.ESCOLA, 0.21, 0.88),
        VerticeVisual(5, "Delegacia Oeste", TipoLocal.DELEGACIA, 0.44, 0.12),
        VerticeVisual(6, "Estação Central", TipoLocal.ESTACAO, 0.44, 0.50),
        VerticeVisual(7, "Restaurante Popular", TipoLocal.RESTAURANTE, 0.44, 0.88),
        VerticeVisual(8, "Universidade Nova", TipoLocal.UNIVERSIDADE, 0.67, 0.12),
        VerticeVisual(9, "Praça Industrial", TipoLocal.PRACA, 0.67, 0.50),
        VerticeVisual(10, "Estação Sul", TipoLocal.ESTACAO, 0.67, 0.88),
        VerticeVisual(11, "Hospital Metropolitano", TipoLocal.HOSPITAL, 0.95, 0.50),
    )


def _locais_labirinto() -> tuple[VerticeVisual, ...]:
    return (
        VerticeVisual(1, "Casa do Jogador", TipoLocal.CASA, 0.04, 0.50),
        VerticeVisual(2, "Mercado Oeste", TipoLocal.MERCADO, 0.21, 0.10),
        VerticeVisual(3, "Praça do Relógio", TipoLocal.PRACA, 0.21, 0.47),
        VerticeVisual(4, "Escola Sul", TipoLocal.ESCOLA, 0.21, 0.88),
        VerticeVisual(5, "Delegacia do Centro", TipoLocal.DELEGACIA, 0.44, 0.10),
        VerticeVisual(6, "Estação Labirinto", TipoLocal.ESTACAO, 0.44, 0.47),
        VerticeVisual(7, "Restaurante Sul", TipoLocal.RESTAURANTE, 0.44, 0.88),
        VerticeVisual(8, "Universidade Norte", TipoLocal.UNIVERSIDADE, 0.67, 0.10),
        VerticeVisual(9, "Praça das Rotas", TipoLocal.PRACA, 0.67, 0.47),
        VerticeVisual(10, "Mercado Sul", TipoLocal.MERCADO, 0.67, 0.88),
        VerticeVisual(11, "Estação Nordeste", TipoLocal.ESTACAO, 0.84, 0.18),
        VerticeVisual(12, "Hospital do Labirinto", TipoLocal.HOSPITAL, 0.96, 0.52),
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
        dificuldade=1,
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
        dificuldade=2,
    ),
    Mapa(
        identificador="parque-dos-desvios",
        nome="Parque dos Desvios",
        descricao="Rotas cruzadas e um bloqueio escondem o melhor acesso ao hospital.",
        vertices=_locais_parque(),
        arestas=(
            ArestaVisual(1, 3, 1), ArestaVisual(1, 2, 2),
            ArestaVisual(1, 4, 5), ArestaVisual(2, 3, 1),
            ArestaVisual(2, 5, 5), ArestaVisual(2, 6, 0),
            ArestaVisual(3, 4, 2), ArestaVisual(3, 5, 2),
            ArestaVisual(3, 6, 10), ArestaVisual(4, 7, 1),
            ArestaVisual(5, 8, 1), ArestaVisual(6, 7, 1),
            ArestaVisual(6, 8, 2), ArestaVisual(6, 9, 5),
            ArestaVisual(7, 9, 2), ArestaVisual(8, 9, 1),
        ),
        inicio=1,
        destino=9,
        ponderado=True,
        dificuldade=3,
    ),
    Mapa(
        identificador="distrito-das-pontes",
        nome="Distrito das Pontes",
        descricao="Ciclos e travessias caras exigem atenção antes de cruzar o distrito.",
        vertices=_locais_pontes(),
        arestas=(
            ArestaVisual(1, 2, 1), ArestaVisual(1, 3, 5),
            ArestaVisual(1, 4, 2), ArestaVisual(2, 3, 1),
            ArestaVisual(2, 5, 2), ArestaVisual(3, 4, 1),
            ArestaVisual(3, 6, 10), ArestaVisual(4, 7, 2),
            ArestaVisual(5, 6, 1), ArestaVisual(5, 8, 5),
            ArestaVisual(5, 9, 0), ArestaVisual(6, 8, 2),
            ArestaVisual(6, 9, 5), ArestaVisual(7, 9, 1),
            ArestaVisual(7, 10, 10), ArestaVisual(8, 10, 2),
            ArestaVisual(9, 10, 1),
        ),
        inicio=1,
        destino=10,
        ponderado=True,
        dificuldade=4,
    ),
    Mapa(
        identificador="metropole-em-obras",
        nome="Metrópole em Obras",
        descricao="Atalhos de lama parecem bons, mas ruas longas podem custar muito menos.",
        vertices=_locais_obras(),
        arestas=(
            ArestaVisual(1, 3, 10), ArestaVisual(3, 6, 10),
            ArestaVisual(6, 9, 10), ArestaVisual(9, 11, 10),
            ArestaVisual(1, 2, 1), ArestaVisual(2, 5, 2),
            ArestaVisual(5, 8, 1), ArestaVisual(8, 9, 2),
            ArestaVisual(9, 10, 1), ArestaVisual(10, 11, 2),
            ArestaVisual(1, 4, 5), ArestaVisual(2, 3, 2),
            ArestaVisual(3, 4, 1), ArestaVisual(3, 5, 0),
            ArestaVisual(4, 7, 2), ArestaVisual(5, 6, 5),
            ArestaVisual(6, 7, 1), ArestaVisual(6, 8, 2),
            ArestaVisual(7, 10, 5), ArestaVisual(8, 11, 10),
        ),
        inicio=1,
        destino=11,
        ponderado=True,
        dificuldade=5,
    ),
    Mapa(
        identificador="labirinto-urbano",
        nome="Labirinto Urbano",
        descricao="Doze locais, becos, ciclos e obras formam o desafio mais complexo.",
        vertices=_locais_labirinto(),
        arestas=(
            ArestaVisual(1, 2, 1), ArestaVisual(1, 3, 10),
            ArestaVisual(1, 4, 2), ArestaVisual(2, 3, 5),
            ArestaVisual(2, 5, 2), ArestaVisual(3, 4, 2),
            ArestaVisual(3, 5, 0), ArestaVisual(3, 6, 10),
            ArestaVisual(4, 7, 1), ArestaVisual(5, 6, 5),
            ArestaVisual(5, 8, 1), ArestaVisual(6, 7, 1),
            ArestaVisual(6, 8, 2), ArestaVisual(6, 9, 10),
            ArestaVisual(7, 9, 2), ArestaVisual(7, 10, 2),
            ArestaVisual(8, 9, 5), ArestaVisual(8, 11, 2),
            ArestaVisual(9, 10, 1), ArestaVisual(9, 11, 0),
            ArestaVisual(9, 12, 10), ArestaVisual(10, 12, 5),
            ArestaVisual(11, 12, 1),
        ),
        inicio=1,
        destino=12,
        ponderado=True,
        dificuldade=6,
    ),
)


def obter_mapa(identificador: str) -> Mapa:
    for mapa in MAPAS:
        if mapa.identificador == identificador:
            return mapa
    raise ValueError(f"Mapa inexistente: {identificador}.")
