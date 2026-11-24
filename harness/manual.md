# Harness e laboratório — operação

O agente conduz a conversa. O usuário pode pedir EP1, NEXT, STATUS, RESUME, CAST, LOCATION, PROPS, LOOK, PREVIS, EXPERIMENT, COMPARE, JUDGE, REVISE, APPROVE, LOCK, MODEL, PROMPT, EXPORT, IMPORT, INSPECT, QC, LEARN, CHECKPOINT ou RECOVER em linguagem natural. DOCTOR isolado diagnostica o ambiente; “Script Doctor deste roteiro” mantém a revisão de roteiro G4. Não exigir comandos nem caminhos técnicos do usuário quando já estão disponíveis.

## Ciclo integrado

1. Consultar o estado nativo atual pelo conector. Ler as tabelas e a fila pelo plano de `desk-read-plan` e reconstruir com `desk-read-copy`. Resolver projeto, episódio e dependências na cópia validada. Em criação autorizada, preparar `init` ou `new-episode` e confirmar a escrita antes de apresentar o cadastro. Retomar decisões e bloqueados.
2. Resolver fase em `gates.json`, recuperar conhecimento e exemplos pertinentes. `cpe.py task` lê arquivos reais por rota e registra hashes. O resultado é contexto de uma cópia lida, sem alegar consulta remota pelo CLI. Priorizar aprovados e protegidos. Registrar aplicação concreta em `used_knowledge`, com trecho/quadro e limite; leitura sozinha não prova uso.
3. Delimitar uma etapa decisória e a entrega esperada. Se for útil, escolher laboratório e formular hipótese. Referência, cálculo, planta, overlay ou texto podem resolver a questão sem geração. Experimentos são opcionais.
4. Executar ferramenta local disponível e guardar saída real. Pedidos de ferramenta nativa de imagem exigem mensagem explícita do usuário, finalidade PREVIS/CONCEPT/VISUAL_DRAFT e quantidade máxima. O CLI apenas prepara esse pedido; o agente usa a ferramenta nativa disponível dentro do escopo. Nunca substitui por API paga. Plano solicitado não é resultado executado.
5. Avaliar técnica e arte separadamente, usando rubrica real e evidência acessível. Para crítica independente, utilizar agentes relevantes se disponíveis e autorizados. Conservar limitações e divergências.
6. Corrigir somente a causa testável, preservar aprovados e reavaliar. Default duas rodadas, sem aprovação artificial ao atingir limite.
7. Apresentar a entrega no painel da conversa, com o controle que a sessão oferece ou resposta natural. Aguardar a decisão humana vinculada ao material apresentado. Validar conteúdo e versão antes de planejar persistência. No harness, `prepare` exige review corrente e departamento pertinente para gates/asset approvals. Não combinar mudança de conteúdo e aprovação; primeiro salvar rascunho, depois avaliar. O review deve incluir record_sha256 da leitura atual, além do hash do material. QC pode apontar a um asset de G10 com `context.review_gate_id=G13/G14`, mantendo seu gate de origem.
8. Aplicar o protocolo Google Sheets PREPARED → nova leitura/guardas → escrita → leitura independente → CONFIRMED → releitura. Fragmentos de journal conservam ordem e digest canônico; ausência/duplicação/divergência impede confirmação. Não há compare-and-swap nem transação atômica.
9. Criar checkpoint local após confirmação, aprovação, bloqueio, importação, exportação ou alteração material. Local não sincronizado permanece identificado. Antes de recuperar/gravar, reler o Sheets e reconciliar divergências; nunca repor uma cópia antiga cegamente.

## Comandos de conversa e CLI

| Pedido na conversa | Operação real |
| --- | --- |
| STATUS, NEXT, RESUME | `cpe.py status`, `next`, `resume`. Leia as etapas elegíveis. |
| MINE, IDEATE, DEVELOP, WRITE, DIRECT, QC | `cpe.py task --task ALIAS` ou `--gate Gx`. Recupere o contexto e execute a etapa. |
| PROMPT, PROMPTS | Em produção, `task --task PROMPT` ou `PROMPTS` seleciona G10. Use `compile` para um prompt avulso ou `shot-handoff` para um plano vinculado. |
| ANALYZE, ANALISAR | `cpe.py analyze` ou `analisar`, ou `task --task ANALYZE` / `ANALISAR`. Escopo de análise, sem avanço automático. |
| JUDGE, REVISE | `judge` prepara ou valida um parecer, `revise` prepara uma revisão. Use a rota do departamento e a mesma versão observada. |
| IMPORT | `import` para artefato local, `shot-import` para take de plano. O resultado exige revisão. |
| DOCTOR, Script Doctor | `doctor` diagnostica o ambiente. `task --task DOCTOR` recupera G4 para uma revisão de roteiro. |

Passe `--workspace` nas execuções. Para contexto de produção, passe `--snapshot`, `--project` e `--episode` com a leitura e o escopo resolvidos. Use os seletores documentados no [Router](../orchestration/knowledge-router.json). Comandos de conversa como FULL, APPROVE e LOCK são operações conduzidas pelo agente, com a elegibilidade e as guardas aplicáveis. Quando o pedido autorizar gravação, siga o contrato nativo e confira o resultado por releitura.

