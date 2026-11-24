# Conduzir uma série na 1.2

## Começar o próximo episódio

Ao receber «começar EP2», leia o projeto no Google Sheets, identifique o último episódio e apresente a passagem de continuidade. Em projeto existente, use `new-episode` com o identificador real do projeto, título, duração e autorização recebida. O plano cria apenas o episódio e seu próprio fluxo. O próximo número segue o maior já registrado. Quando o pedido deixar a série ou a mudança ambígua, mostre a passagem sem gravar até esclarecer a decisão.

Mostre separadamente o conhecimento do público e o de cada personagem, as relações, os objetos, as locações e as perguntas em aberto. Cada fato registrado traz episódio, momento, motivo e decisão de origem. Uma nova conclusão sobre o mesmo assunto precisa apontar o identificador da decisão anterior. Uma hipótese continua em propostas. Decisões antigas em texto livre permanecem disponíveis para o agente propor sua estruturação junto ao diretor. Para uma cena intermediária, preserve a posição na história e evite antecipar revelações.

O agente transforma os pressupostos de uma cena em afirmações verificáveis. Por exemplo, se Davi diz «foi a vizinha que buzinou», consulte o que **Davi** sabia até aquela fala. `scene-check` compara personagem, assunto e valor. Uma contradição recupera a decisão de origem. Uma informação sem fato registrado pede interpretação do diretor. A ferramenta não infere sozinha a semântica de um roteiro livre.

Use `bible` para leitura, `canon-plan` para propor ou registrar fatos autorizados e `briefing-view` para entregar o HTML do episódio. O número de linha de um link do Sheets reflete a consulta. Depois de ordenar a planilha, refaça a leitura e localize pelo ID. Os exemplos incluídos são simulações.

## Levar um plano até a montagem

Abra `shot-card` para ver intenção, ação, duração, som, câmera, entrada e saída, versões das referências e take escolhido. `storyboard` reutiliza esses dados. Uma divergência entre planos pede explicação, transferência em quadro ou ajuste. Para «o que muda se Lia trocar a mão?», use `shot-impact` e examine os vínculos registrados. Peça ao diretor que identifique dependências editoriais ainda implícitas. Uma exceção documentada preserva os dois estados e o motivo.

Aplique `shot-repair` com o impacto exibido, o campo e as versões que foram examinadas. Preserve ativos aprovados criando sucessores. Em `shot-handoff`, selecione um modelo do catálogo, confira a interface na data da produção, leia o pacote por plano e entregue as referências nos campos indicados. O retorno manual passa por `shot-import`. Ele entra em revisão com origem, direitos, arquivo, hash e plano de origem. Escolher um take para montagem deixa pendentes seus critérios de aprovação final.

## Comparar takes e aprender o gosto do diretor

Use [Comparar takes](../panels/takes.html) ou apresente os arquivos acessíveis à pessoa e registre sua escolha por mensagem. Guarde o manifesto do par apresentado, a identidade e a revisão das duas mídias e o intervalo. Por exemplo, «B, de 3,8 s a 4,6 s, porque a pausa aos 4,2 s deixa a dúvida aparecer. Vale para este episódio». Empate e rejeição dos dois também são escolhas possíveis. Recupere a preferência apenas dentro do escopo indicado e conserve as opiniões divergentes.

Cada voto autorizado usa Examples, Pairwise Comparisons e Human Feedback. Cada fato narrativo é uma decisão em Decisions. Os vínculos entre materiais usam decisões tipadas e referências já existentes. O procedimento de gravação e releitura continua o mesmo. [Guia do comparador](../examples/takes/README.md) · [Integridade do estado](../integrations/state-integrity-1.2.md).

## Experimentar sem alterar uma produção

Abra a [bíblia de exemplo do EP2](../examples/series-worked/EP2/episode-guide.html) ou os [cartões de seis planos do EP1](../examples/series-worked/episode-guide.html). Para reproduzir a história completa em uma pasta vazia, execute `python -B examples/series-worked/run.py PASTA_DE_ENSAIO` a partir da raiz do pacote. Para um projeto real, peça ao agente a mesma visualização com uma nova leitura da sua planilha.

