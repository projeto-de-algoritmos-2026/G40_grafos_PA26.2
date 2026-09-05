import unittest

from grafo import GrafoPonderado


class TestBuscaEmLarguraExistente(unittest.TestCase):
    def test_bfs_prioriza_menor_quantidade_de_arestas(self) -> None:
        grafo = GrafoPonderado()
        grafo.adicionar_n_vertices(5)
        grafo.adicionar_aresta(0, 1, 20)
        grafo.adicionar_aresta(1, 4, 20)
        grafo.adicionar_aresta(0, 2, 1)
        grafo.adicionar_aresta(2, 3, 1)
        grafo.adicionar_aresta(3, 4, 1)

        self.assertEqual(grafo.busca_em_largura(0, 4), [0, 1, 4])

    def test_bfs_pode_informar_vertices_descobertos_sem_mudar_resultado(self) -> None:
        grafo = GrafoPonderado()
        grafo.adicionar_n_vertices(4)
        grafo.adicionar_aresta(0, 1, 1)
        grafo.adicionar_aresta(0, 2, 1)
        grafo.adicionar_aresta(1, 3, 1)
        descobertos: list[int] = []

        caminho = grafo.busca_em_largura(0, 3, ao_descobrir=descobertos.append)

        self.assertEqual(caminho, [0, 1, 3])
        self.assertEqual(descobertos, [0, 1, 2, 3])


if __name__ == "__main__":
    unittest.main()
