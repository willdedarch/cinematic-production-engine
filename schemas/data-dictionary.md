# Dicionário de dados1.1

Schema de estado compatível3.1; tabelas completas exigidas na leitura. IDs globais, revisão positiva, timestamps ISO com fuso; status/enum e relações conforme abaixo. A coluna is_test separa teste de produção/biblioteca.

## Projects

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| name | string |  |
| mode | string | guided,manual,hybrid |
| credits_allowed | integer |  |
| generation_mode | string | manual |
| status | string | ACTIVE,ARCHIVED |

## Episodes

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| title | string |  |
| episode_number | integer |  |
| target_seconds | number |  |
| aspect_ratio | string | 9:16,16:9,1:1 |
| genre | string |  |
| continuity_ref | string |  |
| status | string | ACTIVE,ARCHIVED |

## Workflow

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string | G0,G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,G11,G12,G13,G14,G15 |
| name | string |  |
| status | string | PENDING,IN_PROGRESS,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,SKIPPED |
| depends_on | string |  |
| skippable | boolean |  |
| deliverable_ref | string |  |
| evidence | string |  |
| reason | string |  |

## Screenplays

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| version | string |  |
| title | string |  |
| text_or_ref | string |  |
| source_refs | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,ARCHIVED |
| supersedes_id | string | → Screenplays |

## Characters

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| version | string |  |
| name | string |  |
| identity | string |  |
| costume | string |  |
| performance | string |  |
| reference_roles | string |  |
| asset_ref | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,ARCHIVED |
| supersedes_id | string | → Characters |

## Locations

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| version | string |  |
| name | string |  |
| geo_version | string |  |
| anchors | string |  |
| dimensions | string |  |
| light_weather | string |  |
| state | string |  |
| asset_ref | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,ARCHIVED |
| supersedes_id | string | → Locations |

## Props

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| version | string |  |
| name | string |  |
| material_scale | string |  |
| owner_character_id | string | → Characters |
| state | string |  |
| asset_ref | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,ARCHIVED |
| supersedes_id | string | → Props |

## Cinematography

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| version | string |  |
| intent | string |  |
| sensor_reference | string |  |
| lens_family | string | spherical,anamorphic,vintage,custom |
| focal_mm | number |  |
| camera_distance_m | number |  |
| composition | string |  |
| light | string |  |
| texture | string |  |
| motion | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,ARCHIVED |
| supersedes_id | string | → Cinematography |

## Shot List

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| version | string |  |
| scene_beat | string |  |
| order | integer |  |
| duration_s | number |  |
| purpose | string |  |
| location_id | string | → Locations |
| character_ids | string |  |
| prop_ids | string |  |
| camera_blocking | string |  |
| action | string |  |
| start_end_state | string |  |
| sound_edit | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,ARCHIVED |
| supersedes_id | string | → Shot List |

## Prompts

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| version | string |  |
| target_table | string |  |
| target_id | string |  |
| model | string |  |
| model_checked_at | string |  |
| reference_roles | string |  |
| locked_constraints | string |  |
| prompt_text | string |  |
| native_parameters | string |  |
| unverified_suggestions | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,CHANGES_REQUESTED,ARCHIVED |
| supersedes_id | string | → Prompts |

## Checklists

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| workflow_id | string | → Workflow |
| gate_id | string |  |
| item_index | integer |  |
| criterion | string |  |
| checked | boolean |  |
| evidence | string |  |
| observed_or_planned | string | planned,observed,not_accessible |

## Approvals

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| workflow_id | string | → Workflow |
| gate_id | string |  |
| gate_revision | integer |  |
| decision | string | PENDING,APPROVE,LOCK,REVISE,SKIP |
| approver | string |  |
| user_message_ref | string |  |
| evidence | string |  |
| status | string | DRAFT,RECORDED,SUPERSEDED |

## Continuity

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| entity_table | string |  |
| entity_id | string |  |
| scene_beat | string |  |
| before_state | string |  |
| event | string |  |
| after_state | string |  |
| source_ref | string |  |
| status | string | DRAFT,CONFIRMED,CHANGES_REQUESTED |

## Decisions

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| gate_id | string |  |
| topic | string |  |
| choice | string |  |
| rationale | string |  |
| user_message_ref | string |  |
| status | string | DRAFT,RECORDED,ARCHIVED |

## Revision History

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| op_id | string |  |
| event | string | TEST_ONLY,PREPARED,CONFIRMED,INCOMPLETE,CONFLICT |
| actor | string |  |
| authorization_ref | string |  |
| changes_json | string |  |
| guards_json | string |  |
| result | string |  |
| evidence_ref | string |  |

## Reference Library

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| title | string |  |
| technique_id | string | → Techniques |
| source_ref | string |  |
| author | string |  |
| rights | string |  |
| context | string |  |
| limitations | string |  |
| provenance | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Reference Library |

## Examples

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| title | string |  |
| kind | string |  |
| department | string |  |
| source_ref | string |  |
| technique_id | string | → Techniques |
| expected | string |  |
| observed | string |  |
| limitations | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Examples |

## Techniques

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| name | string |  |
| department | string |  |
| when_to_use | string |  |
| procedure | string |  |
| tradeoff | string |  |
| example | string |  |
| validation | string |  |
| sources | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Techniques |

## Creative Preferences

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| category | string |  |
| department | string |  |
| context | string |  |
| preference | string |  |
| reason | string |  |
| feedback_ref | string |  |
| scope | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Creative Preferences |

