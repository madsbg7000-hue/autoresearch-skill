# Autoresearch — CHANGELOG

## v1.4.1-community (2026-07-06)
- Ny introduktionssektion "Hvad er autoresearch?" i SKILL.md: forklarer princippet, hvad der kan optimeres, hvad det kræver, og hvorfor generator/grader/loop er adskilt.
- Alle eksempler gjort domæneneutrale: fiktivt e-commerce/kundeservice-eksempel i context_profile-skabelonen og neutrale humanizer-testtekster i example-skill-eval.

## v1.4.0-community (2026-07-04)
- Offentlig delbar version. Personspecifikke eksempler og private eval-matrices erstattet med generiske/fiktive eksempler. Funktionelt identisk med v1.4.0.

## v1.4.0 — Konsolidering (2026-06-18)

Merge af to divergerede grene til én ren version. Før v1.4.0 fandtes to uforenelige spor: v1.3.0 (live) havde verifikationspasset men havde tabt FASE 0 Context Interrogation og pegede på brækkede reference-stier (`eval-matrix-framework/`), mens v1.1.1 havde FASE 0 men intet verifikationspas.

**Tilføjet/bevaret:**
- VERIFIKATIONSPAS som dedikeret sektion (fra v1.3.0) — 5-punkts gate før enhver KEEP, med self-eval-bias-advarsel.
- FASE 0 Context Interrogation (fra v1.1.1) — 3-lags spørgsmål, pre-fill workflow, 5 skill-arketyper, context_profile.json som fastlåst input.
- Den fjerde ufravigelige regel: context_profile ændres aldrig under et loop.
- Ny sektion "Indsigter fra rigtige kørsler" — 5 destillerede læringer fra deep-research-optimeringen (8 iterationer + 2 uafhængige re-evals).
- Verifikationspas indskrevet som trin 8 i loopet.

**Rettet:**
- Reference-stier korrigeret fra `references/eval-matrix-framework/` → `references/eval-matrix/` (matcher faktisk mappestruktur).
- Fejlfindingstabel udvidet med "Score når 16/16 men virker for højt → self-eval bias".

## v1.3.0 — Verifikationspas (2026-06-09)
- Tilføjet VERIFIKATIONSPAS efter sessions-audit. Adresserede den mest gentagne fejl: "score forbedret" uden faktisk verifikation.

## v1.1.1 — Spørgeteknik (2026-04)
- Optimeret Context Interrogation med eksempler, pre-fill workflow, 5 skill-arketyper og downstream-mapping fra context_profile til eval-generering.

## v1.1.0 — Context Interrogation (2026-04)
- Ny obligatorisk FASE 0 inden eval-generering. context_profile.json som READ-ONLY input der styrer hvordan eval_matrix og testcases genereres.

## v1.0 — Baseline
- To niveauer: Simpelt Ja/Nej-loop + Eval Matrix (Karpathy-mønster). Separation of concerns, git som hukommelse, eval-eskalering L1-L4.
