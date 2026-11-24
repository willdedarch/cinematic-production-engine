window.CPE_BOARDS = [
  {
    "id": "references",
    "title": "Referências",
    "gate": "G1",
    "table": "Reference Library",
    "read": "knowledge/README.md",
    "fields": [
      {
        "label": "Finalidade",
        "key": "purpose"
      },
      {
        "label": "Fonte/ID e direitos",
        "key": "reference"
      },
      {
        "label": "Observação verificável",
        "key": "observation"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/README.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "director",
    "title": "Linguagem e direção",
    "gate": "G5",
    "table": "Director Profiles",
    "read": "knowledge/director-profiles.json",
    "fields": [
      {
        "label": "Perfil/obra de referência",
        "key": "profile"
      },
      {
        "label": "Função dramática",
        "key": "intention"
      },
      {
        "label": "Escolhas a combinar",
        "key": "choices"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/director-profiles.json. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "genre",
    "title": "Gênero",
    "gate": "G0",
    "table": "Genre Profiles",
    "read": "knowledge/genre-profiles.json",
    "fields": [
      {
        "label": "Gênero principal",
        "key": "genre"
      },
      {
        "label": "Mistura e intensidade",
        "key": "mix"
      },
      {
        "label": "Limites do projeto",
        "key": "constraints"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/genre-profiles.json. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "cinematography",
    "title": "Fotografia",
    "gate": "G5",
    "table": "Cinematography",
    "read": "knowledge/light.md",
    "fields": [
      {
        "label": "Intenção",
        "key": "intention"
      },
      {
        "label": "Fonte motivada",
        "key": "light"
      },
      {
        "label": "Protegidos",
        "key": "protected"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/light.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "lens",
    "title": "Lentes",
    "gate": "G5",
    "table": "Cinematography",
    "read": "knowledge/optics.md",
    "fields": [
      {
        "label": "Sensor e proporção",
        "key": "sensor"
      },
      {
        "label": "Focal e distância",
        "key": "lens"
      },
      {
        "label": "Motivo e alternativa",
        "key": "tradeoff"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/optics.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "composition",
    "title": "Composição",
    "gate": "G10",
    "table": "Shot List",
    "read": "knowledge/composition.md",
    "fields": [
      {
        "label": "Ordem de atenção",
        "key": "attention"
      },
      {
        "label": "Camadas e eixo",
        "key": "layers"
      },
      {
        "label": "Área útil final",
        "key": "crop"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/composition.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "lighting",
    "title": "Iluminação",
    "gate": "G5",
    "table": "Cinematography",
    "read": "knowledge/light.md",
    "fields": [
      {
        "label": "Fonte e direção",
        "key": "source"
      },
      {
        "label": "Contraste pretendido",
        "key": "contrast"
      },
      {
        "label": "Evidência",
        "key": "evidence"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/light.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "texture",
    "title": "Cor e textura",
    "gate": "G5",
    "table": "Cinematography",
    "read": "knowledge/design.md",
    "fields": [
      {
        "label": "Paleta material",
        "key": "palette"
      },
      {
        "label": "Qualidade de superfície",
        "key": "material"
      },
      {
        "label": "Tratamento e limite",
        "key": "grade"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/design.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "emotion",
    "title": "Emoção",
    "gate": "G3",
    "table": "Screenplays",
    "read": "knowledge/narrative-editing.md",
    "fields": [
      {
        "label": "Expectativa do público",
        "key": "expectation"
      },
      {
        "label": "Estímulo e reação",
        "key": "response"
      },
      {
        "label": "Consequência",
        "key": "consequence"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/narrative-editing.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "living",
    "title": "Mundo vivo",
    "gate": "G8",
    "table": "Locations",
    "read": "knowledge/design.md",
    "fields": [
      {
        "label": "Ação de fundo",
        "key": "background"
      },
      {
        "label": "Causa e duração",
        "key": "cause"
      },
      {
        "label": "Elementos protegidos",
        "key": "protected"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/design.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "cast-compare",
    "title": "Comparar elenco",
    "gate": "G7",
    "table": "Characters",
    "read": "knowledge/design.md",
    "fields": [
      {
        "label": "Candidato A / versão",
        "key": "a"
      },
      {
        "label": "Candidato B / versão",
        "key": "b"
      },
      {
        "label": "Diferença observada",
        "key": "difference"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/design.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "location-compare",
    "title": "Comparar locações",
    "gate": "G8",
    "table": "Locations",
    "read": "knowledge/design.md",
    "fields": [
      {
        "label": "Alternativa A / versão",
        "key": "a"
      },
      {
        "label": "Alternativa B / versão",
        "key": "b"
      },
      {
        "label": "Geometria e intenção",
        "key": "difference"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/design.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "props-compare",
    "title": "Comparar objetos",
    "gate": "G9",
    "table": "Props",
    "read": "knowledge/design.md",
    "fields": [
      {
        "label": "Objeto A / versão",
        "key": "a"
      },
      {
        "label": "Objeto B / versão",
        "key": "b"
      },
      {
        "label": "Material e estados",
        "key": "difference"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/design.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "prompt-lab",
    "title": "Laboratório de prompts",
    "gate": "G10",
    "table": "Prompt Library",
    "read": "adapters/README.md",
    "fields": [
      {
        "label": "Modelo verificado",
        "key": "model_id"
      },
      {
        "label": "Hipótese / uma variável",
        "key": "hypothesis"
      },
      {
        "label": "Protegidos",
        "key": "protected"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia adapters/README.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "model",
    "title": "Compatibilidade de modelo",
    "gate": "G10",
    "table": "Model Compatibility",
    "read": "adapters/README.md",
    "fields": [
      {
        "label": "Modelo / versão",
        "key": "model_id"
      },
      {
        "label": "Capacidade necessária",
        "key": "capability"
      },
      {
        "label": "Fonte atual",
        "key": "source"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia adapters/README.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "failure",
    "title": "Diagnóstico",
    "gate": "G13",
    "table": "Evaluation Results",
    "read": "knowledge/failure-library.json",
    "fields": [
      {
        "label": "Sintoma com evidência",
        "key": "symptom"
      },
      {
        "label": "Hipóteses alternativas",
        "key": "causes"
      },
      {
        "label": "Correção localizada",
        "key": "repair"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/failure-library.json. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "golden",
    "title": "Exemplos",
    "gate": "G2",
    "table": "Examples",
    "read": "examples/golden-index.md",
    "fields": [
      {
        "label": "Competência procurada",
        "key": "competency"
      },
      {
        "label": "Exemplo e proveniência",
        "key": "example"
      },
      {
        "label": "Limite de reutilização",
        "key": "limit"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia examples/golden-index.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "reference-approval",
    "title": "Aprovar referência",
    "gate": "G5",
    "table": "Reference Library",
    "read": "knowledge/README.md",
    "fields": [
      {
        "label": "Referência / revisão",
        "key": "reference"
      },
      {
        "label": "Uso e direitos",
        "key": "rights"
      },
      {
        "label": "Motivo da decisão",
        "key": "reason"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/README.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "learning",
    "title": "Aprendizado",
    "gate": "G15",
    "table": "Production Lessons",
    "read": "knowledge/README.md",
    "fields": [
      {
        "label": "Resultado e decisão real",
        "key": "result"
      },
      {
        "label": "Motivo observado",
        "key": "reason"
      },
      {
        "label": "Escopo de aplicação",
        "key": "scope"
      }
    ],
    "checklist": [
      "Comparação usa a mesma intenção e versão",
      "Fonte e limites registrados",
      "Aprovados e bloqueados preservados"
    ],
    "guidance": "Leia knowledge/README.md. Registre evidência concreta e o escopo. A escolha só será salva após envio na conversa, validação e releitura."
  },
  {
    "id": "judgment",
    "title": "Julgamento cinematográfico",
    "gate": "G13",
    "table": "Evaluation Results",
    "read": "judgment-engine/protocol.md",
    "fields": [
      {
        "label": "Material / versão",
        "key": "material"
      },
      {
        "label": "Intenção e rubrica",
        "key": "intention"
      },
      {
        "label": "Resultado técnico",
        "key": "technical"
      },
      {
        "label": "Interpretação artística e evidência",
        "key": "artistic"
      }
    ],
    "checklist": [
      "Rubrica e alvo/versão corretos",
      "Evidência observada separada de inferência",
      "Recomendação não tratada como aprovação automática"
    ],
    "guidance": "Comparar por evidência e intenção. Empate e reprovação de todas são válidos. Registrar divergências, protegidos e limites; métricas sem dados permanecem ausentes."
  },
  {
    "id": "blind-comparison",
    "title": "Comparação cega",
    "gate": "G13",
    "table": "Pairwise Comparisons",
    "read": "judgment-engine/protocol.md",
    "fields": [
      {
        "label": "Pacote público / revisão",
        "key": "packet"
      },
      {
        "label": "Escolha",
        "key": "choice",
        "options": [
          "A",
          "B",
          "TIE",
          "BOTH_FAIL"
        ]
      },
      {
        "label": "Evidência e justificativa",
        "key": "evidence"
      }
    ],
    "checklist": [
      "Rubrica e alvo/versão corretos",
      "Evidência observada separada de inferência",
      "Recomendação não tratada como aprovação automática"
    ],
    "guidance": "Comparar por evidência e intenção. Empate e reprovação de todas são válidos. Registrar divergências, protegidos e limites; métricas sem dados permanecem ausentes."
  },
  {
    "id": "artistic-calibration",
    "title": "Calibração artística",
    "gate": "G13",
    "table": "Human Feedback",
    "read": "judgment-engine/protocol.md",
    "fields": [
      {
        "label": "Avaliação e material",
        "key": "evaluation"
      },
      {
        "label": "Motivo da divergência",
        "key": "reason"
      },
      {
        "label": "Escopo da preferência",
        "key": "scope",
        "options": [
          "deliverable",
          "episode",
          "project",
          "genre",
          "model",
          "global"
        ]
      }
    ],
    "checklist": [
      "Rubrica e alvo/versão corretos",
      "Evidência observada separada de inferência",
      "Recomendação não tratada como aprovação automática"
    ],
    "guidance": "Comparar por evidência e intenção. Empate e reprovação de todas são válidos. Registrar divergências, protegidos e limites; métricas sem dados permanecem ausentes."
  },
  {
    "id": "causal-diagnosis",
    "title": "Diagnóstico causal",
    "gate": "G13",
    "table": "Failure Diagnostics",
    "read": "judgment-engine/protocol.md",
    "fields": [
      {
        "label": "Sintoma observado",
        "key": "symptom"
      },
      {
        "label": "Hipótese e alternativas",
        "key": "hypotheses"
      },
      {
        "label": "Protegidos e verificação",
        "key": "protected"
      }
    ],
    "checklist": [
      "Rubrica e alvo/versão corretos",
      "Evidência observada separada de inferência",
      "Recomendação não tratada como aprovação automática"
    ],
    "guidance": "Comparar por evidência e intenção. Empate e reprovação de todas são válidos. Registrar divergências, protegidos e limites; métricas sem dados permanecem ausentes."
  },
  {
    "id": "revision-comparison",
    "title": "Comparar revisões",
    "gate": "G13",
    "table": "Revision Results",
    "read": "judgment-engine/protocol.md",
    "fields": [
      {
        "label": "Antes e depois / versões",
        "key": "versions"
      },
      {
        "label": "Resolvido e persistente",
        "key": "resolved"
      },
      {
        "label": "Novos problemas",
        "key": "introduced"
      }
    ],
    "checklist": [
      "Rubrica e alvo/versão corretos",
      "Evidência observada separada de inferência",
      "Recomendação não tratada como aprovação automática"
    ],
    "guidance": "Comparar por evidência e intenção. Empate e reprovação de todas são válidos. Registrar divergências, protegidos e limites; métricas sem dados permanecem ausentes."
  },
  {
    "id": "quality-benchmark",
    "title": "Histórico de qualidade",
    "gate": "G13",
    "table": "Evaluation Results",
    "read": "judgment-engine/protocol.md",
    "fields": [
      {
        "label": "Conjunto e origem dos rótulos",
        "key": "dataset"
      },
      {
        "label": "Resultado com denominador",
        "key": "metric"
      },
      {
        "label": "Limites / dados ausentes",
        "key": "limits"
      }
    ],
    "checklist": [
      "Rubrica e alvo/versão corretos",
      "Evidência observada separada de inferência",
      "Recomendação não tratada como aprovação automática"
    ],
    "guidance": "Comparar por evidência e intenção. Empate e reprovação de todas são válidos. Registrar divergências, protegidos e limites; métricas sem dados permanecem ausentes."
  },
  {
    "id": "environment",
    "title": "Ferramentas disponíveis",
    "gate": "G0",
    "table": "Tool Capabilities",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Capacidade necessária",
        "key": "capability"
      },
      {
        "label": "Evidência de teste e limite",
        "key": "evidence"
      },
      {
        "label": "Alternativa disponível",
        "key": "alternative"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "visual-lab",
    "title": "Laboratório visual",
    "gate": "G5",
    "table": "Experiments",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Questão cinematográfica",
        "key": "question"
      },
      {
        "label": "Laboratório",
        "key": "lab",
        "options": [
          "Lens",
          "Camera",
          "Composition",
          "Lighting",
          "Color",
          "Texture",
          "Material",
          "Casting",
          "Wardrobe",
          "Performance",
          "Location",
          "Atmosphere",
          "Living World",
          "Storyboard",
          "Continuity",
          "Hook"
        ]
      },
      {
        "label": "Ferramenta proporcional à decisão",
        "key": "tool"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "experiment",
    "title": "Controlar experimento",
    "gate": "G5",
    "table": "Experiments",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Hipótese e variável principal",
        "key": "hypothesis"
      },
      {
        "label": "Quantidade máxima autorizada",
        "key": "max_variants"
      },
      {
        "label": "Referências e protegidos",
        "key": "protected"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "optical-lab",
    "title": "Laboratório óptico",
    "gate": "G5",
    "table": "Experiments",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Sensor ativo e proporção",
        "key": "sensor"
      },
      {
        "label": "Focal, distância e squeeze",
        "key": "optics"
      },
      {
        "label": "Abertura, foco e CoC",
        "key": "dof"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "composition-analyzer",
    "title": "Analisar composição",
    "gate": "G10",
    "table": "Artifact Registry",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Imagem / versão",
        "key": "source"
      },
      {
        "label": "Guias e recorte desejados",
        "key": "guides"
      },
      {
        "label": "Áreas e ordem de atenção",
        "key": "regions"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "media-inspector",
    "title": "Inspecionar mídia",
    "gate": "G13",
    "table": "Evaluation Results",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Arquivo e origem autorizada",
        "key": "source"
      },
      {
        "label": "Escopo e duração de análise",
        "key": "scope"
      },
      {
        "label": "Achados candidatos e limites",
        "key": "findings"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "blender-previs",
    "title": "Pré-visualização espacial",
    "gate": "G8",
    "table": "Experiments",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Planta aprovada e marcos",
        "key": "geometry"
      },
      {
        "label": "Câmeras e blocking",
        "key": "cameras"
      },
      {
        "label": "Blender disponível ou planta2D",
        "key": "tool"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "correction-control",
    "title": "Correção localizada",
    "gate": "G13",
    "table": "Revision Results",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Deficiência e evidência",
        "key": "problem"
      },
      {
        "label": "Mudança mínima e risco",
        "key": "change"
      },
      {
        "label": "Protegidos e critério de reavaliação",
        "key": "protected"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "production-export",
    "title": "Pacote para produção manual",
    "gate": "G10",
    "table": "Artifact Registry",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Intenção e referências aprovadas",
        "key": "intent"
      },
      {
        "label": "Modelo e versão consultada",
        "key": "model"
      },
      {
        "label": "Prompts, parâmetros e pendências",
        "key": "package"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "asset-import",
    "title": "Importar resultado",
    "gate": "G12",
    "table": "Artifact Registry",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Arquivo, origem e direitos",
        "key": "source"
      },
      {
        "label": "Classe e versão do material",
        "key": "kind",
        "options": [
          "REFERENCE",
          "TECHNICAL_PREVIS",
          "ARTISTIC_PREVIS",
          "NARRATIVE_PREVIS",
          "VISUAL_DRAFT",
          "PRODUCTION_EXPORT",
          "FINAL_ASSET"
        ]
      },
      {
        "label": "Nova avaliação técnica e artística",
        "key": "review"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "execution-evidence",
    "title": "Evidências da execução",
    "gate": "G13",
    "table": "Execution Evidence",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Execução, ferramenta e saída",
        "key": "run"
      },
      {
        "label": "Conhecimento aplicado e verificação",
        "key": "knowledge"
      },
      {
        "label": "Observado, inferido e pendente",
        "key": "limits"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  },
  {
    "id": "recovery",
    "title": "Retomar produção",
    "gate": "G0",
    "table": "Checkpoints",
    "read": "harness/manual.md",
    "fields": [
      {
        "label": "Último estado confirmado",
        "key": "checkpoint"
      },
      {
        "label": "Leitura atual e divergências",
        "key": "freshness"
      },
      {
        "label": "Pendências e próximo passo",
        "key": "pending"
      }
    ],
    "checklist": [
      "Capacidade e origem verificadas",
      "Escopo, protegidos e custo conferidos",
      "Resultado observado e pendências separados"
    ],
    "guidance": "Use referências ou ferramenta local quando suficiente. Geração conceitual exige autorização específica e limite. O resultado final importado recebe nova avaliação. Envie a escolha em nova mensagem; confirme persistência somente após releitura."
  }
];
