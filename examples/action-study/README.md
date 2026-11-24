# A última frequência

Estudo independente de **guerra ficcional com ação dominante**, com 100 segundos previstos. Durante o confronto num observatório litorâneo, uma locutora tenta transmitir um depoimento antes que o prédio perca a circulação e a última ligação com a praça. O projeto, as facções, as pessoas e o conflito são inventados. A seleção é interna ao estudo e não equivale a aprovação artística.

## Três propostas iniciais

| Proposta | Motor, acontecimento e aposta |
| --- | --- |
| **A última frequência** | Uma transmissão disputa tempo com o colapso de um observatório em confronto. A locutora precisa decidir quais vozes manter no relato enquanto duas posições adversárias se aproximam. O confronto muda a história quando o homem que a deteve a retira do piso que está cedendo. |
| **O lado de baixo** | Durante um confronto sobre um bondinho industrial, uma mecânica perde o último carro vazio e precisa retornar a um carro pendente com um antigo rival. O motor é vertical, de massa e suspensão. A aproximação física tem custo imediato, e o clímax troca a pessoa que controla a posição pela pessoa que sustenta o outro carro. |
| **O salão espelhado** | Numa cidade em guerra, uma testemunha procura a companheira entre grupos em confronto num antigo teatro de espelhos. Entre reflexos quebrados e entradas simultâneas, uma queda diante da plateia redefine quem ela realmente deve seguir. O motor é informação visual sob pressão e a confiança precisa mudar com o reconhecimento. |

## Discussão e seleção

- **A última frequência** alterna progressão física e mudança de aliança sem abandonar o mesmo espaço. O passadiço, a lateral do salão e o console geram estados irreversíveis que podem ser auditados entre planos. O risco é transformar a fita em explicação. A revisão deixou a revelação curta e fez Daro participar fisicamente do resultado antes de falar.
- **O lado de baixo** oferece a trajetória corporal mais distinta. Sua leitura depende da relação entre planos altos e baixos, do peso e da identidade dos carros. A discussão recomendaria ensaiar primeiro as trajetórias, depois os diálogos. Cabe em outro estudo cujo foco seja continuidade de movimento em altura.
- **O salão espelhado** pode fazer o espectador descobrir a informação junto da testemunha. O risco é interpretar a omissão de um efeito físico como mistério: o encontro e a queda precisam de enquadramento inequívoco. Reservado a um estudo que possa validar os reflexos na mídia.

A primeira proposta foi escolhida para este estudo. Ela permite examinar o acontecimento visível, o dano acumulado, a atuação proposta, a passagem entre escalas e a continuidade sem depender de um segundo cenário. Os motivos acima vêm de passes de desenvolvimento no mesmo contexto. A revisão independente deve pronunciar-se separadamente.

## Material de trabalho

| Material | Conteúdo |
| --- | --- |
| [Roteiro](roteiro.md) | Texto literário, falas, ponto de virada e encerramento. |
| [Mapa de acontecimentos](episode-intent.json) | 14 acontecimentos em 12 planos. 65 s de ação física visível e 35 s de história. |
| [Direção e decupagem](direcao.md) | Mapa emocional, elenco, fotografia, atuação, espaço, storyboard, montagem e som. |
| [Geometria](geometry.json) | Implantação e âncoras do plano focal numa locação ficcional. |
| [Plano focal](focal-shot.json) | 12 s contínuos em três beats. Cada beat mantém seu ID do mapa, ação localizada e estado de saída. |
| [Revisão](revisao.md) | Diagnóstico, reparos e rechecagem textual. Exigências para julgar uma mídia futura. |
| [Percurso local](run-study.py) | Prepara cópia de teste, confere intenção, recupera a rota, monta a decupagem e exporta Seedance e MiniMax pelo fluxo oficial. |

Inicie o percurso com `python -B examples/action-study/run-study.py --workspace PASTA_NOVA_FORA_DA_SKILL`. Os recibos, comparações e arquivos gerados vão para essa pasta. O estudo é de pré-produção. Tempos, cena, montagem e som são planejados. A percepção do esforço, do impacto, da continuidade e da intensidade permanece por confirmar em mídia encenada.
