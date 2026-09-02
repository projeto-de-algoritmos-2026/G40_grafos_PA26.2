from grafo import GrafoPonderado


grafo = GrafoPonderado()

grafo.adicionar_n_vertices(4)

# usando essas arestas para teste no terminal
grafo.adicionar_aresta(0, 1, 5)
grafo.adicionar_aresta(0, 2, 2)
grafo.adicionar_aresta(1, 3, 1)
grafo.adicionar_aresta(2, 3, 8)

print()

grafo.exibir_grafo()

caminho = grafo.busca_em_largura(0, 3)
print()
print(f"Caminho encontrado pela BFS: {' -> '.join(map(str, caminho))}")
print()
