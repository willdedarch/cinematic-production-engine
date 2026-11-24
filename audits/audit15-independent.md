# Revisão independente da candidata CPE 1.5

Verificação local da árvore de trabalho `work/cpe-1.5.0`, baseada no commit `9b55e5ad25dc17fabc4c750a1381712c1e903a34` com alterações corretivas ainda em desenvolvimento. A auditoria partiu dos defeitos reproduzidos na tag 1.4.1 e testou entradas adaptadas à candidata. A revisão não alterou o checkout, ambiente de instalação, GitHub ou Google Sheets.

## Correções verificadas

| Caminho | Evidência observada | Alcance |
| --- | --- | --- |
| Continuidade entre planos | Omissão de cantil e tampa em nova revisão de SH06 passou de zero alertas para dois `MISSING_ENTRY`. O handoff estruturado exige os fatos de entrada no primeiro beat e de saída no último. | Validação de estado estruturado. A ação escrita em linguagem natural e o resultado encenado permanecem questões de QC. |
| Retorno e versão do pacote | Confirmada recusa do pacote em outra planilha, mesmo com registros iguais. Uma cópia que passou por JSON canônico conserva o mesmo hash e recebe o mesmo diagnóstico de desvio de duração que o pacote original. | O hash verifica identidade e consistência do documento. Ele não certifica execução passada por um provedor ou direitos de uma mídia. |
| Proveniência e desvio | A versão intermediária aceitou declarar `BOUND_RETURN/SPEC_CHECKED` em uma decisão preparada por via genérica com dois hashes ficcionais. A candidata recomposta rejeitou a declaração. O contrato atual só admite rótulo declarativo com hash de mídia coerente e rechecagem dos bytes antes da tentativa de gravação. | O retorno de mídia conhecido mantém QC artístico pendente. Importação sem pacote permanece identificada como legado, sem vínculo comprovado. |
| Vínculo A/B | Mensagem da mesa contém ID e fingerprint completos. Regressão corrigida força nova apresentação e ordem inversa e rejeita escolha ligada ao fingerprint antigo. | Testes exercitam serialização e resolução do backend com dados locais. Não substituem julgamento no chat ou reprodução em browser. |
| Origem do feedback | `cpe feedback-metrics` ignorou uma referência fictícia de mensagem em `confirmed_messages`, respondeu `real_human_n=0` e origem não verificada pelo CLI. O mesmo feedback DRAFT não entrou em `task`. | Uma referência de planilha, uma asserção do chamador e um voto confirmado pelo host são classes distintas. Saídas de interface de programação baixa não autenticam a origem por si mesmas. |
| Alvo TEST | `cpe judge` sem `--include-test` escrevia pacote para TAKE-06 de ensaio. Após ajuste, terminou com código 1 e nenhum pacote. | É controle do modo CLI com cópia da planilha. |
| Hook de encerramento | `SessionEnd` com arquivo ocupando a pasta de recibos terminou com código 1, stderr e stdout vazio. A versão anterior respondia com um `deny` de PreToolUse. | Chamada direta em stdin e filesystem temporário. Despacho nativo em ambiente autorizado permanece verificação independente. |
| Scanner de distribuição | O marcador sintético de planilha foi identificado em UTF-16 e dentro de XLSX. | O scanner permanece uma verificação de padrões e formatos suportados. |

Foram observados **324/324 testes Python locais** no estado da candidata durante esta revisão e **74/74 verificações de JavaScript** da mesa, dos painéis e do comparador em simuladores de DOM, armazenamento ou relógio de mídia. Uma execução anterior falhou porque o novo teste esperava que inverter a entrada de uma apresentação idempotente criasse outra sessão. O novo cenário usou uma referência de apresentação diferente e uma ordem de reprodução controlada. Os totais precisam ser aferidos novamente na árvore final e no ZIP extraído.

## Limites e pendências

- O scanner ainda ignora a amostra sintética UTF-16 BE sem BOM com prefixo longo de caracteres sem byte nulo. A heurística observa somente os primeiros 512 bytes. A inspeção manual e os formatos de exportação previstos continuam importantes para a distribuição. O scanner de distribuição não consulta objetos antigos acessíveis no GitHub.
- A revisão verificou o diagnóstico de duração com arquivo didático disponível. Ela não mede performance, impacto narrativo, sincronia percebida, resposta do público, qualidade de uma geração definitiva ou melhoria transversal entre gêneros.
- O CLI não autenticou mensagens de produção nesta revisão. A existência de código para armazenar decisões não demonstra que alguém aceitou uma imagem, uma cena ou um resultado do laboratório.
- A auditora local não usou uma conexão de Sheets, acionou hooks nativos, abriu um navegador ou reaprovou material artístico. A escrita autorizada com releitura, ativação de hooks, percurso real em navegador e limpeza do histórico externo exigem evidências próprias.

O reprodutor `audit15-independent-probe.py` cria cópias temporárias e usa exclusivamente mídia didática do repositório. Ele cobre o retorno do pacote, a troca de planilha, a declaração incoerente de origem, omissão de continuidade, os formatos do scanner, o evento de encerramento e as fronteiras de feedback/teste no CLI.
