# Estado compartilhado V3.1

Google Sheets nativo é a fonte de estado desta instalação. Leia `../integrations/google-sheets.md` em toda retomada e antes de alterar estado. O vínculo está em `../integrations/google-sheets.binding.json`. Os dados de produção ficam fora da instalação.

Estados preservados: PENDING, IN_PROGRESS, REVIEW_REQUIRED, APPROVED, LOCKED, CHANGES_REQUESTED, SKIPPED. `gates.json` define dependências e critérios. Cada episódio contém os 16 gates e 53 critérios identificados. Aprovação exige dependências satisfeitas, entrega acessível, evidência por critério e mensagem humana explícita. LOCK exige aprovação anterior. Revisão exige motivo e invalida todos os descendentes, inclusive bloqueados, sem apagar assets, versões ou aprovações antigas. SKIP exige motivo, evidência de não aplicação/reuso e gate dispensável. Teste não é produção.

Cada linha possui chave estável, revisão positiva, executor, data e last_op_id. Toda operação tem ID único. Comparar revisão e conteúdo, inclusive conjunto de IDs, detecta alterações manuais sem incremento de revisão. A conferência ocorre antes e depois da escrita; permanece janela de corrida. Não existe bloqueio distribuído nem atomicidade entre leituras, gravações e histórico. Preferir um executor escrevendo por episódio; indicação de executor não é trava.

Sem conector, informar estado não consultado e preparar somente rascunho local. Não avançar gates, registrar aprovação remota ou chamar isso de sincronização. `studio_state.py` continua como utilitário legado V3 offline e não grava no Sheets. `shared_state.py` valida snapshots e prepara planos offline, também sem rede. Um arquivo produzido por eles não confirma persistência remota.
