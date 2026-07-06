# Eval Matrix Framework — Skill Self-Improvement System

> **Princip:** Hver skill har en fastlåst eval-funktion (som Karpathys `evaluate_bpb`), testcases der aldrig ændres, og en resource-fil der akkumulerer viden. Skillen selv er det der optimeres.

---

## Arkitektur: Karpathy-mønsteret oversat til skills

| Karpathy (LLM-træning) | Eval Matrix (skill-optimering) | Funktion |
|---|---|---|
| `train.py` | `SKILL.md` | Det der optimeres |
| `evaluate_bpb()` | `evals/eval_matrix.json` | Fastlåst bedømmelse |
| `program.md` | `evals/program.md` | Research-org instruktioner |
| `results.tsv` | `evals/results.tsv` | Eksperiment-log |
| `prepare.py` (data) | `evals/testcases.json` | Fastlåst testdata |
| git branch | git branch | Versionskontrol |
| `val_bpb` (lavere = bedre) | `total_score` (højere = bedre) | Enkelt komparativt mål |

### De tre ufravigelige regler

1. **Eval-funktionen ændres aldrig under et loop.** Ligesom `evaluate_bpb()` i prepare.py er read-only, er `eval_matrix.json` fastlåst under en eksperiment-serie.
2. **Testcases ændres aldrig under et loop.** Samme input, altid.
3. **Kun SKILL.md ændres.** Præcis som agenten kun rører `train.py`.

---

## Fil-struktur pr. skill

```
min-skill/
├── SKILL.md                    ← Det der optimeres (= train.py)
├── references/                 ← Skill-specifikke referencer
└── evals/                      ← NY: eval-infrastruktur
    ├── eval_matrix.json        ← Fastlåst: spørgsmål + vægte (= evaluate_bpb)
    ├── testcases.json          ← Fastlåst: input-prompts (= valideringsdata)
    ├── program.md              ← Research-org instruktioner (= program.md)
    ├── resource.md             ← Akkumuleret læring (vokser over tid)
    ├── results.tsv             ← Eksperiment-log
    └── grading/                ← Output fra hver kørsel
        ├── run_001.json
        ├── run_002.json
        └── ...
```

---

## eval_matrix.json — Anatomien

```json
{
  "skill_name": "humanizer",
  "version": "1.0",
  "metric": "total_score",
  "metric_direction": "higher_is_better",
  "max_score": null,
  "categories": [
    {
      "name": "Korrekthed",
      "weight": 2.0,
      "evals": [
        {
          "id": "K1",
          "question": "Er ALLE 10 AI-tells fra cheat-sheet scannet for i outputtet?",
          "type": "binary",
          "grading": "programmatic",
          "grading_hint": "grep output for mentions of each tell category"
        },
        {
          "id": "K2",
          "question": "Er kernebudskabet bevaret uændret efter humanisering?",
          "type": "binary",
          "grading": "llm_judge"
        }
      ]
    },
    {
      "name": "Kvalitet",
      "weight": 1.5,
      "evals": [
        {
          "id": "Q1",
          "question": "Ville en redaktør acceptere teksten uden redigering?",
          "type": "binary",
          "grading": "llm_judge"
        }
      ]
    }
  ],
  "scoring": {
    "method": "weighted_sum",
    "formula": "sum(category_weight * (passed_in_category / total_in_category))"
  }
}
```

### Eval-typer

| Type | Grading | Hvornår |
|---|---|---|
| `binary` + `programmatic` | Script tjekker (regex, ord-tælling, struktur) | Objektive krav: længde, format, tilstedeværelse |
| `binary` + `llm_judge` | Separat Claude-kald scorer (aldrig self-eval) | Subjektive krav: tone, overbevisningskraft |
| `numeric` + `programmatic` | Script returnerer tal (0-10, procent, etc.) | Kontinuerte metrikker: læsbarhed, AI-score |

### Kritisk: Separation of Concerns

```
GENERATOR (den skill der optimeres)
    ↓ producerer output
GRADER (separat kontekst, aldrig samme kald)
    ↓ scorer output
DECISION ENGINE (keep/discard baseret på score)
```

Generatoren scorer ALDRIG sit eget output. Dette forhindrer eval-gaming.

---

## testcases.json — Format

```json
{
  "skill_name": "humanizer",
  "testcases": [
    {
      "id": "TC1",
      "name": "Standard AI-tekst (dansk)",
      "prompt": "Humanisér denne tekst: 'Det er afgørende at bemærke, at digital transformation ikke blot handler om teknologi — det handler grundlæggende om mennesker.'",
      "input_files": [],
      "context": "Dansk professionel kontekst, business-tone",
      "difficulty": "standard"
    },
    {
      "id": "TC2",
      "name": "Teknisk AI-tekst med fagtermer",
      "prompt": "Humanisér: 'Denne banebrydende integration af CRM-data og marketing-dashboards muliggør en holistisk tilgang til datadrevet beslutningstagning, der fundamentalt transformerer organisationens analytiske kapabiliteter.'",
      "input_files": [],
      "context": "Teknisk kontekst, fagtermer skal bevares",
      "difficulty": "hard"
    },
    {
      "id": "TC3",
      "name": "Edge case: allerede naturlig tekst",
      "prompt": "Humanisér: 'Jeg sad i mødet og tænkte: det her giver ikke mening. Så sagde jeg det højt.'",
      "input_files": [],
      "context": "Tekst der allerede er naturlig — skill bør gøre minimal ændring",
      "difficulty": "edge"
    }
  ]
}
```

