# Changelog

## 1.6.2 · 24/11/2026

- Corrige o YAML e os metadados de invocação. O ponto de entrada orienta a inicialização, a etapa atual, a apresentação do painel e a continuidade entre mensagens.
- Alinha o Knowledge Router, as responsabilidades dos agentes e os aliases `PROMPT` e `ANALISAR` às operações existentes.
- Valida o mapa de acontecimentos pelos percentuais do episódio, preservando o formato dos registros existentes.

## 1.6.1 · 24/11/2026

- A mesa abre diretamente o comparador quando há um único par. Quando há mais de um, preserva o plano e o par escolhidos.
- O comparador mostra erros de verificação de integridade. A Oficina usa o nome atual da mesa no título e no rodapé.
- O gerador de hooks usa sintaxe do PowerShell no Windows e preserva grupos anteriores de outras ferramentas. A definição gerada pela versão anterior é substituída quando seus parâmetros coincidem com os da nova configuração.

## 1.6.0 — 24/11/2026

- Recupera referências, métodos e rubricas de acordo com gênero composto e intenção. Restabelece `ANALYZE` e a entrada de conhecimento sobre personagens e atenção.
- Registra a decisão 65/35 por episódio, carrega acontecimentos aprovados no plano e no prompt e exige revisão explícita de omissões, substituições ou falta de evidência.
- Entrega o prompt de produção como texto e verifica duração, vídeo, áudio, streams, formato, negociação de requisitos e integridade dos retornos locais.
- Inclui estudo independente de guerra de ação, duas exportações de modelo, regressões e matriz de aceite. Preserva o estado 3.1.0 e a execução externa manual.

## 1.5.0 — candidata corretiva de 24/11/2026

- Normaliza seletores em português e inglês, gêneros secundários, tipo de entrega e complexidade. Recupera o exemplo pertinente e registra a rota.
- Confere omissões de fatos de continuidade e admite ações paralelas, olhar, subtexto, composição, luz, óptica e ambiente em planos temporais.
- Entrega pacote manual selado e comparação técnica localizada. O retorno vinculado exige planilha, plano e mídia correspondentes e segue para revisão.
- Vincula votos A/B à apresentação exata, distingue referências de mensagens de confirmação humana, melhora respostas dos hooks e amplia a inspeção de distribuição a UTF-16 e arquivos Office compactados.
- Exercita três estudos de direção e revisa fontes profissionais, com escopo de leitura, aplicações, hipóteses e verificações registradas.

## 1.4.1 — candidata local de 24/11/2026

- Unifica os aliases de guerra e escolhe exemplos por etapa e contexto, incluindo departamento, finalidade, problema e modelo.
- Integra o plano temporal opcional a `shot-handoff`, com duração, dependências, estados e revisão do plano conferidos.
- Acrescenta dois cortes de um animatic de ação ficcional, e ensaios textuais de comédia e documentário em três passes.
- Identifica logs históricos e vincula as verificações da candidata ao pacote testado.

## 1.4.0 — 24/11/2026

- Corrige a distribuição pública, substitui exports por fixtures sintéticas e separa configuração e perfis privados. V3 original preservado localmente com fingerprint público.
- Amplia fontes, estudos de direção, mundo vivo e guerra ficcional, com caso coletivo de oito planos. Substitui diagramas genéricos e acrescenta cinco imagens nativas com críticas e limites explícitos.
- Acrescenta plano temporal opcional ao compilador, registro imutável de feedback privado e handlers de lifecycle opcionais, sem modificar confiança do host.
- Executa comparação exploratória de quatro condições de escrita com revisão cega em ordens inversas. Aceite artístico e superioridade geral não estabelecidos.
- Preserva protocolo nativo de leitura/escrita/releitura, estado 3.1, 35 tabelas e produção manual sem créditos externos.


## 1.3.0 — 24/11/2026

- A série ganha uma mesa com endereço local estável, publicada pelo agente após leitura nativa da planilha e da Fila de direção. Série e episódio podem ser solicitados pelo nome. O diretor recebe o link e a hora da consulta.
- A entrada reúne retomada, decisão pendente e três percursos por material. A sequência de quadros leva ao cartão do plano, à continuidade entre cortes, às notas por plano e à bíblia no ponto narrativo disponível. A Oficina conserva as etapas e os painéis especializados.
- A sala A/B oferece exploração local e comparação de versões apresentadas, com repetição de intervalo, marca e alternância de áudio. O voto se vincula ao par original, motivo e alcance. O cartão expõe a preferência confirmada e a decisão de montagem separadamente.
- A fila permite receber, revisar, aceitar e recusar propostas com autor, origem e motivo. Alternativas locais de deslocamento de áudio preservam a mídia original e podem ser escolhidas para o corte após revisão. O protocolo verifica base, escopo, conteúdo relido e histórico.
- A publicação local protege o endereço da série e identifica leituras obsoletas. Os rascunhos ficam no dispositivo. A sincronização com a planilha ocorre nas interações com o agente. [Guia da mesa](integrations/mesa-do-episodio.md) · [Revisão da entrega](AUDIT-REPORT.md)

## 1.2.0 — 24/11/2026

Bíblia por episódio e por momento da história, cartões e storyboard por plano, continuidade e reparo por campo, entrega manual com referências conferidas, importação para revisão, comparador de takes com som, intervalo e preferência contextual. Revisão de aprovações, observações por critério, histórico, ferramentas, laboratórios e rascunhos. [Revisão da série e estado 1.2](audits/revision-1.2-series-and-state.md) · [Revisão de ferramentas 1.2](audits/revision-1.2-tools.md)

## 1.1.0 — 24/11/2026

Versão final solicitada pelo usuário, baseada no V3 oficial e na evolução de estadoV3.1. Adiciona conhecimento operacional, exemplos, comparações, 8 adaptadores, 35 entidades normalizadas, 37 painéis de apoio, 28 rubricas/140 calibradores didáticos, críticas independentes, revisão e feedback contextual; harness/políticas/eventos/CLI, ferramentas locais, laboratório, análise de mídia, previs 2D, importação/exportação manual, checkpoint e recuperação. Corrige problemas de aprovação/recibo/bloqueio/departamento/paths/hiperfocal/recuperação e duração de animatic identificados em auditoria. Blender 3D e hooks nativos têm status limitado/experimental explícito. Ver relatório para contagens verificadas e pendências.

## Checkpoints de migração

Stage 1: estado nativo e auditoria inicial, 54 Python/11 DOM; roundtrip nativo termina arquivado revisão 3. Stage 2: biblioteca, 79 Python/16 DOM. Stage 3: julgamento, 128 Python/17 DOM;149 registros confirmados nativamente. Contagens são marcos históricos e não substituem os testes finais. Nenhum checkpoint equivale a aceite visual ou produção audiovisual final.

## V3 original

65 arquivos preservados privadamente no ZIP original, SHA256 `38582e59b870ff1bb6f261a54cdf8d01569661bbc18bf436f6c38c4a75692e8e`. Não foi sobrescrito.
