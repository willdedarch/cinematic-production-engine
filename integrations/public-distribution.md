# Distribuição pública e configuração privada

O pacote público contém fontes, exemplos autorais e fixtures sintéticas. Exportações da conta, snapshots de produção, caminhos do computador e mensagens pessoais ficam na área privada do proprietário. Os testes de compatibilidade geram jornais sintéticos novos, identificados como tal.

Configure a conta no arquivo privado integrations/local-binding.json usando a mesma estrutura do exemplo google-sheets.binding.json. Esse arquivo tem precedência e é ignorado pelo Git. references/host-setup.md guarda os caminhos de retomada do computador e também é local. O detector de privacidade inspeciona os bytes distribuídos, arquivos binários e qualquer ZIP aninhado, com regras conhecidas e revisão manual complementar. O V3 original conserva contexto privado e permanece somente no arquivo local; seu fingerprint público fica em legacy.

Ao preparar e homologar um ZIP de distribuição pública, execute `python -B scripts/privacy_scan.py PASTA_PUBLICA`, verifique o ZIP extraído e confira branches, tags e assets de releases. Para uma publicação somente de código, confira o diff e indique a verificação efetivamente feita. Um commit limpo acrescentado depois de um commit com identificadores conserva os bytes anteriores acessíveis. Limpeza de histórico exige backup, revisão do novo conjunto e autorização explícita antes de substituir referências remotas.

O resumo público de ensaios históricos relata seu alcance. Ele não é apresentado como um novo recibo do conector. As evidências originais podem continuar válidas na área privada sem serem redistribuídas. Uma fixture sintética comprova comportamento do software naquele caso, sem demonstrar gravação real no Google.

## Descoberta e formatos

Use a mesma pasta versionada de Skill. Para Codex, disponibilize a pasta que contém `SKILL.md` em um local suportado, com `agents/openai.yaml` e os recursos associados. O `AGENTS.md` orienta o escopo em que o cliente o descobre, independentemente do carregamento da Skill. Metadados de invocação auxiliam a descoberta e a seleção. A condução exige aplicar as instruções e executar o runtime no host. [Build skills](https://learn.chatgpt.com/docs/build-skills) · [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Para distribuir em ChatGPT, empacote a mesma pasta como `skills/cinematic-production-engine/` em um plugin privado de workspace elegível, usando o manifesto oficial. Publique somente o pacote público e mantenha vínculos privados separados. O plugin depende dos recursos e conexões autorizados do host. Uma versão no GitHub não representa instalação, disponibilidade ou execução no ChatGPT. [Build plugins](https://learn.chatgpt.com/docs/build-plugins) · [Empacotamento oficial](https://developers.openai.com/plugins/build/plugins)
