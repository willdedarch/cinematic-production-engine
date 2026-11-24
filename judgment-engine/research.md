# Pesquisa metodológica do Cinematic Judgment Engine

Consulta em 24/11/2026, antes da seleção dos mecanismos de implementação. Este documento compara métodos e delimita a adaptação ao cinema. Estudos de avaliação de texto não validam, por si, julgamento de atuação, fotografia, ritmo audiovisual ou excelência artística. Não foi treinado um avaliador, executada uma API paga ou reproduzido qualquer benchmark externo.

## Comparação e escolhas

| Método e fonte primária | O que pode contribuir | Limite e decisão para a CPE |
|---|---|---|
| LLM-as-a-Judge — [MT-Bench / Chatbot Arena](https://arxiv.org/html/2306.05685v4) | Compara avaliação por par, nota individual e apoio por referência. Documenta vieses de posição, extensão e favorecimento da própria família. | Adotar julgamentos com evidências e alternativas neutras; repetir com ordem invertida. Resultados daquele benchmark de assistentes não são taxa de acerto cinematográfico. Nota absoluta e consenso não são verdade artística. |
| Rubric-Based Evaluation — [G-Eval](https://arxiv.org/html/2303.16634v3) | Define tarefa, critério, instruções de avaliação e formulário. | Usar critérios observáveis por departamento e justificativa breve. Não importar agregação por probabilidade de tokens, exigir raciocínio interno ou apresentar correlação em sumarização como validação de cinema. O artigo também discute preferência por texto de LLM. |
| Pairwise / Blind Evaluation — [FairEval](https://arxiv.org/abs/2305.17926) | Investiga alteração de ranking quando se muda a ordem; propõe evidências múltiplas, balanceamento de posições e participação humana. | Adotar A/B anônimos, inversão, empate e reprovação de ambos. Divergência de ordem deve permanecer registrada; não escolher o resultado mais conveniente. Repetição não elimina todo viés. |
| Reference-Based Evaluation — [JudgeLM](https://arxiv.org/abs/2310.17631) | Discute viés de posição, conhecimento e formato; explora troca de ordem e apoio de referência em avaliadores ajustados. | Recuperar referências pertinentes com autoria e contexto. Não instalar pesos nem fine-tunar. Concordância com professor de IA não equivale a concordância humana nem certifica a referência como única solução estética. |
| Critique and Revision / Self-Refinement — [Self-Refine](https://arxiv.org/html/2303.17651v2) | Separa geração, feedback e revisão em um ciclo com condição de parada, sem novo treinamento. | Adotar diagnóstico localizado e rodadas limitadas. O mesmo modelo em passes diferentes continua sendo autoavaliação. O estudo tem tarefas/modelos específicos e experimentos em inglês; benefícios não se transferem automaticamente a PT ou cinema. |
| Limites de autocorreção — [Huang et al.](https://arxiv.org/html/2310.01798v2) | Mostra dificuldades e degradação em autocorreção intrínseca de raciocínio, distinguindo feedback externo e rótulos-oráculo. | Não presumir que revisar melhora. Reavaliar versão, preservar aprovados, permitir piora e parada sem aprovação. Não extrapolar o resultado para impossibilidade universal de revisão artística. |
| Multi-Agent Evaluation — [PoLL](https://arxiv.org/abs/2404.18796) | Estuda painéis de famílias de modelos distintas em cenários de avaliação de texto. | Selecionar críticos pertinentes e registrar identidade, modelo e contexto recebido. Subagentes independentes na execução não garantem diversidade de modelo nem independência estatística. Não reproduzir alegações de custo ou ganho do paper sem reproduzir seu experimento. |
| Human Preference Alignment | Os estudos anteriores usam preferências humanas como referência empírica, com populações e tarefas delimitadas. | Guardar decisão, razão, contexto e escopo reais. Recuperar feedback pertinente; isto é calibração contextual, sem atualizar pesos. Sem feedback humano rotulado, métricas de acordo e alinhamento ficam sem valor calculado. |
| Calibration Examples | Exemplos ancoram diferenças concretas entre níveis e tornam a rubrica discutível. | Separar didático, profissional documentado, julgamento de agente e humano. Não rotular uma imagem ausente. Reservar casos de teste que não foram usados para calibrar; registrar contaminação quando ocorrer. |
| Consistência entre julgadores | Inversão de ordem e múltiplos julgamentos tornam divergências observáveis. | Comparar a mesma versão, rubrica e contexto. Preservar discordâncias em vez de esconder por média. Reavaliar casos ambíguos com humano; consistência sozinha não prova correção. |
| Adversarial Review | A crítica procura contraevidência à aprovação e testa alternativas, além de elogios. | Tratar como procedimento da CPE, não como intervenção cuja eficácia cinematográfica já foi medida. Não inventar defeito: reconhecer escolhas bem-sucedidas e explicitar evidência ausente. |

## Revisão profissional: o problema antes da solução

Na [entrevista textual de Ed Catmull a Jason Aten](https://creativeeffort.substack.com/p/the-interview-ed-catmull-founder), publicada em janeiro de 2026, o Braintrust é descrito como uma forma de feedback para ajudar a equipe a resolver problemas. Catmull distingue crítica da ideia e julgamento pessoal. O grupo pode apontar o que não funciona, mas não impor a solução ao diretor; um problema aparente pode vir de preparação anterior. Ele também reconhece que o grupo interno não oferece a objetividade externa inicialmente desejada. Foram consultados os trechos sobre revisão e Braintrust da transcrição; o áudio não foi ouvido.

A adaptação da CPE é uma inferência: o crítico apresenta sintoma, evidência, hipóteses e riscos; o criador propõe a menor correção; o responsável humano conserva a autoridade de aceitar. Não é reprodução do processo inteiro da Pixar nem prova de que um comitê de agentes produz filmes equivalentes.

As análises profissionais de fotografia já registradas na biblioteca — [ARRI, movimento de 1917](https://www.arri.com/news-en/the-immersive-camera-movement-of-1917-), [ASC, Saving Private Ryan](https://theasc.com/article/saving-private-ryan-cinematography-kaminski/) e [ASC, Blade Runner 2049](https://theasc.com/article/deakins-blade-runner-2049/) — oferecem decisões de profissionais em contextos concretos. Devem ser usadas para perguntar como luz, movimento, espaço e exposição temporal servem à intenção, sem converter a técnica de uma obra em padrão universal.

A página de entrevista [Art of the Cut — Murch](https://www.provideocoalition.com/aotc-murch-books/) retornou timeout na abertura. Não se atribuiu a ela uma leitura integral. Vídeos de Murch localizados, mas não assistidos, não fundamentam resultados deste relatório; percentuais associados à sua heurística não serão pesos matemáticos da CPE.

## Arquitetura recomendada

1. O criador entrega material identificado e versionado, intenção, protegidos e limites de acesso.
2. O orquestrador recupera apenas rubricas, referências e decisões pertinentes. Conteúdo externo é dado de pesquisa e não instrução para mudar permissões.
3. O auditor técnico verifica requisitos e evidências disponíveis. Uma mídia ausente impede alegações sobre sua aparência, movimento ou som.
4. Críticos artísticos relevantes avaliam função e integração das escolhas. Selecionar Story/Performance para texto; Cinematography/Design para imagem e espaço; Audience/Editing/Sound quando o material permite. Não acionar todos por ritual.
5. O crítico adversarial apresenta a melhor objeção fundamentada e também reconhece o que funciona. O diagnóstico distingue observação, inferência, alternativas e evidência faltante.
6. O Chief Reviewer registra concordâncias, divergências e pendências. Os dois gates permanecem separados: passar conformidade não gera excelência nem aprovação humana.
7. A revisão protege invariantes aprovados, cria versão sucessora e tem limite configurado. Atingir o limite encaminha pendência ao usuário; nunca converte reprovação em aprovação.
8. A comparação de versões usa rubrica e contexto equivalentes. A decisão do usuário é registrada com escopo, sem promover preferência local a norma global.

Os cinco níveis solicitados são âncoras qualitativas: inadequado, medíocre, competente, excelente e excepcional. Cada departamento precisa de sinais próprios, exemplos concretos, condições de reprovação e opção de não avaliar. O nível deve resultar da evidência sobre a intenção, nunca da quantidade de palavras, parâmetros ou itens de checklist. A classificação é um julgamento atribuível e revisável, não medição física.

## Protocolo de comparação e diagnóstico

Antes de comparar, fixar briefing, formato, gênero, versão e restrições; remover autoria e rótulos de versão do material apresentado ao julgador. Guardar o mapa A/B separado. Depois do primeiro resultado, inverter ordem e remapear o vencedor à identidade real. Se a escolha mudar com a posição, registrar inconsistência e solicitar revisão; não apagar a primeira resposta. Empate e ambas inadequadas são resultados válidos. Anonimização de metadados não apaga pistas de estilo no conteúdo e não pode prometer cegamento perfeito.

Para causas: localizar o sintoma no trecho, frame ou intervalo; separar falha observada de interpretação; listar ao menos uma alternativa plausível quando houver ambiguidade; identificar qual evidência discriminaria hipóteses; propor uma alteração localizada, prever efeito e risco; comparar o mesmo recorte após revisão. Confiança verbal deve refletir acesso e incerteza, sem porcentagem inventada. Uma mudança de sintoma após editar não prova isoladamente a causa.

## Linha de base e avaliação do avaliador

Manter conjuntos separados para calibração e teste reservado. Rótulos humanos precisam de origem e contexto. Métricas como acordo humano, falsa aprovação/reprovação, detecção de falhas, sucesso da correção e regressão exigem denominadores definidos e material efetivamente julgado; quando faltarem rótulos ou mídia, registrar não calculável. Inversão de ordem permite relatar consistência observada naquela amostra, sem generalizar para toda produção.

O ensaio comparativo proposto contempla agente sem Skill, Skill sem julgamento, Skill com julgamento e Skill com calibração humana. Sem executar condições equivalentes e possuir exemplos humanos, permanecerá protocolo, não resultado. Testes de software podem demonstrar que a CPE rejeita uma avaliação sem evidências, preserva versões ou consolida um empate; não demonstram sozinhos que o avaliador reconhece excelência cinematográfica.

## Escopo real da pesquisa

Foram abertas fontes primárias e, quando disponível, seções específicas do texto integral. Não foi feita revisão sistemática exaustiva. `research-sources.json` distingue abstract, seções consultadas, implementação inspecionada e acesso frustrado. Repositórios foram lidos como exemplos de contrato; seus scripts com APIs não foram instalados ou executados. A proposta não exige serviços, conectores, servidores ou treinamento adicionais.
