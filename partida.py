"""Motor temporal da partida e movimentação restrita ao grafo."""

from algoritmos import (
    EventoBusca,
    ResultadoBusca,
    TipoEventoBusca,
    executar_bfs,
    executar_dijkstra,
)
from mapas import Mapa, VerticeVisual
from simulacao import (
    EstadoCompetidor,
    EstadoPartida,
    FaseRobo,
    MovimentoEmCurso,
    TipoAdversario,
)


class Partida:
    DURACAO_TERRENO_MS = {1: 600, 2: 850, 5: 1250, 10: 1800}
    INTERVALO_ANALISE_MS = {
        TipoAdversario.BFS: 420,
        TipoAdversario.DIJKSTRA: 260,
    }
    PAUSA_ANTES_DA_ROTA_MS = 450

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
        mensagem = (
            "Montando a fila..."
            if self.adversario == TipoAdversario.BFS
            else "Lendo os custos do mapa..."
        )
        return EstadoPartida(
            adversario=self.adversario,
            jogador=EstadoCompetidor("Jogador", self.mapa.inicio),
            algoritmo=EstadoCompetidor(self.adversario.value, self.mapa.inicio),
            rota_algoritmo=self.resultado_algoritmo.caminho,
            ordem_exploracao=self.resultado_algoritmo.ordem_exploracao,
            mensagem_robo=mensagem,
        )

    def destinos_disponiveis(self) -> tuple[VerticeVisual, ...]:
        if self.estado.concluida or self.estado.jogador.movimento is not None:
            return ()
        return self.mapa.vizinhos_validos(self.estado.jogador.local_atual)

    def solicitar_movimento_jogador(self, destino: int) -> None:
        if self.estado.concluida:
            raise RuntimeError("A partida já foi concluída.")
        if self.estado.jogador.movimento is not None:
            raise RuntimeError("Aguarde o jogador chegar ao próximo local.")
        disponiveis = {
            vertice.identificador for vertice in self.destinos_disponiveis()
        }
        if destino not in disponiveis:
            raise ValueError("O jogador só pode se mover para um local vizinho.")
        self._iniciar_movimento(self.estado.jogador, destino)

    def mover_jogador(self, destino: int) -> None:
        """Nome mantido para compatibilidade; o movimento agora leva tempo."""
        self.solicitar_movimento_jogador(destino)

    def atualizar(self, delta_ms: float) -> None:
        """Avança o relógio sem depender da velocidade de atualização da tela."""
        if delta_ms <= 0 or self.estado.concluida:
            return
        restante = delta_ms
        while restante > 0 and not self.estado.concluida:
            passo = min(restante, 50.0)
            self.estado.tempo_decorrido_ms += passo
            self._avancar_movimento(self.estado.jogador, passo)
            self._atualizar_robo(passo)
            self._verificar_resultado()
            restante -= passo

    def _atualizar_robo(self, delta_ms: float) -> None:
        estado = self.estado
        if estado.fase_robo == FaseRobo.ANALISANDO:
            estado.tempo_ate_evento_ms -= delta_ms
            if estado.tempo_ate_evento_ms <= 0:
                if estado.indice_evento < len(self.resultado_algoritmo.eventos):
                    evento = self.resultado_algoritmo.eventos[estado.indice_evento]
                    estado.indice_evento += 1
                    self._revelar_evento(evento)
                    if estado.fase_robo == FaseRobo.ANALISANDO:
                        estado.tempo_ate_evento_ms += self.INTERVALO_ANALISE_MS[
                            self.adversario
                        ]
                else:
                    self._preparar_rota()
            return

        if estado.fase_robo == FaseRobo.PREPARANDO:
            estado.tempo_ate_evento_ms -= delta_ms
            if estado.tempo_ate_evento_ms <= 0:
                estado.fase_robo = FaseRobo.MOVENDO
                self._iniciar_proximo_movimento_robo()
            return

        if estado.fase_robo == FaseRobo.MOVENDO:
            terminou_trecho = self._avancar_movimento(estado.algoritmo, delta_ms)
            if terminou_trecho:
                if estado.algoritmo.local_atual == self.mapa.destino:
                    estado.fase_robo = FaseRobo.CHEGOU
                    estado.mensagem_robo = "Destino alcançado!"
                else:
                    self._iniciar_proximo_movimento_robo()

    def _revelar_evento(self, evento: EventoBusca) -> None:
        estado = self.estado
        estado.no_em_analise = evento.vertice
        local = self.mapa.obter_vertice(evento.vertice)

        if evento.tipo == TipoEventoBusca.DESCOBRIU:
            estado.exploracao_revelada += 1
            estado.algoritmo.nos_analisados += 1
            estado.mensagem_robo = (
                f"Fila BFS\n{local.nome} entrou na busca"
            )
        elif evento.tipo == TipoEventoBusca.PROCESSOU:
            estado.exploracao_revelada += 1
            estado.algoritmo.nos_analisados += 1
            estado.mensagem_robo = (
                f"Analisando {local.nome}\nCusto acumulado: {evento.custo}"
            )
        elif evento.tipo == TipoEventoBusca.ATUALIZOU_CUSTO:
            if evento.custo is not None:
                estado.custos_estimados[evento.vertice] = evento.custo
            estado.mensagem_robo = (
                f"Encontrei uma rota melhor!\n{local.nome}: custo {evento.custo}"
            )
        elif evento.tipo == TipoEventoBusca.CONCLUIU:
            self._preparar_rota()

    def _preparar_rota(self) -> None:
        estado = self.estado
        estado.fase_robo = FaseRobo.PREPARANDO
        estado.no_em_analise = None
        estado.tempo_ate_evento_ms = self.PAUSA_ANTES_DA_ROTA_MS
        estado.mensagem_robo = (
            f"Rota pronta!\n{self.resultado_algoritmo.distancia} trechos · "
            f"custo {self.resultado_algoritmo.custo_total}"
        )

    def _iniciar_proximo_movimento_robo(self) -> None:
        algoritmo = self.estado.algoritmo
        indice_destino = algoritmo.movimentos + 1
        if indice_destino >= len(self.estado.rota_algoritmo):
            return
        destino = self.estado.rota_algoritmo[indice_destino]
        local = self.mapa.obter_vertice(destino)
        self.estado.mensagem_robo = f"Seguindo a rota...\nPróximo: {local.nome}"
        self._iniciar_movimento(algoritmo, destino)

    def _iniciar_movimento(
        self, competidor: EstadoCompetidor, destino: int
    ) -> None:
        aresta = self.mapa.obter_aresta(competidor.local_atual, destino)
        if aresta.terreno.bloqueado:
            raise ValueError("Este caminho está bloqueado.")
        competidor.movimento = MovimentoEmCurso(
            origem=competidor.local_atual,
            destino=destino,
            duracao_ms=self.DURACAO_TERRENO_MS[aresta.peso],
        )

    def _avancar_movimento(
        self, competidor: EstadoCompetidor, delta_ms: float
    ) -> bool:
        movimento = competidor.movimento
        if movimento is None:
            return False
        movimento.decorrido_ms = min(
            movimento.decorrido_ms + delta_ms, movimento.duracao_ms
        )
        if movimento.progresso < 1:
            return False

        aresta = self.mapa.obter_aresta(movimento.origem, movimento.destino)
        competidor.local_atual = movimento.destino
        competidor.movimentos += 1
        competidor.custo += aresta.peso
        competidor.caminho_percorrido.append(movimento.destino)
        competidor.movimento = None
        if competidor.local_atual == self.mapa.destino:
            competidor.tempo_chegada_ms = self.estado.tempo_decorrido_ms
        return True

    def _verificar_resultado(self) -> None:
        jogador = self.estado.jogador.tempo_chegada_ms
        algoritmo = self.estado.algoritmo.tempo_chegada_ms
        if jogador is None and algoritmo is None:
            return
        if jogador is not None and algoritmo is not None:
            if abs(jogador - algoritmo) <= 50:
                self.estado.vencedor = "empate"
            elif jogador < algoritmo:
                self.estado.vencedor = "jogador"
            else:
                self.estado.vencedor = "algoritmo"
        elif jogador is not None:
            self.estado.vencedor = "jogador"
        else:
            self.estado.vencedor = "algoritmo"

    def reiniciar(self) -> None:
        self.estado = self._estado_inicial()

    def conclusao_tecnica(self) -> str:
        jogador = self.estado.jogador
        algoritmo = self.resultado_algoritmo
        if self.estado.vencedor == "jogador":
            chegada = "Você chegou primeiro."
        elif self.estado.vencedor == "algoritmo":
            chegada = f"{self.adversario.value} chegou primeiro."
        else:
            chegada = "Vocês chegaram praticamente juntos."
        return (
            f"{chegada} Sua rota custou {jogador.custo}; a rota calculada "
            f"pelo algoritmo custa {algoritmo.custo_total}."
        )

    def explicacao_educacional(self) -> str:
        if self.adversario == TipoAdversario.BFS:
            return (
                "BFS organiza os locais em uma fila e prioriza menos arestas, "
                "mesmo que a rota atravesse terrenos mais caros."
            )
        return (
            "Dijkstra atualiza o menor custo conhecido de cada local. Ele pode "
            "pensar por mais tempo para escolher uma rota total mais barata."
        )

    def nos_explorados_visiveis(self) -> tuple[int, ...]:
        limite = self.estado.exploracao_revelada
        return self.estado.ordem_exploracao[:limite]
