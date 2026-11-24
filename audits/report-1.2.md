# Cinematic Production Engine 1.2 — implementação e revisão final

**24 de novembro de 2026.** A versão 1.2 incorpora a revisão da 1.1, acrescenta a bíblia viva e a comparação audiovisual de takes e preserva o ZIP 1.1 e a base V3. A planilha da conta usada no ensaio histórico continua sendo a fonte de estado nas interações. [Abrir planilha](https://docs.google.com/spreadsheets/d/CONFIGURE_YOUR_SPREADSHEET_ID/edit).

## As duas entregas prioritárias

**Bíblia viva.** O ensaio de *A última água* abre o EP2 com sete fatos vigentes, oito decisões narrativas na linha do tempo e uma hipótese em revisão. O público já ouviu quão pouca água resta. Lia conhece essa escassez. Davi ouviu a buzina e desconhece quem chegou. A relação evoluiu da oferta unilateral de Davi para o cuidado recíproco. Cada fato mostra pessoa ou objeto, assunto, momento da história, decisão de origem e revisão. A passagem conserva a porta oeste da estação e o cantil na direita de Lia. Uma fala que atribui a Davi o conhecimento de quem chegou retorna uma contradição com a decisão correspondente. Atribuir esse conhecimento a Lia retorna informação desconhecida. A Skill explicita os pressupostos de um diálogo para poder verificá-los.

**Comparação de takes.** O diretor pode reproduzir dois takes juntos, trocar a ordem na tela, alternar o som e marcar início, instante decisivo e fim. Escolhe A, B, empate ou rejeitar ambos, informa o motivo e onde a preferência vale. O registro vincula esses dados às duas versões e ao conteúdo dos arquivos. Uma troca de arquivo exige nova apresentação do par. No ensaio entre episódios, uma preferência de projeto chegou à cena seguinte. A de episódio ficou no EP1 e a de entrega exigiu o alvo correto. Há três pares didáticos de seis segundos com imagem e som, em comédia, documentário e suspense. Os seis vídeos foram decodificados e suas diferenças temporais foram medidas com FFmpeg. Os clips são estudos gráficos autorais. A calibração do gosto pessoal fica em aberto até haver escolhas reais do diretor.

## Correções da revisão anterior

| Área | Implementação | O que foi verificado |
|---|---|---|
| Aprovação e QC | A aprovação vincula cada entrega, revisão e conteúdo examinado. Os critérios observacionais exigem evidência. | Uma revisão de outro roteiro, observação planejada ou entrega omitida impede a aprovação. |
| Histórico e concorrência | O plano guarda o estado anterior do histórico. O agente confere operações concorrentes, partes e sequência dos eventos. Registros longos podem ser repartidos e recompostos. | Houve testes com edição de histórico, preparo concorrente, conteúdo longo com Unicode, parte ausente, evento fora do escopo e formatos antigos. |
| Novo episódio e continuidade | Criação de episódio com suas próprias 16 etapas e 53 critérios. Retomada, correção de fatos por decisão sucessora e consulta por ponto na história. | Abrir EP2 preserva EP1. Número duplicado no projeto é recusado. Uma decisão futura fica fora da resposta sobre cena anterior. |
| Studio e referências | O painel restaura rascunhos de etapas e de painéis auxiliares. Mudanças na base exigem tratar a divergência. A busca ordena referências por intenção, gênero, departamento e projeto. | Abrir a comparação não escolhe A. A consulta de locação recupera a referência relevante mesmo quando foi cadastrada por último. |
| Julgamento | A crítica separa desacordo entre pessoas de mudança de voto quando a ordem se inverte. A métrica converte feedback nativo com vínculo e origem verificáveis. | Votos de teste e preferências fora do escopo ficam fora do indicador de produção. O teste de nova cena usou escolhas fictícias identificadas. |
| Cartão, storyboard e mapa de impacto | O cartão reúne intenção, câmera, som, ação, estados, referências, take e decisão. O reparo fixa o mapa exibido, os alvos e os campos autorizados. | Nos seis planos de *A última água*, os cinco cortes mantêm a continuidade do cantil e da tampa. SH05 termina com o cantil na esquerda de Lia. Em SH06, ela o passa à direita em quadro. |
| Handoff e retorno manual | Cada plano exporta prompt, proporção, duração e referências com papel, ordem, revisão e hash. O take importado entra em revisão e fica ligado à versão de origem. | Seis pacotes de plano usam seis referências correspondentes. SH06 retorna como prévia esquemática de 10 s, com 240 quadros e áudio. O gesto precede a buzina. |
| Ferramentas e laboratórios | A inspeção respeita a janela pedida. O compilador valida campos obrigatórios e opções de PNG/GIF. Os experimentos diferenciam repetição, mudança controlada e mudanças simultâneas. | O vídeo de controle deu zero cortes até 0,4 s e cortes em 1 e 2 s até 2,5 s. Os 16 laboratórios foram exercitados, dez com resultado técnico e seis com ficha para observação humana. |
| Blender e hooks | O diagnóstico distingue aplicativo disponível, sessão pessoal conectada e resultado de um processo isolado. | Duas câmeras renderizadas, arquivo salvo e reaberto, dez objetos e movimento da CAM35 conferido. Os hooks continuam opcionais. O ensaio não os instalou. |

## Revisão independente depois das correções

A segunda passagem encontrou defeitos adicionais. Um reparo podia ser recalculado sobre uma origem que já havia mudado ou criar sucessor em outro episódio. A ordem física das linhas podia influenciar anexos com o mesmo papel. Uma preferência podia reaparecer pela busca genérica de exemplos fora do contexto autorizado. Também era possível confundir decisões técnicas com narrativa, aceitar número de episódio repetido ou confirmar histórico com escopo ou datas incoerentes. As correções foram reapresentadas aos testes, incluindo ordenação da planilha, troca de versão, intervalo de cena e passagem EP1 → EP2.

## Verificação nativa no Google Sheets

O conector existente gravou **seis registros de teste** no projeto de ensaio da conta usada no ensaio histórico. São dois arquivos registrados por referência, um fato do cantil, um exemplo, uma comparação e um feedback sintético. A escolha B corresponde ao intervalo de **3,8 a 4,6 s** com marca em **4,2 s**. Os arquivos de mídia permanecem locais. Todos os registros foram mantidos com `is_test=true`. Há zero votos artísticos atribuídos ao usuário.

A operação `CPE12-SHARED-REHEARSAL-20261124` foi lida após o preparo, após a gravação dos dados e após a confirmação do histórico. A releitura final das 35 tabelas ocorreu às **10h31min58s de Brasília**. Os seis registros estavam na revisão 1. As abas de instrução e apresentação também foram atualizadas e relidas. A planilha conserva 38 abas. [Decisão de teste](https://docs.google.com/spreadsheets/d/CONFIGURE_YOUR_SPREADSHEET_ID/edit#gid=1322208699&range=A3) · [Histórico do ensaio](https://docs.google.com/spreadsheets/d/CONFIGURE_YOUR_SPREADSHEET_ID/edit#gid=1686667430&range=A23:A24).

## Pacote, testes e limites

- **265 testes Python, 25 verificações do Studio e 10 do comparador.** A validação do ZIP inclui extração, nova execução das suítes, verificação SHA-256 dos arquivos inventariados e integridade do V3 original. O recibo externo `VALIDACAO-1.2.json` identifica o ZIP exato e os resultados dessa cópia.
- As verificações dos controles dos painéis utilizaram representação simulada do navegador. A reprodução dos vídeos, o áudio, os quadros do storyboard e o arquivo Blender tiveram conferências próprias. A homologação visual e a preferência artística pessoal permanecem pendentes.
- A sincronização acontece quando o usuário envia uma mensagem. A Skill consulta o Sheets, valida as revisões e relê cada alteração autorizada. Existe uma janela de concorrência entre a última leitura e a gravação. Uma intervenção simultânea exige reconciliação.
- O mapa de impacto considera os vínculos registrados. Uma dependência editorial apenas implícita precisa ser identificada pelo diretor ou pelo agente. Os controles de modelo devem ser conferidos na interface utilizada para a produção real.
- A entrega é o pacote 1.2 e o Studio local pronto para abrir. A instalação na lista de Skills do host é separada. Produção definitiva manual, zero créditos pagos, sem geração externa, novo conector ou servidor.

