# Verificação da mesa e do comparador CPE 1.6.0

## Teste local da publicação

Em 24/11/2026, os comandos `desk-pair` e `desk-publish` executaram pelo `scripts/cpe.py` da candidata. O teste usou uma cópia sintética de `examples/takes/demo-state.json`, isolada como `TEST-CPE16-BROWSER`, e os dois MP4 didáticos COM-01. A publicação devolveu `PUBLISHED_LOCAL_DESK`, com um plano, um par e os endereços locais da mesa, do comparador e da projeção do estado. O recibo registrou zero transferências de arquivos e leitura remota `false`. O marcador de proprietário da mesa identificou o projeto de teste.

O FFprobe abriu os dois arquivos. Ambos têm faixas H.264 e AAC de 6,000 s. A leitura confirma os streams e a duração das fontes. Ouvintes e decodificação de mídia no navegador exigem observações próprias.

| Artefato da execução | SHA-256 |
| --- | --- |
| `studio.html` | `d658f6f75201743b69a308f9cabafac0a8dffd43fef6799a36d90a3e1b85f0fc` |
| `takes.html` | `a7fb164b25245f469e75e8c88427df8f3068b9dfeb5e847bf208e10326cb9fc4` |

## Tentativa no navegador

O navegador Chrome gerenciado recusou a navegação direta para o arquivo local por política de protocolo. A superfície autorizada informou que aceita apenas HTTP e HTTPS e bloqueou caminhos alternativos para o mesmo acesso. A tentativa terminou antes de carregar o DOM. A execução ocorreu sem servidor, mudança de configuração ou conexão com a planilha de produção.

Estado do navegador real `BLOCKED_EXTERNAL`. A inspeção de visualização, responsividade, playback, alternância de áudio real e restauração de rascunho em navegador ficou pendente nessa superfície. Uma gravação no estado nativo e uma decisão humana também estão fora desta verificação local.

## Cobertura simulada nesta candidata

Node `v22.22.2`. As três execuções retornaram código zero.

| Comando | Passes | Ambiente observado |
| --- | --- | --- |
| `node evals/test_panel_runtime.cjs` | 29 de 29, incluindo 37 painéis de apoio | Node VM com implementação mínima do DOM |
| `node evals/test_desk_runtime.cjs` | 24 de 24 | JavaScript da mesa com substitutos para DOM e armazenamento |
| `node evals/test_take_player.cjs` | 21 de 21 | Controlador do comparador com substitutos para DOM e relógio de mídia |

A cobertura simulada combina seleção e preparação de mensagens, retomada, restauração de rascunho, timecode, intervalo e áudio A/B. Os testes reportam ausência de verificação em navegador. A publicação executada pela CLI e a inspeção real dos streams são evidências técnicas separadas.
