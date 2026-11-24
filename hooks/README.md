# Hooks opcionais

`lifecycle.py` tem respostas específicas para os eventos de início, mensagem e uso de ferramenta. Compactação, parada, interrupção e encerramento podem registrar recibos privados e mínimos. A falha de um recibo de encerramento usa a saída de erro do evento. O bloqueio estruturado é reservado a `PreToolUse`. A cobertura nativa exige observar o host disparando as definições confiáveis.

scripts/configure_hooks.py prepara e mescla as definições exatas preservando hooks existentes. Use o arquivo .codex/hooks.json de um projeto dedicado à CPE para restringir a guarda de ferramentas a esse projeto. Revise a definição no painel Hooks do host. A confiança depende da definição vigente e da revisão exigida pelo Codex. O instalador não altera o cadastro de confiança. Uma configuração preparada ou um teste por stdin não demonstra acionamento no ciclo nativo.

O adaptador `cpe_hook.py` foi testado com entradas JSON locais. O exemplo de configuração não foi instalado nem acionado pelo ciclo nativo desta sessão. Revise os caminhos e a definição antes de habilitar no host. [Documentação oficial consultada em 24/11/2026](https://learn.chatgpt.com/docs/hooks).

O host exige confiança na definição vigente. Há diferenças entre execução local e orquestração em nuvem; alguns caminhos não passam pelos hooks e falhas podem deixar a chamada prosseguir. Portanto este adaptador não é um bloqueio universal. Ele recusa operações Higgsfield diretas fora da lista de leituras verificada. Não intercepta todo código arbitrário, callbacks remotos ou todas as ferramentas hospedadas.

Sem hooks, as políticas e validações explícitas do harness continuam operando. Os eventos internos são emitidos por `cpe.py`, com logs reais por execução; não são hooks nativos. Geração conceitual nativa continua sob autorização específica e limite de alternativas, conferidos pelo agente e Cost Guard. Não instalar novo MCP, criar servidor ou contornar a revisão do host.
