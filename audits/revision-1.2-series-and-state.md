# Revisão cruzada da bíblia e do estado compartilhado

## Série

O ensaio de dois episódios executou seis planos, seis pacotes manuais de prompt e a importação de um arquivo audiovisual local em estado de revisão. A leitura de abertura do EP2 conseguiu remontar sete fatos do EP1, consultar a proposta pendente e identificar a decisão, sua revisão, a mensagem de origem e o motivo de cada fato. Os dados de roteiro e decisões do ensaio são fictícios.

A revisão encontrou e corrigiu três problemas. Um projeto podia conter dois episódios com o mesmo número. Um registro antigo sem cena podia antecipar uma revelação em consulta limitada a um ponto do episódio. As vinculações técnicas de arquivos apareciam entre as decisões de história. O leitor passou a rejeitar a cronologia ambígua, a usar apenas decisões temporalmente conhecidas na consulta por cena e a deixar as vinculações técnicas nos planos correspondentes.

Os sete testes de `evals/test_series_release.py` verificam essa cronologia, a separação entre produção e ensaio, fatos por personagem e por público, o roteiro de continuidade, a seleção motivada de referências e os produtos do ensaio. A suíte também confere que iniciar o episódio seguinte mantém as versões anteriores e prepara as 16 etapas e os 53 itens desse episódio.

## Estado e aprovações

Foram lidos os contratos de uso da planilha, a reconstrução das leituras, o preparo de mudanças, o verificador de aprovações e o código que gera e recompõe o histórico. A revisão encontrou confirmações que ainda podiam passar com o episódio, escopo de teste, operação, executor ou ordem temporal trocados. Os registros de preparo e confirmação agora precisam identificar a mesma operação e o mesmo escopo. Cada confirmação ocorre depois de todas as partes do preparo e até o instante da leitura que a observou. A mesma verificação impede que uma confirmação incoerente libere outra alteração sobre o mesmo material.

Os seis testes de `evals/test_journal_event_scope.py` cobrem essas condições e leem as cópias históricas de três verificações nativas anteriores ao pacote. A revisão preservou o formato antigo em que o evento está associado à série inteira. A suíte de revisão de regressões passou em 21 casos. A suíte de integridade passou em 14 casos no momento da revisão e inclui rejeição de aprovação com bytes ou versões de outras entregas, exigência de observação no controle de qualidade, cobertura de revisão para múltiplas entregas e preservação dos registros de histórico.

O contrato da planilha documenta a paginação, a autorização por mensagem, as releituras, o formato das partes extensas e a retomada de operação interrompida. Estas verificações usaram cópias locais e registros históricos. Uma escrita feita hoje depende de confirmação própria pelo conector na interação em que ocorrer. A comparação otimista mantém uma janela de concorrência entre a releitura e a escrita.