## Model Compatibility

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| model_id | string |  |
| catalog_ref | string |  |
| output_type | string |  |
| checked_at | string |  |
| generation_tested | boolean |  |
| limitations | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Model Compatibility |

## Production Lessons

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| department | string |  |
| context | string |  |
| hypothesis | string |  |
| observation | string |  |
| correction | string |  |
| evidence_ref | string |  |
| scope | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Production Lessons |

## Director Profiles

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| title | string |  |
| intention | string |  |
| principle | string |  |
| application | string |  |
| sources | string |  |
| limitations | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Director Profiles |

## Genre Profiles

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| name | string |  |
| question | string |  |
| tools | string |  |
| pacing | string |  |
| limitations | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Genre Profiles |

## Visual Standards

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| department | string |  |
| context | string |  |
| criterion | string |  |
| good_example_ref | string | → Examples |
| bad_example_ref | string | → Examples |
| limitations | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Visual Standards |

## Evaluation Results

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| target_table | string |  |
| target_id | string |  |
| target_revision | integer |  |
| department | string |  |
| rubric_ref | string |  |
| reviewer | string |  |
| technical_result | string |  |
| artistic_result | string |  |
| evidence | string |  |
| limitations | string |  |
| decision | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Evaluation Results |

## Prompt Library

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| name | string |  |
| model_id | string |  |
| intent_ref | string |  |
| compiled_ref | string |  |
| catalog_checked_at | string |  |
| generation_tested | boolean |  |
| observed | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Prompt Library |

## Pairwise Comparisons

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| target_id | string | → Examples |
| target_revision | integer |  |
| department | string |  |
| session_ref | string |  |
| reviewer_ids | string |  |
| order_results_json | string |  |
| outcome | string |  |
| divergences | string |  |
| human_decision_ref | string |  |
| limitations | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Pairwise Comparisons |

## Human Feedback

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| evaluation_id | string | → Evaluation Results |
| target_table | string |  |
| target_id | string |  |
| target_revision | integer |  |
| human_decision | string |  |
| user_message_ref | string |  |
| reason | string |  |
| evidence | string |  |
| preference_scope | string |  |
| context | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Human Feedback |

## Failure Diagnostics

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| target_table | string |  |
| target_id | string |  |
| target_revision | integer |  |
| department | string |  |
| symptom | string |  |
| evidence | string |  |
| probable_cause | string |  |
| alternative_causes | string |  |
| missing_evidence | string |  |
| confidence | string |  |
| repair | string |  |
| protected | string |  |
| verification | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Failure Diagnostics |

## Revision Results

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| target_table | string |  |
| previous_id | string |  |
| previous_revision | integer |  |
| current_id | string |  |
| current_revision | integer |  |
| problem | string |  |
| changed_elements | string |  |
| protected_elements | string |  |
| resolved | string |  |
| persistent | string |  |
| introduced | string |  |
| technical_result | string |  |
| artistic_result | string |  |
| evidence | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Revision Results |

## Experiments

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| department | string |  |
| lab | string |  |
| objective | string |  |
| hypothesis | string |  |
| primary_variable | string |  |
| secondary_variables | string |  |
| protected | string |  |
| references | string |  |
| tool | string |  |
| authorized_max_variants | integer |  |
| authorization_ref | string |  |
| variants_json | string |  |
| evaluation_criteria | string |  |
| expected | string |  |
| observed | string |  |
| limitations | string |  |
| human_decision_ref | string |  |
| lesson_ref | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Experiments |

## Artifact Registry

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| kind | string | REFERENCE,TECHNICAL_PREVIS,ARTISTIC_PREVIS,NARRATIVE_PREVIS,VISUAL_DRAFT,PRODUCTION_EXPORT,FINAL_ASSET |
| department | string |  |
| gate_id | string |  |
| version | integer |  |
| uri | string |  |
| sha256 | string |  |
| origin | string |  |
| rights | string |  |
| experiment_id | string | → Experiments |
| technical_review_id | string | → Evaluation Results |
| artistic_review_id | string | → Evaluation Results |
| approval_id | string | → Approvals |
| supersedes_id | string | → Artifact Registry |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |

## Tool Capabilities

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| name | string |  |
| environment | string |  |
| availability | string | AVAILABLE_VALIDATED,AVAILABLE_UNTESTED,UNAVAILABLE,NOT_AUTHORIZED,LIMITED,UNKNOWN |
| scope | string |  |
| evidence_ref | string |  |
| alternative | string |  |
| checked_at | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Tool Capabilities |

## Execution Evidence

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| run_id | string |  |
| event_type | string |  |
| department | string |  |
| operation | string |  |
| execution_state | string | PLANNED,REQUESTED,EXECUTED,RETURNED,VALIDATED,APPROVED,FAILED |
| context_ref | string |  |
| knowledge_used | string |  |
| validators | string |  |
| tools | string |  |
| result | string |  |
| evidence_ref | string |  |
| limitations | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Execution Evidence |

## Checkpoints

| Coluna | Tipo | Enum / relação |
|---|---|---|
| id | string |  |
| project_id | string |  |
| episode_id | string |  |
| revision | integer |  |
| updated_at | string |  |
| updated_by | string |  |
| is_test | boolean |  |
| last_op_id | string |  |
| run_id | string |  |
| snapshot_ref | string |  |
| snapshot_sha256 | string |  |
| source_read_at | string |  |
| sync_status | string |  |
| last_confirmed_op | string |  |
| pending | string |  |
| recovery_ref | string |  |
| status | string | DRAFT,REVIEW_REQUIRED,APPROVED,LOCKED,REJECTED,ARCHIVED |
| supersedes_id | string | → Checkpoints |
