---
name: autoresearch
description: "Autonomt selvforbedringssystem baseret på Karpathys Auto Research-princip. Brug denne skill når du vil bygge et system der automatisk eksperimenterer, evaluerer og forbedrer et output over tid uden menneskelig indblanding. Trigger på: byg en self-improving loop, autoresearch, autonom optimering, lad AI forbedre sig selv, kør eksperimenter autonomt, skill-optimering, prompt-optimering, selvforbedrende agent, eval matrix, kør evals, forbedre mine skills, KEEP, DISCARD, score forbedret, iterér på skill. Relevant for alle use cases der har et målbart output og en klar succesmetrik: email copy, prompt kvalitet, rapportformat, nyhedsbrev, landingssider, skill-kvalitet."
version: 1.4.1-community
---

# Auto Research Skill

> **TL;DR:** Et autonomt forbedringssystem i to niveauer. **Simpelt loop** (Ja/Nej-spørgsmål, hurtig start) til enkelttekster, og **Eval Matrix** (kategoriserede evals med vægte, programmatisk grading, git-baseret versionskontrol) til at forbedre hele skills over tid. Kerneprincippet, lånt 1:1 fra Karpathy: eval-funktion, testdata og kontekst låses fast, kun det optimerede artefakt ændres. Vælg det niveau der matcher din opgaves kompleksitet.

---

## Hvad er autoresearch?

Idéen kommer fra Andrej Karpathys autoresearch-projekt: i stedet for at bede en AI "gør det bedre" og håbe på det bedste, kører du et kontrolleret eksperiment. Tre ting låses fast, nemlig hvordan der måles (eval-funktionen), hvad der testes på (testdata) og hvilken kontekst der gælder (context_profile). Derefter må AI'en ændre præcis én ting ad gangen i det artefakt du vil forbedre. Hver ny version scores mod de fastlåste kriterier. Er scoren bedre, beholdes ændringen (KEEP). Er den dårligere, ryger den ud (DISCARD). Gentag.

Hvorfor så rigidt? Fordi en AI uden fastlåste målekriterier "forbedrer" i cirkler. Den omskriver, du nikker, og tre versioner senere kan ingen sige om v5 faktisk er bedre end v2. Med fastlåste kriterier får du en dokumenteret forbedringskurve du kan stole på.

**Hvad kan optimeres?** Alt med et målbart output der gentages: prompts, skills, emailskabeloner, rapportformater, nyhedsbreve, landingssidetekster.

**Hvad kræver det?** Niveau 1 kræver kun en samtale med Claude og fem minutter. Niveau 2 kræver git og lidt opsætning, men giver en permanent eval-suite der kan genbruges hver gang skillen ændres.

**Tre roller, adskilt med vilje:** en generator der laver nye versioner, en grader der scorer dem i separat kontekst, og et loop der beslutter KEEP eller DISCARD. Adskillelsen er ikke pedanteri. En agent der scorer sit eget arbejde scorer det for højt, se verifikationspasset nedenfor.

---

## VERIFIKATIONSPAS (obligatorisk før enhver KEEP)

**Før du committer en KEEP eller siger "score forbedret":**

1. Vis FAKTISK ny score, ikke gennemsnit eller skøn — citér fra results.tsv.
2. Verificér at git diff KUN viser ændringer i det optimerede artefakt (SKILL.md), ikke i eval_matrix.json, testcases.json eller context_profile.json.
3. Bekræft at grader-konteksten var separat (generatoren så IKKE eval_matrix).
4. Hvis score er på eller over 95%, mistanke om eval-inflation — kør L3/L4 adversarial check.
5. Hvis "score forbedret" rapporteres, citér baseline-tal + nyt tal + delta.

Spring ikke disse trin over, heller ikke ved små iterationer. "Score forbedret" uden verifikation er den mest gentagne fejl-cyklus. Self-eval bias er reel: i den dokumenterede deep-research-kørsel gav samme agent sig selv 16/16, mens en uafhængig bedømmer gav 14/16 på præcis samme output.

