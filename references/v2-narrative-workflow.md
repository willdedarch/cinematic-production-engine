# Workflow narrativo herdado
## Roteamento de intenção
| Modo | Módulos essenciais | Entrega |
|---|---|---|
| EP N / IDEATE | story-mining, writers-room, dramaturgy, anti-cliche, continuity | três propostas distintas, fundamentos e comparação |
| MINE | story-mining | banco de sementes narrativas com rastreabilidade |
| DEVELOP | dramaturgy, emotional-engine, audience-psychology, suspense-engine, character-engine | beat sheet, mapa de informação, arco emocional e duração |
| WRITE | dramaturgy, dialogue-engine, character-engine | roteiro literário em formato screenplay |
| DOCTOR | script-doctor, anti-cliche, emotional-engine, audience-psychology | diagnóstico, correções propostas, sem alterar texto bloqueado |
| DIRECT | performance-direction, cinematic-direction, editorial-sound | encenação, decupagem textual e plano de montagem/som quando solicitado |
| ANALYZE | viral-intelligence, audience-psychology | análise observacional e mecanismos transferíveis |
| LEARN | learning, continuity | registro de decisões e hipóteses de melhoria |
| FULL | todos os necessários por etapa | desenvolvimento até revisão e direção, com handoff |

Leia apenas os módulos necessários em `modules/`. Consulte `project-profiles/project-template.md` quando precisar preparar um perfil privado do projeto atual. Para formatos e exemplos, consulte `templates/deliverables.md`. Não acrescente entregas que o usuário não pediu.

EP 1: comece do zero salvo abertura aprovada explicitamente. EP N>1: consulte final anterior, estado do cânone e gancho. Se houver decisão não tomada, ofereça continuar o gancho ou abrir outro fio, e pergunte somente se a escolha for necessária. Não fabrique episódios anteriores. Se o usuário escolheu uma direção, execute. Mantenha as versões aprovadas intactas.

## Fluxo de trabalho
0. **Intake:** ler briefing, fontes inteiras relevantes, restrições, formato, duração, cânone e nível de aprovação. Separar fatos, inferências, ficção e desconhecidos. Se faltarem dados não essenciais, avançar com suposições explícitas; se bloquearem o resultado, pedir apenas o indispensável.
1. **Descoberta:** minerar material antes de escrever. Levantar sementes, contradições, relações, dilemas, custo humano e possibilidades de ponto de vista; ligar cada proposta ao material quando houver base factual. Descartar narrativas dependentes de coincidência ou exposição longa.
2. **Sala criativa:** desenvolver alternativas causalmente diferentes e confrontá-las em passes independentes. Só selecionar automaticamente quando autorizado; se não, entregar propostas sem escrever o episódio inteiro.
3. **Arquitetura:** fixar pergunta dramática, desejo, oposição, risco, mudança de conhecimento, consequência, recompensa e final. Criar beats com duração estimada e estados emocionais observáveis. Não impor número de beats ou porcentagem de ação universal.
4. **Roteiro:** ações no presente, legíveis e filmáveis, diálogos com voz e intenção distintas. Evitar narrar o que pode ser mostrado. Cada cena tem função e mudança ou preparação necessária. Preservar falas bloqueadas e fatos aprovados.
5. **Crítica adversarial:** revisar a versão congelada com evidências, procurar explicações alternativas, clichês e problemas de tempo. Priorizar problemas, sugerir reparos e medir efeitos colaterais. Não reescrever sem autorização.
6. **Direção:** só após roteiro suficientemente estável. Separar ação autoral de encenação; preservar fatos, falas e eventos. Planejar intenção, atuação, continuidade, som e montagem textuais. Não acrescentar instruções operacionais de violência real.
7. **Validação:** verificar fontes, continuidade, duração, cobertura, causalidade, emoção, compreensão, começo/fim e escopo. Registre riscos não resolvidos, não declare qualidade provada. Use o rubric em `modules/quality-gates.md` e validador opcional para JSON.
8. **Handoff/aprendizado:** registrar versão, decisões, fios abertos, estados e dados reais disponíveis. Escrever arquivos persistentes apenas quando o usuário autorizar ou a tarefa explicitamente pedir. Não alegar memória persistente quando não houver armazenamento.
