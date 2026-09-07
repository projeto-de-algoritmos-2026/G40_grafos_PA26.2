"""Regras da partida e movimentação restrita às conexões do mapa."""

from algoritmos import ResultadoBusca, executar_bfs, executar_dijkstra
from mapas import Mapa, VerticeVisual
from simulacao import EstadoCompetidor, EstadoPartida, TipoAdversario


class Partida:
    def __init__(self, mapa: Mapa, adversario: TipoAdversario) -> None:
        if not mapa.disponivel:
            raise ValueError("O mapa selecionado ainda não está disponível.")
        self.mapa = mapa
        self.grafo = mapa.criar_grafo()
        self.adversario = adversario
        self.resultado_algoritmo = self._executar_algoritmo()
        if not self.resultado_algoritmo.caminho:
            raise ValueError("O destino não pode ser alcançado neste mapa.")
        self.estado = self._estado_inicial()

    def _executar_algoritmo(self) -> ResultadoBusca:
        if self.adversario == TipoAdversario.BFS:
            return executar_bfs(self.grafo, self.mapa.inicio, self.mapa.destino)
        return executar_dijkstra(
            self.grafo,
            tuple(vertice.identificador for vertice in self.mapa.vertices),
            self.mapa.inicio,
            self.mapa.destino,
        )

    def _estado_inicial(self) -> EstadoPartida:
        return EstadoPartida(
            adversario=self.adversario,
            jogador=EstadoCompetidor("Jogador", self.mapa.inicio),
            algoritmo=EstadoCompetidor(
                self.adversario.value,
                self.mapa.inicio,
                nos_analisados=len(self.resultado_algoritmo.ordem_exploracao),
            ),
            rota_algoritmo=self.resultado_algoritmo.caminho,
            ordem_exploracao=self.resultado_algoritmo.ordem_exploracao,
        )

    def destinos_disponiveis(self) -> tuple[VerticeVisual, ...]:
        if self.estado.concluida:
            return ()
        return self.mapa.vizinhos_validos(self.estado.jogador.local_atual)

    def mover_jogador(self, destino: int) -> None:
        if self.estado.concluida:
            raise RuntimeError("A partida já foi concluída.")
        disponiveis = {
            vertice.identificador for vertice in self.destinos_disponiveis()
        }
        if destino not in disponiveis:
            raise ValueError("O jogador só pode se mover para um local vizinho.")

        self._mover_competidor(self.estado.jogador, destino)
        self._mover_adversario()
        self.estado.turno += 1

        self.estado.exploracao_revelada = min(
            self.estado.exploracao_revelada + 1, len(self.estado.ordem_exploracao)
        )

        self._verificar_resultado()

    def _mover_adversario(self) -> None:
        indice = self.estado.algoritmo.movimentos + 1
        if indice < len(self.estado.rota_algoritmo):
            self._mover_competidor(
                self.estado.algoritmo, self.estado.rota_algoritmo[indice]
            )

    def _mover_competidor(self, competidor: EstadoCompetidor, destino: int) -> None:
        aresta = self.mapa.obter_aresta(competidor.local_atual, destino)
        if aresta.terreno.bloqueado:
            raise ValueError("Este caminho está bloqueado.")
        competidor.local_atual = destino
        competidor.movimentos += 1
        competidor.custo += aresta.peso
        competidor.caminho_percorrido.append(destino)

    def _verificar_resultado(self) -> None:
        jogador_chegou = (self.estado.jogador.local_atual == self.mapa.destino)
        algoritmo_chegou = (self.estado.algoritmo.local_atual == self.mapa.destino)

        if algoritmo_chegou and not jogador_chegou:
            return

        if jogador_chegou:
            custo_jogador = self.estado.jogador.custo
            custo_algoritmo = self.resultado_algoritmo.custo_total

            if custo_jogador < custo_algoritmo:
                self.estado.vencedor = "jogador"

            elif custo_jogador > custo_algoritmo:
                self.estado.vencedor = "algoritmo"

            else:
                self.estado.vencedor = "empate"

    def reiniciar(self) -> None:
        self.estado = self._estado_inicial()

    def conclusao_tecnica(self) -> str:
        jogador = self.estado.jogador
        custo_algoritmo = self.resultado_algoritmo.custo_total

        if self.estado.vencedor == "jogador":
            return (
                f"Você venceu pelo menor custo: "
                f"{jogador.custo} contra {custo_algoritmo}."
            )

        if self.estado.vencedor == "algoritmo":
            return (
                f"{self.adversario.value} venceu pelo menor custo: "
                f"{custo_algoritmo} contra {jogador.custo}."
            )

        if self.estado.vencedor == "empate":
            return (
                f"Empate: ambos possuem uma rota com custo total "
                f"de {jogador.custo}."
            )

        return "A partida ainda não foi concluída."

    def explicacao_educacional(self) -> str:
        if self.adversario == TipoAdversario.BFS:
            return (
                "BFS prioriza a quantidade de arestas. Por isso, escolhe uma rota "
                "com menos movimentos mesmo quando os terrenos são mais caros."
            )
        return (
            "Dijkstra considera o custo acumulado. Por isso, pode preferir uma rota "
            "mais longa em movimentos quando ela possui menor custo total."
        )

    def nos_explorados_visiveis(self):
        limite = self.estado.exploracao_revelada
        return self.estado.ordem_exploracao[:limite]