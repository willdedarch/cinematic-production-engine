# Hooks opcionais

`lifecycle.py` tem respostas específicas para os eventos de início, mensagem e uso de ferramenta. Compactação, parada, interrupção e encerramento podem registrar recibos privados e mínimos. A falha de um recibo de encerramento usa a saída de erro do evento. O bloqueio estruturado é reservado a `PreToolUse`. A cobertura nativa exige observar o host disparando as definições confiáveis.

scripts/configure_hooks.py prepara e mescla as definições exatas preservando hooks existentes. Use o arquivo .codex/hooks.json de um projeto dedicado à CPE para restringir a guarda de ferramentas a esse projeto. Revise a definição no painel Hooks do host. A confiança depende da definição vigente e da revisão exigida pelo Codex. O instalador não altera o cadastro de confiança. Uma configuração preparada ou um teste por stdin não demonstra acionamento no ciclo nativo.

No Windows, o gerador usa a sintaxe de execução do PowerShell. Para corrigir uma definição gerada pela versão anterior, use os mesmos caminhos de Python, da instalação e dos recibos. O gerador guarda uma cópia do JSON anterior e substitui o grupo que coincidir com a definição antiga. Revise a nova definição no host antes de confiar nela. [Documentação oficial consultada em 24/11/2026](https://learn.chatgpt.com/docs/hooks).

O host exige confiança na definição vigente. O [ensaio da 1.6.1](../audits/review-1.6.1.md) observou os 11 eventos em uma pasta aprovada no Codex CLI para Windows. O despacho de `PreToolUse` usou um comando local. O matcher do Higgsfield e a regra de recusa foram verificados separadamente. Alguns caminhos locais ou remotos podem ficar fora dos hooks e falhas podem deixar a chamada prosseguir.

Sem hooks, as políticas e validações explícitas do harness continuam operando. Os eventos internos são emitidos por `cpe.py`, com logs reais por execução; não são hooks nativos. Geração conceitual nativa continua sob autorização específica e limite de alternativas, conferidos pelo agente e Cost Guard. Não instalar novo MCP, criar servidor ou contornar a revisão do host.
