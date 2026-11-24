# Auditoria técnica independente — Harness 1.1

Revisor: agente `judgment_adversarial`, no papel Technical Auditor, distinto do implementador. Data: 24/11/2026. Escopo: código real de `harness_runtime.py`, `cpe.py`, `optics.py`, `image_tools.py`, `media_tools.py`, `previs.py`, `blender_previs.py`, políticas, schema de políticas e testes atuais. O revisor escreveu somente este relatório e `evals/test_harness_review.py`.

Não foi executado Blender, navegador, geração nativa, geração externa, instalação, escrita no Sheets ou importação no Drive. Os cenários são cópias sintéticas em memória, com um checkpoint em diretório temporário. Teste local não autentica uma mensagem humana nem comprova qualidade artística.

## Achados e correções

| Área | Achado no código inspecionado | Situação no último reteste independente |
|---|---|---|
| Aprovação de assets | Review era requerida somente ao mudar o Workflow; asset sob gate já aprovado podia passar pela outra rota. | Implementador incluiu aprovação/bloqueio de assets na exigência de review corrente. Regressão negativa passou. |
| Versão julgada | Aprovação do gate podia incluir patch de conteúdo do asset; a review vinculava o snapshot anterior. | Conteúdo precisa ser salvo e revisto antes da aprovação; alteração de conteúdo junto da aprovação é rejeitada. Regressão passou, com controle positivo válido. |
| Departamento da review | Review de geometry conseguia apoiar aprovação de Screenplays/G4. | Caso foi executado e inicialmente falhou; após correção, departamento incompatível é rejeitado. |
| Autorização de Drive | `cost_guard('google_drive.authorized_import')` aceitava acesso sem mensagem de autorização. | Caso inicialmente falhou; após correção, autorização ausente é rejeitada. Isso não autentica por si só um identificador textual. |
| Identificadores de saída | IDs de câmera com caminhos eram aceitos e usados como nomes de PNG do Blender. | IDs com caminho agora são rejeitados antes de executar Blender. Não houve tentativa real de sobrescrita. |
| Colisão de nomes no Windows | CAM e cam passavam como IDs distintos, mas podem representar o mesmo arquivo de saída. | Corrigido com unicidade casefold. Regressão independente passou. |
| Óptica | Focar na hiperfocal H retornada produzia far finito; fórmulas de H e limites não eram coerentes entre si. | Corrigido. Regressões verificaram infinito no limite distante e limite próximo H/2. |
| Recuperação | Alterar apenas `saved.scope_guards` para corresponder a um estado diferente permitia informar MATCHES_CURRENT_READ_COPY. | Corrigido. Guardas são conferidas contra o snapshot salvo antes da comparação; regressão independente passou. Não houve sobrescrita, mesmo no caso defeituoso. |
| Overview de mídia | Com 15–19 frames, o limite de 14 podia descartar o último frame apesar da intenção de mostrar início/fim. | Código corrigido para índices distribuídos incluindo as extremidades e reinspecionado pelo revisor. Não foi executado um teste FFmpeg de 19 frames nesta revisão. Frames brutos continuam disponíveis. |

## Verificação independente executada

O arquivo `evals/test_harness_review.py` contém dez casos focados nos riscos, sem repetir os cálculos gerais já cobertos no toolkit. A primeira execução das dez regressões encontrou duas falhas (CAM/cam e guardas de checkpoint); o implementador corrigiu ambas. No reteste independente posterior, **10/10 testes passaram**. Esse resultado é da suíte independente focada, não a contagem total do pacote.

O teste positivo confirma que um gate G4 com checklist, dependências, autorização sintética e review corrente ligada ao registro gera um plano local. A saída continua WRITE_PLAN_NOT_SAVED. Os demais testes confirmam recusas, sem realizar gravações externas. O teste de recuperação preserva o snapshot original e altera as guardas isoladamente para verificar consistência interna, sem adulterar arquivos reais do usuário.

## Evidência óptica

