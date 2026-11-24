# Benchmarks de julgamento CPE 1.5

A rodada exploratória verificou três pares de texto em duas ordens. O mesmo parecerista preferiu o reparo de *A linha azul* e de *O intervalo* e manteve empate em *Farinha na dobra*. O código preservou as ordens, as alternativas e os pareceres. A leitura é descritiva e tem zero decisões humanas. O [registro de execução](results-1.5.json) contém entradas, hashes, rubricas, votos e consolidações.

## Releitura da comparação 1.4

A [comparação publicada](../examples/benchmark14/README.md) usou um briefing, quatro variantes e dois críticos com contextos próprios documentados, da mesma família de modelo. A crítica A recebeu B17, F62, R94 e W38 nessa ordem. A crítica B recebeu W38, R94, F62 e B17. Recalculei os hashes e comprimentos documentados. Os quatro hashes correspondem, com 1.342, 1.212, 1.144 e 1.084 palavras, respectivamente.

| Par | Crítica A | Crítica B |
| --- | --- | --- |
| B17 / F62 | F62 | F62 |
| B17 / R94 | R94 | R94 |
| B17 / W38 | W38 | W38 |
| F62 / R94 | R94 | F62 |
| F62 / W38 | W38 | F62 |
| R94 / W38 | Empate | R94 |

A concordância descritiva foi de três dos seis pares, concentrada nos confrontos com B17. Os dois críticos localizaram a lacuna da tigela na ação final do controle. A preferiu a renúncia de Berta em R94 e valorizou a cooperação de W38. B preferiu a continuidade do espaço e das tarefas de F62, que recebeu métodos da CPE sem revisão de julgamento. Os seis pares combinam os mesmos quatro textos e um só briefing, portanto não são réplicas independentes.

Identidade do crítico e ordem de apresentação variaram juntas. Um único texto por condição, tamanhos distintos, exposição adicional a rubricas e ausência de orçamento de tokens pareado impedem atribuição causal. O feedback de W38 era negativo e vinha de outro estudo. O arquivo público não contém essa entrada particular, impedindo replicação integral dessa condição. Não houve decisão humana sobre os quatro roteiros. Os primeiros ensaios com contexto herdado ficam excluídos conforme o registro histórico. A hipótese de que métodos ajudaram naquele brief é compatível com a falha comum que os críticos detectaram. Benefício adicional do Judgment Engine e efeito do feedback permanecem inconclusivos.

As fichas de [comédia e documentário da 1.4.1](../examples/benchmark141/README.md) registram revisões cumulativas por gênero e limites do mesmo autor em contexto partilhado. Elas ajudam a examinar alterações localizadas, sem servir como comparativo controlado. Reexecutei também a consolidação do par histórico MAT-71/MAT-84 com os votos registrados. O resultado voltou MAT-84, com base humana zero no registro histórico e sem taxa de viés de posição.

## Rodada 1.5 com três briefings

Usei os recortes já registrados em [Revisão do piloto e estudos contrastivos](../examples/pilot15/revisao-e-estudos.md), sem reescrever versões. Em *A linha azul*, as duas células são o recorte R0 e o reparo R1 da mesma passagem entre SH05 e SH06. Nos outros dois casos, o texto é a concatenação do tempo e da célula da variante em cada uma das três linhas. A primeira ordem preserva Antes → Reparo. A segunda é a inversão feita pelo código. A documentação de reparo já estava visível ao parecerista e os recortes remetem ao original. Rótulos A/B permitem verificar a consolidação, sem estabelecer cegamento.

Usei `rubric` para selecionar a escala pertinente e `blind_packets` para empacotar cada par. `consolidate` converteu as escolhas A/B para a versão original e preservou empate e ordem. `metrics([])` confirmou denominadores humanos vazios. Um único parecerista da sessão Codex/GPT avaliou as duas ordens de cada caso. O identificador exato do modelo e o orçamento de contexto em tokens não estão disponíveis. As entradas textuais foram congeladas, com extensão e hashes disponíveis no registro. As decisões do piloto permanecem autorais e não entraram como rótulo humano.

