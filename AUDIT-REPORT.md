# Auditorias da Cinematic Production Engine

## Revisão 1.6.0

A [auditoria 1.6.0](audits/review-1.6.0.md) reúne a investigação do viés de exemplos, a correção da transição do roteiro ao take, as verificações nativas e a matriz de aceite.

## Registro histórico da CPE 1.4

24 de novembro de 2026. Evolução da Skill 1.3.0 auditada, com contrato de estado 3.1.0 preservado. A arquitetura de produção, a bíblia viva, os takes e as 35 tabelas continuam disponíveis. Os painéis de apoio são apresentados na conversa; o HTML é complementar. Esta entrega corrige software e amplia métodos e evidências. O aceite artístico é uma decisão separada.

## Correções conferidas

| Área da auditoria anterior | Resultado desta revisão | Evidência e limite |
| --- | --- | --- |
| Bibliotecas externas consultadas superficialmente | Inventários recursivos de cinco repositórios, 124 documentos obtidos e 113 lidos integralmente no conjunto selecionado | [Fontes e escopo](SOURCES-REVISION-1.4.md). Onze exclusões O-Side, livros e corpus volumoso fora do escopo. Não é auditoria integral de todos os repositórios |
| Incorporação metodológica | Síntese própria aplicada e nove conflitos de heurísticas identificados, incluindo eixo, luz no espaço/tela, zoom e deslocamento | [Métodos e conflitos](knowledge/source-methods.md). Origem oficial de mirrors não autenticada |
| Biblioteca visual genérica | 21 diagramas específicos por assunto, cinco imagens nativas e três cartões profissionais com links | [Biblioteca](references/visual/README.md). Um still observado diretamente; vídeos completos não assistidos. Nenhuma redistribuição dos stills profissionais |
| Living World e guerra pouco desenvolvidos | Estado físico, objetivos simultâneos, profundidade, atmosfera causal, pressão e custo persistente | [Mundo vivo](engines/living-world.md), [guerra ficcional](engines/war-film.md), [caso de oito planos](examples/shelter/caso14-roteiro-e-direcao.md). Ficção não verificada, sem atuação filmada ou combate de grande escala |
| Estudos de direção superficiais | Relações aplicadas de arquitetura, fonte, lente, gesto, movimento e montagem, com alternativas e testes possíveis | [Estudos](knowledge/style-studies.md). Limites de atribuição explícitos; citar um cineasta não garante seu resultado |
| Compilador organiza campos | Plano temporal opcional com sujeitos, intervalos, referências e estados de entrada/saída; exemplo documental corrigido | [Adaptadores](adapters/cinematic-plans.md). Não inventa conteúdo ou garante aderência do modelo. Catálogo de oito modelos relido sem geração externa |
| Julgamento sem material real | Cinco imagens nativas, duas críticas independentes da mesma família e registro privado de decisões humanas | [Laboratório](examples/native-lab/README.md). Estudos de cena continuam reprovados; superioridade relativa não constitui aprovação |
| Calibração sem dados humanos | Registro privado imutável ligado à mensagem e ao hash dos materiais, com alcance restrito e taxa artística indefinida | [Calibração](judgment-engine/director-calibration.md). Rejeições pontuais não definem gosto global, referência positiva ou treino do modelo |
| Benchmark incompleto | Quatro condições de escrita, um brief comum e revisão textual cega em ordens inversas | [Ensaio comparativo](examples/benchmark14/README.md). Estudo exploratório de um brief, sem atuação, duração realizada ou eficácia causal demonstrada |
| Hooks incompletos | Handlers de lifecycle, gerador de configuração com backup e recibos mínimos privados | [Hooks](hooks/README.md). Confiança no host e acionamento nativo ainda exigem verificação; não há interceptação universal |
| Publicação contém ambiente anterior | Exports e journals reais retirados; fixtures novas; perfil e V3 original preservados somente privadamente; vínculo privado ignorado pelo Git | [Distribuição](integrations/public-distribution.md). Scanner complementado por revisão semântica independente. Clones e caches antigos podem persistir após limpeza remota |
| Evidências e caminhos inconsistentes | Referência impossível ao journal e receita FFconcat corrigidas; matriz de capacidades, manual, versões e fontes atualizados | [Capacidades](audits/capability-matrix.csv). Resumos históricos classificados, sem fingir nova gravação remota |

