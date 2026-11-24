# Controle técnico do take devolvido

Ao preparar um plano para produção manual, a CPE registra no pacote a duração do plano, a proporção do episódio e o tipo de mídia esperado. A opção nativa `generate_audio` explicitamente escolhida entra como `audio_stream`. `true` exige áudio. `false` exige a ausência de faixa. Se o parâmetro e o requisito de entrega estiverem ausentes, o resultado continua informando a presença do áudio. O contrato permite escolher de acordo com a intenção de som e qualquer trilha que já esteja no material de entrada.

Quando o diretor precisar de configurações específicas para o arquivo devolvido, a ficha de `shot-handoff` recebe `return_requirements`. Esses dados internos passam a fazer parte da assinatura do pacote. O diretor pode declarar largura, altura, FPS, presença ou ausência de áudio, quantidade de streams por tipo, contêiner e codecs na conversa. O contrato de entrega não acrescenta controles nativos aos modelos.

| Requisito | Dado conferido |
| --- | --- |
| `media_type` e `integrity` | Vídeo reproduzível distinto de imagem fixa, áudio ou capa anexada. Conferência do hash local e decodificação integral dos streams de áudio e vídeo com FFmpeg. |
| `duration_s` | Duração declarada do vídeo e do contêiner, com tolerância de 0,05 s ou um frame. O contêiner sozinho tem confiança limitada. |
| `width`, `height`, `resolution` | Dimensões em pixels antes da rotação. É possível exigir dimensões exatas, como `1280x720`. Classes `480p`, `720p` e `1080p` usam a menor dimensão, inclusive para retrato. Classes como `2K` e `4K` pedem largura e altura confirmadas para conferência exata. |
| `aspect_ratio` | Proporção de exibição e rotação registradas. A proporção da tela fica pendente se o FFprobe não puder comprovar a relação dos pixels. |
| `fps` | Taxa média declarada no stream. Aceita número ou fração, como `24000/1001`. Taxas média e nominal diferentes geram aviso. |
| `audio_stream`, `streams` | Existência de faixa de áudio e contagem por tipo explicitamente declarado. Capa anexada conta como `attachment`. Uma faixa decodificável pode conter silêncio. |
| `format`, `video_codec`, `audio_codec` | Contêiner documentado e codecs dos streams correspondentes. Formatos que dividem um mesmo demuxer exigem evidência que os distinga, como a marca do contêiner. Renomear a extensão não muda a medição. |

Em `shot-compare`, `check_details` registra separadamente cada requisito, valor esperado, medida observada e evidência. `PASS` indica conformidade observada. `FAIL` aponta desvio obrigatório. `UNKNOWN` sinaliza medição indisponível. `WARNING` indica evidência que precisa de interpretação ou é preliminar. `NOT_APPLICABLE` identifica propriedades que o contrato não exige. O resumo continua usando `SPEC_CHECKED`, `MISMATCH`, `INCOMPLETE` e `UNAVAILABLE`. A ausência de FFmpeg ou uma verificação interrompida deixam a integridade pendente. A decodificação automática completa usa um limite de 120 segundos de duração declarada e 45 segundos de execução local.

`shot-import` bloqueia os desvios obrigatórios de um pacote selado. Material elegível entra primeiro como `REVIEW_REQUIRED`, mesmo com `SPEC_CHECKED`. Uma ficha anterior à correção pode ser conferida se a reconstrução exata do pacote continuar válida. Os controles explícitos do modelo, inclusive áudio, passam pela checagem atual. Uma importação avulsa anterior à vinculação mantém seu estado de revisão e a marca `UNBOUND_LEGACY_IMPORT`. A aprovação registra evidência técnica apropriada e decisão humana sobre o material, a revisão e o hash. Integridade do arquivo e medidas de stream não comprovam atuação, continuidade, conteúdo do som, sincronia nem qualidade artística.
