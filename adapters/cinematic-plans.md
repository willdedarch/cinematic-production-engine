# Da intenção ao plano que será solicitado ao modelo

Ler o roteiro e o estado aprovado antes de preencher o adaptador. O catálogo informa controles e papéis suportados. A direção define sujeitos, gesto, espaço, informação, fonte e consequência. O plano textual é uma solicitação que precisa ser confrontada com o vídeo retornado.

Uma especificação antiga com intent continua válida. Para vídeo, cinematic_plan é opcional e acrescenta objetivo, espaço, pessoas nomeadas, duração e beats. Cada beat identifica intervalo, participantes, ação observável, atuação, atenção, câmera, som e estados de entrada e saída. Ações simultâneas podem estar no mesmo beat com os participantes nomeados.

O compilador verifica duração, sujeitos, referências efetivamente anexadas e saltos de estado conhecidos. Não transforma objetivo abstrato em atuação convincente. Uma exceção de continuidade precisa da justificativa escrita e segue para revisão humana. Espaços sem ação descrita geram avisos em vez de ações inventadas.

## Escolher a organização por rota

| Rota | Preparação cinematográfica | Limite que exige inspeção |
| --- | --- | --- |
| Seedance omni | Fixar papel de cada imagem e mídia. Narrar o estado inicial e a transformação com pessoas nomeadas. Separar o que começa no quadro e o que entra depois. | Referências válidas não garantem identidade, contato ou cronologia. Regras do modo devem vir do catálogo atual. |
| Seedance edit/extend | Conservar origem e hash, indicar região temporal e mudança pretendida. Reconhecer quais controles o modo ignora. | Uma extensão pode repetir o fim em vez de continuar a ação. Comparar a junção e o novo estado. |
| Kling | Usar o início suportado e descrever o que muda sem inventar um papel de imagem final. | Conferir inversão de ação e o deslocamento do eixo na mídia. |
| MiniMax | Organizar imagem inicial/final e áudio conforme dependências nativas retornadas. | Dois extremos corretos não comprovam gesto intermediário ou sincronismo. |
| Wan | Proteger início, estado final e intenção sonora com as dependências realmente conhecidas. | Dependências não publicadas continuam desconhecidas. |
| Seedream, GPT Image, Nano Banana e FLUX | Para still, declarar função da imagem, identidade, lado visível, acesso, fonte e material. Referência de personagem, de cenário e de encenação têm funções distintas. | Uma ficha com dois perfis repetidos falha mesmo que o prompt peça lados opostos. A câmera e a luz devem ser observadas no quadro. |

## Exemplo executável

Use examples/prompt-specs/seedance_cinematic.json. O gesto muda da mão fechada à oferta e à reação. O estado da manta passa de um beat para outro, enquanto o irmão conserva posição. Uma troca de mão sem ação intermediária é recusada antes da exportação.

Oito modelos foram consultados gratuitamente no catálogo em 24/11/2026 nesta revisão. Nenhuma chamada de geração desses modelos foi executada. O laboratório nativo de imagens do chat tem seu próprio registro de autorização e avaliação.
