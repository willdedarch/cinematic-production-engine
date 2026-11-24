# Publicar a mesa do episódio

O diretor pode dizer **“abre o EP2 de A última água”**. O agente consulta a planilha pelo conector autorizado e reconstrói o estado com a data real daquela leitura. Nomes sem acentos, o título do episódio e formas como “EP 2” são aceitos. Se houver duas séries correspondentes, o agente pergunta qual abrir. Um projeto de ensaio exige inclusão explícita dos registros de teste.

## Ler a produção e a fila

1. Em cada mensagem sobre a produção, confira a conta e o vínculo em `google-sheets.binding.json`. Obtenha os metadados atuais da planilha pelo conector. Guarde a resposta original, a conta, o identificador da conexão e a hora da observação em uma pasta de trabalho privada.
2. Use `desk-read-plan` com o registro inicial de metadados. Percorra os lotes e intervalos devolvidos, incluindo **Fila de direção**. Para cada lote, retenha índice, origem, ranges, horário e resposta original do conector. Obtenha outra leitura dos metadados ao terminar. Se faltou uma página ou houve mudança de aba/grade, recupere uma leitura completa antes de recomendar ou preparar escrita.
3. Use `desk-read-copy` com os dois conjuntos de metadados e os lotes da mesma leitura. O resultado validado alimenta a publicação. Preserve respostas do conector e evidência de tempo junto ao trabalho privado. Releitura de dados e histórico após uma alteração exige novas respostas. A leitura paginada pode atravessar edições simultâneas. [Campos, comandos e limites da leitura em lotes](leitura-em-lotes.md)

O diretor não produz, importa nem exporta esses arquivos técnicos. Ao abrir a mesa sem acesso ao conector, identifique a data da cópia local e apresente as pendências que aguardam consulta. A conta Google da equipe continua sob as permissões existentes.

## Entrada do agente

Use a mesma pasta de trabalho em todas as interações do projeto. Ela deve estar fora da pasta da Skill. Depois da leitura nativa, o comando local é:

```
python scripts/cpe.py desk-publish --workspace PASTA-DO-PROJETO --snapshot LEITURA --input PEDIDO
```

Exemplo do pedido que o agente prepara internamente:

```json
{"project":"A última água","episode":"EP2"}
```

O recibo devolve o caminho de `studio.html`, do comparador e o instante consultado. O diretor abre a página no computador onde a pasta existe. Se já estiver aberta, basta recarregar. O agente pode preparar um par antes da publicação com `desk-pair` na mesma pasta de trabalho. O primeiro clique no comparador recupera as letras e os hashes do par que o agente apresentou. Uma escolha que só ocorreu no navegador fica local até o diretor comunicar a decisão.

A saída da CLI indica o caminho de `result.json`. Leia esse arquivo para obter `studio`, `comparator` e `source_read_at`. Entregue o link local da mesa e a data em horário identificável. O endereço permanece o mesmo entre episódios da mesma série, exibindo a leitura que foi publicada por último. Ao apresentar um segundo episódio, informe qual está aberto.

## Receber a decisão do diretor

| Pedido ou gesto | Procedimento do agente |
| --- | --- |
| “Quero revisar uma cena” | Resolva o plano pelo nome na série e episódio correntes. Abra a faixa de quadros ou o cartão. Mostre dependências e fontes de exceções. Restaurar notas no navegador é uma operação local. |
| “O que Davi sabia quando falou isso?” | Identifique o momento da história e filtre fatos cronologicamente. Quando só houver posição de cena, identifique a precisão. Se ela faltar, mostre os fatos anteriores ao episódio e a lacuna de posição. |
| “Tenho dois takes” | Ofereça explorar os arquivos locais. Para guardar uma preferência, procure os vínculos com o plano, as revisões e os bytes dos dois takes, defina a pergunta de direção e use `desk-pair`. Publique a mesa com o par recuperável antes de solicitar a escolha. |
| “Registre B pela pausa aos 4,2 s, de 3,8 a 4,6 s, neste plano” | Associe a mensagem real ao par apresentado, respeite a ordem A/B e informe ao `desk-vote` marca 4200, início 3800, fim 4600, motivo e alcance `deliverable`. Um ponto isolado pode ser guardado como intervalo de duração zero. Use o trecho que o diretor comunicou. |
| “Escolha a variação adiantada para o corte” | Localize a alternativa específica e o motivo. Resolva a proposta com `desk-resolve` após conferir mídia, versão, origem e dependências. Um voto A/B e um take escolhido têm registros próprios. |

