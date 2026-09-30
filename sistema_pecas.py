"""
Sistema de Controle de Produção e Qualidade de Peças
=====================================================

Protótipo de automação digital para inspeção de peças em linha de
montagem industrial. Avalia automaticamente a qualidade de cada peça,
organiza as peças aprovadas em caixas de capacidade limitada e gera
relatórios consolidados de produção.

Critérios de aprovação:
    - Peso entre 95g e 105g (inclusive)
    - Cor azul ou verde
    - Comprimento entre 10cm e 20cm (inclusive)

Autor: Protótipo acadêmico - Algoritmos e Lógica de Programação
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constantes de configuração (regras de negócio centralizadas)
# ---------------------------------------------------------------------------

PESO_MINIMO = 95.0
PESO_MAXIMO = 105.0
CORES_APROVADAS = {"azul", "verde"}
COMPRIMENTO_MINIMO = 10.0
COMPRIMENTO_MAXIMO = 20.0
CAPACIDADE_CAIXA = 10


# ---------------------------------------------------------------------------
# Modelos de dados
# ---------------------------------------------------------------------------

@dataclass
class Peca:
    """Representa uma peça cadastrada no sistema."""
    id: str
    peso: float
    cor: str
    comprimento: float
    aprovada: bool = field(init=False)
    motivos_reprovacao: List[str] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.motivos_reprovacao = self._avaliar()
        self.aprovada = len(self.motivos_reprovacao) == 0

    def _avaliar(self) -> List[str]:
        """Aplica as regras de qualidade e retorna a lista de motivos de
        reprovação (vazia se a peça for aprovada)."""
        motivos = []

        if not (PESO_MINIMO <= self.peso <= PESO_MAXIMO):
            motivos.append(
                f"Peso fora do padrão ({self.peso}g; esperado entre "
                f"{PESO_MINIMO}g e {PESO_MAXIMO}g)"
            )

        if self.cor.strip().lower() not in CORES_APROVADAS:
            motivos.append(
                f"Cor não aceita ({self.cor}; esperado azul ou verde)"
            )

        if not (COMPRIMENTO_MINIMO <= self.comprimento <= COMPRIMENTO_MAXIMO):
            motivos.append(
                f"Comprimento fora do padrão ({self.comprimento}cm; "
                f"esperado entre {COMPRIMENTO_MINIMO}cm e {COMPRIMENTO_MAXIMO}cm)"
            )

        return motivos

    def __str__(self):
        status = "APROVADA" if self.aprovada else "REPROVADA"
        base = (f"[{self.id}] peso={self.peso}g, cor={self.cor}, "
                f"comprimento={self.comprimento}cm -> {status}")
        if not self.aprovada:
            base += " | Motivo(s): " + "; ".join(self.motivos_reprovacao)
        return base


class Caixa:
    """Representa uma caixa de armazenamento de peças aprovadas."""

    def __init__(self, numero: int, capacidade: int = CAPACIDADE_CAIXA):
        self.numero = numero
        self.capacidade = capacidade
        self.pecas: List[Peca] = []
        self.fechada = False

    def adicionar(self, peca: Peca) -> bool:
        """Tenta adicionar uma peça à caixa. Retorna False se a caixa já
        estiver cheia (fechada)."""
        if self.fechada:
            return False
        self.pecas.append(peca)
        if len(self.pecas) >= self.capacidade:
            self.fechada = True
        return True

    def __str__(self):
        estado = "FECHADA" if self.fechada else "EM USO"
        ids = ", ".join(p.id for p in self.pecas)
        return (f"Caixa #{self.numero} [{estado}] - "
                f"{len(self.pecas)}/{self.capacidade} peças ({ids})")


# ---------------------------------------------------------------------------
# Sistema principal
# ---------------------------------------------------------------------------

class SistemaControleQualidade:
    """Orquestra o cadastro de peças, a organização em caixas e a geração
    de relatórios."""

    def __init__(self, capacidade_caixa: int = CAPACIDADE_CAIXA):
        self.capacidade_caixa = capacidade_caixa
        self.pecas: List[Peca] = []
        self.caixas: List[Caixa] = [Caixa(1, capacidade_caixa)]

    # -- Cadastro -----------------------------------------------------

    def cadastrar_peca(self, id_peca: str, peso: float, cor: str,
                        comprimento: float) -> Peca:
        if any(p.id == id_peca for p in self.pecas):
            raise ValueError(f"Já existe uma peça cadastrada com o id '{id_peca}'.")

        peca = Peca(id=id_peca, peso=peso, cor=cor, comprimento=comprimento)
        self.pecas.append(peca)

        if peca.aprovada:
            self._armazenar_em_caixa(peca)

        return peca

    def _armazenar_em_caixa(self, peca: Peca) -> None:
        caixa_atual = self.caixas[-1]
        if not caixa_atual.adicionar(peca):
            # Caixa atual já fechada por alguma razão: cria nova
            nova_caixa = Caixa(len(self.caixas) + 1, self.capacidade_caixa)
            nova_caixa.adicionar(peca)
            self.caixas.append(nova_caixa)
        elif caixa_atual.fechada:
            # A peça que acabou de entrar fechou a caixa: já prepara a próxima
            self.caixas.append(Caixa(len(self.caixas) + 1, self.capacidade_caixa))

    # -- Consultas ------------------------------------------------------

    def listar_aprovadas(self) -> List[Peca]:
        return [p for p in self.pecas if p.aprovada]

    def listar_reprovadas(self) -> List[Peca]:
        return [p for p in self.pecas if not p.aprovada]

    def buscar_peca(self, id_peca: str) -> Optional[Peca]:
        for p in self.pecas:
            if p.id == id_peca:
                return p
        return None

    def listar_caixas_fechadas(self) -> List[Caixa]:
        return [c for c in self.caixas if c.fechada]

    # -- Remoção ----------------------------------------------------------

    def remover_peca(self, id_peca: str) -> bool:
        """Remove uma peça cadastrada pelo id. Peças aprovadas só podem ser
        removidas se ainda estiverem em uma caixa aberta (para preservar a
        integridade de caixas já fechadas)."""
        peca = self.buscar_peca(id_peca)
        if peca is None:
            return False

        if peca.aprovada:
            for caixa in self.caixas:
                if peca in caixa.pecas:
                    if caixa.fechada:
                        raise ValueError(
                            "Não é possível remover: a peça já está em uma "
                            "caixa fechada."
                        )
                    caixa.pecas.remove(peca)
                    break

        self.pecas.remove(peca)
        return True

    # -- Relatório --------------------------------------------------------

    def gerar_relatorio(self) -> str:
        aprovadas = self.listar_aprovadas()
        reprovadas = self.listar_reprovadas()
        caixas_usadas = [c for c in self.caixas if len(c.pecas) > 0]

        # Consolida motivos de reprovação
        contagem_motivos = {}
        for p in reprovadas:
            for motivo in p.motivos_reprovacao:
                chave = motivo.split(" (")[0]  # agrupa por tipo de motivo
                contagem_motivos[chave] = contagem_motivos.get(chave, 0) + 1

        linhas = []
        linhas.append("=" * 60)
        linhas.append("RELATÓRIO CONSOLIDADO DE PRODUÇÃO")
        linhas.append("=" * 60)
        linhas.append(f"Total de peças cadastradas : {len(self.pecas)}")
        linhas.append(f"Total de peças aprovadas   : {len(aprovadas)}")
        linhas.append(f"Total de peças reprovadas  : {len(reprovadas)}")
        linhas.append("")

        if contagem_motivos:
            linhas.append("Motivos de reprovação:")
            for motivo, qtd in contagem_motivos.items():
                linhas.append(f"  - {motivo}: {qtd} ocorrência(s)")
        else:
            linhas.append("Motivos de reprovação: nenhuma peça reprovada.")

        linhas.append("")
        linhas.append(f"Caixas utilizadas (com ao menos 1 peça): {len(caixas_usadas)}")
        for caixa in caixas_usadas:
            linhas.append(f"  - {caixa}")
        linhas.append("=" * 60)

        return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Interface de linha de comando (menu interativo)
# ---------------------------------------------------------------------------

def ler_float(mensagem: str) -> float:
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            print("  Valor inválido. Digite um número (ex.: 98.5).")


def menu_cadastrar(sistema: SistemaControleQualidade) -> None:
    print("\n--- Cadastro de nova peça ---")
    id_peca = input("ID da peça: ").strip()
    if not id_peca:
        print("  ID não pode ser vazio.")
        return
    peso = ler_float("Peso (g): ")
    cor = input("Cor (azul/verde/outra): ").strip()
    comprimento = ler_float("Comprimento (cm): ")

    try:
        peca = sistema.cadastrar_peca(id_peca, peso, cor, comprimento)
    except ValueError as erro:
        print(f"  Erro: {erro}")
        return

    print(f"  Resultado: {peca}")


def menu_listar(sistema: SistemaControleQualidade) -> None:
    print("\n--- Peças aprovadas ---")
    aprovadas = sistema.listar_aprovadas()
    if not aprovadas:
        print("  Nenhuma peça aprovada até o momento.")
    for p in aprovadas:
        print(f"  {p}")

    print("\n--- Peças reprovadas ---")
    reprovadas = sistema.listar_reprovadas()
    if not reprovadas:
        print("  Nenhuma peça reprovada até o momento.")
    for p in reprovadas:
        print(f"  {p}")


def menu_remover(sistema: SistemaControleQualidade) -> None:
    print("\n--- Remover peça cadastrada ---")
    id_peca = input("ID da peça a remover: ").strip()
    try:
        removida = sistema.remover_peca(id_peca)
    except ValueError as erro:
        print(f"  Erro: {erro}")
        return

    if removida:
        print(f"  Peça '{id_peca}' removida com sucesso.")
    else:
        print(f"  Nenhuma peça encontrada com o id '{id_peca}'.")


def menu_caixas_fechadas(sistema: SistemaControleQualidade) -> None:
    print("\n--- Caixas fechadas ---")
    fechadas = sistema.listar_caixas_fechadas()
    if not fechadas:
        print("  Nenhuma caixa fechada até o momento.")
    for c in fechadas:
        print(f"  {c}")


def menu_relatorio(sistema: SistemaControleQualidade) -> None:
    print()
    print(sistema.gerar_relatorio())


def exibir_menu() -> None:
    print("\n===== SISTEMA DE CONTROLE DE QUALIDADE =====")
    print("1. Cadastrar nova peça")
    print("2. Listar peças aprovadas/reprovadas")
    print("3. Remover peça cadastrada")
    print("4. Listar caixas fechadas")
    print("5. Gerar relatório final")
    print("0. Sair")


def main() -> None:
    sistema = SistemaControleQualidade()

    opcoes = {
        "1": menu_cadastrar,
        "2": menu_listar,
        "3": menu_remover,
        "4": menu_caixas_fechadas,
        "5": menu_relatorio,
    }

    while True:
        exibir_menu()
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando o sistema. Até logo!")
            break

        acao = opcoes.get(escolha)
        if acao is None:
            print("  Opção inválida. Tente novamente.")
            continue

        acao(sistema)


if __name__ == "__main__":
    main()
