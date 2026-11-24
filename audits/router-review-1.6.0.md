# Auditoria de recuperação e viés narrativo

Escopo reproduzido diretamente no código oficial 1.5.0, commit `6ef740286ff61bc553d6d6ae18428beb0011382f`. Esta verificação reproduz o comportamento de recuperação. A repetição gerativa de determinado enredo depende também das decisões que o agente e o diretor tomam no projeto.

## Causa reproduzida

1. `route('G2', [rótulo])` devolveu condições vazias e `examples/last-water/production.md` para Histórico, Drama, Ação, Terror psicológico, Ficção científica, Épico, Noir e Realismo. O arquivo de perfis já citava vários desses gêneros. O roteador reconhecia só rótulos em um pequeno grupo de condições e casos com aliases coincidentes. A G2 usava o mesmo estudo de partilha como exemplo geral.
2. `Guerra de ação` carregou `A última água` e `A linha azul`. A função `matching_genre_cases('war')` selecionou `A última água`, cujo cartão trata de partilha e cuidado. A rota não distinguia a intenção de guerra orientada por ação. `O pano vermelho` e `A linha azul` são estudos de pressão e travessia, com o combate fora de quadro. O recuperador indicava ambos em gênero de guerra sem uma escolha de escopo.
3. `G10` podia carregar a montagem de travessia, o estudo de evacuação e um exemplo de adaptador de mantas para um briefing de ação. A lista compartilhada ainda podia priorizar o registro didático integrado por departamento ou similaridade lexical, sem confrontar a finalidade com o pedido.
4. `modules/character-engine.md`, `modules/viral-intelligence.md` e `engines/virality-lab.md` ficavam sem rota. O comando natural `ANALYZE` não resolvia uma etapa. A camada de crítica comparava rótulos do gênero por texto exato, com risco de retomar outro repertório após a criação.

## Correção e evidência

- Perfis públicos com 21 gêneros e estilos e aliases bilíngues. O casamento local escolhe a expressão mais específica e conserva a ordem do briefing, inclusive os gêneros secundários. `genre_example`, `genre_profiles`, `genre_cards` e `rubrics` expõem a seleção efetiva. Os documentos recuperados têm hash da leitura. O [inventário dos estudos](../examples/narrative-index.md) separa estudos autorais de fontes, exercícios diagnósticos e aprovações humanas.
- `action_led_war` no perfil de um projeto de guerra, uma combinação de rótulos orientada por ação ou uma intenção de ação física afirmativa redireciona os exemplos. O resultado registra o modo de recuperação e os casos selecionados. A distribuição de tempo e os acontecimentos protegidos são responsabilidades do plano aprovado e da sua validação, sob seu próprio contrato.
- O recuperador prefere `A última frequência` para ação e exclui exemplos compartilhados identificados como estudos de partilha, abrigo ou evacuação. Uma escolha explícita de sobrevivência ainda consegue recorrer a `A última água`. Referências aprovadas dentro do projeto continuam vinculadas ao contexto e à sua origem.
- `ANALYZE` recupera o laboratório de atenção, a leitura audiovisual e a rubrica de retenção. O Character Engine aparece nos gates onde escolhas, interpretação ou identidade são entregas efetivas. A contagem de público depende de dados reais e denominador.

Os testes em [test_routes.py](../evals/test_routes.py) exercitam português e inglês, gêneros compostos, intenção de ação e intenção negada, escolha de exemplo, relevância da biblioteca e o comando `task --task ANALYZE` através do Context Engine. O registro de regressão independente da distribuição consta no relatório principal da versão.