Se dois pares satisfizerem a frase, `PAIR_CLARIFICATION` fornece pergunta, plano e hora de apresentação. Identifique qual deles o diretor viu antes de gerar o plano de gravação. Uma dúvida sobre intenção ou um teste livre permite seguir a conversa sem escrita. Uma mensagem inequívoca que pede registrar a escolha já autoriza o registro no escopo indicado. Em ensaios, mantenha a marca de teste até o recibo. Registre o ator real e a referência de autorização, sem atribuir uma preferência de demonstração ao diretor.

## Fila, alternativas e recibos

O colaborador usa uma linha com `Pedido` disponível e preenche série, episódio, plano ou material, proposta e colaborador. Preserve os números dos pedidos e as colunas calculadas da aba. A consulta do agente usa títulos exatos ou referências correntes. Quando houver dúvida sobre o material ou a autoria, conserve a proposta na fila e resolva o contexto pela conversa.

- `desk-inbox` lê a projeção da fila a partir da cópia nativa já reconstruída. `desk-context` recupera a origem e as revisões a conferir. `desk-propose` prepara o registro de uma proposta de chat ou de uma linha identificada da fila. Para uma linha, use o pedido e o resumo criptográfico das seis células originais. Se ela mudou, volte à leitura.
- `desk-edit` prepara uma variação local de deslocamento de áudio de um take já vinculado. Use a revisão e a origem verificadas e um deslocamento em milissegundos. Valores negativos adiantam o áudio, positivos o atrasam. A operação requer arquivo local com vídeo e áudio, origem, direitos e ferramentas disponíveis. A derivação fica pendente de avaliação. Outras formas de revisão seguem o fluxo do material correspondente.
- `desk-resolve` recebe o identificador e o resumo da proposta apresentada, decisão de aceitar ou recusar, autorização e motivo. Aceitar uma alternativa de mídia vincula o take escolhido ao plano. Aceitar um pedido textual registra o desfecho da proposta. Se ele exigir edição de conteúdo, execute e verifique a alteração de conteúdo em sua etapa própria. Recusar conserva o original e a trilha.
- Um resultado `WRITE_PLAN_NOT_SAVED` prepara apenas a operação. Conduza o [protocolo de escrita e releitura](google-sheets.md) pela conexão existente. Reler os eventos de preparo e confirmação com seus fragmentos, o conteúdo e as revisões efetivamente escritos. Em falha parcial, retenha o identificador da operação e reconcilie o estado corrente antes de qualquer repetição.
- `desk-receipts` propõe os campos que espelham recibos confirmados na fila. Antes de aplicá-los pelo conector, relocalize o pedido e confira as seis células de origem (`expected_A_to_F`). Se coincidirem, atualize somente o intervalo `I:P` daquela linha e releia a linha inteira para conferir o espelho. Se divergirem, preserve a nova proposta e informe o conflito. Após as releituras, publique a mesa atualizada.

Os estados exibidos incluem proposta, em revisão, confirmada, recusada e conflito conforme a evidência. Uma alternativa aceita aparece como escolhida. Na conversa, indique a alteração, a revisão verificada e o recibo. Informe explicitamente qualquer histórico ou espelho da fila ainda pendente.

## O que compõe a visualização

A mesa reúne os planos e materiais do episódio, os fatos narrativos que podem precedê-lo, a fila correspondente e os pares retidos no projeto. A miniatura vem de referência com direitos identificados, versão e bytes confirmados. Se o arquivo estiver ausente ou alterado, o cartão continua disponível. Os vídeos permanecem locais. Mídia maior é carregada sob demanda quando existe uma cópia local verificada.

