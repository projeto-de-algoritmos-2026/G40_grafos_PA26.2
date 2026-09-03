import math
from heap import heap_inserir, heap_remover
from collections import deque

class GrafoPonderado:

    def __init__(self) -> None: # para iniciar
        # to criando um dicionário de forma que  esteje representado
        # X (vertice X): {Y: k (aponta para Y com peso K), ...} 
        self._adjacencias: dict[int, dict[int, int]] = {}

    @staticmethod
    def _validar_vertice(vertice: int) -> None:
        if not isinstance(vertice, int):
            raise TypeError("Os vertices são números")
        if vertice < 0:
            raise ValueError("O vertice também não será nulo.")

    @staticmethod
    def _validar_peso(peso: int) -> None:
        if not isinstance(peso, (int)):
            raise TypeError("O peso deve ser um numero inteiro.")
        if not math.isfinite(peso):
            raise ValueError("O peso deve ser um numero finito")
        if peso < 0:
            raise ValueError("O peso da aresta nao pode ser negativo")

    def adicionar_vertice(self, vertice: int) -> None:
        # aqui verifica se existe antes de criar um vertice
        self._validar_vertice(vertice)
        if vertice not in self._adjacencias:
            self._adjacencias[vertice] = {}

    # criei um que cria logo n vertices pra evitar problema
    def adicionar_n_vertices(self, total: int) -> None:
        self._validar_vertice(total)
        for i in range(0, total):
            self.adicionar_vertice(i)


    def adicionar_aresta(
        self, origem: int, destino: int, peso: int
    ) -> None:
        # começa validando os vértices e o peso
        self._validar_vertice(origem)
        self._validar_vertice(destino)
        self._validar_peso(peso)

        # se não tiver vertice no grafo
        inexistentes = [
            vertice
            for vertice in (origem, destino)
            if vertice not in self._adjacencias
        ]
        if inexistentes:
            nomes = ", ".join(map(str, inexistentes))
            raise ValueError(f"Vertice(s) inexistente(s): {nomes}.")

        # coloca para para mabos os lador porque a pista vai e volta
        self._adjacencias[origem][destino] = peso
        self._adjacencias[destino][origem] = peso

    def obter_vizinhos(self, vertice: int) -> dict[int, int]:
        # retorna uma copia do vizinho
        self._validar_vertice(vertice)
        if vertice not in self._adjacencias:
            raise ValueError(f"Vertice inexistente: {vertice}.")
        return self._adjacencias[vertice].copy()

    def exibir_grafo(self) -> None:
        # mostra no terminal o grafo completo
        if not self._adjacencias:
            print("Grafo vazio.")
            return

        for vertice, vizinhos in self._adjacencias.items():
            if not vizinhos:
                print(f"{vertice} -> sem vizinhos")
                continue

            adjacencias = ", ".join(
                f"{vizinho} (peso: {peso})"
                for vizinho, peso in vizinhos.items()
            )
            print(f"{vertice} -> {adjacencias}")

    def busca_em_largura( self, origem: int, destino: int ) -> list[int]:
        
        self._validar_vertice(origem)
        self._validar_vertice(destino)

        # verifica se eles existem dentro do grafo
        inexistentes = [
            vertice
            for vertice in (origem, destino)
            if vertice not in self._adjacencias
        ]
        if inexistentes:
            nomes = ", ".join(map(str, inexistentes))
            raise ValueError(f"Vertice(s) inexistente(s): {nomes}.")

        # se comeca e termina no mesmo lugar o caminho ja esta pronto
        if origem == destino:
            return [origem]

        # a fila guarda os proximos e visitados evita passar duas vezes
        fila = deque([origem])
        visitados = {origem}
        antecessores: dict[int, int] = {}

        while fila:
            atual = fila.popleft()

            # passa pelos vizinhos
            for vizinho in self._adjacencias[atual]:
                if vizinho in visitados:
                    continue

                visitados.add(vizinho)
                # guarda de onde veio para montar o caminho depois
                antecessores[vizinho] = atual

                if vizinho == destino:
                    # volta pelos antecessores ate chegar na origem
                    caminho = [destino]
                    while caminho[-1] != origem:
                        caminho.append(antecessores[caminho[-1]])
                    caminho.reverse()
                    return caminho

                fila.append(vizinho)

        # se a fila acabar nao existe caminho ate o destino
        return [] # e fim


    def dijkstra(self, origem, destino):

            self._validar_vertice(origem)
            self._validar_vertice(destino)

            if origem == destino:
                return ([origem], 0)

            distancias = {}
            antecessores = {}
            heap = []

            distancias[origem] = 0

            heap_inserir(heap, (0, origem))

            while heap:
                distancia_atual, vertice_atual = heap_remover(heap)

                if distancia_atual > distancias.get(vertice_atual, math.inf):
                    continue

                if vertice_atual == destino: 
                    break

                vizinhos = self.obter_vizinhos(vertice_atual)

                for vizinho, peso in vizinhos.items():
                    nova_distancia = distancia_atual + peso

                    if nova_distancia < distancias.get(vizinho, math.inf):
                        distancias[vizinho] = nova_distancia
                        antecessores[vizinho] = vertice_atual
                        heap_inserir(heap, (nova_distancia, vizinho))


            if destino not in distancias:
                return ([], math.inf)

            caminho = [destino]
            atual = destino 

            while atual != origem:
                atual = antecessores[atual]
                caminho.append(atual)

            caminho.reverse()
            return caminho, distancias[destino]