# Cinematic Judgment Engine

O mecanismo prepara avaliações, valida seus contratos, conserva versões, organiza comparações e limita revisões. A interpretação artística é feita pelo agente e pelo usuário a partir do material acessível. O código não calcula excelência a partir de pixels, duração ou quantidade de campos preenchidos.

## Entrada e seleção

Antes de JUDGE, reler o projeto no Sheets. Identificar material, revisão e hash, intenção, gênero, formato, protegidos, referências aprovadas e fatos verificados. Recuperar a rubrica daquele departamento e os exemplos pertinentes, distinguindo rótulo didático de julgamento humano. Mídia não acessível significa UNKNOWN para critérios que dependem dela. Não avaliar atuação temporal por um frame isolado.

`scripts/judgment.py roles <departamento>` seleciona somente papéis relevantes. Creative Agent produz; críticos recebem material e contexto, não a defesa do criador; Chief Reviewer consolida sem apagar desacordos. Há dez papéis disponíveis: Creative Agent, Film Critic, Story Critic, Cinematography Critic, Performance Critic, Production Design Critic, Audience Critic, Continuity Auditor, Technical Auditor e Chief Reviewer. Papéis são instruções e seleção de trabalho; não são dez processos sempre ativos.

Quando a plataforma oferecer agentes independentes e houver autorização, executar críticos em agentes distintos e registrar IDs reais. No modo de um agente, usar passes separados e declarar essa condição. Dois subagentes da mesma família não equivalem à diversidade de modelos de um experimento publicado. O validador confere os IDs declarados e contratos, não prova identidade externa ou independência estatística.

## Dois gates

1. Technical: requisitos, estados, compatibilidade, continuidade, precisão e viabilidade. Cada PASS/FAIL precisa de observação e evidência. Requisito não observado é UNKNOWN; não vira PASS por silêncio.
2. Artistic: função, identidade, originalidade contextual, hierarquia, expressividade e integração. Usar níveis 1 inadequado, 2 medíocre, 3 competente, 4 excelente, 5 excepcional com a rubrica específica. Uma entrega pode ser tecnicamente PASS e artisticamente CHANGES_REQUESTED. O alvo depende do contexto; não impor uma estética a todos os gêneros.

Níveis 4/5 exigem explicar a integração de escolhas com evidências; o formulário completo não garante que o julgamento esteja correto. `READY_FOR_HUMAN_DECISION` é recomendação, nunca aprovação ou bloqueio automático. Aprovação real requer mensagem recebida, escopo e versão corretos, checklist e estado atual. Revisão histórica permanece válida como histórico quando o alvo muda; não pode aprovar silenciosamente a versão nova.

## Comparação cega

`pair` recebe exatamente dois materiais, remove metadados editoriais dos pacotes públicos e cria A/B e ordem invertida, com mapa privado separado. Inspecionar pistas de autoria no próprio texto. Não mandar o mapa privado ao crítico. Registrar qual pacote foi julgado, rubrica, evidência e escolha A/B/TIE/BOTH_FAIL. Repetir em ordem invertida. `consolidate` exige duas ordens por avaliador, rejeita duplicatas, converte rótulos para materiais e preserva divergência. Um revisor não tem acesso ao voto do outro antes de terminar.

O experimento desta entrega usa agentes da mesma família e repetições no mesmo contexto. Mede apenas concordância descritiva nesse pequeno conjunto; não isola viés de posição nem demonstra superioridade geral. Para um estudo de viés, reservar contextos frescos, randomizar ordens, fixar casos e pré-definir análise sem olhar resultados.

## Crítica, causa e revisão

O crítico procura falhas fundamentadas e registra também escolhas bem-sucedidas. Não inventar defeitos. Perguntar se o efeito foi construído ou apenas declarado, se a alternativa serve à intenção e se a suposta falha pode ser escolha legítima. Cada diagnóstico separa sintoma, evidência, causa provável, alternativas, ausência de evidência, confiança qualitativa, reparo, risco, protegidos e verificação.

Loop: proposta → contexto/rubrica → technical → artistic → adversarial → diagnóstico → correção localizada → nova avaliação → comparação antes/depois → usuário. Default duas rodadas, configurável de 1 a 5. Ao atingir limite, apresentar problemas não resolvidos; nunca aprovar para encerrar. `revision_decision` recusa mudanças declaradas em elementos protegidos. Não intercepta editores externos; conferir o diff real e fazer versão sucessora, sem sobrescrever aprovados.

Exemplo: locação plana. Primeiro verificar imagem/frame, planta, luz e intenção. Hipóteses: luz uniforme, câmera frontal, distâncias pequenas, materiais ou desfoque. Se planta já aprovada, testar somente câmera ou luz. Não reconstruir arquitetura por impulso. Reavaliar o mesmo gesto e a mesma área do quadro, não escolher um recorte que esconda a falha.

## Preferência humana e persistência

Registro de feedback: avaliação anterior/versão, decisão humana real, mensagem de origem, motivo, evidência, escopo e possível recalibração. Escopos: entregável, episódio, projeto, gênero, modelo e global. Global somente quando explicitamente escolhido. Uma divergência pode ser gosto, interpretação, erro técnico ou limite do avaliador; não presumir quem errou.

Calibração é recuperação contextual, não retreinamento. Reutilizar Examples para calibração, Evaluation Results para avaliações/divergências/benchmarks, Creative Preferences para preferências, Revision History para operações. Novas entidades específicas: Pairwise Comparisons, Human Feedback, Failure Diagnostics e Revision Results. Cada uma conserva alvo e versão. Não sobrescrever avaliação anterior para parecer que o agente acertou.

## Métricas e holdout

Guardar exemplos didáticos de calibração separados dos casos de benchmark. Um avaliador que viu o rótulo de um teste não produziu resultado de holdout. Registrar origem, modelo/agente, rubrica, contexto e exposição anterior. A linha de base humana deste pacote é n=0, taxas null. Não há evidência para Human Agreement, preferência humana ou retenção real. `metrics` só calcula acordo e falsas aprovações/reprovações para decisões reais identificadas, com denominadores. Não inventar meta. Ranking, detecção de falhas, sucesso de correção e regressão exigem dados com origem e critérios conhecidos, e devem ser reportados separadamente de arte.

Quatro condições comparativas desejáveis: sem Skill; Skill sem julgamento; com julgamento; com calibração humana. A comparação controlada das quatro não foi executada. O baseline estrutural V3/stage1/stage2, os casos independentes de stage3 e os testes de contrato não substituem esse experimento. Relatar isso como pendência metodológica, não benefício comprovado.

## Guerra e outros contextos

Guerra: perigo, percepção limitada, desgaste, materialidade, geografia, consequência, agência humana e fatos de época verificáveis. Uma morte pertinente não reprova por si; violência gratuita não constitui excelência. Romance, comédia, horror, documental e contemplação exigem critérios de intenção distintos. Conservar políticas do ambiente e não contornar filtros.
