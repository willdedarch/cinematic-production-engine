# Distribuição pública e configuração privada

O pacote público contém fontes, exemplos autorais e fixtures sintéticas. Exportações da conta, snapshots de produção, caminhos do computador e mensagens pessoais ficam na área privada do proprietário. Os testes de compatibilidade geram jornais sintéticos novos, identificados como tal.

Configure a conta no arquivo privado integrations/local-binding.json usando a mesma estrutura do exemplo google-sheets.binding.json. Esse arquivo tem precedência e é ignorado pelo Git. references/host-setup.md guarda os caminhos de retomada do computador e também é local. O detector de privacidade inspeciona os bytes distribuídos, arquivos binários e qualquer ZIP aninhado, com regras conhecidas e revisão manual complementar. O V3 original conserva contexto privado e permanece somente no arquivo local; seu fingerprint público fica em legacy.

Antes de publicar, execute python -B scripts/privacy_scan.py PASTA_PUBLICA, teste o ZIP extraído e confira também branches, tags e assets de releases. Um commit limpo acrescentado depois de um commit com identificadores conserva os bytes anteriores acessíveis. Limpeza de histórico exige backup, revisão do novo conjunto e autorização explícita antes de substituir referências remotas.

O resumo público de ensaios históricos relata seu alcance. Ele não é apresentado como um novo recibo do conector. As evidências originais podem continuar válidas na área privada sem serem redistribuídas. Uma fixture sintética comprova comportamento do software naquele caso, sem demonstrar gravação real no Google.
