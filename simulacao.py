"""Modelos de estado independentes da interface e dos algoritmos."""

from dataclasses import dataclass, field
from enum import StrEnum


class EstadoVertice(StrEnum):
    NORMAL = "normal"
    VISITADO_BFS = "visitado-bfs"
    VISITADO_DIJKSTRA = "visitado-dijkstra"
    ATUAL_BFS = "atual-bfs"
    ATUAL_DIJKSTRA = "atual-dijkstra"
    INICIO = "inicio"
    DESTINO = "destino"
    CAMINHO_FINAL = "caminho-final"


class TipoAdversario(StrEnum):
    BFS = "BFS"
    DIJKSTRA = "Dijkstra"


class FaseRobo(StrEnum):
    ANALISANDO = "Analisando o mapa"
    PREPARANDO = "Rota encontrada"
    MOVENDO = "A caminho"
    CHEGOU = "Chegou ao destino"


@dataclass
class MovimentoEmCurso:
    origem: int
    destino: int
    duracao_ms: float
    decorrido_ms: float = 0

    @property
    def progresso(self) -> float:
        if self.duracao_ms <= 0:
            return 1.0
        return min(self.decorrido_ms / self.duracao_ms, 1.0)


@dataclass
class EstadoCompetidor:
    nome: str
    local_atual: int
    movimentos: int = 0
    custo: int = 0
    caminho_percorrido: list[int] = field(default_factory=list)
    nos_analisados: int = 0
    movimento: MovimentoEmCurso | None = None
    tempo_chegada_ms: float | None = None

    def __post_init__(self) -> None:
        if not self.caminho_percorrido:
            self.caminho_percorrido.append(self.local_atual)


@dataclass
class EstadoPartida:
    adversario: TipoAdversario
    jogador: EstadoCompetidor
    algoritmo: EstadoCompetidor
    rota_algoritmo: tuple[int, ...]
    ordem_exploracao: tuple[int, ...]
    turno: int = 0
    vencedor: str | None = None
    exploracao_revelada: int = 0
    tempo_decorrido_ms: float = 0
    fase_robo: FaseRobo = FaseRobo.ANALISANDO
    indice_evento: int = 0
    tempo_ate_evento_ms: float = 350
    no_em_analise: int | None = None
    mensagem_robo: str = "Preparando a busca..."
    custos_estimados: dict[int, int] = field(default_factory=dict)

    @property
    def concluida(self) -> bool:
        return self.vencedor is not None


@dataclass
class EstadoAlgoritmo:
    nome: str
    status: str = "Aguardando"
    nos_explorados: int = 0
    distancia: int | None = None
    custo: int | None = None
    caminho: list[int] = field(default_factory=list)

    def reiniciar(self) -> None:
        self.status = "Aguardando"
        self.nos_explorados = 0
        self.distancia = None
        self.custo = None
        self.caminho.clear()


@dataclass
class EstadoSimulacao:
    bfs: EstadoAlgoritmo = field(default_factory=lambda: EstadoAlgoritmo("BFS"))
    dijkstra: EstadoAlgoritmo = field(
        default_factory=lambda: EstadoAlgoritmo("Dijkstra")
    )
    vertices: dict[int, set[EstadoVertice]] = field(default_factory=dict)
    pausada: bool = False
    concluida: bool = False

    def preparar_vertices(self, ids: list[int], inicio: int, destino: int) -> None:
        self.vertices = {identificador: {EstadoVertice.NORMAL} for identificador in ids}
        self.vertices[inicio] = {EstadoVertice.INICIO}
        self.vertices[destino] = {EstadoVertice.DESTINO}

    def reiniciar(self) -> None:
        self.bfs.reiniciar()
        self.dijkstra.reiniciar()
        self.pausada = False
        self.concluida = False
        for estados in self.vertices.values():
            estados.intersection_update({EstadoVertice.INICIO, EstadoVertice.DESTINO})
            if not estados:
                estados.add(EstadoVertice.NORMAL)
