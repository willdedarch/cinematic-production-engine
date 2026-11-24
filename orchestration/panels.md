# Painéis conectados por mensagem

Em cada etapa, ler primeiro o estado nativo. Mostrar projeto/episódio, horário da leitura, revisão, decisões atuais, dependências, entrega, evidências e pendências. Oferecer 2–3 alternativas e recomendação fundamentada, somente para a decisão atual. O usuário seleciona, corrige, importa referência, reaproveita versão ou pede revisão. Carregar módulos do router antes de recomendar. Nenhum controle gera mídia.

O painel principal é a conversa. Apresente-o ao concluir as operações da etapa, junto da entrega. Confirme as capacidades da sessão antes de escolher o formato.

- **ChatGPT Chat.** Use seleção, comparação, aprovação, reprovação ou revisão nos controles interativos nativos que realmente retornem a decisão.
- **ChatGPT Work.** Use as perguntas e escolhas expostas pelo host. Se a visualização for apenas de leitura, receba a decisão por mensagem.
- **Codex.** Use os controles oferecidos pelo cliente e pela sessão. Em qualquer host sem controle compatível, informe a limitação e apresente A/B/C com resposta natural. O painel continua na conversa.

Vincule cada retorno do controle ou nova mensagem ao material, versão e escopo apresentados. A mesa HTML prepara uma mensagem copiável. Silêncio e pré-seleção não autorizam escrita. Uma autorização inequívoca para a alteração validada dispensa nova confirmação.

Validar escolha, escopo e base, produzir diff, conferir autorização, reler e gravar conforme `../integrations/google-sheets.md`. Emitir recibo somente após releitura dos dados e histórico. Distinguir RASCUNHO LOCAL, MENSAGEM PREPARADA, CONFLITO, GRAVAÇÃO NÃO CONFIRMADA e CONFIRMADO POR RELEITURA. Renderização de painel não prova integração.

## Painéis de fase preservados

| Gate | Painel e decisão | Tabelas principais |
|---|---|---|
| G0 | Project Control: escopo, formato, duração, gênero, modo | Projects, Episodes, Decisions |
| G1 | Research Board: fontes, fatos, ficção, lacunas | Decisions, Screenplays |
| G2 | Story Room: proposta e conflito | Decisions |
| G3 | Emotional Design: causalidade, informação, ritmo | Screenplays, Decisions |
| G4 | Script Doctor: versão e correções | Screenplays |
| G5 | Director Board e Cinematography: intenção, lente, luz, composição | Cinematography |
| G6 | Breakdown: inventário e reuso | Characters, Locations, Props |
| G7 | Casting: identidade, figurino e performance | Characters |
| G8 | Location: GEO, âncoras e contraângulos | Locations |
| G9 | Props: estrutura, material, dono e estado | Props |
| G10 | Previs/Prompt Compiler: cobertura, eixo, tempo | Shot List, Prompts, Continuity |
| G11 | Look Test, Visual Laboratory e Judgment Board: referências externas disponíveis | Decisions, Approvals |
| G12 | Production Control: importação e versões | Shot List, Continuity |
| G13 | Post-production: corte e mapa sonoro | Shot List, Decisions |
| G14 | Quality Control e Judgment Board: observado, pendente e aceite | Checklists, Approvals |
| G15 | Learning/Progress: lições e retomada | Decisions, Continuity |

Workflow, Checklists, Approvals e Revision History acompanham todas as fases. Dashboard exclui is_test=true e exige episódio escolhido; ausência de produção não equivale a conclusão.

## HTML complementar

Abrir `../panels/studio.html`. Uma cópia produzida a partir da leitura do agente pode ser importada opcionalmente. O caminho principal é a conversa e dispensa JSON manual. O HTML não possui OAuth, token, conector, acesso direto ao Sheets ou processo em segundo plano. Sua cópia tem data e pode estar desatualizada; origem não é autenticada pelo HTML. O rascunho nunca altera a cópia importada. Preparar mensagem e enviá-la ao agente; ele relê a planilha e pode recusar conflito. Fechar perde escolhas não exportadas. V3 requer migração revisada pelo agente e não importa aprovação silenciosamente.
