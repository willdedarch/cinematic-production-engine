# Cinematic Production Engine 1.5.0 · auditoria corretiva

A candidata local parte da 1.4.1 publicada no commit `9b55e5ad25dc17fabc4c750a1381712c1e903a34`. Esta revisão corrige os defeitos reproduzidos localmente e registra as verificações que dependem de conta, host ou decisão de direção. O contrato compartilhado permanece em 3.1.0. O pacote original V3 e a distribuição 1.4.1 foram preservados.

| Frente | Mudança | Verificação e limite |
| --- | --- | --- |
| Recuperação de repertório | Seletores canônicos para aliases em português e inglês, gêneros secundários, departamento, tipo de entrega, problema e complexidade. Guerra recupera estudos por etapa. | Os testes percorrem os 16 gates e o caminho `task`. No piloto, a curva da fila, o gesto focal e o estado final demonstram aplicação no plano. A leitura do arquivo só comprova recuperação. |
| Plano e continuidade | O cartão alerta quando o estado de saída deixa de aparecer no plano seguinte. A linha do tempo explicita ações simultâneas e exige as entradas e saídas protegidas no primeiro e último beat. | Omissão de fatos, duração diferente, pacote em outra planilha e versão desatualizada têm regressões próprias. Estados estruturados conferidos seguem para revisão do gesto no take. |
| Pacote e retorno | Um pacote mantém direção, prompt independente, adaptação, geometria, elementos vinculados, referências, condições e critérios em campos próprios. `shot-compare` verifica o retorno. `shot-import` prepara o registro com proveniência declarada e status `REVIEW_REQUIRED`. | A mesma intenção foi exportada para Seedance e MiniMax. A prévia local de 8 segundos corresponde às medidas de vídeo. O vídeo de outro estudo foi recusado no fluxo vinculado. A conferência local não implica geração de provedor, sincronia, gravação remota nem aceite. |
| Painel A/B e feedback | O voto identifica o par e a versão exibida. O CLI distingue mensagem citada de origem humana confirmada e exige escopo explícito em julgamento de alvo de teste. | A regressão rejeita o fingerprint antigo na apresentação invertida. Testes de interface usam DOM, armazenamento e relógio de mídia simulados. O piloto humano da 1.4.1 foi conduzido no chat e pertence àquele ensaio. |
| Modelos e fontes | As orientações manuais variam conforme formato, modo e função dos anexos. Releitura gratuita de oito modelos pelo catálogo. Cinema Studio mantém formulário de fluxo próprio. | A atualização valida os dados retornados pelo conector, sem homologar a interface web nem a qualidade de uma geração. A [revisão de fontes](../sources/review-1.5.md) diferencia leitura, hipótese, aplicação e teste. |
| Julgamento | Três estudos textuais comparados em duas ordens. Revisão do experimento anterior e registro de critérios, exemplos e divergências. | Um parecerista na rodada nova e zero votos humanos. Os dados não estimam viés de posição isolado ou efeito sobre público. Consulte o [relatório comparativo](../benchmarks/review-1.5.md). |
| Hooks, custo e privacidade | Resposta de erro adequada ao evento de encerramento, recibos mínimos, leitura de marcadores também em UTF-16 e arquivos Office compactados. | Chamadas locais dos scripts e inspeção do pacote. O despacho dos hooks depende da revisão de confiança do host. Zero créditos, chamadas de geração pagas ou instalação de dependência. |
| Estado compartilhado | Leitura nativa de metadados da planilha Força antes e depois de seis intervalos delimitados. A carteira de estado mantém leitura por interação, guardas otimistas e confirmação por releitura. | As duas leituras de metadados concordaram e as 39 abas estão acessíveis. A leitura delimitada foi uma prova de conexão e cabeçalhos. A leitura completa de produção continua obrigatória a cada interação. Esta candidata fez zero escritas na planilha. |

## Piloto integrado

[A linha azul](../examples/pilot15/README.md) cobre briefing, repertório, referência, propostas, narrativa e roteiro, direção, fotografia, casting, figurino, geografia, objetos, composição de grupo, continuidade, decupagem e montagem em papel. A versão executável usa os comandos da Skill para preparar uma cópia sintética, recuperar conhecimento, consultar cartão e storyboard, conferir a geometria, compilar, comparar a mídia, preparar a importação, abrir um pacote de julgamento e recuperar o estado local. A prévia esquemática permite observar a mão desocupar antes de a personagem receber o peso da outra. O teste documenta atuação, presença, efeito sonoro e reação do público como pendências. O diagnóstico e a reavaliação artística dos casos complementares são leituras de texto.

O Blender 5.4.0 Alpha renderizou e reabriu o cenário de teste em processo separado. A inspeção do primeiro quadro mostrou o caderno perto da borda e dois volumes sobrepostos. A revisão manteve a câmera em 35 mm, colocou o marcador do caderno inteiro no quadro e separou os quatro volumes. O resultado verifica implantação e enquadramento estático. A sessão que já estava aberta permaneceu em execução.

## Revisão e verificação

- [Auditoria inicial independente](audit15-initial.md) e [matriz de 144 requisitos](audit15-coverage.csv), que registram a situação da tag 1.4.1 no início da auditoria.
- [Reteste independente da candidata](audit15-independent.md), seguido de regressão adicional para prefixo longo em UTF-16 sem BOM. O verificador de distribuição procura padrões conhecidos e depende de inspeção complementar.
- [Evidência das consultas nativas](connector-readback-1.5.json) sem exportar linhas ou a identidade da conta.

## Homologações pendentes

Na tentativa real dos hooks, o host manteve configuração de projeto sem confiança e a inicialização isolada apresentou um erro de identidade do pacote Windows. A execução direta por stdin comprova comportamento do script. A ativação e a observação dos eventos nativos exigem a decisão de confiança já solicitada. A mesa HTML continua complementar. Não houve homologação em navegador real nem escuta do comparador desse pacote no navegador.

O histórico principal e as releases visíveis do GitHub estão saneados. Uma consulta anônima observou HTTP 200 para um endereço histórico fora dessas referências. A retirada de referências públicas e a remoção dos objetos acessíveis são verificações distintas. Há um pedido privado de remoção preparado, pendente de autorização de envio e ação do GitHub. A publicação e a instalação públicas continuam na 1.4.1.

O piloto, a revisão independente e os testes de distribuição são evidência técnica. O diretor ainda precisa decidir sobre qualidade artística do material e critérios da produção. Uma aprovação ou gravação futura exige autorização e releitura no destino efetivo.