| Brief e rubrica | Palavras R0 / R1 | Ordem original / invertida | Observação editorial | Pendente |
| --- | --- | --- | --- | --- |
| A linha azul · ação coletiva em guerra · RUB-CONTINUITY | 29 / 46 | B / A, R1 | O R0 pula do apoio para a frente da fila já alinhada. O R1 marca a percepção de Bento, o início do giro e o fim da curva no mesmo eixo. É um reparo de ligação escrita, com possibilidade de manter a desorientação pretendida. | Visibilidade das ações concorrentes, execução dos oito segundos, contato, eixo e som no trecho realizado. |
| O intervalo · suspense psicológico · RUB-SUSPENSE | 58 / 64 | B / A, R1 | Retirar a pergunta e deslocar a segunda batida depois da parada reduzem a associação explícita entre fala e resposta. O roteiro preserva o som lateral e a mão suspensa. Duas variáveis mudam no mesmo recorte. | Escuta e suspense percebido. Uma rodada nova deveria alterar separadamente o instante da batida e a presença da fala. |
| Farinha na dobra · drama emocional · RUB-DIALOGUE | 68 / 53 | Empate / empate | O pedido de desculpa pode mostrar a iniciativa de Rui; o silêncio faz o gesto carregar a decisão. A rubrica pede função da fala, e as duas versões preservam a ação de refazer a dobra. A indicação de respiração também muda no registro do reparo. | Identificar em atuação se o dedo, a respiração e a abertura de espaço fazem a mudança legível. |

As três consolidações permaneceram iguais na ordem inversa. Isso documenta estabilidade no mesmo contexto e com o resultado anterior acessível. Viés de posição em contextos frescos, divergência entre avaliadores, originalidade percebida, melhora geral e efeito audiovisual ficam sem medição. Os três recortes testam continuidade, distribuição de informação e a função da fala. A rodada não repete as quatro condições de escrita, nem oferece amostras de casting, fotografia, locação e prompt sob controle equivalente.

## Reprodução local

Execute na raiz do pacote com Python 3.10 ou superior. O trecho confere o arquivo-fonte, a implementação, as rubricas, as quatro variantes históricas, as permutações, os hashes de textos e a consolidação. É um teste do registro e do código de comparação. Um novo parecer editorial exige um avaliador e contexto próprios.

```python
import hashlib
import json
from pathlib import Path

from scripts import judgment

report = json.loads(Path("benchmarks/results-1.5.json").read_text(encoding="utf-8"))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

assert sha(report["script"]["path"]) == report["script"]["sha256"]
assert sha(report["inputs"]["path"]) == report["inputs"]["sha256"]
assert sha(report["inputs"]["rubrics_path"]) == report["inputs"]["rubrics_sha256"]

for material, evidence in report["legacy14"]["word_counts_and_hashes"].items():
    assert sha(f"examples/benchmark14/{material}.txt") == evidence["expected"]

for case in report["cases"]:
    session = case["packet_session"]
    first, second = session["public_packets"]
    assert [item["text"] for item in first["alternatives"]] == [
        item["text"] for item in reversed(second["alternatives"])
    ]
    for packet in session["public_packets"]:
        mapping = session["private_mapping"][packet["packet_id"]]
        for item in packet["alternatives"]:
            assert judgment.digest(item["text"]) == session["source_hashes"][mapping[item["label"]]]
    assert judgment.digest(judgment.rubric(case["department"])) == case["rubric_sha256"]
    assert judgment.consolidate(session, case["reviews"]) == case["consolidation"]

assert judgment.metrics([]) == report["experimental"]["human_metrics"]
```

## Próxima comparação controlada

Separe casos de calibração e avaliação antes de gerar textos. Use briefings reservados e mantenha constantes a entrega, os critérios, os materiais de entrada e o orçamento por condição. Registre os textos antes e depois da crítica. Inclua um passe de revisão com o mesmo orçamento, sem Judgment, para distinguir revisão adicional e efeito do protocolo. Distribua aleatoriamente ordens a críticos em contextos sem acesso ao mapa ou aos ensaios anteriores. Preserve julgamentos discordantes, empates, trechos frágeis e reparos que prejudiquem originalidade. Para um critério que depende de execução, teste com o meio correspondente. Taxas humanas dependem de decisões reais, identificadas e autorizadas.
