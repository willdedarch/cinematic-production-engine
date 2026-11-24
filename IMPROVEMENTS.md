# Melhorias e correções 1.4

| Apontamento | Implementação verificável | Limite |
| --- | --- | --- |
| Fontes lidas apenas na entrada | Inventários completos de cinco árvores, 124 documentos obtidos, 113 lidos no escopo enumerado, síntese autoral e conflitos resolvidos | Não é leitura de todos os repositórios ou livros; origem oficial de mirrors não confirmada |
| Diagramas quase idênticos | 21 diagramas específicos, cinco imagens nativas, três cartões profissionais com links e um still observado | Esquema técnico e imagem conceitual não demonstram excelência de filme |
| Mundo vivo e guerra superficiais | Camadas físicas, objetivos simultâneos, ponto de vista, consequência e caso coletivo de oito planos | Caso ficcional escrito; atuação e montagem não realizadas |
| Perfis estilísticos curtos | Estudos aplicados de luz, espaço, lente, gesto, montagem e alternativas | Atribuição limitada às fontes consultadas; sem imitação garantida |
| Compilador só organiza campos | Plano temporal opcional com validação de intervalos, sujeitos, referências e transições | Intenção escrita não comprova execução pelo modelo |
| Julgamento pouco testado | Críticas independentes das imagens, comparação textual de quatro condições e feedback privado real | Mesma família de modelos; amostra pequena; diretor rejeitou os estudos de cena |
| Hooks incompletos | Handlers de lifecycle, gerador de configuração, recibos privados mínimos | Exigem confiança da definição no host e observação do ciclo nativo |
| Dados publicados | Exports removidos, fixtures novas, vínculo privado, original V3 fora do público, scanner recursivo e revisão manual | Scanner não prova ausência de toda informação privada; clones antigos podem persistir |

O [relatório final](AUDIT-REPORT.md) separa implementação, evidência, rejeição e pendência. As melhorias anteriores permanecem abaixo como histórico.

# Melhorias e correções

## 1.3.0 — do roteiro à decisão

| Necessidade da revisão | Implementação | Como conferir |
| --- | --- | --- |
| Retomar sem transportar cópias entre painel e agente | Publicação de uma mesa por série, com leitura nativa em lotes, hora da consulta, episódio e plano recuperado no navegador. | Abra o episódio pelo nome, guarde o link, peça nova consulta e recarregue o mesmo endereço. |
| Ver o plano no contexto da montagem | Faixa de quadros, filtro de cena, dados de imagem e som, continuidade de entrada/saída, dependências e fonte das exceções. | Abra o cartão de um plano com vizinho e siga as decisões associadas. |
| Saber o que Davi e o público já conheciam | Consulta por personagem, categoria e posição narrativa documentada. Antes de uma fala não posicionada, a mesa informa o limite de precisão. | Compare a abertura do episódio e um momento com fato registrado. Abra sua origem. |
| Julgar uma pausa e recuperar o exemplo real | Repetição por intervalo, marca, controle de áudio, par versionado e voto recuperável pelo plano, com versões e alcance. | Alterne o mesmo trecho, registre a preferência por mensagem e confira o recibo na leitura seguinte. |
| Propor sem perder a montagem atual | Fila compartilhada, origem e motivo, alternativa local de deslocamento de áudio e escolha explícita da versão de montagem. | Prepare ou recuse uma alternativa e verifique o take escolhido e a integridade da origem. |
| Evitar perda de contexto ou confirmação enganosa | Rascunhos locais por escopo, comparação da base para reutilização, nova mensagem após mudança, proteção das revisões e releitura nativa do histórico. | Troque de plano, volte, atualize a base ou compare uma proposta alterada. Confira a indicação de revisão. |

O [relatório da entrega](AUDIT-REPORT.md) distingue resultados observados de verificações ainda pendentes. A [revisão de interface](audits/revision-1.3-ui-crosscheck.md) registra correções específicas. O histórico de 1.2 permanece na [revisão de estado e série](audits/revision-1.2-series-and-state.md) e na [revisão das ferramentas](audits/revision-1.2-tools.md).

# Melhorias e correções — 1.1.0

## Estado compartilhado e confiabilidade

