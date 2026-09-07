import unittest

from mapas import obter_mapa
from partida import Partida
from simulacao import FaseRobo, TipoAdversario


def avancar(partida: Partida, duracao_ms: int, passo_ms: int = 50) -> None:
    for _ in range(duracao_ms // passo_ms):
        partida.atualizar(passo_ms)


def aguardar_jogador(partida: Partida) -> None:
    while partida.estado.jogador.movimento is not None:
        partida.atualizar(50)


class TestPartida(unittest.TestCase):
    def setUp(self) -> None:
        self.mapa = obter_mapa("ponderado")

    def test_jogador_so_pode_usar_conexao_direta_valida(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        with self.assertRaises(ValueError):
            partida.mover_jogador(8)
        with self.assertRaises(ValueError):
            partida.mover_jogador(5)  # conexão visualmente bloqueada

    def test_movimento_leva_tempo_e_bloqueia_nova_escolha(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        partida.mover_jogador(4)
        partida.atualizar(300)
        self.assertEqual(partida.estado.jogador.local_atual, 1)
        self.assertIsNotNone(partida.estado.jogador.movimento)
        with self.assertRaises(RuntimeError):
            partida.mover_jogador(2)

    def test_jogador_pode_voltar_e_paga_novamente_o_caminho(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        partida.mover_jogador(2)
        aguardar_jogador(partida)
        partida.mover_jogador(1)
        aguardar_jogador(partida)
        self.assertEqual(partida.estado.jogador.local_atual, 1)
        self.assertEqual(partida.estado.jogador.movimentos, 2)
        self.assertEqual(partida.estado.jogador.custo, 2)

    def test_robo_analisa_e_avanca_sem_clique_do_jogador(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        avancar(partida, 5000)
        self.assertEqual(partida.estado.jogador.local_atual, 1)
        self.assertGreater(partida.estado.algoritmo.nos_analisados, 0)
        self.assertIn(
            partida.estado.fase_robo,
            {FaseRobo.PREPARANDO, FaseRobo.MOVENDO, FaseRobo.CHEGOU},
        )

    def test_dijkstra_exibe_atualizacoes_de_menor_custo(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        avancar(partida, 1200)
        self.assertTrue(partida.estado.custos_estimados)
        self.assertIn("custo", partida.estado.mensagem_robo.lower())

    def test_bfs_pode_chegar_sem_acao_do_jogador(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.BFS)
        avancar(partida, 9000)
        self.assertEqual(partida.estado.vencedor, "algoritmo")
        self.assertEqual(partida.estado.algoritmo.caminho_percorrido, [1, 4, 8])

    def test_jogador_pode_vencer_dijkstra_pela_rota_curta(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        partida.mover_jogador(4)
        aguardar_jogador(partida)
        partida.mover_jogador(8)
        aguardar_jogador(partida)
        self.assertEqual(partida.estado.vencedor, "jogador")
        self.assertEqual(partida.estado.jogador.custo, 20)

    def test_reiniciar_restaura_relogio_e_competidores(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        partida.mover_jogador(4)
        avancar(partida, 500)
        partida.reiniciar()
        self.assertEqual(partida.estado.jogador.local_atual, self.mapa.inicio)
        self.assertEqual(partida.estado.algoritmo.local_atual, self.mapa.inicio)
        self.assertEqual(partida.estado.tempo_decorrido_ms, 0)
        self.assertEqual(partida.estado.fase_robo, FaseRobo.ANALISANDO)


if __name__ == "__main__":
    unittest.main()
