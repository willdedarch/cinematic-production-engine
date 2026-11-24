# Rubricas e calibração artística

Esta biblioteca contém **28 rubricas e 140 microexemplos autorais didáticos**. O contexto de calibração é **A chave**, separado de A última água. Cada departamento possui cinco variantes, construídas para tornar uma diferença específica discutível. Elas não são produção audiovisual, avaliação humana nem prova de excelência.

## Contrato de leitura

`rubrics.json` tem raiz com `schema_version`, `scale`, `context` e `rubrics`. Cada rubrica usa `id`, `name`, `department`, `objective`, `criteria` (lista de strings), `observable_indicators`, `levels` (dict de strings 1–5), `critical_failures`, `examples` (IDs), `source_ids`, `diagnostic_questions`, `approval`, `rejection`, `limitations`, `correction` e `required_evidence`.

`calibration-examples.json` possui raiz com metadados e `examples`. Cada exemplo referencia uma rubrica e informa `level_designated`, `origin`, texto, intenção, evidências textuais, qualidades, deficiências, razão do rótulo e limites. O campo `level_designated` não deve ser importado como se fosse nota emitida por um julgador ou preferência do usuário. A origem é sempre `DIDACTIC_TARGET_NOT_VALIDATED`.

## Aplicação no julgamento

1. Recuperar estado, versão, restrições e decisões aprovadas. Selecionar apenas rubricas pertinentes e suas referências. Não carregar os 140 casos em toda interação.
2. Identificar qual parte é proposta textual e qual é resultado realmente acessível. Texto não comprova naturalidade de atuação, identidade entre imagens, perspectiva em vídeo ou qualidade sonora.
3. Fazer o Technical Quality Gate com requisitos, consistência e viabilidade. Registrar lacunas como pendentes ou não avaliáveis.
4. Fazer o Artistic Quality Gate separadamente: apontar a escolha concreta, sua função na intenção, evidência e uma alternativa plausível. Correção formal não implica excelência.
5. Confrontar o caso com as diferenças entre níveis do departamento, em vez de contar palavras-chave. Preservar empate, discordância e ausência de evidência. A classificação é ordinal, contextual e contestável.
6. Em comparação cega, usar identificadores neutros, mesma intenção e rubrica; inverter a ordem sem revelar autoria. Maior extensão ou sofisticação verbal não é critério de vitória.
7. Diagnosticar sintoma, causa provável, hipóteses alternativas e informação ausente. Propor a menor correção que permita testar uma causa e preserve aprovados. Reavaliar a versão alterada sem apagar a anterior.
8. Apresentar força, problema, contraponto e limite ao usuário. Aprovação e bloqueio exigem a decisão humana aplicável; chegar ao limite de revisão não autoriza aprovar.

## Como interpretar os cinco níveis

- **1 — Inadequado:** uma falha observável impede a intenção ou contradiz requisito central. Quando a questão é apenas falta de acesso, marcar pendência em vez de atribuir nível 1 por ausência de observação.
- **2 — Medíocre:** pode cumprir partes técnicas, mas resolve a tarefa por solução genérica, declarativa ou superficial. A rubrica explica qual função ficou fraca.
- **3 — Competente:** há clareza e domínio funcional observável. Isso pode satisfazer uma entrega de escopo simples; não implica identidade marcante.
- **4 — Excelente:** escolhas específicas se relacionam à intenção e integram mais de uma camada sem efeito gratuito. Verificar a execução e o contexto, não premiar uma lista de termos.
- **5 — Excepcional:** integração extraordinária é uma conclusão exigente, que precisa apontar como as escolhas reconfiguram a experiência e por que uma alternativa competente não produz a mesma função. O exemplo didático apenas demonstra esse alvo em texto.

Não calcular uma média das camadas para converter nível técnico alto em nível artístico alto. Não usar porcentagens arbitrárias de emoção ou retenção. Um quadro simétrico, câmera imóvel, montagem lenta ou narração expositiva pode ser deliberado e adequado; a crítica precisa demonstrar incompatibilidade com a intenção, não apenas divergência de gosto.

## Limites, fontes e separação dos testes

Os identificadores de fontes remetem a `references/source-index.json`. Essas fontes sustentam conceitos e decisões profissionais consultadas; não foram usadas para dar notas 1–5 aos filmes citados. As cinco variantes são texto novo. Nenhum still protegido é redistribuído, e nenhum resultado de modelo é inventado.

Os casos de calibração são material de aprendizado contextual. Não podem ser reutilizados para alegar acurácia do julgador no conjunto reservado. Benchmarks devem usar outros textos e problemas, congelar critérios antes das respostas e distinguir avaliação humana, agentes independentes, passes do mesmo agente e testes determinísticos. Receber feedback humano calibra a recuperação e o contexto; não retreina o modelo.

Slugs disponíveis: story, screenplay, dialogue, emotion, suspense, retention, direction, performance, casting, character-sheets, performance-sheets, wardrobe, locations, geometry, props, photography, optics, composition, lighting, color-texture, atmosphere, living-world, storyboards, shot-design, prompts, continuity, editing, sound.