O V3 dependia de estado local/JSON entregue ao agente. A fonte operacional agora é uma planilha nativa do Google na conta escolhida, lida por interação. As 15 entidades originais foram preservadas e a ampliação normalizada chegou a 35 tabelas. Biblioteca, avaliações, experimentos e evidências usam IDs, escopos, revisão, origem e linhagem. Nenhuma atualização da Skill sobrescreve uma produção.

O recibo passou a conferir conteúdo/membros do escopo, revisão e PREPARED/CONFIRMED ligados ao plano, ator e autorização. Journals grandes são fragmentados com digest canônico e reconstrução completa; faltas e duplicatas falham. O planejamento de leitura usa bounds e páginas, rejeitando truncamento e conteúdo sem chave. Isso detecta divergência, sem criar atomicidade.

## Aprovação e revisão

Foram reparados: aprovação fora do episódio/gate; alteração de bloqueados; conhecimento aprovado sem proteção; avaliações órfãs/obsoletas; departamento incompatível; edição e aprovação na mesma operação; ausência de revisão para aprovação direta de asset; aprovação de Registry sem avaliações técnicas/artísticas ligadas ao hash; aprovação humana de gate alheio; perda de referências históricas; ciclos de sucessão; links anteriores/atuais do benchmark apontando para o mesmo registro.

As regressões incluem positivos, para não resolver o problema recusando toda aprovação. QC pode avaliar material de outra fase mantendo o gate de origem. Conteúdo alterado é salvo e julgado antes da aprovação. Helpers verificam contratos e vínculos; mensagem textual sintética ou checkbox não autentica pessoa real.

## Conhecimento e julgamento

Rotas carregam conhecimento pertinente, fontes e exemplos reais com hash. Cartões incluem quando usar, procedimento, tradeoff e critério. Óptica e composição deixam de ser apenas vocabulário de prompt. Teatro de métricas é evitado separando technical PASS de mérito artístico; 28 rubricas e 140 alvos didáticos não são vendidos como calibrados por humanos.

No par de teste, dois críticos rejeitaram a versão genérica como nível 2 e mantiveram a melhor em nível 3, apesar de vencer A/B. A revisão substituiu um reparo sem motivação pela decisão de ler agora ou após a partida. Um crítico a avaliou em nível 4 com ressalvas e sem aprovação humana. Isso é um exemplo concreto e limitado de crítica/reparo, sem provar superioridade populacional.

## Harness e ferramentas

Policies passaram a ser lidas/validadas em execução. CLI emite eventos e conserva falhas. Cost Guard exige autorização explícita de importação Drive e conceito nativo e recusa custo desconhecido nos caminhos cobertos. Hook restringe Higgsfield a nomes de leitura exatos, rejeitando sufixos falsificados; cobertura universal não é alegada.

Reparos técnicos: fórmulas coerentes de DOF na hiperfocal (próximo H/2 e distante infinito); guardas de checkpoint conferidas contra seu próprio snapshot; rejeição de IDs com path e colisões CAM/cam no Windows; último frame preservado em overview de mídia; animatic corrigido de 69.958333 s para 60.000000 s; labels de câmeras antes sobrepostos receberam posição/cor legível em planta v 2.

O compilador passou a respeitar tipos, enumerações, duração, proporção, papéis e dependências de referências de 8 modelos. Corrigidos extension_mode null, endframe sem start e rotas de prompts inconsistentes. Exports permanecem manuais e sem geração.

## Interface e redundâncias

16 etapas e 37 apoios usam controles que preparam mensagem; nenhuma gravação direta. Importação de nova cópia, inclusive inválida, limpa autorização e saída anterior. Digest compacto substitui centenas de hashes no texto; incompatibilidade exige cópia nova, nunca ignorar conflito. Examples normaliza calibração/golden/falhas; variantes ficam em Experiments; análises em Evaluation Results; evitadas abas e orquestradores duplicados.

## O que não foi convertido em promessa

Blender permaneceu experimental após falha real de startup. Hook de exemplo não está ativo. O bloqueio de file:// não foi contornado; DOM não é aceite visual. ASR local não foi executado, bibliotecas ausentes não foram instaladas. Sem decisões humanas reais, métricas continuam null. Sem autorização de experimento, nenhuma imagem nativa foi gerada. Não há filme final, retenção medida, garantia de atomicidade ou sincronização em segundo plano.
