# Comparação de takes

No Studio, abra **Comparar takes**. O seletor **Estudo de exemplo** apresenta três pares locais com imagem e som. Abra um par, reproduza os dois takes, alterne o áudio e pause no instante decisivo. **Marcar este instante** cria uma marca pontual. Para incluir contexto, defina o início e o fim em posições ao redor dela. As letras A e B continuam ligadas aos mesmos arquivos quando se inverte sua posição na tela.

Escolha A, B, empate ou rejeitar ambos. Escreva o motivo, defina onde essa preferência deverá valer e prepare a nova mensagem. Ao receber um voto de produção, o agente relê o estado, confere o par original, os arquivos e as versões vigentes e prepara a alteração autorizada. Ele confirma a gravação somente após escrever e reler os dados e o histórico pelo conector existente. O exemplo do painel já contém a mídia dos três estudos para uso offline.

| Estudo | O que observar nos dois takes de 6 s |
|---|---|
| COM-01 · comédia | Uma marca surge aos 2 s. A resposta visual e a batida sonora chegam aos 2,30 s em um take e aos 2,82 s no outro. Observe se a pausa permite antecipar a resposta. |
| DOC-01 · documentário | A imagem muda aos 3 s em ambos. O som entra aos 2,65 s ou aos 3,45 s. Compare quando o ouvido anuncia a mudança espacial. |
| SUS-01 · suspense | O som surge aos 2 s. A forma que o explica aparece aos 2,25 s ou aos 3,25 s. Compare quanto tempo a informação permanece em aberto. |

Os seis MP4 são exercícios originais com formas gráficas e um sinal sonoro. Cada par possui um manifesto com os dois hashes, a identificação de registro, a revisão, a versão do material e a duração. As letras foram atribuídas ao preparar o par. O arquivo `demo-state.json` contém somente o estado local do ensaio. Nenhum dos estudos vem com preferência humana atribuída.

## Como preparar um par de produção

1. Cadastre dois takes no registro de artefatos do mesmo episódio com origem, direitos e SHA256. Na leitura atual, obtenha o ID e a revisão de cada registro. A versão do conteúdo e a revisão do registro serão preservadas separadamente.
2. Prepare o pedido abaixo substituindo os identificadores e caminhos pelos do projeto. Um arquivo de imagem fica como quadro estático. Áudio ou vídeo precisa ter duração legível pelo FFprobe disponível. Para fotografia, o agente usa Pillow para verificar o arquivo.

```json
{
  "project_id": "SERIE",
  "episode_id": "SERIE-EP2",
  "question": "Qual pausa permite perceber que Lia percebeu a mentira?",
  "takes": [
    {"id":"TAKE-017", "revision":3, "path":"./takes/reacao-curta.mp4"},
    {"id":"TAKE-021", "revision":1, "path":"./takes/reacao-longa.mp4"}
  ]
}
```

3. Use `python scripts/cpe.py take-pair --workspace PASTA_DE_TRABALHO --snapshot LEITURA.json --input PEDIDO.json`. Guarde o `result.json` do comando. Ele é o par de referência do agente. O arquivo não embute o material do usuário.
4. No [comparador](../../panels/takes.html), carregue esse manifesto e selecione os dois arquivos. A conferência dos hashes atribui A e B independentemente da ordem de seleção. Um arquivo substituído solicita reapresentação. O relógio para no fim do take temporal mais curto. Para duas imagens estáticas, a marca é 0 s. Os controles de áudio permitem alternar o take audível mantendo a posição comum. A decodificação dos formatos disponíveis depende do navegador.
5. Para registrar a escolha, o agente chama `take-vote` com uma **nova leitura** e um objeto com `manifest` (o manifesto retido), `vote` (a mensagem recebida) e `authorization` (mensagem real, ator identificado, autorização para registrar). Ambos os arquivos são conferidos novamente. Se o registro contiver um endereço remoto, fornecer em `paths` um mapa de ID para a cópia local autorizada de cada take. O agente precisa identificar a mensagem humana no host.

```text
python scripts/cpe.py take-vote --workspace PASTA_DE_TRABALHO --snapshot NOVA_LEITURA.json --input REGISTRO_DO_VOTO.json
```

O plano acrescenta o par em Examples, o resultado em Pairwise Comparisons e a preferência em Human Feedback. O registro inclui início, fim e instante decisivo em milissegundos, motivo, escopo de reutilização, mensagem de origem e as duas versões com hashes. A, B, empate e rejeitar ambos descrevem uma escolha relativa ao par. Aprovar uma versão definitiva requer a decisão específica sobre a entrega. Reenvio da mesma mensagem e par usa o mesmo identificador de operação para reconciliação.

Na retomada, uma preferência sobre os takes vale para aqueles materiais. Uma preferência de episódio fica no episódio e a de projeto pode orientar outras cenas da série. O agente mostra a origem e o trecho antes de usar a preferência. A métrica de aprovação/rejeição usa votos binários com mensagem verificada e avaliação ligada à mesma versão. O relatório explica as exclusões, inclusive as preferências relativas.

Ao iniciar outra cena, o agente traz da planilha os votos e os pares vinculados nos episódios pertinentes da série. Em `task`, `target_ids` identifica os takes em revisão. Em `judge`, o alvo já vem identificado no pedido. Assim, uma preferência restrita à entrega aparece quando a versão correspondente volta a ser examinada, uma preferência de episódio acompanha novas cenas daquele episódio e uma preferência de projeto atravessa episódios. O agente recebe o intervalo, o instante, o motivo e a mensagem de origem. Uma referência encontrada na planilha aparece como `SHEET_MESSAGE_REFERENCE`. O estado `HOST_VERIFIED` exige que o agente tenha conferido a mensagem correspondente e a incluído em `confirmed_messages`. Ensaios aparecem como `TEST` e precisam de escopo de teste explícito. O julgamento reservado para medir desempenho sem exemplos (`holdout`) omite as preferências anteriores.

## Recuperar um rascunho do Studio

**Exportar rascunho local** salva a etapa aberta, os dados dos painéis auxiliares e uma cópia da base. Em outra sessão, use **Importar cópia ou restaurar rascunho**. As notas voltam e a autorização precisa ser expressa novamente. Importe então a leitura atual do mesmo episódio. Se mudaram dados do episódio, do projeto compartilhado ou da biblioteca, o painel mostra registros, revisões e campos alterados. Você pode conservar as anotações e reconferir marcas, referências e votos ou escolher a leitura atual e descartar o rascunho. Mudanças em outro projeto sem relação permitem retomar diretamente. Arquivos de rascunho da 1.1 que contêm apenas as fases também são aceitos.
