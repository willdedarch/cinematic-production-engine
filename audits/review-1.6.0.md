# Revisão corretiva e entrega 1.6.0

Base pública 1.5.0, commit `6ef740286ff61bc553d6d6ae18428beb0011382f`. A correção mantém o contrato 3.1.0, a execução externa manual e a estrutura de fases. A validação final da cópia extraída, o hash do ZIP e a publicação são registrados no recibo externo da release.

## Causas verificadas e correções

| Frente | Problema reproduzido | Correção e evidência |
| --- | --- | --- |
| Repertório | Na 1.5.0, oito briefings sem correspondência específica recuperavam o mesmo estudo de partilha. A rota de guerra recuperava abrigo, manta e travessia sem considerar a ação solicitada. | A [revisão do roteador](router-review-1.6.0.md) documenta a reprodução e a classificação de 21 gêneros, bilinguismo, combinações, seleção de exemplos, rubricas e `ANALYZE`. |
| Criação | Os módulos tratavam sobrevivência e necessidades como exemplos centrais mesmo em ação intensa. | As instruções de criação, suspenses, personagens, atuação, mundo, direção e som partem do acontecimento que muda fisicamente a situação. O [inventário narrativo](../examples/narrative-index.md) conserva a finalidade de cada estudo. |
| Continuidade da intenção | O plano poderia citar ou omitir o acontecimento e a duração do episódio poderia divergir da decisão vigente. | A decisão versionada registra ação, consequência, plano, tempo e visibilidade. Casos negativos recusam substituição, corte e deslocamento. O prompt neutro e o adaptado carregam os acontecimentos com o mesmo vínculo. |
| Crítica | Uma revisão genérica podia deixar a intenção central sem avaliação. | O fluxo exige observação por acontecimento, revisa a duração, a consequência e a intensidade, e recusa omissão ou substituição. A aprovação considera a versão vigente e o conteúdo revisado. Veja a [auditoria independente](independent-1.6-creative.md). |
| QC | Um MP4 sem áudio passava com `generate_audio=true`. | A [checagem de retorno](../adapters/media-qc.md) testa arquivo real, streams, duração, resolução, dimensões, proporção, FPS, formato e codecs declarados. Divergência exigida bloqueia a importação vinculada. Resultado inconclusivo mantém a revisão aberta. |

## Estudo e integrações

- [A última frequência](../examples/action-study/README.md) tem três propostas e uma sequência autoral de pré-produção com 100 segundos. Os 65 segundos de ação visível apresentam mudanças observáveis no corpo, na luz, na fita e no ambiente. Os outros 35 segundos desenvolvem a decisão, a relação e a consequência. SA08 passa pelo mesmo fluxo de plano, exportação para Seedance e MiniMax, retorno técnico, julgamento e recuperação. Revisão artística final exige material interpretado e decisão humana.
- [Sheets e Drive](native-connector-1.6.0.json) confirmaram `PREPARED`, guardas, escrita sintética, releitura de dados, `CONFIRMED`, conferência do histórico, checkpoint e recuperação. A planilha isolada foi enviada à lixeira do Drive. Produção utiliza o vínculo privado existente e leitura nova por interação.
- FFmpeg e FFprobe executaram controle com vídeo e áudio. Pillow e NumPy apoiaram a prévia esquemática. O Blender executou o layout do estudo em processo isolado e devolveu `RENDERED_REOPENED_REQUIRES_VISUAL_REVIEW`. OpenCV, PySceneDetect e Faster Whisper não estavam disponíveis no ambiente testado. As alternativas locais continuam documentadas.
- [Painéis](panel-browser-1.6.0.md) preservam o percurso de conversa. Mesa e comparador foram publicados localmente com um par sintético. Testes de interface simulados têm cobertura própria. A política do navegador gerenciado recusou `file://` antes do carregamento da página. Visual, responsividade, reprodução e escuta nesse navegador dependem de acesso autorizado.
- Hooks e Cost Guard continuam disponíveis. As regressões validam entradas, saídas e limites locais. O projeto anterior de ensaio foi desativado. A ativação nativa e o despacho de eventos dependem de um escopo local selecionado e aprovado no host.
- A distribuição é verificada por inventário, scanner e extração separada. A exposição de uma referência histórica fora dos ponteiros publicados foi evidenciada no ciclo anterior. A ação de remoção depende do GitHub e fica fora desta publicação.

[Matriz de execução e aceite](execution-1.6.0.csv). As matrizes e as quatro especificações originais permanecem no pacote para rastreabilidade. O encerramento da revisão estrutural separa evidência técnica, instalação, homologação nativa e decisão artística.