---

## Hurtigvalg: Hvilket niveau?

| Spørgsmål | → Simpelt Loop | → Eval Matrix |
|---|---|---|
| Skal jeg optimere en enkelt tekst/prompt? | ✓ | |
| Skal jeg forbedre en hel skill over tid? | | ✓ |
| Har jeg under 5 evalkriterier? | ✓ | |
| Har jeg brug for kategorier med vægte? | | ✓ |
| Vil jeg køre det som engangsforbedring? | ✓ | |
| Vil jeg have en permanent eval-suite? | | ✓ |

---

# NIVEAU 1: Simpelt Loop

> Forbedrer din tekst automatisk — laver en ny version (Challenger), scorer den med Ja/Nej-spørgsmål, og beslutter: KEEP eller DISCARD.

## De 3 ingredienser

| Ingrediens | Hvad det er | Eksempel |
|---|---|---|
| **Noget du vil forbedre** | Den tekst eller instruktion du optimerer | System prompt, email copy, rapport-format |
| **Tjekliste med Ja/Nej-spørgsmål** | Din målestok for "godt nok" | "Dækker rapporten alle 15 spørgsmål?" |
| **Én ændring ad gangen** | Hvad Claude ændrer i hver runde | Ordvalg, struktur, eksempler, format |

### Hurtigstart

```
Kør autoresearch-loopet på dette:

BASELINE: "Skriv en email-emnelinje for et nyhedsbrev om AI-trends i 2025"

EVALS:
1. Er emnelinjen under 50 tegn? (Ja/Nej)
2. Starter den med et tal eller handlingsord? (Ja/Nej)
3. Nævner den et specifikt emne (ikke bare "AI")? (Ja/Nej)
4. Er den fri for spam-ord (gratis, klik her, tilbud)? (Ja/Nej)

Kør 5 iterationer. Vis results.tsv til sidst.
```

### Loopet

```
  baseline.md → Ny version → Tjek score → score > baseline? → KEEP/DISCARD → gentag
                (1 ændring)   (Ja/Nej)
```

Se `references/use-cases.md` for flere eksempler.

---

# NIVEAU 2: Eval Matrix (Karpathy-mønsteret)

