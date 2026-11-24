# Prompt Laboratory e adaptadores

O compilador é local e não chama ferramentas de geração. Ele lê o snapshot oficial consultado em 24/11/2026 e produz pacote para execução manual. IDs no catálogo: Seedance 2.5, Seedream 5.0 Pro, Kling 3.0 Turbo, GPT Image 2.6, Nano Banana 2.1, FLUX.3, MiniMax H3, Wan 2.7. Não extrapolar nomes de versões a partir de buscas aproximadas. Consultar novamente no momento da produção.

`python scripts/prompt_compiler.py examples/prompt-specs/seedance_2_5.json` valida parâmetros, enumerações, duração, proporção e papéis de referência. Parâmetro desconhecido é erro. O arquivo exportado preserva a intenção e as restrições; não executa o modelo. Ao mudar o modelo, recompilar a especificação; não apenas trocar o nome em um prompt.

| Adaptador | Organização editorial | Referências e cuidado |
|---|---|---|
| Seedance | estado → ação → atuação → câmera → som → protegidos | t2v sem refs; omni aceita start/end e refs; editar/estender exige vídeo. Controles ignorados em certos modos geram aviso. |
| Seedream | sujeito → espaço → composição → luz → material → protegidos | até 10 imagens; sem papel de vídeo/start/end no catálogo consultado. |
| GPT Image | finalidade → sujeito → espaço → composição → luz → material → protegidos | até 16 imagens, proibidas com SVG; esta é rota Higgsfield manual, distinta da ferramenta nativa do chat. |
| Nano Banana | finalidade/edição → sujeito → espaço → composição → luz → protegidos | imagem, máscara e até um vídeo; não inventar força de identidade. |
| FLUX | sujeito → espaço → luz → material → composição → protegidos | até 10 imagens na ordem; descrever papel sem fabricar sintaxe de binding. |
| MiniMax | estado → ação → atuação → câmera → som → protegidos | fim exige início; áudio exige imagem/vídeo; respeitar limites. |
| Wan | estado → ação → câmera → atuação → som → protegidos | início/fim/áudio no catálogo; não enviar lista genérica de imagens. Dependências não publicadas continuam desconhecidas. |
| Kling | estado → ação → câmera → atuação → protegidos | versão verificada aceita início; não inventar quadro final ou vídeo de referência. |

A organização editorial acima é hipótese de autoria, não desempenho comparativo demonstrado. Não há benchmark gerado desses oito modelos. Câmera, lente, acting, luz e escala são linguagem natural quando não aparecem entre os parâmetros nativos. Avaliar resultado importado novamente.

Cinema Studio é uma interface, não um único modelo. O guia oficial consultado era da versão 3.0 e a interface pode estar em outra versão. Usar `cinema-studio.worksheet.json` como checklist experimental; confirmar controles visíveis e modelo no projeto real antes de prometer suporte. Não existe compilação nativa certificada dessa UI neste pacote.

Exemplo negativo: `camera_focal_length=35` como parâmetro nativo genérico — rejeitado. Exemplo correto: focal e posição na intenção textual; parâmetros apenas do catálogo, referência anexada com papel suportado e geografia protegida. Mais texto não garante obediência. Reprovar ou corrigir de modo localizado após inspecionar mídia real.
