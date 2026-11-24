# Revisão independente anterior ao Judgment Engine

Revisor: agente `judgment_adversarial`, distinto do autor da implementação. Data: 24/11/2026. Escopo: inspeção direta dos scripts, schemas e JavaScript atuais em `work/v3.1`; execução local de casos sintéticos em memória. Não houve escrita no Google Sheets, geração, alteração da implementação ou aprovação estética. Os achados abaixo descrevem a versão inspecionada; correções posteriores precisam de nova execução dos casos.

## Achados reproduzidos

1. **Alta — bloqueio de conhecimento não protegido.** `scripts/shared_state.py:14,143` restringe mutações de aprovados/bloqueados somente às sete tabelas de assets originais. Em memória, um registro `Techniques` com `status=LOCKED` teve `procedure` alterado por `prepare` sem erro. Referências, perfis e demais entidades novas têm os mesmos estados e a mesma lacuna. Estender a proteção aos tipos de conteúdo pertinentes, preservar a versão anterior e exigir sucessor ligado, motivo e autorização quando houver revisão. Não basta acrescentar a palavra LOCKED ao schema.

2. **Alta — aprovação vinculada a gate/episódio incorretos é aceita.** `scripts/shared_state.py:104` procura `workflow_id`, revisão, decisão e estado, mas não compara `Approvals.gate_id`, projeto e episódio exatos ao gate aprovado. Um G0 marcado APPROVED e com seus checks completos foi validado com uma aprovação que tinha `gate_id=G5` e `episode_id=''`. Conferir a identidade completa do alvo da aprovação, além do vínculo por ID e revisão. Um registro histórico da aprovação de outra versão não deve aprovar o estado atual.

3. **Alta — avaliações podem apontar para alvo inexistente e parecer aprovadas.** `schemas/shared-state.tables.json` define `Evaluation Results.target_table/target_id/target_revision` como campos sem vínculo validado. `shared_state.validate` só verifica referências polimórficas de Prompts e Continuity. Um Evaluation Results com `status=APPROVED`, tabela inexistente, ID ausente, revisão 999 e evidência vazia passou. Validar existência e escopo do entregável e a revisão exata observada. Separar conformidade técnica, julgamento artístico e decisão humana; exigir rubrica, evidência e limitações antes de qualquer recomendação de aprovação. Avaliação histórica pode apontar para versão preservada, não precisa ser silenciosamente atualizada para a mais recente.

4. **Alta — confirmação de journal não é vinculada integralmente ao plano.** `scripts/shared_state.py:188` aceita qualquer evento CONFIRMED do mesmo `op_id`. Foi aceito um evento com ator alheio, autorização vazia, `changes_json={}` e `guards_json={}`; a função retornou CONFIRMED porque o snapshot de dados coincidia com o candidato. Conferir ator, autorização, alterações, guardas e PREPARED correspondentes; se o journal divergir, manter estado de reconciliação. Essa checagem melhora integridade do recibo, mas continua sem autenticar por si só chamadas remotas ou criar atomicidade.

5. **Média — direção obrigatória de extensão aceita null.** `scripts/prompt_compiler.py:52` compara presença da chave `extension_mode` com o modo, enquanto o validador genérico aceita null quando o parâmetro é nullable no catálogo. Uma especificação Seedance `video_extension` com um vídeo e `extension_mode=null` foi compilada. Para esse modo, exigir explicitamente `forward` ou `backward`; ausência/null não satisfaz a dependência contextual. Não inventar dependências que não constam das especificações consultadas.

6. **Média — rascunhos dos painéis de apoio sobrevivem à troca de snapshot.** `panels/boards-runtime.js:2,7` mantém `supportDrafts` global por nome do painel. `panels/studio.js:57` limpa somente `drafts`, sem limpar ou separar `supportDrafts` por projeto/episódio/revisão. Após importar outro projeto, valores, alvo textual e checks anteriores podem reaparecer sob o novo escopo. Limpar os rascunhos de apoio no import ou conservá-los com chave de escopo e confirmação explícita; limpar a mensagem e autorização junto da troca. Este achado decorre do percurso direto do código; não foi validado em navegador real.

## Reproduções locais executadas

Foram usadas cópias em memória de `templates/shared-state.test-fixture.json` e linhas de `templates/library-seed.json`, com `is_test=true` e escopo do projeto de teste. A implementação original não foi editada. Resultados observados:

```text
LOCKED_KNOWLEDGE_MUTATION_ACCEPTED Changed locked content
WRONG_GATE_APPROVAL_ACCEPTED True
DANGLING_APPROVED_EVALUATION_ACCEPTED True
UNBOUND_HISTORY_CONFIRMATION_ACCEPTED CONFIRMED
NULL_REQUIRED_EXTENSION_DIRECTION_ACCEPTED {'mode': 'video_extension', 'extension_mode': None}
```