---

## program.md — Research-org instruktioner (pr. skill)

```markdown
# [Skill-navn] — Eval Matrix Self-Improvement

## Formål
Optimér [SKILL.md] så den scorer højere på eval_matrix.json
uden at ændre testcases eller eval-spørgsmål.

## Loop — kør autonomt

1. **Læs** SKILL.md + resource.md + seneste results.tsv
2. **Analysér** svageste eval-kategori fra seneste kørsel
3. **Lav ÉN ændring** i SKILL.md rettet mod den svageste kategori
4. **Git commit** ændringen med beskrivende besked
5. **Kør alle testcases** med den opdaterede skill
6. **Grade hvert output** med eval_matrix.json (SEPARAT kontekst)
7. **Beregn total_score**
8. **Beslut:**
   - score > baseline → KEEP (branch avancerer)
   - score ≤ baseline → DISCARD (git reset til forrige commit)
9. **Log** i results.tsv og resource.md
10. **Gentag fra 1**

## Regler
- Ændr kun SKILL.md (og references/ hvis relevant)
- Ændr ALDRIG eval_matrix.json eller testcases.json
- Log ALLE forsøg inkl. fejl
- Lav kun ÉN ændring per forsøg
- Kør autonomt — stop ikke for at spørge

## Eval-eskalering
Når score er maxed (3+ runder uden forbedring):
1. Tilføj 2-3 nye, hårdere evals til eval_matrix.json
2. Re-score baseline med nye evals
3. Fortsæt loop med udvidet eval-sæt
```

---

## results.tsv — Format

```
run_id	commit	total_score	max_score	category_scores	status	description
001	a1b2c3d	4.2	7.0	K:2.8/4.0|Q:1.4/3.0	baseline	Udgangspunkt
002	b2c3d4e	5.1	7.0	K:3.2/4.0|Q:1.9/3.0	keep	Tilføjet eksplicitte regler for em-dash
003	c3d4e5f	4.0	7.0	K:2.5/4.0|Q:1.5/3.0	discard	Fjernet tone-matching sektion
```

---

## Grading — Sådan scores (det vigtigste)

### Programmatisk grading (foretrukket)

For evals markeret `"grading": "programmatic"` — skriv et script:

```python
# evals/graders/check_word_count.py
def grade(output_text: str, testcase: dict) -> dict:
    word_count = len(output_text.split())
    passed = word_count <= 800
    return {
        "eval_id": "K3",
        "passed": passed,
        "evidence": f"Ordtælling: {word_count} (maks 800)",
        "value": word_count
    }
```

### LLM-judge grading (når nødvendigt)

For evals markeret `"grading": "llm_judge"` — brug separat kald:

```
Du er en uafhængig bedømmer. Du har ALDRIG set SKILL.md.
Du vurderer KUN outputtet.

Testcase: {testcase.prompt}
Output: {output_text}
Spørgsmål: {eval.question}

Svar KUN med JSON: {"passed": true/false, "evidence": "kort begrundelse"}
```

### Samlet score-beregning

```
total_score = Σ (category_weight × (passed_in_category / total_in_category))
```

Eksempel:
- Korrekthed (vægt 2.0): 3/4 bestået → 2.0 × 0.75 = 1.50
- Kvalitet (vægt 1.5): 2/3 bestået → 1.5 × 0.67 = 1.00
- **Total: 2.50 / 3.50 max**

---

## Eval-eskalering (fra Karpathy-mønsteret)

Når en skill maxer sine evals, eskaler:

| Niveau | Eval-type | Eksempel |
|---|---|---|
| **L1: Basis** | Strukturel korrekthed | "Indeholder outputtet alle 5 sektioner?" |
| **L2: Kvalitet** | Indholdsmæssig kvalitet | "Er alle anbefalinger understøttet af data?" |
| **L3: Ekspert** | Ville en ekspert godkende? | "Ville en VP acceptere dette som board-materiale?" |
| **L4: Stress** | Edge cases og adversarial | "Håndterer skillen manglende input-data korrekt?" |

Start med L1+L2. Tilføj L3 når score > 80%. Tilføj L4 når score > 90%.

---

## Integration med skill-creator

Eval Matrix frameworket er kompatibelt med skill-creator's eval-system:

1. `eval_matrix.json` → kan konverteres til skill-creator's `evals.json`
2. `testcases.json` → kan bruges som skill-creator's test prompts
3. `results.tsv` → supplerer skill-creator's `benchmark.json`

Forskellen: skill-creator kræver menneske-i-loopet. Eval Matrix kører autonomt.