> Baseret direkte på [karpathy/autoresearch](https://github.com/karpathy/autoresearch). Oversætter det autonome eksperiment-loop fra LLM-træning til skill-optimering.

## Kerneprincippet

Karpathys system har fire ufravigelige regler der gør det effektivt:

1. **Eval-funktionen ændres aldrig under et loop.** Hans `evaluate_bpb()` i prepare.py er read-only. Vores `eval_matrix.json` er tilsvarende fastlåst.
2. **Testdata ændres aldrig.** Hans valideringsshard er pinned. Vores `testcases.json` er fastlåst.
3. **Kun én fil ændres.** Hans agent rører kun `train.py`. Vores agent rører kun `SKILL.md`.
4. **Kontekst-profilen ændres aldrig under et loop.** `context_profile.json` definerer domænet evals tester mod og er read-only.

### Rolleoversigt

| Karpathy | Eval Matrix | Rolle |
|---|---|---|
| `train.py` | `SKILL.md` | Det der optimeres |
| `evaluate_bpb()` | `eval_matrix.json` | Fastlåst bedømmelse |
| (implicit) | `context_profile.json` | Fastlåst domæne-kontekst |
| `program.md` | `evals/program.md` | Research-org instruktioner |
| `results.tsv` | `evals/results.tsv` | Eksperiment-log |
| validation shard | `testcases.json` | Fastlåst testdata |
| git branch | git branch | Versionskontrol |

### Separation of Concerns (det vigtigste)

```
GENERATOR (skill der optimeres) → producerer output
     ↓
GRADER (separat kontekst) → scorer output mod eval_matrix
     ↓
DECISION ENGINE → keep/discard baseret på score
```

**Generatoren scorer ALDRIG sit eget output.** Karpathy løser dette med en fastlåst Python-funktion. Vi løser det med enten programmatiske checks eller et separat LLM-kald der aldrig har set skill-instruktionerne. Dette er ikke teori: self-eval bias har målbart inflateret borderline-cases (16/16 vs. uafhængig 14/16).

## Fil-struktur

```
min-skill/
├── SKILL.md                    ← Det der optimeres
├── references/
└── evals/                      ← Eval-infrastruktur
    ├── context_profile.json    ← Fastlåst domæne-kontekst fra Fase 0
    ├── eval_matrix.json        ← Fastlåst: kategorier, spørgsmål, vægte
    ├── testcases.json          ← Fastlåst: input-prompts
    ├── program.md              ← Research-org instruktioner
    ├── resource.md             ← Akkumuleret læring
    ├── results.tsv             ← Eksperiment-log
    └── grading/                ← Output fra hver kørsel
```

## eval_matrix.json — Format

```json
{
  "skill_name": "min-skill",
  "context_profile": "evals/context_profile.json",
  "categories": [
    {
      "name": "Korrekthed",
      "weight": 2.0,
      "evals": [
        {
          "id": "K1",
          "question": "Er alle sektioner til stede?",
          "type": "binary",
          "grading": "programmatic",
          "grading_hint": "Scan for sektion-headers"
        },
        {
          "id": "K2",
          "question": "Er kernebudskabet bevaret?",
          "type": "binary",
          "grading": "llm_judge"
        }
      ]
    }
  ],
  "scoring": {
    "method": "weighted_sum",
    "formula": "sum(category_weight * (passed / total))"
  }
}
```

### Eval-typer

| Grading | Hvornår | Fordel |
|---|---|---|
| `programmatic` | Objektive: længde, format, tilstedeværelse af nøgleord | Hurtig, deterministisk, ingen eval-gaming |
| `llm_judge` | Subjektive: tone, overbevisningskraft, kvalitet | Fleksibel, men kræver separat kontekst |

**Tommelfingerregel:** Brug `programmatic` for alt der kan tjekkes med regex/tælling. Brug `llm_judge` kun for det der kræver forståelse.

## testcases.json — Format

```json
{
  "testcases": [
    {
      "id": "TC1",
      "name": "Standard case",
      "prompt": "Den opgave der gives til skillen",
      "context": "Ekstra kontekst til graderen",
      "difficulty": "standard"
    }
  ]
}
```

Inkludér altid: 1 standard case, 1 hard case, 1 edge case.

## Loopet (kør autonomt)

```
1. Læs SKILL.md + resource.md + context_profile.json + seneste results.tsv
2. Analysér svageste eval-kategori
3. Lav ÉN ændring i SKILL.md → git commit
4. Kør alle testcases med opdateret skill
5. Grade hvert output med eval_matrix (SEPARAT kontekst)
6. Beregn total_score
7. score > baseline → KEEP (branch avancerer)
   score ≤ baseline → DISCARD (git reset)
8. Kør VERIFIKATIONSPAS før KEEP committes
9. Log i results.tsv og resource.md
10. Gentag fra 1
```

## Eval-eskalering

Når score er maxed (3+ runder uden forbedring):

| Niveau | Type | Eksempel |
|---|---|---|
| L1 | Strukturel korrekthed | "Indeholder outputtet alle sektioner?" |
| L2 | Indholdsmæssig kvalitet | "Er anbefalinger understøttet af data?" |
| L3 | Ekspert-godkendelse | "Ville en VP godkende dette?" |
| L4 | Stress/adversarial | "Håndterer skillen manglende data?" |

Start med L1+L2. Tilføj L3 ved score > 80%. Tilføj L4 ved score > 90%.

**Erfaring:** Strukturelle evals (L1) plateauer hurtigt — baseline rammer ofte fuld score på første forsøg. Det betyder ikke at skillen er færdig, men at evalsne er for lette. Eskalér.

## Scoring

```
total_score = Σ (category_weight × passed_in_category / total_in_category)
```

Eksempel med 2 kategorier:
- Korrekthed (vægt 2.0): 3/4 bestået → 2.0 × 0.75 = 1.50
- Kvalitet (vægt 1.5): 2/3 bestået → 1.5 × 0.67 = 1.00
- **Total: 2.50 / 3.50**

---

## Kom i gang med Eval Matrix

### FASE 0: Context Interrogation (OBLIGATORISK)

> **Princip:** Evals der tester generisk viden er værdiløse. Evals skal teste mod den specifikke kontekst skillen opererer i. Denne fase indsnævrer scope FØR eval_matrix.json og testcases.json genereres.

**Hvornår:** ALTID inden Trin 1. Ingen undtagelser — selv "generelle" skills har en specifik bruger og kontekst.

**Processen:** Stil brugeren 5-8 spørgsmål i tre lag. Gem svarene i `evals/context_profile.json`.

#### Lag 1: Domæne-afgrænsning — "Hvad er skillen *ikke* til?"

| # | Spørgsmål | Hvorfor |
|---|---|---|
| D1 | Hvilken branche/virksomhed/sektor opererer denne skill inden for? | Styrer terminologi og realisme i testcases |
| D2 | Hvem læser outputtet — hvilken rolle, titel og beslutningsniveau? | Styrer tone, detaljegrad og kvalitetskriterier i llm_judge |
| D3 | Nævn 2-3 konkrete scenarier skillen SKAL klare perfekt. | Bliver direkte til testcases — standard, hard og edge |
| D4 | Hvad skal skillen eksplicit IKKE bruges til? | Forhindrer scope-creep og genererer out-of-scope edge case |

#### Lag 2: Kontekst-dybde — "Hvad skal evals vide om din verden?"

| # | Spørgsmål | Hvorfor |
|---|---|---|
| K1 | List 5-10 specifikke termer, forkortelser eller navne skillen SKAL kende. | Bliver til programmatic grading: regex-check for term-tilstedeværelse |
| K2 | Hvilke interne regler eller begrænsninger gælder? | Danner "must include/must avoid" evals — hvert regel-element → ét binary eval |
| K3 | Er der eksisterende skills, dokumenter eller knowledge bases med relevant kontekst? | Undgår genopfinding — agenten læser disse som reference |

#### Lag 3: Optimerings-scope — "Hvor bredt eller smalt tester vi?"

| # | Spørgsmål | Hvorfor |
|---|---|---|
| S1 | Vil du optimere bredt (hele skillen) eller smalt (én use case)? Bredt = 5-8 testcases. Smalt = 3-5. | Bestemmer antal og type testcases direkte |
| S2 | Hvem er "godkenderen" — hvem ville sige "dette er godt nok"? | Definerer L3-eval: "Ville [godkender] acceptere dette uden redigering?" |
| S3 | Har du set et konkret output der er "gold standard"? Hvis ja, indsæt eller link det. | Bruges som reference i llm_judge |

#### Pre-fill workflow (OBLIGATORISK før spørgsmål stilles)

1. **Scan:** Læs brugerens memories, eksisterende skills og CLAUDE.md for kontekst om domæne, rolle, organisation og terminologi.
2. **Pre-fill:** Udfyld så mange svar som muligt. Markér hvert med `[PRE-FILLED fra: kilde]`.
3. **Præsentér:** Vis de pre-filled svar sammen med de resterende åbne spørgsmål: "Baseret på din kontekst foreslår jeg følgende — ret til eller bekræft:"
4. **Bekræft:** Kun åbne spørgsmål kræver nyt input.

**Effekt:** For en bruger med rig eksisterende kontekst reduceres interrogationen fra 10 spørgsmål til 2-4 supplerende.

#### Skill-arketype → spørgsmålsprofil

| Skill-arketype | Eksempler | Spørgsmål at stille | Spring over |
|---|---|---|---|
| **Tekst-transformation** | humanizer, oversætter, formatter | D1, D2, K1, S1 | K2, S2, D3 |
| **Strategisk kommunikation** | executive-communication | D1-D4, K1-K3, S1-S3 | Ingen — alle |
| **Data/analyse** | salgsdata-analyse | D1, D2, D3, K1, K2, S1, S2 | D4, S3, K3 |
| **Personlig branding** | linkedin-presence | D1, D2, K1, S1, S3 | K2, K3, D4 |
| **Coaching/ledelse** | leadership-excellence | D1, D2, D3, K1, K2, S1 | D4, S3, K3 |

**Regel:** Hvis skill-typen ikke matcher en arketype, stil alle 10 spørgsmål.

#### Interrogation-regler

1. **Stil alle relevante spørgsmål i én samlet blok** — ikke ét ad gangen.
2. **Pre-fill er obligatorisk.** Spring aldrig denne over.
3. **Adaptér til skill-arketype.**
4. **Aldrig mere end 10 spørgsmål.**
5. **Ved kontekst-konflikt:** Brugerens svar trumfer pre-filled kontekst. Notér konflikten i context_profile under `"context_conflicts"`.

#### context_profile.json — Output-format

Gem svarene i denne struktur. Filen er **READ-ONLY under loopet** (ligesom eval_matrix.json).

```json
{
  "skill_name": "kundeservice-svar",
  "interrogation_date": "2026-04-06",
  "domain": {
    "industry": "E-commerce (webshop, B2C)",
    "company": "Fiktiv webshop (eksempel)",
    "sector_specifics": "Onlinesalg med høj ordrevolumen, sæsonspidser og returhåndtering",
    "not_for": ["B2B-kontrakter", "juridisk rådgivning", "fysisk butiksdrift"]
  },
  "audience": {
    "primary_recipient": "Kundeservicemedarbejder (skill-ejeren)",
    "secondary_recipients": ["kundeservicechefen", "kunderne der modtager svarene"],
    "approval_authority": "Kundeservicechefen for svar der involverer kompensation"
  },
  "must_know_terms": ["returret", "reklamation", "fortrydelsesret", "track & trace"],
  "must_know_rules": [
    "Svar altid i brandets tone, venlig og direkte",
    "Lov aldrig kompensation uden godkendelse"
  ],
  "existing_context_sources": ["brand-tone-guide", "FAQ-dokument"],
  "optimization_scope": "narrow",
  "scope_detail": "Fokus: de 10 hyppigste henvendelsestyper",
  "gold_standard": null,
  "success_criteria": "Svar som kundeservicechefen ville sende uden redigering"
}
```

#### Sådan driver context_profile eval-generering

| context_profile felt | Bruges i | Konkret effekt |
|---|---|---|
| `domain.industry` + `sector_specifics` | testcases.json | Branchespecifikke scenarier, ikke generiske |
| `domain.not_for` | testcases.json → edge cases | Edge-case der tester at skillen afviser out-of-scope input |
| `audience.primary_recipient` | eval_matrix → llm_judge | "Vurder om output er passende for [rolle]" |
| `audience.approval_authority` | eval_matrix → L3 eval | "Ville [godkender] acceptere dette uden redigering?" |
| `must_know_terms` | eval_matrix → programmatic | Regex-check: output SKAL indeholde mindst 50% af termerne |
| `must_know_rules` | eval_matrix → must include/avoid | Hvert regel-element → ét binary eval |
| `existing_context_sources` | Loop-agentens read-list | Agenten læser disse ved Challenger-generering |
| `optimization_scope` + `scope_detail` | testcases.json | narrow = 3-5, broad = 5-8 testcases |
| `gold_standard` | eval_matrix → llm_judge reference | Hvis sat: sammenlign output med gold_standard |
| `success_criteria` | eval_matrix → kvalitetsmål | Indgår i alle llm_judge prompts |

---

### Trin 1: Opret eval_matrix.json for din skill
```
Opret en eval_matrix.json for min [skill-navn] skill.
Brug context_profile.json til at forme kategorier og evals.
Inkludér 3-4 kategorier med 2-3 evals hver.
Brug programmatic grading hvor muligt.
Alle llm_judge prompts skal inkludere audience og success_criteria fra context_profile.
```

### Trin 2: Opret testcases
```
Opret testcases.json baseret på context_profile.json.
Brug domain, must_know_terms og scope_detail til at forme realistiske prompts.
Standard case = typisk arbejdsdag. Hard case = politisk kompleks situation. Edge case = manglende data/modstand.
```

### Trin 3: Kør baseline
```
Kør min skill på alle testcases og grade med eval_matrix.
Gem som baseline i results.tsv.
```

### Trin 4: Start loopet
```
Kør autoresearch eval matrix loopet på min [skill-navn] skill.
Brug evals/ mappen som reference. 10 iterationer.
Kør VERIFIKATIONSPAS før hver KEEP.
```

---

## Fejlfinding

| Symptom | Årsag | Løsning |
|---|---|---|
| Score sidder fast | Evals for brede | Split svær eval i to specifikke |
| Challenger vinder altid | Evals for lette | Tilføj L3/L4 evals |
| 20+ iterationer uden fremgang | Agenten gentager ændringer | Tilføj: "Hvis score uændret i 3 runder: radikal strukturændring" |
| Output passer evals men kvalitet faldet | Eval-gaming | Erstat gamed eval med substans-eval |
| Programmatic grader er for streng/mild | Threshold forkert | Justér grading_hint parametre |
| resource.md over 150 linjer | Naturlig vækst | Konsolidér: top-10 indsigter, arkivér resten |
| LLM-judge er inkonsistent | Grading-prompt for vag | Gør judge-prompt mere specifik med eksempler |
| Score når 16/16 men virker for højt | Self-eval bias | Kør uafhængig grader — borderline-cases trender mod Ja |
| Evals tester generisk viden | Context Interrogation sprunget over | Kør Fase 0 — gengenerer evals baseret på context_profile |

---

## Indsigter fra rigtige kørsler

Destilleret fra deep-research-agent optimeringen (8 iterationer + 2 uafhængige re-evals):

1. **Eksplicitte forbud slår positive instruktioner.** "Vær specifik" gør intet. "Skriv aldrig X, Y, Z" virker. Gælder for al sproglig kvalitet.
2. **Stakeholder + deadline er den enkeltændring med størst effekt.** At tvinge "hvem handler, hvornår?" ind i outputtet flytter det fra informativt til beslutningsklart.
3. **Reasoning-depth er ofte en emergent egenskab** af multi-pass metoden, ikke noget der kræver eksplicit prompting. Metoden ER prompt engineering.
4. **Self-eval bias er reel og målbar.** Separat grader er ikke valgfri ved scores over 90%.
5. **Nogle "fejl" er domæneviden-problemer, ikke prompt-problemer.** Løsning: tilføj en kontekst-reference-fil, ikke endnu en prompt-instruktion.

---

## Eksempel Eval Matrix (klar til brug)

| Skill | Kategorier | Evals | Fokus |
|---|---|---|---|
| `humanizer` (eksempel) | Detektion, Bevarelse, Naturlighed, Format | 8 | AI-tell fjernelse |

Se `references/eval-matrix/example-skill-eval/` for komplet eval_matrix.json + testcases.json du kan bruge som skabelon til dine egne skills.

---

## Referencemateriale

- `references/use-cases.md` — Eksempler på simpelt loop
- `references/eval-matrix/EVAL-MATRIX.md` — Fuld framework-dokumentation
- `references/eval-matrix/QUICKSTART.md` — Hurtig opsætning
- `references/eval-matrix/example-skill-eval/` — Komplet eksempel eval matrix
- `references/eval-matrix/runner/run_eval.py` — Programmatisk grader
- `references/n8n-integration.md` — n8n workflow integration
- `references/github-actions.md` — GitHub Actions cloud-kørsel
