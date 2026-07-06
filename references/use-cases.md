# Use Case Bibliotek — Auto Research Templates

Færdige skabeloner tilpasset din kontekst. Kopiér og tilpas.

---

## Use Case 1: Survey Rapport-optimering

**Hvad optimeres:** System prompt der genererer Word-rapporter fra survey-data  
**Feedback-loop:** ~2 minutter  
**Kræver:** Python-miljø

### `program.md`
```markdown
# Survey Intelligence — Auto Research

## Formål
Optimér system prompt der genererer Bird's Eye View-rapporter fra survey-data
(15 spørgsmål, 50+ respondenter). Mål: maksimal dækning, konsistent tone, 
ingen hallucinationer.

## Eval Suite (score X/5)
1. Dækker rapporten ALLE 15 spørgsmål eksplicit? (Ja/Nej)
2. Indeholder rapporten en Bird's Eye View-sektion med overordnet tendens? (Ja/Nej)
3. Er alle konklusioner understøttet af direkte citater fra svar? (Ja/Nej)
4. Er sprogtonen professionel og konsistent (ikke "AI-agtig")? (Ja/Nej)
5. Er rapporten fri for information der ikke fremgår af survey-data? (Ja/Nej)

## Loop
1. Generér rapport med nuværende baseline-prompt + testdata
2. Evaluer mod 5 spørgsmål (score /5)
3. KEEP hvis score ≥ baseline-score
4. Log læring i resource.md

## Hvad må ændres
- System prompt indhold og struktur
- Instruktioner om format og tone
- Eksempler i few-shot prompt

## Hvad må IKKE ændres
- Testdata (brug altid samme survey-eksempel)
- Eval-spørgsmålene
- Output-format (Word via python-docx)
```

---

## Use Case 2: Daglig Intelligence Briefing (e-commerce brand)

**Hvad optimeres:** Prompt der genererer daglige HTML intelligence briefings  
**Feedback-loop:** ~1 minut  
**Kræver:** Claude API-adgang

### `evals.md`
```markdown
## Briefing Eval Suite (score X/6)

1. Indeholder briefingen en "Top Story" sektion? (Ja/Nej)
2. Er alle kilder citeret med navn og dato? (Ja/Nej)
3. Er briefingen under 800 ord? (Ja/Nej)
4. Er brand-tonen konsistent med brandets identitet? (Ja/Nej)
5. Indeholder briefingen mindst 3 kategorier (marked, trend, konkurrent)? (Ja/Nej)
6. Er briefingen fri for generiske AI-fraser ("it's worth noting", "importantly")? (Ja/Nej)
```

---

## Use Case 3: Skill-optimering (Prompt/Skill forbedring)

**Hvad optimeres:** En eksisterende `.skill`-fil (SKILL.md)  
**Feedback-loop:** ~3 minutter (generér output → evaluer)  
**Kræver:** Claude API + testcases

### Generisk `program.md` til skill-optimering
```markdown
# [Skill navn] — Auto Research Optimering

## Formål
Forbedre [SKILL NAME] skill så den producerer [ØNSKET OUTPUT] 
mere konsistent og præcist.

## Testcases
Brug altid disse 3 testprompts (må aldrig ændres):
1. "[Testprompt 1 — typisk use case]"
2. "[Testprompt 2 — edge case]"  
3. "[Testprompt 3 — kompleks case]"

## Eval Suite (score X/4)
1. Producerer outputtet den forventede struktur? (Ja/Nej)
2. Er outputtet på det rette sprog og tone? (Ja/Nej)
3. Dækker outputtet alle nødvendige elementer? (Ja/Nej)
4. Er outputtet fri for generiske svar uden specifikt indhold? (Ja/Nej)

## Loop
1. Kør skill på alle 3 testcases
2. Evaluer hvert output mod eval-suite
3. Beregn samlet score (maks 12)
4. KEEP hvis score > baseline-score

## Hvad må ændres
- SKILL.md indhold og instruktioner
- Eksempler og templates i skillen
- Struktur og rækkefølge af instruktioner

## Hvad må IKKE ændres
- Testcases
- Eval-spørgsmål
- Skill-navn og frontmatter (name/description)
```

---

## Use Case 4: Newsletter Emnelinjer (n8n integration)

**Hvad optimeres:** Prompt der genererer nyhedsbrev-emnelinjer  
**Feedback-loop:** Dage (åbningsrate via email-platform)  
**Kræver:** n8n + email platform API

> ⚠️ Langt feedback-loop — anbefal proxy-metrik i stedet:
> "Score emnelinjen på 4 binære kriterier" som proxy for åbningsrate.

### Proxy eval-suite (til hurtig iteration)
```markdown
## Newsletter Emnelinje Eval (score X/4)

1. Er emnelinjen under 50 tegn? (Ja/Nej)
2. Starter emnelinjen med et handlingsord eller tal? (Ja/Nej)
3. Indeholder emnelinjen et specifikt keyword fra artiklen? (Ja/Nej)
4. Er emnelinjen fri for spam-trigger ord ("gratis", "vind", "klik nu")? (Ja/Nej)
```

---

## Use Case 5: Generisk Tekst-output Optimering

Brug denne når ingen af ovenstående passer.

### Minimal `program.md` skabelon
```markdown
# [Projektnavn] — Auto Research

## Kontekst
[Beskriv hvad du optimerer på 2-3 linjer]

## Baseline
Se `baseline.md`

## Eval Suite
[Indsæt 3-6 binære Ja/Nej spørgsmål]

## Loop
1. Generér Challenger (én ændring ad gangen)
2. Evaluer: score /[maks]
3. KEEP hvis score ≥ baseline / DISCARD hvis score < baseline
4. Log i resource.md: hvad, score, status, læring
5. Gentag

## Ændringsrum
[Hvad må AI'en ændre]

## Fastlåst
[Hvad må IKKE ændres — testdata, eval-metode, output-format krav]
```

---

## resource.md startskabelon

Kopiér dette til ny `resource.md` ved projektstart:

```markdown
# Resource — [Projektnavn]

## Core Insights
*(Udfyldes automatisk efter konsolidering)*

## Eksperiment Log

| # | Score | Status | Beskrivelse | Læring |
|---|-------|--------|-------------|--------|
| 1 | -/- | BASELINE | Startpunkt | - |

## Mønstre der virker
*(Udfyldes løbende)*

## Mønstre der ikke virker
*(Udfyldes løbende)*
```
