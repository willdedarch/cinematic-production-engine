# A linha azul

Estudo original de pré-produção da Cinematic Production Engine. Uma travessia coletiva de 67 segundos dentro de um terminal fluvial fictício, numa cidade sob combate. Todos os personagens são adultos. A ação decorre do fechamento de um acesso, da redistribuição da multidão e da perda parcial de luz e visibilidade. O combate que obriga a evacuação fica fora de quadro. O recorte acompanha quem tenta sair e quem pode ficar para trás.

## Briefing

| Decisão | Proposta |
| --- | --- |
| Formato | Sequência de ficção em quadro 16:9 para uma longa ou minissérie. Tempos de decupagem são estimativas. |
| Ponto de vista | Joana sabe onde o terminal levava seus passageiros em dias comuns. O público vê áreas que ela pode enxergar e ouve o entorno com ela. A origem exata dos impactos não entra no recorte. |
| Objetivo externo | Levar o grupo do térreo ao patamar norte em meio à interrupção da travessia. O patamar permite reagrupar o trecho visível da fila. O destino posterior fica em aberto. |
| Pergunta da cena | Quando a lista deixa de organizar a saída, Joana consegue abrir mão dela a tempo de ajudar Ema sem perder o resto do grupo de vista? |
| Quebra dramática | O portão que concentra movimento cai e fica fechado. O arco norte já foi estabelecido. O segundo impacto remove a luz de parte do térreo e corta a linha de visão de Joana. |
| Custo | Ema sai do térreo mancando. O caderno fica no piso e absorve água. Joana perde a contagem e a última imagem de quem vinha atrás. |
| Entrega | Roteiro, proposta de casting, projeto de locação, storyboard textual, decupagem, continuidade, cartão focal e insumo real de compilação para 8 segundos. |
| Estado | Exercício textual sem mídia encenada, sem aprovação humana e sem preferência de diretor associada. Nenhuma geração foi solicitada neste estudo. |

## Propostas narrativas

| Critério | A · A linha azul | B · Caixa de voz |
| --- | --- | --- |
| Conceito | Acompanhamos a funcionária de um terminal no nível da multidão, no instante em que a rota prevista fecha. Três movimentos coexistem em profundidade enquanto ela decide entre lista e apoio físico. | Acompanhamos um operador de anúncios num mezanino. Ele vê a concentração no portão e tenta orientar duas áreas pela voz. O retorno do sistema falha e ele desce para verificar se chegaram a ouvi-lo. |
| Mudança visível | A rota lateral vira uma rota em profundidade, o apoio muda de mãos e parte da sala perde a fonte fria. | A visão global desaparece quando o operador perde a escuta da sala e desce ao térreo. |
| Custo filmável | Papel no chão, apoio corporal sustentado e contagem interrompida no patamar. | O operador abandona o ponto elevado. A descida limita o que ele pode observar e seu próximo anúncio fica por escrever. |
| Potencial de escala | O plano pode mostrar fila, banco lotado e contrafluxo com tarefas diferentes. O risco é perder a mudança de eixo no meio da pressão. | A altura favorece escala e desenho sonoro. O risco é a transformação ocorrer principalmente na voz de uma pessoa, deixando em segundo plano as decisões do grupo. |

Adotar A para testar se uma mudança de geografia produz ação legível e uma perda verificável de plano a plano. Preservar a relação entre ruído e informação que B tornava explícita. A escolha é autoral para este estudo, com base no briefing e nas propostas escritas.

## Recuperação e seleção

| Material consultado | Uso no piloto | Rastro na entrega |
| --- | --- | --- |
| [War Film](../../engines/war-film.md) | Preparar referência espacial, estímulo, resposta e consequência. Conservar percepção parcial. | Portão estabelecido em SH01, fechado em SH03 e imóvel aos olhos de Joana em SH07. |
| [Living World](../../engines/living-world.md) | Dar origem e persistência a alterações do lugar e incorporar tarefas simultâneas ao roteiro. | Luz do sul diminui em SH07, casaco fica sujo e o caderno molhado permanece no térreo. |
| [Direção coletiva](../../knowledge/collective-direction.md) | Fixar intenção, corpo, informação e lugar para personagens e grupos. | A mão muda de função em SH05. Ema inicia a carga e Bento ainda escolhe para onde olhar em SH09. |
| [A parte seca](../shelter/caso14-roteiro-e-direcao.md) | Referência interna de continuidade de apoio e de custo após o gesto. | O antebraço de Joana continua sob carga após o corte. O piloto adiciona pressão coletiva e perda simultânea de acesso e visão. |
| [Planos cinematográficos](../../adapters/cinematic-plans.md) | Converter uma decisão de cena em beats temporizados, sujeitos, espaço, som e transição verificável. | Estados e alvo no cartão e no JSON de compilação de SH05. |
| [Protocolo de julgamento](../../judgment-engine/protocol.md) | Examinar continuidade e direção em passes separados, localizar reparo e anotar o que depende de mídia. | [Revisão do piloto e estudos contrastivos](revisao-e-estudos.md). |

A referência visual de escala é a própria planta de pré-produção. O mundo do terminal é ficcional. Para filmar em local real, a produção deverá verificar o espaço, a segurança e a operação do local antes de encenar a multidão.

## Entregas e percurso

| Etapa | Artefato e situação |
| --- | --- |
| Briefing, repertório, seleção e idea | Comparação A/B e decisão justificada acima. |
| Beats, engenharia emocional e roteiro | [Roteiro e mapa de beats](roteiro.md). |
| Direção, mundo, breakdown, casting, figurino e props | [Direção e decupagem](direcao-e-decupagem.md). |
| Geometria, blocking e storyboard | Planta, trabalho simultâneo, folha de continuidade e SH01–SH10 em [Direção e decupagem](direcao-e-decupagem.md). |
| Cinematic Plan SH05 | [Cartão de direção](focal-card.json) e [entrada para compilação](focal-shot.json). Modelo manual pretendido Seedance 2.5, modo texto para vídeo, 8 s. |
| Diagnóstico, correção e reavaliação | Revisão de construção em papel e dois [estudos contrastivos](revisao-e-estudos.md). |
| Previs, compilação, troca de modelo, exportação, importação, controle e retomada | [Geometria em metros](geometry.json), [prévia esquemática de 8 s](SH05-animatic.mp4) e [fluxo executável](run-pilot.py). Use `python -B examples/pilot15/run-pilot.py --workspace PASTA_NOVA_FORA_DA_SKILL`. Os recibos guardam as comparações, o plano de importação local e a recuperação. |

O teste textual pode verificar objetivos em conflito, sucessão dos estados, coerência do eixo e continuidade escrita. Peso encenado, leitura da multidão, inteligibilidade sonora, suficiência dos tempos e impacto artístico permanecem pendentes de material ou ensaio.
