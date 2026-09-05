import unittest

from mapas import MAPAS, obter_mapa


class TestMapas(unittest.TestCase):
    def test_mapas_disponiveis_criam_grafo_existente(self) -> None:
        for mapa in MAPAS:
            if not mapa.disponivel:
                continue
            grafo = mapa.criar_grafo()
            self.assertTrue(grafo.obter_vizinhos(mapa.inicio))

    def test_mapa_sem_pesos_usa_custo_unitario(self) -> None:
        mapa = obter_mapa("sem-pesos")
        self.assertTrue(all(aresta.peso == 1 for aresta in mapa.arestas))

    def test_mapa_ponderado_oferece_pesos_distintos(self) -> None:
        mapa = obter_mapa("ponderado")
        self.assertGreater(len({aresta.peso for aresta in mapa.arestas}), 1)

    def test_caminho_bloqueado_nao_vira_conexao_logica(self) -> None:
        mapa = obter_mapa("ponderado")
        grafo = mapa.criar_grafo()
        self.assertNotIn(5, grafo.obter_vizinhos(1))

    def test_vertices_possuem_identidade_de_local(self) -> None:
        mapa = obter_mapa("ponderado")
        hospital = mapa.obter_vertice(mapa.destino)
        self.assertEqual(hospital.nome, "Hospital Central")
        self.assertEqual(hospital.tipo, "hospital")

    def test_identificador_inexistente_e_rejeitado(self) -> None:
        with self.assertRaises(ValueError):
            obter_mapa("inexistente")


if __name__ == "__main__":
    unittest.main()
