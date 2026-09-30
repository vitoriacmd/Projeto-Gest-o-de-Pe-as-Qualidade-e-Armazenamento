# Sistema de Controle de Produção e Qualidade de Peças

Protótipo em Python de um sistema de automação digital para inspeção de
peças em uma linha de montagem industrial. O sistema recebe os dados de
cada peça, avalia automaticamente sua qualidade, organiza as peças
aprovadas em caixas de capacidade limitada e gera relatórios
consolidados de produção.

## Funcionamento

Cada peça cadastrada possui quatro atributos: **id**, **peso (g)**,
**cor** e **comprimento (cm)**. O sistema aplica três critérios de
qualidade para decidir se a peça é aprovada ou reprovada:

| Critério     | Regra de aprovação      |
|--------------|--------------------------|
| Peso         | Entre 95g e 105g (inclusive) |
| Cor          | Azul ou verde            |
| Comprimento  | Entre 10cm e 20cm (inclusive) |

Se qualquer critério falhar, a peça é reprovada e o(s) motivo(s) da
reprovação são registrados. Peças aprovadas são automaticamente
colocadas na caixa em uso; quando uma caixa atinge 10 peças, ela é
fechada e uma nova caixa é aberta para as próximas peças aprovadas.

O programa oferece um menu interativo em texto com as seguintes opções:

1. **Cadastrar nova peça** – solicita id, peso, cor e comprimento, avalia
   a peça e informa o resultado (aprovada/reprovada).
2. **Listar peças aprovadas/reprovadas** – exibe duas listas: peças
   aprovadas e peças reprovadas (com o motivo da reprovação).
3. **Remover peça cadastrada** – remove uma peça pelo id. Peças
   aprovadas só podem ser removidas enquanto ainda estiverem em uma
   caixa aberta (caixas fechadas são consideradas definitivas).
4. **Listar caixas fechadas** – exibe todas as caixas que já atingiram a
   capacidade máxima.
5. **Gerar relatório final** – mostra o total de peças aprovadas,
   total de reprovadas (com contagem por motivo) e a quantidade de
   caixas utilizadas.

## Como rodar o programa

**Pré-requisitos:** Python 3.8 ou superior (não há dependências
externas — apenas biblioteca padrão).

1. Baixe/clone o repositório.
2. Abra um terminal na pasta do projeto.
3. Execute:

   ```bash
   python3 sistema_pecas.py
   ```

4. Use os números do menu para navegar entre as opções. Para encerrar,
   digite `0`.

## Exemplos de entrada e saída

### Cadastro de uma peça aprovada

```
Escolha uma opção: 1

--- Cadastro de nova peça ---
ID da peça: P001
Peso (g): 100
Cor (azul/verde/outra): azul
Comprimento (cm): 15
  Resultado: [P001] peso=100.0g, cor=azul, comprimento=15.0cm -> APROVADA
```

### Cadastro de uma peça reprovada (múltiplos motivos)

```
Escolha uma opção: 1

--- Cadastro de nova peça ---
ID da peça: P002
Peso (g): 88
Cor (azul/verde/outra): amarelo
Comprimento (cm): 25
  Resultado: [P002] peso=88.0g, cor=amarelo, comprimento=25.0cm -> REPROVADA
  | Motivo(s): Peso fora do padrão (88.0g; esperado entre 95.0g e 105.0g);
  Cor não aceita (amarelo; esperado azul ou verde);
  Comprimento fora do padrão (25.0cm; esperado entre 10.0cm e 20.0cm)
```

### Relatório final

```
Escolha uma opção: 5

============================================================
RELATÓRIO CONSOLIDADO DE PRODUÇÃO
============================================================
Total de peças cadastradas : 7
Total de peças aprovadas   : 4
Total de peças reprovadas  : 3

Motivos de reprovação:
  - Peso fora do padrão: 1 ocorrência(s)
  - Cor não aceita: 1 ocorrência(s)
  - Comprimento fora do padrão: 1 ocorrência(s)

Caixas utilizadas (com ao menos 1 peça): 2
  - Caixa #1 [FECHADA] - 10/10 peças (...)
  - Caixa #2 [EM USO] - 1/10 peças (...)
============================================================
```

## Estrutura do código

- `Peca`: representa uma peça e aplica as regras de qualidade
  automaticamente no momento da criação (via `__post_init__`).
- `Caixa`: representa uma caixa de armazenamento, controlando sua
  capacidade e o momento de fechamento.
- `SistemaControleQualidade`: classe central que cadastra peças,
  distribui as aprovadas entre as caixas, permite remoção e gera o
  relatório consolidado.
- Funções `menu_*`: camada de interface (entrada/saída via terminal),
  separada da lógica de negócio para facilitar testes e manutenção.