Na oficina, os cartões mostram os registros do episódio e os materiais da série aplicáveis. As referências da biblioteca editorial compartilhada passam pela seleção de conhecimento do episódio. Os cartões resumem os campos de apresentação.

Uma preferência sobre A/B acompanha o plano e a versão em que foi expressa. A mesa lê a mesma evidência em Human Feedback e Pairwise Comparisons, com os horários, o motivo, o alcance e as duas versões apresentadas. A confirmação exige o registro correspondente nos eventos de preparação e confirmação da mesma operação. Uma alteração posterior do plano ou dos takes identifica a preferência como histórica. O take escolhido para a montagem tem decisão própria.

Para a bíblia, cada ponto oferecido vem de um fato com episódio, beat e posição documentados. Uma referência como SH06 também pode corresponder ao sufixo único do ID técnico naquele episódio. O agente precisa vincular a fala a uma posição para reivindicar precisão por fala. Uma cena sem posição registrada abre com os fatos de episódios anteriores.

## Atualização e recuperação

O endereço é estável por planilha, projeto e escopo de teste, inclusive quando se altera o título da série. O lançador conserva o mesmo endereço para o armazenamento local das notas. A mesa nova é preparada por inteiro antes de substituir a leitura visível. Uma interrupção pode deixar arquivos auxiliares de mídia sem referência. A leitura anterior permanece acessível.

Duas publicações sobre a mesma mesa são coordenadas por bloqueio local do sistema operacional. Uma leitura anterior à já publicada ou com conteúdo divergente para o mesmo instante exige nova consulta. O recibo comprova a atualização local. A persistência de uma decisão no Google Sheets exige a releitura independente do conector.

A entrega portátil corresponde exclusivamente à pasta `mesas/serie-…` indicada no recibo. Os arquivos privados do agente ficam na pasta irmã `desk-pairs`. Ela guarda os pares e os planos usados para conferir os recibos e pode conter estados completos da produção. Mantenha essa pasta privada quando compartilhar uma mesa.

Para separar a área privada e a entrega desde a origem, use uma pasta de trabalho privada em `--workspace` e defina `publish_root` na especificação de `desk-publish`. O valor é o caminho absoluto local da coleção de mesas a entregar. O agente continua resolvendo os pares na pasta de trabalho e publica apenas a pasta da série no destino.

Uma pasta do projeto pertence à sua produção. Ao encontrar marcador de propriedade incorreto, lançador adulterado ou fonte de produção diferente, interrompa a atualização, preserve o estado e confira o vínculo. A abertura de cópias locais em navegadores pode depender de política do host. O aceite visual é registrado após testar o percurso em ambiente autorizado.

## Instalar, atualizar e validar

Extraia a nova Skill inteira em pasta própria e indique-a ao host. Preserve a pasta da produção, os pares privados, os arquivos de mídia, as versões instaladas anteriormente e o arquivo V3. Ao retomar, verifique o vínculo da conta e faça nova leitura antes de publicar no mesmo destino. A Oficina oferece acesso às etapas e cópias de versões anteriores. Importação legada só deve afetar o estado compartilhado mediante diff, autorização e protocolo de gravação. [Migração V3](google-sheets.md#migração-v3)

Para verificar o fluxo, peça explicitamente um episódio de ensaio. Confira a data e o plano na entrada, navegue pelo cartão e pela bíblia, repita e escute o trecho no comparador, retorne ao plano e confira as notas. Exercite também consulta nova e conflito por mudança de revisão. O recibo local comprova a publicação dos arquivos. O recibo nativo comprova a operação que foi gravada e relida no Sheets. A avaliação de imagem, som, gestos e legibilidade precisa ocorrer no ambiente em que cada recurso está acessível, com aceite visual expresso pelo usuário. [Relatório da entrega](../AUDIT-REPORT.md)