Esses resultados são evidência de aceitação indevida pelos componentes locais, não de ocorrência de corrupção na planilha real. Recomenda-se acrescentar regressões negativas para cada caso antes de concluir a etapa.

## Limites e pontos preservados

O helper de estado declara que não conecta ao Google. Um JSON com `authorized=true` ou um `user_message_ref` não comprova autorização humana por si só: o agente deve ligar a alteração à mensagem realmente recebida. O painel mantém essa explicação e encaminha escolhas por nova mensagem, sem implementar gravação direta. Não tratar isso como autenticação automática.

As guardas incluem conteúdo e membros do escopo, detectando alterações manuais sem incremento de revisão. Há proteção de assets originais, dependências, checklists e gates críticos. Readback compara o candidato e não apenas o sucesso da chamada. Esses controles são úteis, mas não demonstram isolamento entre escritores nem transação atômica, conforme a própria documentação.

Não avaliei aparência fotográfica, atuação, montagem real, retenção, eficiência dos modelos ou qualidade cinematográfica final. Exemplos didáticos e testes de código não permitem concluir excelência artística. Avaliação cega posterior deve usar rubrica, material e versão explícitos, com empate/reprovação de todas e origem do julgamento registrados.

## Reteste independente após correção

O autor corrigiu os cinco achados reproduzidos. O revisor releu o código alterado e criou `evals/test_review_regressions.py` sem modificar a implementação. Foram executados **17 testes, todos aprovados**, em 24/11/2026. Cobrem alteração de conhecimento bloqueado/aprovado, vínculo gate/episódio da aprovação, existência/revisão/escopo/evidência/rubrica/revisor da avaliação, PREPARED e CONFIRMED vinculados ao plano, corrupção de alterações/guardas e direção não nula da extensão. Há também controles positivos para evitar que as correções rejeitem fluxos válidos.

Esse reteste confirma a rejeição local dos cinco casos anteriores. O achado dos rascunhos de apoio depende de correção/reteste separado do painel. Não houve nova escrita remota ou validação em navegador.

Observação de integração enviada ao autor: avaliações históricas precisam continuar válidas quando o alvo avança de revisão; a verificação de atualidade deve ocorrer quando a avaliação é usada para aprovar o alvo, e não apagar ou invalidar o histórico. As tabelas de conhecimento precisam de ligação formal entre sucessores se a entrega declarar versionamento vinculado. Esses pontos exigem integração do motor, além dos cinco reparos locais retestados.

## Segunda revisão da integração de julgamento

O revisor inspecionou diretamente `scripts/judgment.py`, a proteção e linhagem atualizadas de `shared_state.py` e os campos do schema. O histórico aprovado de avaliações agora continua válido quando o alvo avança. A linhagem `supersedes_id` tem vínculo para a mesma tabela e rejeita ciclos. Quatro regressões adicionais exercitaram histórico aprovado, sucessor de predecessor bloqueado, predecessor ausente e ciclo; **21/21 testes independentes passaram** nessa execução. A verificação usa dados em memória e não equivale a validação de produção artística.

O painel recebeu limpeza de `supportDrafts` ao importar estado segundo o autor. A revisão independente não abriu navegador nem contornou a restrição de `file://`; a evidência de execução do painel é o teste DOM separado, não inspeção visual real.

**Novo achado reproduzido — validação causal insuficiente.** `judgment.diagnosis` aceitou um objeto com sintoma, confidence HIGH, alternatives=[''] e verification=[''], mas evidence, probable_cause, repair, risks e protected vazios; retornou `valid=True, causation_proven=False`. A ressalva de causalidade não torna esse diagnóstico útil ou fundamentado. Exigir tipos e itens significativos, evidência ou ausência explicitamente declarada, correção executável e verificação. Causa desconhecida pode ser válida como hipótese aberta; não deve parecer diagnóstico causal confirmado. Achado enviado imediatamente ao autor; correção/reteste deve ser registrada abaixo quando executada.

Cobertura real: o script valida contratos de avaliações, prepara pacotes cegos, consolida votos e limita rodadas. Ele não verifica sozinho se uma interpretação artística é verdadeira, se uma URL descreve o quadro alegado, nem autentica independência estatística dos revisores. O helper compartilhado preserva gates e aprovação humana, mas não chama o validador de julgamento diretamente em toda operação. Uma chamada orientada por workflow e uma proteção automática de execução são resultados distintos; o harness deve declarar o que efetivamente intercepta.

Métricas humanas continuam sem baseline real. O método `metrics` atual conta entradas elegíveis fornecidas, sem deduplicação de uma mesma decisão; antes de utilizá-lo com amostras reais, exigir IDs únicos ou explicitar esse denominador e evitar inflar a amostra com linhas repetidas. Não houve resultado humano afetado nesta revisão.
