# Manual de utilização

## Instalação e versão

Extraia o ZIP em uma pasta nova e mantenha a estrutura, inclusive `SKILL.md`, `scripts`, `panels` e `integrations`. Disponibilize essa pasta pelo mecanismo de Skills do seu ambiente. A versão da Skill é 1.4.0 e o contrato de estado é 3.1.0. O arquivo V3 original permanece privado e seu fingerprint está em `legacy`. Cada produção usa outra pasta de trabalho, que deve ser mantida entre interações. Abra a conversa com a conta configurada já conectada. O ZIP pode ser atualizado sem mover a produção. Vincular a Skill ao host e autorizar o conector são operações distintas.

## Produzir o episódio seguinte

Peça **“Abra o episódio dois de [nome da série] e mostre o que mudou desde o primeiro”**. Na presença de títulos repetidos, o agente apresenta as opções. Um episódio de ensaio precisa ser solicitado como ensaio. Você recebe o link da mesa da série, o episódio aberto e a hora da leitura. Guarde esse endereço. Para rever mudanças de outro colaborador, peça “atualize meu episódio” e depois use **Recarregar mesa**. Duas abas abertas em momentos diferentes podem mostrar leituras diferentes.

Na entrada, **Continuar episódio** retoma o último plano aberto naquele navegador. Na primeira visita a chamada identifica o plano de entrada. A próxima decisão mostra a proposta ou o par disponível naquela leitura. Também é possível começar pelo roteiro, por uma cena ou por dois takes. Para começar pelo texto, abra o roteiro registrado ou leia um arquivo local em texto. Quando quiser incorporá-lo à produção, indique o arquivo e a mudança na conversa.

## Revisar um plano e sua continuidade

Em **Planos**, filtre a cena, escolha uma miniatura e consulte a duração, a ação, a câmera, o som e o take escolhido. O cartão mostra vínculos e dependências, a transição do plano precedente e as exceções com suas decisões. Na ausência do quadro, o plano continua consultável. Escreva notas no próprio cartão. Elas reaparecem naquele navegador se o armazenamento local estiver disponível. Ao reencontrar uma nota com base alterada, confira a versão. Para compartilhar uma nota, envie seu conteúdo ao agente ou apresente uma proposta na fila.

Em **Bíblia na cena**, selecione o momento da história e clique no personagem. O quadro conserva também o que o público sabia, as relações, os objetos, as locações e as perguntas abertas. Abra a decisão para entender a origem de um fato. Uma hipótese em revisão permanece identificada. Se a fala ainda não tiver posição documentada, a consulta indica a precisão disponível. Sem posição na cena, ela recua à abertura do episódio. O [guia de continuidade](references/serie-e-planos.md) traz um exemplo completo.

Também é possível partir da fala. Em **Tenho um roteiro**, abra a versão do texto e clique no nome sublinhado do personagem, por exemplo **DAVI** em “DAVI: Quem chegou?”. A ficha mostra a fala, o conhecimento dele e o do público. A versão atual do roteiro oferece texto sem vínculo temporal por linha. Por isso, a ficha começa na abertura do episódio em cada consulta. Para examinar outro recorte, selecione o plano e o momento documentado. **Voltar à fala** devolve o foco ao nome no texto. Indicações de diálogo no formato Fountain também são reconhecidas.

## Comparar, votar e montar

1. Para trabalhar livremente, abra **Tenho dois takes** e escolha os arquivos locais. Para registrar uma preferência reutilizável, peça **“apresente dois takes deste plano para comparar a pausa”**. O agente verifica as mídias e prepara o par com versões identificadas.
2. Entre no comparador pelo plano, marque 3,8 a 4,6 segundos, ative a repetição e alterne o áudio entre A e B. Marque o instante que motivou sua escolha. O link de retorno leva ao mesmo plano e às suas notas.
3. Na conversa, diga **“Registre B neste plano pela pausa antes da fala aos 4,2 s. O trecho é de 3,8 a 4,6 s.”** Também cabem empate ou rejeição dos dois. O agente guarda marca, trecho, razão, alcance e versões. Se houver vários pares compatíveis, ele identifica o par pela pergunta e pelo contexto de apresentação.
4. A preferência aparece no cartão com o recibo após a atualização. Uma versão posterior preserva o voto como histórico. Para usar uma alternativa na montagem, peça expressamente para escolher aquela versão para o corte e dê o motivo. Uma escolha sobre a pausa de um plano só ganha alcance de cena, episódio ou série se o diretor assim indicar.

