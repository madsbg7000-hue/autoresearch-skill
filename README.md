# Autoresearch — en selvforbedrende Claude-skill

En Claude-skill der forbedrer dine andre skills (eller prompts, emails, rapportformater) gennem autonome eksperiment-loops. Baseret på princippet fra [Andrej Karpathys autoresearch](https://github.com/karpathy/autoresearch): lås målestokken fast, ændr én ting ad gangen, mål, behold eller smid væk, gentag.

## Hvad den kan

**Niveau 1 — Simpelt Loop.** Optimér en enkelt tekst eller prompt med Ja/Nej-evals. Kør i gang på 5 minutter, kræver ingen teknisk setup. Se hurtigstart-eksemplet i `SKILL.md`.

**Niveau 2 — Eval Matrix.** Forbedr en hel skill over tid med kategoriserede evals, vægte, programmatisk grading og git som hukommelse. Karpathy-mønsteret oversat fra LLM-træning til skill-optimering.

Kerneprincipperne der gør det til mere end "bed AI om at forbedre noget":

1. Eval-funktionen ændres aldrig under et loop
2. Testdata ændres aldrig
3. Kun én fil må ændres
4. Generatoren scorer aldrig sit eget output — self-eval bias er målt og reel (en agent gav sig selv 16/16 hvor en uafhængig bedømmer gav 14/16 på samme output)

## Installation

1. Download `autoresearch.skill` fra [Releases](../../releases) (eller zip repoet selv)
2. Claude Desktop / claude.ai: Settings → Capabilities → upload skillen
3. Claude Code: pak ud i din skills-mappe

## Kom i gang

Skriv til Claude:

```
Kør autoresearch-loopet på dette:

BASELINE: "Skriv en email-emnelinje for et nyhedsbrev om AI-trends"

EVALS:
1. Er emnelinjen under 50 tegn? (Ja/Nej)
2. Starter den med et tal eller handlingsord? (Ja/Nej)
3. Nævner den et specifikt emne? (Ja/Nej)

Kør 5 iterationer. Vis results.tsv til sidst.
```

Til skill-optimering (Niveau 2): se `references/eval-matrix/QUICKSTART.md` og det komplette eksempel i `references/eval-matrix/example-skill-eval/`.

## Struktur

```
SKILL.md                        ← Selve skillen (to niveauer + FASE 0 context interrogation)
evals/                          ← Skillens egen eval-suite (ja, den evaluerer sig selv)
references/
├── use-cases.md                ← 5 færdige skabeloner
└── eval-matrix/
    ├── EVAL-MATRIX.md          ← Fuld framework-dokumentation
    ├── QUICKSTART.md           ← Hurtig opsætning
    ├── example-skill-eval/     ← Komplet eksempel (eval_matrix + testcases)
    └── runner/run_eval.py      ← Programmatisk grader
```

## Sprog

Skillen er skrevet på dansk. Konceptet virker på alle sprog — Claude følger instruktionerne uanset.

## Licens

MIT. Brug den, byg videre på den, del hvad du lærer.
