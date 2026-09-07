# G40_grafos_PA26.2

Número da Lista: 40<br>
Conteúdo da Disciplina: Grafos<br>

## Alunos

| Matrícula | Aluno                        |
| --------- | ---------------------------- |
| 231011515 | Isaque Camargos Nascimento   |
| 231011088 | ANA LUIZA SOARES DE CARVALHO |

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

## Sobre

Este repositório apresenta a implementação de um jogo visual desenvolvido para comparar as estratégias de busca dos algoritmos BFS e o Dijkstra. Em grafos não ponderados, ou com todas as arestas de mesmo peso, a BFS encontra o caminho com a menor quantidade de arestas, mas quando o mapa possui diferentes pesos, esse caminho nem sempre apresenta o menor custo total. No jogo, o usuário poderá escolher o tipo de mapa e visualizar o percurso realizado por cada algoritmo em tempo real, observando qual robô chega primeiro ou se ocorre um empate.

## Screenshots

Adicione 3 ou mais screenshots do projeto em funcionamento.

## Instalação

Linguagem: Python 3.12.3<br>
Interface: Tkinter 8.6, incluído na instalação padrão do Python.<br>

Não há dependências externas. Execute na raiz do projeto:

```bash
python main.py
```

## Uso

Escolha um mapa e um algoritmo adversário. A corrida começa imediatamente:

- avance por seis mapas com dificuldade, ramificações e bloqueios crescentes;
- clique em um local vizinho para caminhar até ele;
- cada terreno consome um tempo e custo diferentes;
- é possível voltar por uma conexão válida, pagando novamente seu custo;
- o balão do robô mostra a fila do BFS ou os custos calculados por Dijkstra;
- o cronômetro continua enquanto jogador e robô analisam ou se movimentam.

## Outros

Quaisquer outras informações sobre seu projeto podem ser descritas abaixo.
