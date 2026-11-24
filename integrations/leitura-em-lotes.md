# Leitura da mesa pelo conector nativo

Ao receber uma mensagem sobre a produção, o agente consulta o Google Sheets na conta vinculada. O diretor pode pedir “continuar EP2” em linguagem natural. O agente prepara as cópias de trabalho em uma pasta privada e publica a mesa do episódio. O diretor só precisa recarregar a página.

## Percurso do agente

1. Confira a identidade da conta entre as conexões disponíveis no host. Use o ID atual da conexão dessa conta e o ID da planilha do vínculo. Execute `get_spreadsheet_metadata` e guarde a resposta estruturada nativa, o nome da ferramenta e o instante do retorno com fuso horário.
2. Rode `desk-read-plan` com o envelope inicial. Leia os pedidos de `batches` no arquivo indicado por `result`. Cada pedido contém os argumentos exatos para `get_spreadsheet_cells`. Os títulos são citados em A1, os limites vêm da grade e cada lote tem até cinco abas. A paginação padrão é de 1.000 linhas. A fila tem seis colunas. As tabelas de produção usam todas as colunas do schema.
3. Faça as chamadas de células pelo conector da mesma conta. Conserve o índice, os intervalos exatos, o horário e a resposta `structuredContent` de cada chamada, inclusive os blocos vazios. Lotes independentes podem ser recebidos em qualquer ordem. Em caso de truncamento, falha do conector ou ausência de um bloco, inicie nova consulta com um `page_rows` menor. Aplique o mesmo valor ao plano e à reconstrução.
4. Depois que todos os lotes retornarem, repita a consulta de metadados indicada por `after_request`. Use o horário efetivo do retorno. Para incluir um controle adicional sobre edições simultâneas, o agente pode obter o campo `version` dos metadados nativos do arquivo no Drive antes e depois dos lotes, fornecendo os dois valores como `drive_version` nos respectivos envelopes. Divergência exige uma nova leitura.
5. Rode `desk-read-copy` com as duas consultas de metadados e os lotes capturados. O arquivo `result.json` dessa execução já é o snapshot para `desk-publish`, para preparar um pedido ou para examinar uma operação. A cópia inclui endereços de linhas de origem, fila e registro de proveniência. Mantenha os retornos integrais e o snapshot na área privada do agente.

## Entradas locais

O nome `response` contém o objeto estruturado original da ferramenta. Os campos `account`, `link_id` e `observed_at` descrevem a chamada que o agente realmente fez. O campo opcional `tool` usa `get_spreadsheet_metadata` ou `get_spreadsheet_cells`.

```text
python scripts/cpe.py desk-read-plan --workspace PASTA_PRIVADA --input metadados-iniciais.json
python scripts/cpe.py desk-read-copy --workspace PASTA_PRIVADA --input leitura-completa.json
python scripts/cpe.py desk-publish --workspace PASTA_PRIVADA --snapshot CAMINHO_DO_RESULTADO --input episodio.json
```

Estrutura de `metadados-iniciais.json` no agente, em pseudocódigo:

```text
{
  before: {account, link_id, observed_at, tool, response},
  page_rows: 1000
}
```

Estrutura de `leitura-completa.json`:

```text
{
  before: {account, link_id, observed_at, tool, response},
  after:  {account, link_id, observed_at, tool, response},
  page_rows: 1000,
  batches: [
    {index, account, link_id, observed_at, tool, ranges, cell_fields: "effectiveValue", response},
    ...
  ]
}
```

O índice começa em zero. `scope` pode registrar o projeto e o episódio de trabalho. As 35 tabelas são reconstruídas antes da seleção do episódio. O agente mantém células booleanas, numéricas e textuais com seus tipos originais. Uma fórmula com erro, cabeçalho divergente, linha populada sem chave, intervalo ausente, aba substituída ou célula da fila com tipo inválido interrompe a reconstrução. As posições de linhas vazias entre páginas da fila são preservadas.

## Garantia e limite

A validação compara a conta e a conexão declaradas, o ID da planilha, o ID e os limites das abas, as coordenadas das páginas, os tipos e os horários. A autenticidade da consulta depende de o agente obter os retornos diretamente do conector. Os metadados de grade sozinhos não detectam uma edição que preserve as dimensões. Uma leitura em vários lotes continua sujeita a edição concorrente. Toda gravação segue as guardas de revisão e a releitura posterior previstas no contrato da produção.

No ensaio de 24/11/2026, duas consultas de metadados cercaram 11 lotes reais entre 14h28min59s e 14h30min15s UTC. A reconstrução validou 601 registros nas 35 tabelas e duas entradas da fila. A projeção recuperou os seis planos de EP2 e a preferência sintética B em SH06 a 4,2 segundos.