Reprodução anterior ao reparo: para 50 mm, f/2.8 e CoC de 0,03 mm, H reportado era aproximadamente 29,8119 m; com foco nesse H, o limite distante retornava aproximadamente 17.774,99 m e rótulo finite. A definição de foco em H com profundidade até infinito foi conferida na fonte primária [Toshiba Teli, seção 2.1](https://www.toshiba-teli.co.jp/en/technology/technical/t0019_DoF_HyperfocalDistance.htm). A fonte adota convenções de distância próprias, que precisam permanecer explícitas. O resultado continua planejamento de lente ideal: não mede lente real, visualização ou obediência de modelo generativo.

## Cobertura e limites preservados

O CLI executa cálculos e processamento local e produz evidências com hashes. A cadeia de eventos detecta alterações no registro local; ela não autentica identidade externa. O Cost Guard cobre chamadas feitas pelos caminhos do CPE, e não intercepta universalmente outras ferramentas do host. A contagem de gerações nativas recebida pelo helper é um dado fornecido pelo chamador; o agente deve verificar o experimento e o histórico antes de acionar uma ferramenta, mantendo propósito e limite da autorização.

O estado fornecido ao CLI é uma cópia lida pelo agente. CLI não faz leitura remota nem escrita automática. Checkpoint sem recibo confirmado permanece não sincronizado. Readback e revisão otimista não constituem atomicidade. Um hash de registro e um contrato de review verificam vínculo e preenchimento, não provam que uma interpretação artística é correta ou que a origem de uma mensagem foi autenticada.

O implementador adicionou Artifact Registry aos alvos e à proteção pertinente. Gates QC que avaliam materiais de outra fase usam `context.review_gate_id`; o gate de origem permanece no registro. A integração recebeu o reteste específico descrito a seguir.

Blender permanece experimental enquanto o ambiente não completar startup/render/reabertura. O revisor não tentou contornar a falha conhecida nem usar a cena viva do usuário. A restrição de acesso a HTML local também foi respeitada; testes DOM e revisão de código não equivalem a validação visual em navegador ou aceite do usuário.

## Reteste final do Artifact Registry e QC

A suíte independente foi ampliada somente para os casos pertinentes solicitados pelo implementador. O código atual foi relido e a última execução foi **22/22 testes aprovados** em `evals/test_harness_review.py`. Esse total inclui os dez casos anteriores; não deve ser somado novamente a eles. Não é a contagem total da suíte do pacote.

Positivos integrados: uma cópia sintética consistente passou por G0–G13 com as dependências, os checklists e as aprovações vinculadas a gate/episódio/revisão corretos. O teste preparou a aprovação QC G14 sobre um artefato cujo gate de origem era G10; o candidato validou, G14 ficou aprovado no plano e o registro de origem permaneceu byte a byte igual. Outro caso produziu um plano local de aprovação de Registry com review corrente, duas avaliações estruturadas ligadas ao hash do material e aprovação humana sintética pertinente. Criação em DRAFT continua somente um plano, sem aprovação ou escrita remota.

Negativos executados: alvo novo criado diretamente APPROVED; aprovação Registry sem review; hash ou revisão de alvo obsoletos; hash da mídia diferente do Registry; review_gate_id incompatível; avaliações persistidas da revisão anterior; resultados FAIL/UNKNOWN ligados como suporte de aprovação; aprovação G0 alheia ao material G10. Todos foram rejeitados no reteste final. O último par de falhas havia sido reproduzido na implementação intermediária e foi corrigido pelo autor antes deste resultado.

O contrato persistido agora conserva resultados técnicos e artísticos estruturados, com evidência e hash do material, e o preparo verifica a revisão da preimage para uma nova aprovação. A mudança de status incrementa a revisão do registro e não torna falsa uma avaliação histórica; sua atualidade é conferida quando utilizada. Aprovações podem vir do gate de origem ou de QC pertinente, preservando a origem. Esses testes comprovam o contrato e os vínculos locais em dados sintéticos, não observação real de uma mídia, decisão real de usuário ou gravação no Sheets.

Encerramento da revisão técnica focada: os achados pertinentes têm reparo e teste, com a ressalva explícita de que o overview de mídia foi reinspecionado no código sem novo teste FFmpeg desta revisão. Limites de Blender, inspeção visual, autorização real, hash de conteúdo acessível e conectores permanecem como descritos acima. Não foi concedido aceite artístico ou visual.
