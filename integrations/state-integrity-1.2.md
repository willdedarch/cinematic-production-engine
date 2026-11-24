# Aprovação de uma versão

Antes de pedir a aprovação de uma etapa criativa, salve na etapa a lista de entregas em `deliverable_ref`. Para uma entrega, basta o ID exato. Para várias, use uma lista JSON como `["ROT-01","ROT-02"]`. Rascunhos e pareceres pertencem ao mesmo projeto e episódio. O diretor recebe os IDs, as revisões e a evidência que pode examinar. A autorização chega por uma nova mensagem.

`cpe prepare --snapshot LEITURA --input INTENCAO --review PARECER --workspace PASTA` aceita um parecer ou uma lista de pareceres, um por entrega. O parecer contém o ID e a revisão do alvo, o SHA-256 dos bytes e a impressão da linha completa em `target.record_sha256`. Para mídia externa, registre a versão e seu hash em Artifact Registry. Um arquivo local usado diretamente em Characters, Props, Locations ou Screenplays precisa corresponder ao caminho da linha e ao conteúdo que foi examinado. Um roteiro ou prompt inline pode ter o hash UTF-8 do texto. A leitura também aceita o hash da representação JSON daquele mesmo texto, usado nas versões anteriores.

O plano inclui em `deliverable_ref` um manifesto `cpe-deliveries-1` com tabela, ID, revisão, hash da linha e hash do material de cada entrega. É essa versão que a autorização cobre. Para promover um item de uma etapa aprovada anteriormente com referência livre, reabra a etapa, identifique as entregas e peça revisão e autorização. Decisões antigas continuam legíveis.

## Observação antes de aprovar

O checklist mantém a distinção entre planejamento e observação. Os itens abaixo exigem `observed` em uma nova aprovação, além da evidência.

| Etapa | Itens que exigem observação |
| --- | --- |
| G7 | 3 |
| G8 | 4 |
| G9 | 3 |
| G11 | 1, 2 e 3 |
| G12 | 1 e 2 |
| G13 | 3 |
| G14 | 1 a 4 |

Em G14, cada item traz, em `evidence`, um objeto JSON com a observação concreta, uma referência acessível e os alvos examinados. Exemplo de estrutura, substituindo os valores pelos da produção:

```json
{"observation":"A pausa permanece audível antes da fala.","evidence_ref":"Corte B, 00:04.200","targets":[{"id":"CORTE-B","revision":2,"sha256":"<SHA-256 real da mídia>"}]}
```

Todas as entregas precisam aparecer pelo menos uma vez. Cada item precisa de uma observação adequada ao seu critério. A pessoa que revisa continua responsável por assistir, ouvir ou ler o material. Alterar a evidência de uma etapa encerrada requer reabertura.

## Releitura, histórico e interrupção

Na interação com o agente, o conector existente lê o estado completo. Depois da autorização, prepare o plano, registre `PREPARED`, releia a planilha e execute `cpe prewrite --snapshot LEITURA --plan PLANO --workspace PASTA`. Esse passo confere a operação preparada, a integridade das linhas já conhecidas e outras preparações abertas que atinjam o mesmo registro. Após a escrita, releia os dados. Registre `CONFIRMED` e releia o histórico completo para emitir um recibo. O intervalo entre a verificação e a escrita ainda permite concorrência. Sem nova interação, o agente não recebe alterações.

O journal mantém os dois formatos 1.1 e aceita partes ordenáveis da representação JSON em UTF-8/base64, com SHA-256 total, quando até uma alteração individual ocupa várias células. Cada parte usa no máximo 44.000 unidades UTF-16. Um campo de negócio com mais de 50.000 unidades exige documento versionado ou divisão editorial antes da gravação. Uma parte faltante ou alterada impede a confirmação.

Depois de um incidente, `python scripts/shared_state.py inspect-incident LEITURA --plan PLANO` mostra a leitura efetiva de cada alvo e sua impressão conjunta. Se o diretor decidir manter precisamente essas versões, use `retain-readback LEITURA --plan PLANO --intent DECISAO` no mesmo programa. A decisão informa `decision=KEPT_OBSERVED_STATE`, `authorized=true`, `actor`, `at`, `user_message_ref`, `reason` e `observed_targets_sha256`. A saída propõe uma linha de encerramento no histórico. Releia imediatamente os alvos e a proposta antes de anexar pelo conector, depois releia a linha e compare seus campos. Essa escolha preserva a leitura autorizada. Uma correção posterior usa nova operação e nova autorização. A operação interrompida permanece no histórico com o seu resultado original.

## Reparo de plano

O pacote manual ordena os anexos pelos campos de mídia declarados pelo adaptador. Para associar duas referências ao mesmo campo, informe posições positivas e distintas em `position` de cada vínculo, ou passe `reference_order` na entrega, por exemplo `{"image_references":["REF-COMPOSICAO","REF-FIGURINO"]}`. O pacote lista o ID do anexo, a posição dentro do campo, o arquivo, a revisão e o hash. Reordenar linhas da planilha preserva essa sequência.

Primeiro, `shot-impact` recebe `shot_id` e `field` e devolve os vínculos com suas versões. O pedido de `shot-repair` repete esse resultado em `impact`, informa em `pins` a referência entregue pelo cartão para cada registro atual ou predecessor e em `fields` os nomes das colunas de conteúdo autorizadas por ID de destino. `changes` lista tabela, ID, revisão esperada e valores. Para um estado como `cantil`, altere somente esse atributo dentro de `start_end_state`. Para um sucessor, informe o ID predecessor, a nova versão, projeto, episódio, marcador de teste e estado de rascunho ou revisão. Campos omitidos herdam a versão anterior. Se um vínculo mudou, releia o cartão e reavalie o impacto antes de prosseguir.