## Testes e revisão final

318 testes Python e 73 verificações dos controles passaram na árvore e novamente no ZIP extraído. As verificações de interface usam DOM e relógio de mídia simulados, com 29 na Oficina, 24 na mesa e 20 no comparador. Incluem navegação, notas por plano, intervalo, áudio, preferências, conflito e vínculos. Os testes de código cobrem plano temporal, feedback, configuração privada, privacidade e os contratos anteriores de estado e aprovação.

O validador confere sintaxe, JSON, links Markdown locais, 16 rotas, 35 entidades, compatibilidade de três journals sintéticos, referências visuais e hashes, identidade dos pacotes manuais, matriz de requisitos, inventário e padrões conhecidos de privacidade. A extração verifica caminhos e duplicatas, integridade e igualdade dos arquivos. A decodificação dos exemplos de vídeo/áudio confere preservação de imagem e o deslocamento de som já previsto. Testes de software não demonstram mérito artístico.

A revisão independente encontrou contexto criativo em perfis e no ZIP V3, dois journals reais, preferência anterior no seed público, referência impossível e caminhos não portáveis. Esses itens foram corrigidos. O V3 original conserva o SHA256 `38582e59b870ff1bb6f261a54cdf8d01569661bbc18bf436f6c38c4a75692e8e` no arquivo privado; o público conserva somente sua proveniência. O histórico público anterior tem backup Git local verificado antes da substituição autorizada.

O laboratório também encontrou falha real de edição na folha de personagem, com perfil lateral duplicado. Esse arquivo permanece identificado como variante problemática. A revisão da cena alterou várias variáveis e não é experimento de efeito isolado. O diretor reprovou os estudos de abrigo. As mensagens e razões recebidas permanecem privadas; nenhuma aprovação positiva foi inferida.

O validador auxiliar do criador de Skills encontrou PyYAML ausente. Nenhuma dependência foi instalada. Nome, descrição e versão do frontmatter foram conferidos pelo validador do pacote; não foi inventado um PASS do utilitário indisponível.

A revisão final também reproduziu dois defeitos novos, corrigidos e rechecados independentemente. A mesclagem de hooks comparava só o comando e podia perder o matcher necessário; agora compara o grupo inteiro e preserva regras anteriores distintas. O vínculo podia conter ID novo com URL antiga; os links agora derivam do ID validado e não apontam para a conta anterior numa migração parcial.

## Estado compartilhado e limites de sincronização

A 1.4 não realizou nova escrita no Google Sheets. Os ensaios históricos de criação, escrita e releitura permanecem documentados num [resumo classificado](audits/native-validation-summary.json), com originais privados. A instalação reconferiu metadados e leituras sentinelas pelo conector existente; isso não substitui uma leitura canônica completa antes de orientar a produção.

A cada interação de produção, consultar a planilha e a fila antes de orientar ou preparar alteração. Uma escolha por nova mensagem passa por validação de conteúdo, escopo, versão e autorização. A gravação exige PREPARED, guardas atuais, escrita, releitura independente de dados e confirmação posterior do histórico. Não há transação atômica, sincronização em segundo plano ou garantia de exclusividade entre agentes. A página reflete a última publicação e precisa ser recarregada. Rascunhos no navegador e estudos locais não são estado compartilhado.

## Pendências que não viraram aprovação

Homologação visual e escuta dos painéis no dispositivo do diretor permanecem pendentes. A política do navegador impediu inspeção local por file:// e não foi contornada. Os controles passaram em simulação. O julgamento artístico ainda precisa de mais decisões humanas contextualizadas e material audiovisual realizado. A amostra atual não certifica excelência ou gosto geral. Hooks precisam da confiança da definição no painel do host e da observação de eventos nativos antes de serem declarados ativos.

Produção definitiva manual, cinco chamadas conceituais nativas autorizadas, zero gerações externas pagas ou créditos Higgsfield. Nenhum MCP, API, Apps Script ou servidor novo. Dependências opcionais ausentes não foram instaladas. Originais, dados e histórico locais preservados.