## Classes de material

REFERENCE é dado de pesquisa; TECHNICAL_PREVIS é planejamento espacial/óptico; ARTISTIC_PREVIS é estudo estético; NARRATIVE_PREVIS é storyboard/animatic; VISUAL_DRAFT é conceito experimental; PRODUCTION_EXPORT é pacote de instruções; FINAL_ASSET é resultado definitivo importado. Aprovar uma prévia não aprova o final. Toda importação começa REVIEW_REQUIRED e tem origem, direitos, ID, versão e hash. A produção externa definitiva é manual.

`Artifact Registry` normaliza essas classes. Experiments contém variantes no mesmo registro, evitando uma aba para cada modalidade. Evaluation Results contém também análises técnicas e benchmarks; Execution Evidence indexa logs/eventos/recuperação; Checkpoints registra cópias e pendências; Tool Capabilities contém disponibilidade com evidência e escopo. Human Feedback não recebe aprovação simulada como se fosse real.

## CLI local

O agente deve localizar um Python real. Neste ambiente o alias `python` do Windows não funcionou; foi usado o interpretador do runtime do aplicativo. Não instalar dependências silenciosamente. O código é portátil e usa biblioteca padrão; imagem depende de Pillow/NumPy, mídia de FFmpeg/FFprobe, Blender é opcional. Toda saída fica em uma pasta de projeto fora da instalação.

Exemplos, substituindo `python` por um interpretador verificado e `PASTA_DO_PROJETO` por pasta autorizada:

```
python scripts/cpe.py doctor --workspace PASTA_DO_PROJETO
python scripts/cpe.py experiment --input templates/optical-experiment.json --workspace PASTA_DO_PROJETO
python scripts/cpe.py previs --input templates/previs-room.json --workspace PASTA_DO_PROJETO
python scripts/cpe.py inspect --source VIDEO_AUTORIZADO.mp4 --workspace PASTA_DO_PROJETO
python scripts/cpe.py compile --input examples/prompt-specs/seedance_2_5.json --workspace PASTA_DO_PROJETO
python scripts/cpe.py judge --review AVALIACAO.json --workspace PASTA_DO_PROJETO
```

O agente pode usar `--snapshot` com a última leitura; STATUS/RESUME/NEXT e task mostram explicitamente que o CLI não conectou ao Google. `init` prepara projeto/episódio com 16 gates e 53 checks sem inventar assets; nunca grava remotamente. `confirm` valida arquivos de plano/releitura e cria cópia local. Credenciais não fazem parte do pacote. Outro host redescobre o link da conta, sem presumir que link_id seja portátil.

## Painéis e escolha compacta

`studio.html` mantém as 16 etapas e oferece painéis de apoio num seletor. Os controles preparam uma mensagem, limpam autorização/rascunhos ao importar nova cópia e nunca fazem gravação direta. O agente pode fornecer `cpe.py panel-copy` com digest canônico produzido por Python. A mensagem envia `base_scope_sha256` compacto, evitando centenas de hashes no texto. `panel-base` compara esse digest à leitura nativa atual antes de qualquer alteração; o formato antigo com base_guards continua aceito. Digest e checkbox não autenticam uma mensagem humana. O agente deve ligar a intenção à mensagem realmente recebida.

Sem interface interativa: mostrar estado/versão, duas ou três alternativas com motivo, evidência e protegidos, solicitar a escolha em nova mensagem e confirmar somente depois de gravar e reler. O painel HTML não atualiza sozinho nem recebe callback imaginário do agente. A inspeção viva de HTML local foi bloqueada pelo protocolo file:// nesta sessão; os testes DOM não são aceite visual do usuário.

## Evidência e cobertura

Cada execução gera diretório único com result.json e events.jsonl, cadeia de hashes, referências, estados de execução e erros. Antes/depois de criar, experimentar, julgar, revisar, aprovar, transicionar, exportar, importar e checkpoint têm contratos. O CLI emite os eventos de sua operação. Ações criativas fora dele precisam de registro explícito pelo agente. Um after_judgment de validação de review valida o contrato; não significa que o script fez crítica artística. Eventos declarativos não são automações nativas. Hooks opcionais estão em `hooks/`, testados por payload e não instalados nesta entrega.

Cost Guard é usado pelos caminhos do harness. Permite consulta verificada, processamento local, cálculos, derivados, conectores existentes e conceito nativo autorizado. Recusa geração externa paga, créditos, aluguel de GPU, custo desconhecido, servidor/API/conector novo e produção definitiva automática. Não intercepta universalmente ferramentas chamadas fora do harness ou caminhos de hook não suportados. Não prometer uso ilimitado do plano do chat.

Dados da produção ficam fora da instalação. Atualizar a Skill não deve apagar projetos, histórico ou preferências. Preservar o ZIP V3 original e checkpoints de migração; snapshots históricos com menos entidades exigem migração explícita e nova leitura, não preenchimento silencioso para gravar.
