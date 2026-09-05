import unittest

from mapas import obter_mapa
from partida import Partida
from simulacao import TipoAdversario


class TestPartida(unittest.TestCase):
    def setUp(self) -> None:
        self.mapa = obter_mapa("ponderado")

    def test_jogador_so_pode_usar_conexao_direta_valida(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        with self.assertRaises(ValueError):
            partida.mover_jogador(8)
        with self.assertRaises(ValueError):
            partida.mover_jogador(5)  # conexão visualmente bloqueada

    def test_adversario_avanca_na_rota_do_algoritmo_a_cada_turno(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        partida.mover_jogador(4)
        self.assertEqual(partida.estado.algoritmo.local_atual, 2)
        self.assertEqual(partida.estado.algoritmo.custo, 1)

    def test_bfs_chega_em_dois_turnos_pela_rota_de_menos_arestas(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.BFS)
        partida.mover_jogador(2)
        partida.mover_jogador(3)
        self.assertEqual(partida.estado.vencedor, "algoritmo")
        self.assertEqual(partida.estado.algoritmo.caminho_percorrido, [1, 4, 8])

    def test_jogador_pode_vencer_dijkstra_pela_rota_curta(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        partida.mover_jogador(4)
        partida.mover_jogador(8)
        self.assertEqual(partida.estado.vencedor, "jogador")
        self.assertEqual(partida.estado.jogador.custo, 20)
        self.assertEqual(partida.resultado_algoritmo.custo_total, 6)

    def test_jogador_pode_empatar_se_seguir_a_rota_de_dijkstra(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        for destino in (2, 3, 6, 8):
            partida.mover_jogador(destino)
        self.assertEqual(partida.estado.vencedor, "empate")
        self.assertEqual(partida.estado.jogador.custo, 6)

    def test_reiniciar_restaura_os_dois_competidores(self) -> None:
        partida = Partida(self.mapa, TipoAdversario.DIJKSTRA)
        partida.mover_jogador(4)
        partida.reiniciar()
        self.assertEqual(partida.estado.jogador.local_atual, self.mapa.inicio)
        self.assertEqual(partida.estado.algoritmo.local_atual, self.mapa.inicio)
        self.assertEqual(partida.estado.turno, 0)


if __name__ == "__main__":
    unittest.main()
