# Revisão da Cinematic Production Engine 1.4.1

A auditoria da 1.4.0 encontrou dois recursos desconectados do fluxo principal. A candidata corrige ambos e adiciona material para o primeiro piloto de ação. O contrato das 35 tabelas continua 3.1.0.

| Apontamento | Resultado nesta revisão |
| --- | --- |
| Roteamento de guerra e exemplos repetidos | `task` recupera guerra mesmo em gênero misto. `guerra`, `war` e `FEB` recuperam a mesma base pública. A etapa escolhe um exemplo, e o pedido pode especificar departamento, finalidade, problema e modelo. O recibo de contexto mostra a seleção e os hashes efetivamente recuperados. |
| Exportação perdia plano temporal | `shot-handoff` inclui blocos autorados, confere duração e estados ligados ao plano e mantém o manifesto de referências. Uma identificação de versão em `shot` é conferida contra a leitura corrente. Exportações anteriores sem plano continuam válidas. |
| Ação de guerra precisava de ensaio | [O pano vermelho](../examples/war-action-pilot/README.md) tem dois cortes de 30 segundos com áudio. Testa orientação, desorientação, ações simultâneas e a perda que persiste. O combate está fora de quadro. A imagem esquemática permite comparar encenação e montagem, e a qualidade de atuação e fotografia segue por testar. |
| Julgamento e generalização | [Comédia e documentário](../examples/benchmark141/README.md) trazem versões comparáveis e reparos localizados. O passe crítico ajudou a ordenar uma reação, sem desempatar o timing da revelação cômica. São dois casos textuais cumulativos, com autor e crítico no mesmo contexto dentro de cada caso. |
| Exemplos de modelo | [Planos temporais](../adapters/cinematic-plans.md) incluem quatro exemplos que compilam localmente, com tratamentos diferentes de imagem inicial e som. As capacidades refletem o catálogo congelado. Cada exportação definitiva continua manual. |
| Log publicado com 208 testes | O nome antigo foi substituído por uma indicação histórica. [Resultados desta candidata](../evals/RESULTS.md) apontam para as evidências atuais. |
| Calibração, painéis e hooks | A comparação A/B pode receber decisão específica do diretor. Referências positivas ainda requerem aceite explícito. Os controles foram exercitados em simulação. A homologação pelo diretor e o acionamento nativo dos hooks continuam por confirmar. |

## Execução e limites

Suíte executada na árvore e depois da extração do ZIP. As regressões usam `cpe.py task` com episódio sintético de suspense e guerra e `cpe.py shot-handoff` com material ligado ao cartão do plano. O pacote não contém respostas privadas, dados da conta ou material de produção. Os ensaios e as exportações não usaram créditos externos.

O suporte a Google Sheets continua por interação. A gravação exige autorização, checagem de revisão e releitura de dados e histórico. Os ensaios ficaram em arquivos locais. O painel da conversa continua a interface primária. O HTML acompanha o pacote para revisão complementar.
