# Cinematic Production Engine 1.5.0

Skill para roteiro, direção e produção audiovisual. Apresenta painéis na conversa e oferece uma mesa HTML complementar, bíblia por momento narrativo, planos, takes com som e marca de tempo e Google Sheets como estado compartilhado.

## Começar

Extraia a release inteira e disponibilize a pasta que contém SKILL.md ao agente. Leia o [manual](MANUAL.md). Cada produção fica numa pasta privada fora da instalação. A Skill usa o conector Google já disponível no host. Prepare `integrations/local-binding.json` a partir do vínculo público, preenchendo sua conta, planilha e os IDs reais de todas as abas e tabelas descobertos pelo conector. O exemplo público não concede acesso a qualquer produção. Esse arquivo privado fica ignorado pelo Git.

Peça “Abra o episódio dois da minha série e mostre o que mudou”. O agente consulta o estado e apresenta o painel pertinente na conversa. O HTML serve como mesa complementar. Escolhas no navegador permanecem locais até serem enviadas por nova mensagem e validadas. A mesa mostra a hora da leitura e precisa ser recarregada após nova publicação.

## Revisão 1.4

Biblioteca aprofundada com encenação coletiva, ambiente dinâmico, guerra ficcional e estudos aplicados de direção/fotografia. Fontes inventariadas recursivamente, leituras e exclusões documentadas. Diagramas específicos e imagens conceituais contrastivas com procedência. Planos temporais opcionais no compilador, feedback privado imutável e hooks opcionais com cobertura explícita. Consulte [melhorias](IMPROVEMENTS.md), [auditoria](AUDIT-REPORT.md) e [fontes](SOURCES-REVISION-1.4.md).

Os estudos de imagem tiveram revisão humana negativa. Preferência relativa de críticos não estabelece aprovação. O benchmark de roteiros é exploratório e não prova excelência artística nem benefício geral da Skill. Os originais privados V3 e o histórico anterior foram preservados localmente, com somente a [proveniência](legacy/README.md) distribuída.

## Candidata 1.5.0

Plano cinematográfico com ações simultâneas, contexto de cena e conferência de estados entre planos. O pacote manual preserva referências versionadas e permite comparar o take devolvido antes de importá-lo para revisão. Votos A/B levam a versão exata do par apresentado. O contrato do Google Sheets continua em 3.1.0. Veja o [piloto A linha azul](examples/pilot15/README.md), [o contrato do plano](adapters/cinematic-plans.md) e [a auditoria corretiva](audits/review-1.5.0.md).

## Verificação e limites

Execute `python -B -m unittest discover -s evals -p "test_*.py"`. Execute os três testes `.cjs` em evals com Node e `python -B scripts/validate_package.py` para o inventário da release. Alguns ensaios requerem FFmpeg e Pillow já disponíveis. Os testes de interface simulam DOM e relógio de mídia. Homologação visual e escuta no dispositivo dependem do diretor.

Leitura por interação, revisão otimista, validação de autorização e confirmação posterior de dados e histórico. Sem atomicidade, atualização em segundo plano ou sucesso de gravação presumido. Produção final manual, zero créditos externos, sem novo MCP, API, Apps Script ou servidor. Recursos ausentes permanecem opcionais.
