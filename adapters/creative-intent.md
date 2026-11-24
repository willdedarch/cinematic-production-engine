# Intenção aprovada entre roteiro, plano e take

No briefing, escolha gênero, intenção e ritmo antes de recuperar exemplos. O perfil `action_led_war` usa os campos `action_percent` e `story_percent` da decisão do episódio. Use os percentuais numéricos definidos pelo diretor, entre 0 e 100, com soma de 100. Por exemplo, 60/40 usa `{"kind":"action_led_war","action_percent":60,"story_percent":40}`. O [estudo A última frequência](../examples/action-study/README.md) demonstra 65/35. As decisões 65/35 existentes conservam o mesmo contrato.

## Da proposta ao plano

1. Desenvolva alternativas, apresente conflitos distintos e deixe o diretor escolher. Construa uma linha do tempo contínua de ações e mudanças. Cada evento registra sua classe, visibilidade e consequência. Diálogo, espera e reação isolada são tempo de história, mesmo se houver sons de confronto ao fundo.
2. `intent-audit` calcula a distribuição a partir do mapa proposto. O cálculo usa as classificações do mapa e compara as duas proporções medidas com o perfil informado. Confira separadamente, com roteiro ou quadro, se cada ação é física e representada diretamente.
3. `intent-plan` prepara uma decisão `CPE_CREATIVE_INTENT_V1` com autorização, episódio e revisão anterior. Use as guardas e a releitura da planilha. Uma alteração da duração aprovada requer decisão sucessora e revisão explícita do episódio na mesma preparação.
4. No `shot-handoff`, use `event_ids` nos beats e mantenha o texto de ação aprovado no campo `action`. Performance, som e câmera têm campos próprios. O handoff exige a janela exata e lista os acontecimentos no prompt neutro e no adaptado. O `prompt-definitivo.txt` saído pela CLI é completo e pode ser copiado sem abrir o manifesto.
5. Se mudar de modelo, compare o mesmo vínculo e as mesmas ações. Apresente limitações concretas de duração, referências ou formato para escolha do diretor. A exportação é manual.

## Avaliação do retorno

`shot-compare` confere propriedades técnicas mensuráveis conforme [o contrato de retorno](media-qc.md). `intent-review` e o julgamento com a cópia atual identificam cada acontecimento por quadro, beat ou timecode. `AUDIBLE_ONLY`, `DIALOGUE_ONLY`, `OMITTED` ou `REPLACED` reprovam um acontecimento exigido em quadro. Consequência ausente ou ritmo inadequado abrem revisão. Com evidência incompleta, o julgamento fica pendente. Um resultado favorável prepara uma decisão humana.

O manifesto de produção conserva a decisão e a versão do plano. Uma checagem técnica favorável ainda exige revisão artística. O retorno antigo pode exigir reexportação quando o contrato, o estado ou as referências mudam.