## Trabalhar com a equipe

Abra a aba **Fila de direção**, selecione uma linha com número de pedido disponível e preencha série, episódio, plano ou material, proposta e colaborador. Use nomes como aparecem na produção, por exemplo “EP2” e “SH06”. Na conversa, peça **“revise as pendências do EP2”**. A equipe também pode propor diretamente na conversa. A aba **Decisões** da mesa mostra o pedido, seu estado, quem o propôs e o motivo do desfecho. Um pedido de revisão pode ser aceito como trabalho a fazer sem que um roteiro ou plano já tenha sido editado.

Para testar uma entrada de som, peça **“prepare uma alternativa do SH06 adiantando o áudio em 0,2 s”**. Quando o take local e a ferramenta estiverem disponíveis, o agente cria um derivado com a origem preservada. Ouça a alternativa. Diga “escolha essa alternativa para o corte pelo encaixe com a respiração” ou “recuse, a pausa ficou curta”. Se alguém mudou a origem ou o material, o agente traz a divergência e preserva a escolha anterior enquanto você reavalia. [Fila nativa da equipe](https://docs.google.com/spreadsheets/d/CONFIGURE_YOUR_SPREADSHEET_ID/edit#gid=1001)

## Uso pela conversa

“EP1” inicia briefing e prepara um novo projeto, sem inventar aprovação. “Retomar projeto…” reconstrói contexto pelo Sheets. “NEXT” mostra a próxima etapa elegível; “STATUS” expõe progresso e pendências. “LOCATION” trabalha a locação preservando geometria; “JUDGE” avalia o material acessível; “EXPORT” prepara produção manual; “IMPORT” recebe resultado e começa nova avaliação. Linguagem natural funciona. A disponibilidade das ferramentas é consultada antes de assumir capacidade.

Em cada decisão, o agente explica intenção, oferece poucas alternativas, recupera referências pertinentes e pede a escolha necessária. O usuário pode aprovar, reprovar, comparar, empatar, solicitar reparo, reutilizar versão ou retornar a uma fase. O silêncio não aprova. Uma aprovação pertence ao material, versão e contexto indicados.

## Guias especializados

- [Publicação e operação da mesa](integrations/mesa-do-episodio.md) e [leitura nativa em lotes](integrations/leitura-em-lotes.md) orientam o agente que recebe a mensagem e atualiza o endereço da série.

- `harness/manual.md`: ciclo completo, CLI, classes, eventos, custo, estado e recuperação.
- `judgment-engine/protocol.md`: dois gates, crítica independente, comparação cega, causa, correção e preferência humana.
- `harness/laboratories.md`:16 modalidades, procedimentos, critérios, exemplos e limites.
- `harness/optics-previs.md`: fórmulas/unidades, previs 2D, adapter Blender e derivados de composição.
- `harness/media-analysis.md`: metadados, frames, som, scopes, indicadores e limites.
- `adapters/README.md`:8 modelos consultados e Cinema Studio experimental; nenhuma geração externa executada.
- `integrations/google-sheets.md`: protocolo nativo, validações, migração e conflitos.
- `orchestration/panels.md`: fluxo por etapa e fallback textual; catálogo completo em panels/boards.json.

## Planilha

Projects/Episodes/Workflow e departamentos preservam as 15 entidades originais. Biblioteca usa Reference Library, Examples, Techniques, Creative Preferences, Model Compatibility, Production Lessons, Director Profiles, Genre Profiles, Visual Standards, Evaluation Results e Prompt Library. Julgamento usa Pairwise Comparisons, Human Feedback, Failure Diagnostics e Revision Results. A operação usa Experiments, Artifact Registry, Tool Capabilities, Execution Evidence e Checkpoints. Fila de direção recebe pedidos da equipe. Dashboard, ReadMe e Data Dictionary orientam o uso. [Planilha da produção](https://docs.google.com/spreadsheets/d/CONFIGURE_YOUR_SPREADSHEET_ID/edit#gid=1002)

LIB-CPE31 identifica a biblioteca compartilhada. TEST-CPE31 identifica o ensaio original arquivado. Outros ensaios da mesa mantêm `is_test=true` em sua própria série. Para abrir um ensaio, mencione essa intenção na conversa. A produção usa os registros do seu projeto. O agente confere chaves, relações, tipos, revisões, versões sucessoras e bloqueios. As validações de entrada da planilha orientam o preenchimento.

## Modo offline e falhas

Se o conector falhar, guardar checkpoint local identificado como não sincronizado; seguir pesquisa/rascunho seguro e registrar pendência. Ao reconectar, ler estado atual e comparar antes de escrever. O CLI valida cópias e planos, sem prometer leitura remota. Fonte Google não é substituída silenciosamente por um JSON. Arquivo de teste não é estado de produção.

Se uma ferramenta faltar, continue com referência, texto, diagrama ou revisão manual pertinente. Registre qual critério de imagem, som ou movimento precisa ser observado. Instalações e downloads ficam sob controle do usuário. Para atuar no Blender aberto, o agente precisa identificar a sessão e a cena pelo recurso disponível no ambiente. A abertura do programa depende do host e do mecanismo de integração. Hooks são pontos de execução que um host compatível pode acionar antes ou depois de uma operação. Os exemplos do pacote precisam ser configurados no host para funcionar. [Integração com Blender](integrations/blender.md) · [Operação das ferramentas](harness/manual.md)

## Verificação e aceitação

Os testes estão em `evals`. O relatório registra as verificações realmente concluídas, inclusive quais operações chegaram à planilha e quais estados foram exercitados localmente. Na avaliação visual, abra a mesa da produção no ambiente autorizado, retome um plano, passe pelo comparador e volte, consulte a bíblia por momento e confira o uso no tamanho de tela desejado. O aceite visual só existe após manifestação do usuário. [Relatório de revisão](AUDIT-REPORT.md)


## O que a revisão 1.4 acrescenta

O painel de estudo permite formular uma pergunta, conservar material e versões, apresentar alternativas e registrar rejeição sem convertê-la em aprovação. `cpe.py study-feedback` conserva mensagem e hashes no workspace privado. O arquivo não autentica uma pessoa sozinho. O agente deve usar uma mensagem realmente recebida e nunca inventar o motivo de uma reprovação. Este registro local não afirma gravação na planilha.

Para cenas coletivas, consultar `knowledge/collective-direction.md`, `engines/living-world.md` e `engines/war-film.md`. Cada ação tem objetivo, estímulo e consequência física. Os estudos de estilo em `knowledge/style-studies.md` descrevem relações entre escolhas e intenção; o nome do cineasta não é receita ou garantia. `knowledge/source-methods.md` explicita conflitos nas fontes comunitárias.

O compilador aceita plano temporal opcional autorado pelo agente/diretor, com intervalos, sujeitos, referências e estados de entrada/saída. Ele verifica consistência e conserva a autoria; não prova que um modelo executará o movimento. Veja `adapters/cinematic-plans.md`.

Use o modelo público `integrations/google-sheets.binding.json` para preparar `integrations/local-binding.json` privado, redescobrindo os IDs da própria planilha. Mantenha dados, feedback e host-setup privados. O scanner procura padrões conhecidos e exige revisão manual de contexto e procedência. Não publique exports ou originais privados com a Skill.

`scripts/configure_hooks.py` prepara definições para um projeto dedicado. A confiança deve ser revista no painel Hooks do host. O script não altera os registros de confiança. Configuração e testes locais não comprovam acionamento nativo; a cobertura efetiva deve ser observada. Os recibos opcionais contêm somente metadados, sem mensagens ou resultados.
