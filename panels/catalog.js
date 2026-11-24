window.CPE_CONFIG = {
  "gates": [
    {
      "id": "G0",
      "name": "Projeto",
      "depends": [],
      "skippable": false,
      "checks": [
        "Escopo, formato e duração",
        "Gênero e intensidade criativa",
        "Modo e continuidade",
        "Zero créditos e geração manual"
      ],
      "deliverable": "Brief e perfil criativo"
    },
    {
      "id": "G1",
      "name": "Pesquisa",
      "depends": [
        "G0"
      ],
      "skippable": true,
      "checks": [
        "Fontes ou material autorizado",
        "Fatos separados de ficção",
        "Sementes dramáticas e lacunas"
      ],
      "deliverable": "Mapa de pesquisa"
    },
    {
      "id": "G2",
      "name": "Ideação",
      "depends": [
        "G1"
      ],
      "skippable": true,
      "checks": [
        "Alternativas causalmente distintas",
        "Conflito, consequência e gancho",
        "Seleção explicitamente registrada"
      ],
      "deliverable": "Propostas e seleção"
    },
    {
      "id": "G3",
      "name": "Desenvolvimento",
      "depends": [
        "G2"
      ],
      "skippable": true,
      "checks": [
        "Beat sheet e duração",
        "Causalidade, emoção e informação",
        "Payoff e final"
      ],
      "deliverable": "Mapa narrativo"
    },
    {
      "id": "G4",
      "name": "Roteiro",
      "depends": [
        "G3"
      ],
      "skippable": false,
      "checks": [
        "Roteiro limpo e versionado",
        "Script doctor e correções",
        "Falas, continuidade e duração"
      ],
      "deliverable": "Screenplay aprovado"
    },
    {
      "id": "G5",
      "name": "Direção e look",
      "depends": [
        "G4"
      ],
      "skippable": false,
      "checks": [
        "Estilo e gênero traduzidos em decisões",
        "Lentes, composição, cor e luz",
        "Ambiente vivo e coerência visual"
      ],
      "deliverable": "Look bible"
    },
    {
      "id": "G6",
      "name": "Breakdown",
      "depends": [
        "G5"
      ],
      "skippable": false,
      "checks": [
        "Elenco e figurinos inventariados",
        "Locações e props inventariados",
        "Dependências e assets existentes"
      ],
      "deliverable": "Inventário de produção"
    },
    {
      "id": "G7",
      "name": "Casting",
      "depends": [
        "G6"
      ],
      "skippable": true,
      "checks": [
        "Identidade e silhueta",
        "Figurino e estados",
        "Referências manuais inspecionadas ou reutilizadas",
        "Versões identificadas"
      ],
      "deliverable": "Fichas e assets de elenco"
    },
    {
      "id": "G8",
      "name": "Locations",
      "depends": [
        "G6"
      ],
      "skippable": true,
      "checks": [
        "GEO e âncoras aprovados",
        "Perspectivas e escala",
        "Materiais, luz, ambiente vivo",
        "Referências manuais inspecionadas ou reutilizadas"
      ],
      "deliverable": "Pacote de locações"
    },
    {
      "id": "G9",
      "name": "Props",
      "depends": [
        "G6"
      ],
      "skippable": true,
      "checks": [
        "Época e material",
        "Dimensão, dono, estado",
        "Referências manuais inspecionadas ou reutilizadas"
      ],
      "deliverable": "Pacote de objetos"
    },
    {
      "id": "G10",
      "name": "Previs",
      "depends": [
        "G7",
        "G8",
        "G9"
      ],
      "skippable": false,
      "checks": [
        "Shot list com propósito e duração",
        "Eixo, geometria e continuidade",
        "Blocking, composição e atuação",
        "Prompts preparados sem disparar geração"
      ],
      "deliverable": "Decupagem e prompt pack"
    },
    {
      "id": "G11",
      "name": "Look test manual",
      "depends": [
        "G10"
      ],
      "skippable": true,
      "checks": [
        "Testes externos ou referências equivalentes",
        "Identidade, textura, ótica e luz",
        "Correções e escolhas registradas"
      ],
      "deliverable": "Avaliação de testes importados"
    },
    {
      "id": "G12",
      "name": "Produção manual",
      "depends": [
        "G11"
      ],
      "skippable": true,
      "checks": [
        "Resultados externos ou reutilizados",
        "Correspondência ao plano e estado",
        "Versões e pendências registradas"
      ],
      "deliverable": "Inventário de planos manuais"
    },
    {
      "id": "G13",
      "name": "Pós-produção manual",
      "depends": [
        "G12"
      ],
      "skippable": true,
      "checks": [
        "Ordem e ritmo",
        "Plano de som e cor",
        "Resultado externo ou escopo textual identificado"
      ],
      "deliverable": "Plano editorial e resultado disponível"
    },
    {
      "id": "G14",
      "name": "QC",
      "depends": [
        "G13"
      ],
      "skippable": false,
      "checks": [
        "Continuidade e cobertura",
        "Defeitos observados vs não verificáveis",
        "Revisão do escopo entregue",
        "Aprovação artística explícita"
      ],
      "deliverable": "Relatório QC do material disponível"
    },
    {
      "id": "G15",
      "name": "Aprendizado",
      "depends": [
        "G14"
      ],
      "skippable": true,
      "checks": [
        "Ledger atualizado",
        "Decisões e hipóteses",
        "Métricas reais ou ausência registrada"
      ],
      "deliverable": "Handoff e aprendizado"
    }
  ],
  "tables": [
    "Projects",
    "Episodes",
    "Workflow",
    "Screenplays",
    "Characters",
    "Locations",
    "Props",
    "Cinematography",
    "Shot List",
    "Prompts",
    "Checklists",
    "Approvals",
    "Continuity",
    "Decisions",
    "Revision History",
    "Reference Library",
    "Examples",
    "Techniques",
    "Creative Preferences",
    "Model Compatibility",
    "Production Lessons",
    "Director Profiles",
    "Genre Profiles",
    "Visual Standards",
    "Evaluation Results",
    "Prompt Library",
    "Pairwise Comparisons",
    "Human Feedback",
    "Failure Diagnostics",
    "Revision Results",
    "Experiments",
    "Artifact Registry",
    "Tool Capabilities",
    "Execution Evidence",
    "Checkpoints"
  ],
  "statuses": [
    "PENDING",
    "IN_PROGRESS",
    "REVIEW_REQUIRED",
    "APPROVED",
    "LOCKED",
    "CHANGES_REQUESTED",
    "SKIPPED"
  ],
  "spreadsheet_id": "CONFIGURE_YOUR_SPREADSHEET_ID",
  "fields": {
    "G0": [
      {
        "label": "Nome do projeto",
        "key": "project_name"
      },
      {
        "label": "Formato",
        "key": "aspect_ratio",
        "options": [
          "16:9",
          "9:16",
          "1:1"
        ]
      },
      {
        "label": "Duração em segundos",
        "key": "target_seconds"
      },
      {
        "label": "Gênero",
        "key": "genre"
      },
      {
        "label": "Modo",
        "key": "mode",
        "options": [
          "guided",
          "manual",
          "hybrid"
        ]
      }
    ],
    "G1": [
      {
        "label": "Fonte e localizador",
        "key": "source_ref"
      },
      {
        "label": "Fato / ficção / lacuna",
        "key": "evidence_class",
        "options": [
          "FATO",
          "FICCAO",
          "HIPOTESE",
          "LACUNA"
        ]
      }
    ],
    "G2": [
      {
        "label": "Proposta escolhida",
        "key": "selected_proposal"
      },
      {
        "label": "Escolha e consequência",
        "key": "causal_choice"
      }
    ],
    "G3": [
      {
        "label": "Virada emocional",
        "key": "emotional_turn"
      },
      {
        "label": "Pergunta do espectador",
        "key": "audience_question"
      },
      {
        "label": "Ritmo",
        "key": "pace",
        "options": [
          "adaptado à cena",
          "mais contido",
          "mais urgente"
        ]
      }
    ],
    "G4": [
      {
        "label": "Versão do roteiro",
        "key": "screenplay_version"
      },
      {
        "label": "Referência do texto",
        "key": "screenplay_ref"
      },
      {
        "label": "Correção localizada",
        "key": "repair"
      }
    ],
    "G5": [
      {
        "label": "Intenção do plano",
        "key": "intent"
      },
      {
        "label": "Família óptica",
        "key": "lens_family",
        "options": [
          "spherical",
          "anamorphic",
          "vintage",
          "custom"
        ]
      },
      {
        "label": "Distância focal de referência (mm)",
        "key": "focal_mm"
      },
      {
        "label": "Composição",
        "key": "composition",
        "options": [
          "profundidade",
          "terços",
          "simetria",
          "espaço negativo",
          "personalizada"
        ]
      },
      {
        "label": "Luz motivada",
        "key": "light"
      }
    ],
    "G6": [
      {
        "label": "Inventário e versão",
        "key": "inventory_ref"
      },
      {
        "label": "Assets já aprovados a reutilizar",
        "key": "reuse_ids"
      }
    ],
    "G7": [
      {
        "label": "Personagem / versão",
        "key": "character_id"
      },
      {
        "label": "Âncoras de identidade",
        "key": "identity"
      },
      {
        "label": "Figurino e estado",
        "key": "costume"
      },
      {
        "label": "Objetivo e ação observável",
        "key": "performance"
      }
    ],
    "G8": [
      {
        "label": "Locação / GEO versão",
        "key": "location_id"
      },
      {
        "label": "Âncoras fixas",
        "key": "anchors"
      },
      {
        "label": "Escala e material",
        "key": "dimensions"
      },
      {
        "label": "Clima, luz e estado",
        "key": "light_weather"
      }
    ],
    "G9": [
      {
        "label": "Objeto / versão",
        "key": "prop_id"
      },
      {
        "label": "Material e escala",
        "key": "material_scale"
      },
      {
        "label": "Dono e estado",
        "key": "owner_state"
      }
    ],
    "G10": [
      {
        "label": "Plano / beat",
        "key": "shot_id"
      },
      {
        "label": "Função e duração",
        "key": "purpose_duration"
      },
      {
        "label": "Posição de câmera e eixo",
        "key": "camera_blocking"
      },
      {
        "label": "Modelo alvo",
        "key": "model"
      },
      {
        "label": "Referências por papel",
        "key": "reference_roles"
      }
    ],
    "G11": [
      {
        "label": "Resultado externo / versão",
        "key": "asset_ref"
      },
      {
        "label": "Observado e não verificável",
        "key": "observations"
      }
    ],
    "G12": [
      {
        "label": "Material importado / versão",
        "key": "asset_ref"
      },
      {
        "label": "Correspondência ao plano",
        "key": "match_to_plan"
      }
    ],
    "G13": [
      {
        "label": "Plano de corte",
        "key": "edit_ref"
      },
      {
        "label": "Mapa sonoro e silêncio",
        "key": "sound_map"
      }
    ],
    "G14": [
      {
        "label": "Entrega e versão",
        "key": "deliverable_ref"
      },
      {
        "label": "Defeito com localizador",
        "key": "issue"
      },
      {
        "label": "Aceite ou correção",
        "key": "review_choice",
        "options": [
          "avaliar",
          "pedir correção",
          "aprovar escopo observado"
        ]
      }
    ],
    "G15": [
      {
        "label": "Lição e evidência",
        "key": "lesson"
      },
      {
        "label": "Escopo da preferência",
        "key": "preference_scope",
        "options": [
          "entrega",
          "episódio",
          "projeto",
          "global somente com autorização"
        ]
      },
      {
        "label": "Próximo teste",
        "key": "next_test"
      }
    ]
  },
  "guidance": {
    "G0": "Recomendação: fixe a intenção, o formato e o limite de duração antes de escolher equipamento. Zero créditos e execução manual permanecem fixos.",
    "G1": "Compare fontes primárias e lacunas. Um detalhe plausível não se torna fato histórico.",
    "G2": "Compare conflitos e consequências diferentes. Trocar apenas o cenário não cria outra proposta.",
    "G3": "Registre o que muda na informação e no vínculo. Urgência não exige cortes uniformemente rápidos.",
    "G4": "Cite a fala ou beat com problema e a menor correção eficaz. Texto bloqueado permanece preservado.",
    "G5": "Escolha posição e profundidade pela informação dramática. Nome de lente é referência estética, não controle físico comprovado do gerador.",
    "G6": "Separe identidade, estado e versão. Reutilize o que está aprovado antes de propor novo asset.",
    "G7": "Compare silhueta, rosto, figurino e comportamento. Ficha textual não comprova identidade visual.",
    "G8": "GEO persiste entre ângulos. Corrija a câmera se ela não vê a porta; não mova a porta para caber no plano.",
    "G9": "Exija sheet separado se a trama depende do detalhe ou se o objeto reaparece. Estado e troca de dono precisam de evento.",
    "G10": "Cada plano tem função, começo/fim e passagem de continuidade. Parametrização nativa exige especificação atual do modelo.",
    "G11": "Importe somente referência disponível. Separe observação da intenção e mantenha pendente o que não foi visto.",
    "G12": "Nenhum botão dispara produção. O usuário produz externamente e traz materiais identificados.",
    "G13": "Corte quando o significado muda. Mapa de som discrimina fala, ambiente, música e silêncio.",
    "G14": "Conformidade formal e qualidade artística são avaliadas separadamente. Só o usuário concede aceite visual.",
    "G15": "Uma preferência pontual não vira regra global. Registre contexto, evidência e o que ainda precisa ser testado."
  }
};
