# Verificação independente da intenção e do retorno técnico

Auditoria feita pela frente de controle de mídia sobre a implementação da intenção, com cópias sintéticas locais. Os casos de escrita produziram somente planos. Nenhum registro nativo foi modificado nesta frente. A revisão do estudo usou o roteiro, as ações, o mapa temporal, a direção e a ficha focal.

## Reprodução e regressão

| Ponto examinado | Evidência | Resultado observado |
| --- | --- | --- |
| Referência prioritária no gênero | Solicitei G10 para `guerra de ação` e Seedance na v1.5.0 e no checkout atual. Na versão anterior, a rota não recebe intenção nem perfil. Na candidata, informei ação física visível e o perfil de guerra de ação. | A v1.5.0 retornou o estudo de evacuação de `pilot15` e um exemplo de modelo baseado na dinâmica da manta. A rota atual recuperou `examples/action-study/README.md` e `examples/action-study/focal-shot.json`. Os arquivos anteriores permanecem disponíveis para seus contextos. |
| Áudio explicitamente exigido na v1.5.0 | A ficha Seedance de 8 s exigia `generate_audio:true`. FFprobe identificou 1280 × 720, 16:9, 12 FPS e nenhum áudio no controle local. | O comparador anterior devolveu `SPEC_CHECKED` com `audio_stream:false`. Na correção, um controle silencioso recebe `MISMATCH`, e a importação vinculada recusa a faixa ausente. |
| Retorno técnico conforme | MP4 produzido localmente com vídeo H.264, áudio AAC, 1280 × 720 e 24 FPS. A CLI executou comparação, importação e tentativa de aprovação. | A comparação retornou `SPEC_CHECKED`. A importação propôs `REVIEW_REQUIRED`. A tentativa de aprovar sem parecer foi recusada. |
| Revisão do take | O asset de teste vinculado à ação aprovada teve sua origem retificada em uma nova revisão. | O parecer sobre a nova revisão exige renovar o vínculo com o plano. A proteção não depende da coincidência de uma pin antiga. |
| Promoção de DRAFT e aprovação em uma operação | O patch da decisão alterava apenas o status para `RECORDED`, deixando o tópico na preimagem. | O fluxo de `prepare` recusou a aprovação conjunta e pediu registrar a nova intenção antes do parecer. |
| Hash e escopo da crítica | `judge --review --snapshot` recebeu primeiro hashes divergentes, depois os hashes correntes e, por fim, os hashes correntes sem inclusão de registros de teste. | Recusou hashes diferentes, admitiu `READY_FOR_HUMAN_DECISION` com os pinos correntes e recusou o alvo de teste sem `--include-test`. |
| Ação aprovada citada dentro de um relato | Um beat incluía a frase aprovada como citação lida no telefone, entre instruções para mostrar apenas a reação. | A primeira versão local exportou a contradição. A nova conferência exigiu a ação aprovada como ação efetiva do beat e recusou o relato. |
| Duração do episódio e da intenção | Uma edição direta elevava o alvo de 20 s para 25 s sem atualizar o mapa. Em seguida, testei um sucessor autorizado com 40 s e mapa correspondente. | A edição isolada, antes aceita, foi recusada. O sucessor autorizado alterou o episódio e a decisão ativa juntos. |
| Ação conflitante no cartão | O cartão dizia para relatar o impacto depois, com o beat aprovado mantido intacto. | A primeira versão local incluía o relato conflitante no Master Prompt e no prompt adaptado. Após a correção, reli os dois arquivos e confirmei que ambos usam a ação do mapa aprovado. |
| Tempos fracionários | Plano de 13 s iniciado aos 0,3 s. Eventos de 0,3–2,3 e 2,3–13,3 s. Beats relativos de 0–2 e 2–13 s. | A igualdade de números binários recusava o primeiro evento. A tolerância corrigida preservou os dois IDs e aceitou os tempos equivalentes. |
| Contrato declarado e leitura direta | Um evento com personagem sentada relatando uma ação anterior foi intencionalmente marcado `ACTION` em ficha sintética. | O cálculo confere a classe declarada e devolveu 65/35. É necessário ler a ocorrência para confirmar a classe como ação física. A porcentagem precisa vir acompanhada dessa auditoria. |

## Leitura direta do estudo **A última frequência**

| Critério | Evidência textual localizada |
| --- | --- |
| Distribuição temporal | Ação em 0–15, 22–37, 45–66 e 76–90 s: 15 + 15 + 21 + 14 = 65 s. História em 15–22, 37–45, 66–76 e 90–100 s: 7 + 8 + 10 + 10 = 35 s. Verifiquei a descrição dos acontecimentos em cada bloco de ação. |
| Hierarquia, intensidade e consequência | E01/02 alteram janela, fachada e posição do vigia. E04/05 alteram placa, apoios e ferimento. E07 deixa uma queda e a grade atravessada. E08A–C removem o passadiço, prendem Abel e mudam a posição de Iara, com a ajuda de Daro. E10/11 abrem a lateral e tornam outras posições inviáveis. |
| Suspense e progressão | A fita muda de função entre E03 e E06. Os estados físicos de E08 condicionam a fala de Daro e de Abel em E09. O nome já escrito na etiqueta volta como voz em E12, abrindo uma pergunta que depende da transmissão. |
| Encenação, atuação e fotografia | SA08 usa três níveis de profundidade para situar Iara, Abel e Daro em 0–4, 4–8 e 8–12 s. O desenho de apoio, queda e tração no casaco dá instruções observáveis. A ficha fixa o eixo e propõe 28 mm esféricos. Havia marcas de conservação para a mão da fita, a manga ferida, Abel no piso, passadiço e abertura. |
| Montagem e som | SA08 conserva os três acontecimentos na mesma tomada. Impacto, raspagem, contato e vibração são propostas de sincronização localizadas. As falas de SA09 vêm depois da mudança física, com efeito sobre a relação. |
| Variação de propostas | As três ideias testam transmissão sob colapso, peso entre vagões industriais e identificação em reflexos. A seleção do observatório explica o que permanece verificável num espaço único. |

A ficha focal reproduz os três eventos e os IDs do mapa. A leitura confirma aderência textual localizada, inclusive ação física antecedendo as duas falas. A efetividade da atuação, os contatos, a intensidade percebida e a sincronia artística exigem mídia realizada. O controle técnico com volumes e sinais de teste verifica o caminho de arquivo e streams. A declaração `SPEC_CHECKED` não avalia esses critérios artísticos.

## Comandos e ambiente

- Python local. `python -B -m unittest test_media_qc test_shot_integrity test_tools12 test_prompt_compiler test_harness_review test_creative_intent`, com `evals` e `scripts` no `PYTHONPATH`. A última checagem focada executou 72 testes em 11,213 s e retornou código 0.
- FFmpeg e FFprobe 9.0.1 na máquina verificada. Controles gerados localmente, incluindo um MP4 silencioso, stream com áudio, vídeo de proporção diferente, áudio sem vídeo, imagem fixa, contêiner com duração sem duração explícita de stream e arquivo truncado após metadados legíveis.
- `python -B examples/action-study/run-study.py --workspace PASTA_NOVA` em pasta isolada e fora da distribuição. Código 0. Seedance e MiniMax exportados para produção manual. Controle técnico preparado para revisão na cópia local e retomada confirmou a cópia corrente. Zero gravações externas e nenhuma geração externa.
- A prova da regra de aprovação verifica a barreira técnica e os pinos. O projeto de teste não recebeu aprovação artística de uma pessoa.
