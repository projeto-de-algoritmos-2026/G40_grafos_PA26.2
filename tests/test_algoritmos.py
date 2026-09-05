import unittest

from algoritmos import executar_bfs, executar_dijkstra
from mapas import obter_mapa


class TestAlgoritmosDaPartida(unittest.TestCase):
    def setUp(self) -> None:
        self.mapa = obter_mapa("ponderado")
        self.grafo = self.mapa.criar_grafo()
        self.vertices = tuple(v.identificador for v in self.mapa.vertices)

    def test_bfs_escolhe_menos_arestas_mesmo_com_maior_custo(self) -> None:
        resultado = executar_bfs(self.grafo, self.mapa.inicio, self.mapa.destino)
        self.assertEqual(resultado.caminho, (1, 4, 8))
        self.assertEqual(resultado.distancia, 2)
        self.assertEqual(resultado.custo_total, 20)

    def test_dijkstra_escolhe_menor_custo_mesmo_com_mais_arestas(self) -> None:
        resultado = executar_dijkstra(
            self.grafo, self.vertices, self.mapa.inicio, self.mapa.destino
        )
        self.assertEqual(resultado.caminho, (1, 2, 3, 6, 8))
        self.assertEqual(resultado.distancia, 4)
        self.assertEqual(resultado.custo_total, 6)


if __name__ == "__main__":
    unittest.main()
