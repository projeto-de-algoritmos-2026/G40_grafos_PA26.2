"""HUD compacto e controles essenciais da corrida em tempo real."""

import tkinter as tk
from collections.abc import Callable

from partida import Partida
from ui.avatares import Avatar, cor_avatar
from ui.componentes import Botao
from ui.tema import CORES, FONTE


def formatar_tempo(tempo_ms: float | None) -> str:
    if tempo_ms is None:
        return "--:--.-"
    total_segundos = max(tempo_ms, 0) / 1000
    minutos = int(total_segundos // 60)
    segundos = total_segundos % 60
    return f"{minutos:02d}:{segundos:04.1f}"


class HUDCompacto(tk.Frame):
    def __init__(self, parent: tk.Misc, partida: Partida) -> None:
        super().__init__(
            parent, bg=CORES["superficie"], padx=14, pady=9,
            highlightbackground=CORES["borda"], highlightthickness=1,
        )
        self.columnconfigure((0, 2), weight=1, uniform="competidores")
        self.columnconfigure(1, weight=1)
        self._jogador = self._criar_competidor(
            0, "Jogador", "VOCÊ", CORES["jogador"]
        )
        self._centro = self._criar_cronometro(partida)
        self._robo = self._criar_competidor(
            2,
            partida.adversario.value,
            partida.adversario.value.upper(),
            cor_avatar(partida.adversario),
        )
        self.atualizar(partida)

    def _criar_competidor(
        self, coluna: int, tipo, nome: str, cor: str
    ) -> dict[str, tk.Label]:
        frame = tk.Frame(self, bg=CORES["superficie"])
        frame.grid(row=0, column=coluna, sticky="nsew")
        Avatar(frame, tipo, tamanho=58).pack(side="left", padx=(0, 9))
        textos = tk.Frame(frame, bg=CORES["superficie"])
        textos.pack(side="left", fill="both", expand=True)
        tk.Label(
            textos, text=nome, bg=CORES["superficie"], fg=cor,
            font=(FONTE, 9, "bold"),
        ).pack(anchor="w")
        local = tk.Label(
            textos, bg=CORES["superficie"], fg=CORES["texto"],
            font=(FONTE, 9, "bold"), anchor="w",
        )
        local.pack(anchor="w", pady=(2, 0))
        detalhes = tk.Label(
            textos, bg=CORES["superficie"], fg=CORES["texto_suave"],
            font=(FONTE, 8), anchor="w",
        )
        detalhes.pack(anchor="w", pady=(2, 0))
        return {"local": local, "detalhes": detalhes}

    def _criar_cronometro(self, partida: Partida) -> dict[str, tk.Label]:
        frame = tk.Frame(self, bg="#10192A", padx=20, pady=8)
        frame.grid(row=0, column=1, padx=16, sticky="nsew")
        tk.Label(
            frame, text="CRONÔMETRO", bg="#10192A", fg=CORES["texto_suave"],
            font=(FONTE, 8, "bold"),
        ).pack()
        tempo = tk.Label(
            frame, bg="#10192A", fg=CORES["caminho"],
            font=(FONTE, 18, "bold"),
        )
        tempo.pack()
        destino = partida.mapa.obter_vertice(partida.mapa.destino)
        tk.Label(
            frame, text=f"DESTINO · {destino.nome}", bg="#10192A",
            fg=CORES["destino"], font=(FONTE, 8, "bold"),
        ).pack()
        return {"tempo": tempo}

    def atualizar(self, partida: Partida) -> None:
        estado = partida.estado
        jogador = estado.jogador
        algoritmo = estado.algoritmo

        if jogador.movimento is not None:
            destino_jogador = partida.mapa.obter_vertice(jogador.movimento.destino)
            local_jogador = f"Indo para {destino_jogador.nome}"
        else:
            local_jogador = partida.mapa.obter_vertice(jogador.local_atual).nome
        self._jogador["local"].configure(text=local_jogador)
        self._jogador["detalhes"].configure(
            text=f"{jogador.movimentos} movimentos · custo {jogador.custo}"
        )

        if algoritmo.movimento is not None:
            destino_robo = partida.mapa.obter_vertice(algoritmo.movimento.destino)
            local_robo = f"Indo para {destino_robo.nome}"
        else:
            local_robo = estado.fase_robo.value
        self._robo["local"].configure(text=local_robo)
        self._robo["detalhes"].configure(
            text=f"{algoritmo.nos_analisados} nós vistos · custo {algoritmo.custo}"
        )
        self._centro["tempo"].configure(
            text=formatar_tempo(estado.tempo_decorrido_ms)
        )


class ControlesMovimento(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        partida: Partida,
        mover: Callable[[int], None],
    ) -> None:
        super().__init__(
            parent, bg=CORES["superficie"], padx=14, pady=9,
            highlightbackground=CORES["borda"], highlightthickness=1,
        )
        self._mover = mover
        self._assinatura: tuple[object, ...] | None = None
        self._texto = tk.Label(
            self, bg=CORES["superficie"], fg=CORES["texto"],
            font=(FONTE, 9, "bold"), anchor="w",
        )
        self._texto.pack(anchor="w")
        self._opcoes = tk.Frame(self, bg=CORES["superficie"])
        self._opcoes.pack(fill="x", pady=(6, 0))
        self.atualizar(partida)

    def atualizar(self, partida: Partida) -> None:
        jogador = partida.estado.jogador
        movimento = jogador.movimento
        assinatura = (
            partida.estado.concluida,
            jogador.local_atual,
            None if movimento is None else movimento.destino,
            None if movimento is None else int(movimento.progresso * 10),
        )
        if assinatura == self._assinatura:
            return
        self._assinatura = assinatura
        for filho in self._opcoes.winfo_children():
            filho.destroy()
        if partida.estado.concluida:
            self._texto.configure(text="Corrida encerrada")
            return
        if jogador.movimento is not None:
            destino = partida.mapa.obter_vertice(jogador.movimento.destino)
            self._texto.configure(
                text=f"Você está atravessando o caminho até {destino.nome}..."
            )
            progresso = int(jogador.movimento.progresso * 100)
            tk.Label(
                self._opcoes, text=f"Em movimento · {progresso}%",
                bg=CORES["superficie"], fg=CORES["jogador"],
                font=(FONTE, 9, "bold"),
            ).pack(side="left")
            return

        atual = partida.mapa.obter_vertice(jogador.local_atual)
        self._texto.configure(
            text=f"Você está em {atual.nome} · escolha o próximo local (você também pode voltar):"
        )
        for destino in partida.destinos_disponiveis():
            aresta = partida.mapa.obter_aresta(
                atual.identificador, destino.identificador
            )
            Botao(
                self._opcoes,
                f"{destino.nome}  ·  {aresta.terreno.nome} {aresta.peso}",
                lambda item=destino.identificador: self._mover(item),
                padx=11,
                pady=7,
                font=(FONTE, 8, "bold"),
            ).pack(side="left", padx=(0, 6))


class ResultadoTempo(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        jogar_novamente: Callable[[], None],
        sair: Callable[[], None],
    ) -> None:
        super().__init__(
            parent, bg=CORES["superficie"], padx=28, pady=22,
            highlightbackground=CORES["caminho"], highlightthickness=3,
        )
        self._titulo = tk.Label(
            self, bg=CORES["superficie"], fg=CORES["caminho"],
            font=(FONTE, 20, "bold"),
        )
        self._titulo.pack()
        self._placar = tk.Label(
            self, bg=CORES["superficie"], fg=CORES["texto"],
            font=(FONTE, 10), justify="left",
        )
        self._placar.pack(pady=14)
        self._conclusao = tk.Label(
            self, bg=CORES["superficie_clara"], fg=CORES["texto_suave"],
            font=(FONTE, 9), wraplength=560, justify="left", padx=14, pady=11,
        )
        self._conclusao.pack(fill="x", pady=(0, 16))
        botoes = tk.Frame(self, bg=CORES["superficie"])
        botoes.pack()
        Botao(botoes, "Jogar novamente", jogar_novamente, destaque=True).pack(
            side="left", padx=4
        )
        Botao(botoes, "Trocar adversário", sair).pack(side="left", padx=4)

    def mostrar(self, partida: Partida) -> None:
        estado = partida.estado
        titulo = {
            "jogador": "Você chegou primeiro!",
            "algoritmo": f"{partida.adversario.value} chegou primeiro!",
            "empate": "Empate na chegada!",
        }.get(estado.vencedor, "Corrida encerrada")
        jogador_tempo = formatar_tempo(estado.jogador.tempo_chegada_ms)
        robo_tempo = formatar_tempo(estado.algoritmo.tempo_chegada_ms)
        rota = partida.resultado_algoritmo
        self._titulo.configure(text=titulo)
        self._placar.configure(
            text=(
                f"VOCÊ · tempo {jogador_tempo} · {estado.jogador.movimentos} movimentos "
                f"· custo {estado.jogador.custo}\n"
                f"{partida.adversario.value.upper()} · tempo {robo_tempo} · "
                f"rota calculada com {rota.distancia} movimentos · custo {rota.custo_total}"
                f" · {estado.algoritmo.nos_analisados} nós analisados"
            )
        )
        self._conclusao.configure(
            text=(
                f"{partida.conclusao_tecnica()}\n\n"
                f"{partida.explicacao_educacional()}"
            )
        )
        self.place(relx=0.5, rely=0.52, anchor="center", relwidth=0.62)
        self.lift()

    def ocultar(self) -> None:
        self.place_forget()
