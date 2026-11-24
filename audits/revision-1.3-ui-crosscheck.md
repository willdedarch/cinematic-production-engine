# Revisão da mesa e do comparador

Em 24 de novembro de 2026 foram reproduzidos os percursos com a leitura do ensaio nativo “A última água”, EP2. A leitura de 14h17min22s UTC tinha seis planos. O percurso pelo publicador e pelo comparador verificou os bytes das seis imagens, as duas mídias da apresentação retida, a recuperação da anotação ao reabrir a mesa e o endereço estável do projeto. Na mesa, Davi e o público tinham informações diferentes antes da revelação. O conhecimento de Davi mudou na posição narrativa 68.

A leitura nativa de 14h21min59s UTC continha a preferência sintética B em SH06. A projeção recuperou o intervalo de 3,8–4,6 segundos, a marca de 4,2 segundos, as duas versões apresentadas e o alcance de cena. O registro de origem foi `HF-325f3b4b3bd0ebe74d3e83db38a3`. A preferência apareceu confirmada pela operação do ensaio.

## Correções verificadas

- O cartão reconhece a lista de decisões que justificam uma mudança de continuidade. O diretor pode abrir a decisão de origem.
- A volta ao plano conserva a anotação local. Preferências confirmadas, votos pendentes, versões anteriores e take escolhido para montagem possuem estados próprios.
- O cartão mostra o motivo da ausência de uma miniatura. Um rótulo curto identifica o plano na faixa de quadros, enquanto a revisão continua disponível no detalhe.
- O comparador preserva a ação padrão de links, botões e campos e descarta a repetição automática de uma tecla pressionada. O teste de transporte verifica o trecho marcado e a troca de fonte de áudio.
- Mídia grande passou a ser materializada com hash e verificada integralmente na publicação. Uma cópia auxiliar local corrompida é recomposta. Referência remota, UNC, arquivo substituído ou indisponível resulta em mensagem na interface.
- Uma pasta privada para o agente pode publicar a mesa em destino separado. Um novo teste assegura que a entrega contém apenas a visualização e seus recursos.
- O nome do personagem no roteiro abre sua ficha com a fala e os fatos anteriores ao episódio. No formato Fountain foram conferidos o marcador de voz, a fala dupla, um nome forçado e a preservação integral de maiúsculas, espaços e quebras de linha. A troca de plano permite selecionar uma posição narrativa documentada. A ficha fecha devolvendo o foco ao mesmo nome e uma nova consulta começa no ponto de corte inicial.
- Na projeção da leitura de 14h30min15s UTC, a fala nativa “DAVI: Quem chegou?” abre com “identidade desconhecida” para Davi e “Rosa está na estação” para o público. Ao selecionar SH06, a revelação continua ausente até a escolha expressa da posição 68. Só então aparece “é Rosa”, com a decisão de origem. O teste também verificou as legendas de continuidade “Saída de SH05” e “Entrada de SH06”.

## Alcance

Os controles usados são os JavaScript de distribuição. Rodaram 29 verificações da oficina de 37 painéis, 24 da mesa e 20 do comparador com objetos controlados de DOM, armazenamento e tempo de mídia. A execução adicional da mesa com a projeção do ensaio e o percurso da fala completou 26 verificações, incluindo as 24 da suíte comum. Os dez testes específicos do publicador também passaram. A revisão de CSS conferiu quebra de colunas, rolagem horizontal da faixa, foco visível, espaço para rótulos e reorganização do comparador nos pontos de corte de 750 e 520 pixels.

Esses ensaios cobrem lógica e integridade. O enquadramento visual, a navegação com teclado real, a sincronização acústica percebida e a reprodução pelos codecs dependem de verificação no navegador autorizado. O aceite visual cabe ao diretor.
