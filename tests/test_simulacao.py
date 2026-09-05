import unittest

from simulacao import EstadoSimulacao, EstadoVertice


class TestEstadoSimulacao(unittest.TestCase):
    def test_prepara_inicio_e_destino(self) -> None:
        estado = EstadoSimulacao()
        estado.preparar_vertices([0, 1, 2], 0, 2)
        self.assertEqual(estado.vertices[0], {EstadoVertice.INICIO})
        self.assertEqual(estado.vertices[1], {EstadoVertice.NORMAL})
        self.assertEqual(estado.vertices[2], {EstadoVertice.DESTINO})

    def test_reiniciar_limpa_resultados_e_preserva_marcadores(self) -> None:
        estado = EstadoSimulacao()
        estado.preparar_vertices([0, 1, 2], 0, 2)
        estado.bfs.caminho.extend([0, 1, 2])
        estado.bfs.nos_explorados = 3
        estado.vertices[1] = {EstadoVertice.VISITADO_BFS}

        estado.reiniciar()

        self.assertEqual(estado.bfs.caminho, [])
        self.assertEqual(estado.bfs.nos_explorados, 0)
        self.assertEqual(estado.vertices[0], {EstadoVertice.INICIO})
        self.assertEqual(estado.vertices[1], {EstadoVertice.NORMAL})
        self.assertEqual(estado.vertices[2], {EstadoVertice.DESTINO})


if __name__ == "__main__":
    unittest.main()
