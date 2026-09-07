import unittest

from algoritmos import TipoEventoBusca, executar_bfs, executar_dijkstra
from mapas import MAPAS, obter_mapa


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
        self.assertIn(TipoEventoBusca.DESCOBRIU, {evento.tipo for evento in resultado.eventos})

    def test_dijkstra_escolhe_menor_custo_mesmo_com_mais_arestas(self) -> None:
        resultado = executar_dijkstra(
            self.grafo, self.vertices, self.mapa.inicio, self.mapa.destino
        )
        self.assertEqual(resultado.caminho, (1, 2, 3, 6, 8))
        self.assertEqual(resultado.distancia, 4)
        self.assertEqual(resultado.custo_total, 6)
        self.assertIn(
            TipoEventoBusca.ATUALIZOU_CUSTO,
            {evento.tipo for evento in resultado.eventos},
        )

    def test_dijkstra_nunca_supera_o_custo_do_bfs_nos_seis_mapas(self) -> None:
        for mapa in MAPAS:
            grafo = mapa.criar_grafo()
            vertices = tuple(item.identificador for item in mapa.vertices)
            bfs = executar_bfs(grafo, mapa.inicio, mapa.destino)
            dijkstra = executar_dijkstra(
                grafo, vertices, mapa.inicio, mapa.destino
            )
            self.assertLessEqual(
                dijkstra.custo_total,
                bfs.custo_total,
                msg=f"Comparação inválida no mapa {mapa.identificador}",
            )


if __name__ == "__main__":
    unittest.main()
