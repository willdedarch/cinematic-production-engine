"""Select references by episode, technique, genre and concrete directorial intention."""
from functools import lru_cache
import json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GATE_DEPTS={"G1":{"research","design"},"G2":{"narrative","story"},"G3":{"narrative","emotion"},"G4":{"narrative","screenplay","dialogue"},"G5":{"optics","light","composition","direction"},"G7":{"casting","performance","design"},"G8":{"design","geometry","locations","composition"},"G9":{"design","props"},"G10":{"optics","direction","composition","continuity"},"G13":{"sound","editing"},"G14":{"continuity","editing","sound"}}


def tokens(text):
    folded = unicodedata.normalize('NFKD', str(text).casefold())
    return tuple(re.findall('[a-z0-9]+', ''.join(c for c in folded if not unicodedata.combining(c))))


def words(text):
    return set(tokens(text)) - {'de','a','as','os','o','em','do','da','um','para','com','the','e'}


@lru_cache(maxsize=1)
def genre_catalog():
    profiles = json.loads((ROOT/'knowledge/genre-profiles.json').read_text(encoding='utf-8'))
    return {profile['genre']: profile for profile in profiles}


@lru_cache(maxsize=1)
def _genre_aliases():
    aliases = {}
    for key, profile in genre_catalog().items():
        for label in (key, profile['name'], *profile['aliases']):
            normalized = tokens(label)
            if normalized in aliases and aliases[normalized] != key:
                raise ValueError('Ambiguous alias in genre catalog: ' + label)
            aliases[normalized] = key
    return aliases, max(map(len, aliases))


def canonical_genres(labels):
    """Recognize explicit bilingual labels in order, preferring the longest local phrase."""
    aliases, max_size = _genre_aliases()
    genres = []
    for label in labels:
        parts = tokens(label)
        offset = 0
        while offset < len(parts):
            for size in range(min(max_size, len(parts) - offset), 0, -1):
                if match := aliases.get(parts[offset:offset + size]):
                    genres.append(match)
                    offset += size
                    break
            else:
                offset += 1
    return list(dict.fromkeys(genres))


def _phrase_found(text, phrases):
    wordline = ' ' + ' '.join(tokens(text)) + ' '
    return any(' ' + ' '.join(tokens(phrase)) + ' ' in wordline for phrase in phrases)


def classify_intention(genres, intention='', creative_profile=''):
    if 'guerra' not in genres:
        return 'genre_default'
    if creative_profile == 'action_led_war':
        return 'action_led_war'
    choices = ('65% ação','65% action','guerra de ação','ação intensa','ação cinematográfica intensa',
               'predominância de ação','combate visível','combate em quadro','combates em quadro',
               'action first','action led','intense action','visible combat','combat on screen')
    # The input phrase is a retrieval cue. Avoid treating an explicit negation as a positive cue.
    clauses = re.split('[,.;!?\n]',str(intention))
    relevant = [clause for clause in clauses if _phrase_found(clause,choices)]
    negative_words = {'nao','sem','evitar','dispensar','no','not','without','avoid','exclude'}
    positive = False
    for clause in relevant:
        clause_terms = ' '.join(tokens(clause))
        for cue in choices:
            cue_terms = ' '.join(tokens(cue))
            before, match, _ = (' ' + clause_terms + ' ').partition(' ' + cue_terms + ' ')
            if match and not (set(before.split()[-4:]) & negative_words):
                positive = True
                break
        if positive:
            break
    if positive or (not relevant and genres[0] in {'guerra','ação'} and 'ação' in genres):
        return 'action_led_war'
    return 'genre_default'


@lru_cache(maxsize=1)
def _genre_cases():
    cases = json.loads((ROOT/'knowledge/genre-cases.json').read_text(encoding='utf-8'))
    return {case['case_id']: case for case in cases}


def genre_cards(genres, *, action_first=False):
    cases = _genre_cases()
    profiles = genre_catalog()
    return [cases['WAR-ACTION-16' if genre == 'guerra' and action_first else profiles[genre]['case_id']]
            for genre in genres]


def matching_genre_cases(genre, *, action_first=False):
    genres = canonical_genres((genre,))
    selected = action_first or classify_intention(genres) == 'action_led_war'
    return genre_cards(genres, action_first=selected)

