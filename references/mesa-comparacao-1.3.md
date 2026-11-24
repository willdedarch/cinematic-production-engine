# Sala de comparação

No cartão do plano, abra **Comparar takes**. A pergunta, as letras A e B e as revisões pertencem ao par apresentado pelo agente. O botão de voltar retorna ao mesmo plano. **Explorar dois arquivos** abre mídias locais avulsas, também com reprodução, marcação e repetição. Para transformar o ensaio em uma decisão registrada, peça ao agente que apresente os arquivos no plano correspondente.

1. Assista aos dois takes e selecione qual deles ouvir. **Inverter posições** muda a posição física das janelas e conserva as letras.
2. Em **Ir para**, digite `3,800`, posicione e marque o início. Posicione em `4,600` e marque o fim. **Repetir trecho** toca esse intervalo nos dois arquivos até pausar ou desligar a repetição. A alternância de áudio e ordem funciona durante a reprodução.
3. Marque o instante decisivo em `4,200`. Início, marca e fim são independentes. Uma marca fora do intervalo pede correção antes da decisão. Para um voto pontual, basta marcar o instante. É possível usar Espaço, I, M, O e R fora dos campos e botões.
4. Diga ao agente, por exemplo, “Registra B no SH06, entre 3,8 e 4,6 s, pela respiração aos 4,2 s. Vale para esta cena”. O botão **Preparar decisão** também produz a frase com o par identificado. A escolha aparece como confirmada depois da gravação e da releitura no Sheets.
5. A nota e a posição do comparador de um par são guardadas por conteúdo no dispositivo quando o navegador disponibiliza armazenamento local. A autorização deve ser renovada a cada abertura. O histórico oficial permanece na produção.

## Operação do agente

O agente seleciona os dois arquivos da leitura atual e conserva a correspondência das letras no workspace da produção. A entrada `desk-pair` recebe `project_id`, `episode_id`, `shot_id`, `question` e dois registros em `takes`, cada um com ID e revisão. O caminho pode ser fornecido pelo agente ao localizar o material em outro dispositivo. Em ensaio, usar `include_test: true`. O resultado devolve `manifest`. Um novo critério, uma mídia substituída ou uma revisão de plano exige apresentação correspondente. Com as mesmas entradas, a correspondência é reaproveitada. Um novo `presentation_ref` permite uma sessão distinta.

`desk-vote` interpreta a escolha já identificada pelo agente na mensagem recebida. Encaminhe projeto, episódio, plano, escolha (`A`, `B`, `TIE` ou `BOTH_FAIL`), marca, motivo, escopo, autorização, `pair_id` e `pair_sha256` do par apresentado. As posições são em milissegundos. Forneça `start_ms` e `end_ms` se o diretor informou o intervalo. O HTML traz a identificação e o hash no final do texto copiável. Na conversa, o agente os recupera da apresentação à qual o usuário respondeu. Se houver mais de um par possível, `PAIR_CLARIFICATION` lista os pares para confirmação. O escopo `scene` restringe a recuperação a planos da mesma cena e episódio. Os escopos herdados são `deliverable`, `episode` e `project`.

O plano de voto produz três registros por operação nas tabelas do contrato 3.1. Use a gravação nativa autorizada com PREPARED, releitura dos dados, CONFIRMED e releitura final. Reenvios depois de dados ou eventos parciais retornam `RECONCILIATION_REQUIRED`. O retorno `ALREADY_CONFIRMED` requer reconhecimento do plano retido, integridade do histórico e correspondência das três linhas na leitura. Ambos impedem a repetição cega da escrita. Antes do primeiro envio, a mesma decisão pode ser replanejada sobre uma base atualizada sem perder sua identidade. O workspace precisa permanecer disponível para recuperar uma apresentação anterior e seus recibos.

Um take já vinculado a outro plano ou a outra revisão precisa de vínculo explícito com a versão em análise. O agente pode apresentar dois arquivos registrados no episódio e ainda sem vínculo quando o diretor indica o plano. A preferência identificará esse plano. A preparação e a última conferência antes da gravação verificam os bytes dos dois arquivos.

## Propostas de variação

Uma proposta pode apontar para um take já vinculado ao plano ou para uma nova montagem local de som. A edição preserva o vídeo e gera uma cópia com o deslocamento solicitado. A origem precisa estar identificada, ter direitos de uso registrados e estar disponível na versão apresentada. Se os termos de uso estiverem ambíguos, esclareça-os com o diretor. A mesa compara os arquivos e as declarações que constam do registro.

Ao aceitar, o agente prepara a decisão e a seleção da versão exata do take na mesma operação. Um item criado por outra pessoa na fila também depende da releitura do pedido, do material e da proposta originais. É possível mover a linha na planilha. Alterar o conteúdo exige reapresentação. O recibo depende do histórico e da releitura de todos os itens envolvidos.

## Mídia e limites

O projetor publica mídia pequena incorporada. Para volumes maiores, o parâmetro `media_dir` de `presentable_pairs` gera arquivos locais no diretório `media` ao lado da sala. Cada mídia passa pela verificação de hash na origem e no navegador. O navegador precisa de memória suficiente para a decodificação e a conferência de integridade. Um arquivo indisponível ou outro conteúdo pede nova apresentação. A cópia local também pode conter mídia protegida da produção e deve ficar no espaço de trabalho autorizado.

O controlador programa o retorno ao início do trecho pelo relógio reproduzido pelo navegador. O instante real de saída do som depende do formato, dispositivo e precisão de reprodução. A rodada de testes de controlador usa relógios simulados e três repetições do trecho. A suíte audiovisual decodifica os seis arquivos didáticos reais com FFmpeg. O aceite de escuta e da experiência visual depende da reprodução no dispositivo do diretor.

