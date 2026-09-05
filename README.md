# G40_grafos_PA26.2

Este repositório apresenta um jogo educacional para comparar as estratégias de
busca de BFS e Dijkstra. O jogador escolhe um mapa e um algoritmo adversário,
depois percorre uma cidade usando exclusivamente as conexões válidas do grafo.
Cada terreno tem um custo, tornando visível a diferença entre buscar menos
arestas e buscar o menor custo total.

### Observações

O README.md ainda vai ser atualizado posteriormente

## Ferramentas utilizadas

- Python 3.12.3
- Tkinter 8.6 (incluído no Python, sem dependências externas)

## Executando

```bash
python main.py
```

A versão atual inclui:

- menu e seleção de cidade;
- escolha entre BFS e Dijkstra como adversário;
- mapa urbano com locais, terrenos, origem e destino;
- avatares vetoriais do jogador e dos algoritmos;
- movimentação por turnos limitada às arestas válidas;
- HUD, legenda recolhível e resultado educacional;
- BFS existente integrado e Dijkstra com busca real de menor custo.

Os cenários de demonstração continuam isolados em `mapas.py`. No mapa
ponderado, BFS encontra a rota de menos movimentos e Dijkstra encontra uma
rota maior, porém de menor custo.

## Testes

```bash
python -m unittest discover -v
```

## Integrantes

<center>
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/Ana-Luiza-SC">
        <img
          src="https://github.com/Ana-Luiza-SC.png"
          width="100px"
          alt="Foto de Ana Luiza"
        />
        <br />
        <sub><b>Ana Luiza Soares</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/isaqzin">
        <img
          src="https://github.com/isaqzin.png"
          width="100px"
          alt="Foto de isaqzin"
        />
        <br />
        <sub><b>Isaque Camargos</b></sub>
      </a>
    </td>
  </tr>
</table>
</center>