def genre_case(genre):
    return next(iter(matching_genre_cases(genre)),None)

def select(snapshot,project,episode,gate,facets,model,intention,*,confirmed_messages=(),classification=None):
    project_id,episode_id=project["id"],episode["id"]
    depts=set(facets)|GATE_DEPTS.get(gate,set())
    keywords=words(intention)
    classification = classification or {}
    genres = set(classification.get('genres', canonical_genres((episode['genre'],))))
    action_first = classification.get('intent_mode') == 'action_led_war'
    omit_quiet_war_examples = action_first or ('guerra' in genres and not classification.get('war_study_relevant',False))
    techniques={t["id"]:t for t in snapshot["tables"]["Techniques"]}
    results,explanations={},{}
    for table in ("Techniques","Examples","Reference Library","Creative Preferences","Production Lessons","Model Compatibility","Human Feedback","Failure Diagnostics","Evaluation Results"):
        ranked=[]
        for row in snapshot["tables"][table]:
            if table=="Human Feedback" and (row["target_table"]=="Pairwise Comparisons" or row["is_test"]
                    or row["status"] not in {"APPROVED","LOCKED"} or row["user_message_ref"] not in confirmed_messages):continue
            if table=="Examples" and row["kind"]=="TAKE_COMPARISON":continue
            local=row["project_id"]==project_id and row["episode_id"] in ("",episode_id)
            shared=row["project_id"]=="LIB-CPE31" and table in {"Techniques","Examples","Reference Library","Production Lessons","Model Compatibility","Creative Preferences"}
            if not (local or shared) or row["status"] in {"ARCHIVED","REJECTED"}:continue
            if shared and table=="Creative Preferences" and row.get("category")!="USER_CONSTRAINT":continue
            if table=="Model Compatibility" and model and row.get("model_id")!=model:continue
            technique=techniques.get(row.get("technique_id"),{})
            dep=row.get("department",technique.get("department",""))
            descriptor=" ".join(str(row.get(k,"")) for k in ("title","name","context","expected","when_to_use","observation","scope"))
            if omit_quiet_war_examples and shared and table in {'Examples','Reference Library'}:
                identity = ' '.join(str(row.get(k,'')) for k in ('title','name','context','uri','artifact_ref','media_ref'))
                quiet_case = _phrase_found(identity, ('A última água','A parte seca','A linha azul','O pano vermelho',
                                                       'last water','shelter','war action pilot','pilot15',
                                                       'partilha do cantil','entrega da manta','partilhar água'))
                if quiet_case:
                    continue
                if action_first and dep == 'integrated' and not (_phrase_found(descriptor, ('combate visível','ação física','ação cinematográfica',
                                                                           'destruição ficcional','visible combat','action driven'))
                                                     or 'ação' in canonical_genres((descriptor,))):
                    continue
            matches=keywords&words(descriptor+" "+technique.get("when_to_use",""))
            reasons=[]
            if matches:reasons.append("intenção: "+", ".join(sorted(matches)))
            if dep in depts:reasons.append("departamento: "+dep)
            genre_match=genres&set(canonical_genres((descriptor,)))
            if genre_match:reasons.append("gênero: "+", ".join(sorted(genre_match)))
            if local:reasons.append("contexto do projeto")
            if model and row.get("model_id")==model:reasons.append("modelo escolhido")
            constraint=(table=="Creative Preferences" and row.get("category")=="USER_CONSTRAINT"
                        and row["status"] in {"APPROVED","LOCKED"})
            if constraint:reasons.append("restrição explícita")
            if not reasons and dep!="integrated":continue
            score=50*constraint+12*bool(matches)+min(len(matches),8)+8*(dep in depts)+6*bool(genre_match)+4*local+2*(row["status"] in {"APPROVED","LOCKED"})
            ranked.append((-score,row["id"],row,reasons or ["exemplo integrado"]))
        ranked.sort(key=lambda item:(item[0],item[1]))
        chosen=ranked if table=="Creative Preferences" else ranked[:8]
        results[table]=[x[2] for x in chosen]
        explanations[table]=[{"id":x[1],"why":x[3],"apply":x[2].get("context") or x[2].get("procedure") or x[2].get("expected") or ""} for x in chosen]
    return results,explanations
