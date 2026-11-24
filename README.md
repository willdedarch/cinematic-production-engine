# Cinematic Production Engine 1.6.2

Skill para roteiro, direção e produção audiovisual. Apresenta painéis na conversa e oferece uma mesa HTML complementar, bíblia por momento narrativo, planos, takes com som e marca de tempo e Google Sheets como estado compartilhado.

## Começar

Use a pasta completa que contém [SKILL.md](SKILL.md) no local de descoberta suportado pelo Codex. Em ChatGPT Chat ou Work, a distribuição pode usar um plugin privado de um workspace elegível, com a mesma pasta completa de Skill. Consulte [distribuição pública e configuração privada](integrations/public-distribution.md). Leia o [manual](MANUAL.md). Cada produção fica numa pasta privada fora da instalação. A Skill usa o conector Google já disponível no host. Prepare `integrations/local-binding.json` a partir do vínculo público, preenchendo sua conta, planilha e os IDs reais de todas as abas e tabelas descobertos pelo conector. O exemplo público não concede acesso a qualquer produção. Esse arquivo privado fica ignorado pelo Git.

Peça “Abra o episódio dois da minha série e mostre o que mudou”. O agente consulta e valida o estado, executa o runtime da etapa e apresenta o painel na conversa. Continue com a próxima decisão em linguagem natural. O HTML serve como mesa complementar. Escolhas no navegador permanecem locais até serem enviadas por nova mensagem e validadas. A mesa mostra a hora da leitura e precisa ser recarregada após nova publicação.

## Revisão 1.4

Biblioteca aprofundada com encenação coletiva, ambiente dinâmico, guerra ficcional e estudos aplicados de direção/fotografia. Fontes inventariadas recursivamente, leituras e exclusões documentadas. Diagramas específicos e imagens conceituais contrastivas com procedência. Planos temporais opcionais no compilador, feedback privado imutável e hooks opcionais com cobertura explícita. Consulte [melhorias](IMPROVEMENTS.md), [auditoria](AUDIT-REPORT.md) e [fontes](SOURCES-REVISION-1.4.md).

Os estudos de imagem tiveram revisão humana negativa. Preferência relativa de críticos não estabelece aprovação. O benchmark de roteiros é exploratório e não prova excelência artística nem benefício geral da Skill. Os originais privados V3 e o histórico anterior foram preservados localmente, com somente a [proveniência](legacy/README.md) distribuída.

## Candidata 1.5.0

Plano cinematográfico com ações simultâneas, contexto de cena e conferência de estados entre planos. O pacote manual preserva referências versionadas e permite comparar o take devolvido antes de importá-lo para revisão. Votos A/B levam a versão exata do par apresentado. O contrato do Google Sheets continua em 3.1.0. Veja o [piloto A linha azul](examples/pilot15/README.md), [o contrato do plano](adapters/cinematic-plans.md) e [a auditoria corretiva](audits/review-1.5.0.md).

## Revisão 1.6.0

O repertório acompanha o gênero e a intenção do episódio. Para guerra de ação, o perfil escolhido pelo diretor pode vincular 65% de ação física visível e 35% de história a um mapa de acontecimentos versionado. O plano, a exportação e o julgamento conferem esse vínculo. A entrega inclui o prompt pronto em texto. A checagem de retorno confere propriedades mensuráveis, inclusive presença ou ausência de áudio quando solicitada. [Estudo A última frequência](examples/action-study/README.md) · [Auditoria](audits/review-1.6.0.md)

## Revisão 1.6.2

O ponto de entrada define a inicialização, a recuperação de conhecimentos, as responsabilidades da Writers' Room e a apresentação do painel na conversa. O mapa de tempo usa os percentuais do episódio, incluindo 60/40 e os registros existentes em 65/35. O contrato do estado permanece em 3.1.0.

## Verificação e limites

A 1.6.2 foi revisada por inspeção dos arquivos e do diff. As evidências a seguir dizem respeito à versão anterior.

A 1.6.1 corrige a abertura do comparador a partir da mesa e a geração dos comandos de hooks no Windows. O ensaio conferiu a comparação audiovisual na mesa local e os 11 eventos no Codex CLI em uma pasta dedicada. [Evidências e escopo da 1.6.1](audits/review-1.6.1.md)

Execute `python -B -m unittest discover -s evals -p "test_*.py"`. Execute os três testes `.cjs` em evals com Node e `python -B scripts/validate_package.py` para o inventário da release. Alguns ensaios requerem FFmpeg e Pillow já disponíveis. Os testes de interface simulam DOM e relógio de mídia. Homologação visual e escuta no dispositivo dependem do diretor.

Leitura por interação, revisão otimista, validação de autorização e confirmação posterior de dados e histórico. Sem atomicidade, atualização em segundo plano ou sucesso de gravação presumido. Produção final manual, zero créditos externos, sem novo MCP, API, Apps Script ou servidor. Recursos ausentes permanecem opcionais.
