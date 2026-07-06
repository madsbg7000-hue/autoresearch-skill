# Eval Matrix Quickstart — Sådan forbedrer du en skill

## 1-minutters oversigt

Du har nu et system der lader Claude forbedre dine skills autonomt — præcis som Karpathys autoresearch forbedrer LLM-modeller. Forskellen er at i stedet for `val_bpb` bruger vi en `eval_matrix.json` med kategoriserede, vægtede checks.

---

## Hurtigste vej: Forbedre en eksisterende skill

Kopiér og paste dette til Claude:

```
Jeg vil forbedre min [din-skill] skill
med eval matrix systemet.

1. Læs eval_matrix.json og testcases.json fra evals/ mappen
2. Kør min nuværende skill på alle testcases (baseline)
3. Grade baseline med eval_matrix
4. Kør autoresearch-loopet: 5 iterationer, ÉN ændring per runde
5. Vis results.tsv og resource.md til sidst
```

---

## Opret eval matrix for en NY skill

```
Opret en eval_matrix.json for min [skill-navn] skill.

Skillen gør: [beskriv hvad skillen producerer]
Godt output er: [beskriv hvad der kendetegner et godt resultat]
Typisk input: [giv et eksempel på hvad brugeren skriver]

Brug 3-4 kategorier. Prioritér programmatic grading.
Opret også 3 testcases (standard, hard, edge).
```

---

## Filplacering

Evalfiler placeres som undermappe i skillen:

```
din-skill/
├── SKILL.md
├── references/
└── evals/
    ├── eval_matrix.json     ← Opret denne
    ├── testcases.json       ← Og denne
    ├── program.md           ← Valgfri: custom loop-instruktioner
    ├── resource.md          ← Oprettes automatisk af loopet
    └── results.tsv          ← Oprettes automatisk af loopet
```

---

## Sådan læser du results.tsv

```
run_id  commit   total_score  max_score  category_scores              status   description
001     a1b2c3d  4.2          7.0        K:2.8/4.0|Q:1.4/3.0         baseline Udgangspunkt
002     b2c3d4e  5.1          7.0        K:3.2/4.0|Q:1.9/3.0         keep     Tilføjet eksplicitte regler
003     c3d4e5f  4.0          7.0        K:2.5/4.0|Q:1.5/3.0         discard  Fjernet tone-matching
```

- **total_score stiger** = skillen bliver bedre
- **keep** = ændring beholdt (baseline opdateret)
- **discard** = ændring kasseret (ingen effekt)
- **category_scores** = viser hvor forbedringen skete

---

## De 4 færdige eval matrices

| Skill | Fil | Klar? |
|---|---|---|
| humanizer (eksempel) | `example-skill-eval/` | ✓ eval_matrix + testcases |
