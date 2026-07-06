# n8n Integration — Auto Research Loop

Kør autoresearch-loopet automatisk via n8n på tidsplan.

---

## Arkitektur

```
Cron trigger (hvert X min/timer)
    ↓
HTTP Request: Læs baseline.md + resource.md fra disk/GitHub
    ↓
Claude API: Generér Challenger baseret på resource.md
    ↓
Claude API: Evaluer Challenger mod eval-suite (returnér score som JSON)
    ↓
IF score > baseline_score:
    → Overskriv baseline.md med Challenger
    → Tilføj KEEP-entry til resource.md
    → Send Slack notifikation
ELSE:
    → Tilføj DISCARD-entry til resource.md
    ↓
Vent til næste trigger
```

---

## n8n Workflow (JSON-import)

Importér dette i din n8n-instans:

```json
{
  "name": "Auto Research Loop",
  "nodes": [
    {
      "name": "Cron",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 1 }]
        }
      }
    },
    {
      "name": "Læs Baseline",
      "type": "n8n-nodes-base.readBinaryFile",
      "parameters": {
        "filePath": "/data/baseline.md"
      }
    },
    {
      "name": "Læs Resource",
      "type": "n8n-nodes-base.readBinaryFile",
      "parameters": {
        "filePath": "/data/resource.md"
      }
    },
    {
      "name": "Generér Challenger",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.anthropic.com/v1/messages",
        "method": "POST",
        "headers": {
          "x-api-key": "{{ $env.ANTHROPIC_API_KEY }}",
          "anthropic-version": "2023-06-01",
          "content-type": "application/json"
        },
        "body": {
          "model": "claude-sonnet-4-20250514",
          "max_tokens": 2000,
          "messages": [{
            "role": "user",
            "content": "Du er en autonomt optimerende agent.\n\nNuværende baseline:\n{{ $node['Læs Baseline'].json.data }}\n\nTidligere læringer:\n{{ $node['Læs Resource'].json.data }}\n\nGenerér ÉN forbedret Challenger-version af baseline. Foreslå kun én ændring ad gangen. Returner JSON: {\"challenger\": \"[NY VERSION]\", \"hypothesis\": \"[HVAD DU TESTER]\", \"expected_improvement\": \"[HVORFOR DET VIRKER]\"}\n\nReturnér KUN JSON, ingen andre tekst."
          }]
        }
      }
    },
    {
      "name": "Evaluér Challenger",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.anthropic.com/v1/messages",
        "method": "POST",
        "headers": {
          "x-api-key": "{{ $env.ANTHROPIC_API_KEY }}",
          "anthropic-version": "2023-06-01",
          "content-type": "application/json"
        },
        "body": {
          "model": "claude-sonnet-4-20250514",
          "max_tokens": 500,
          "messages": [{
            "role": "user",
            "content": "Evaluer dette output mod eval-suite.\n\nOutput at evaluere:\n{{ JSON.parse($node['Generér Challenger'].json.content[0].text).challenger }}\n\n[INDSÆT DINE BINÆRE EVAL-SPØRGSMÅL HER]\n\nReturnér JSON: {\"scores\": [true/false per eval], \"total\": X, \"max\": Y}\n\nReturnér KUN JSON."
          }]
        }
      }
    },
    {
      "name": "Sammenlign Scores",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [{
            "value1": "={{ JSON.parse($node['Evaluér Challenger'].json.content[0].text).total }}",
            "operation": "larger",
            "value2": "={{ $node['Baseline Score'].json.score }}"
          }]
        }
      }
    },
    {
      "name": "Slack Notifikation (KEEP)",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#autoresearch",
        "text": "✅ *KEEP* — Ny baseline!\nScore: {{ JSON.parse($node['Evaluér Challenger'].json.content[0].text).total }}/{{ JSON.parse($node['Evaluér Challenger'].json.content[0].text).max }}\nHypotese: {{ JSON.parse($node['Generér Challenger'].json.content[0].text).hypothesis }}"
      }
    }
  ]
}
```

---

## Konfiguration

### Miljøvariabler i n8n
```
ANTHROPIC_API_KEY = din-api-nøgle
SLACK_WEBHOOK_URL = din-webhook-url (optional)
BASELINE_PATH = /data/baseline.md
RESOURCE_PATH = /data/resource.md
RESULTS_PATH = /data/results.tsv
```

### Tilpas eval-spørgsmål
Find denne linje i "Evaluér Challenger"-noden og erstat placeholder:
```
[INDSÆT DINE BINÆRE EVAL-SPØRGSMÅL HER]
```

Med dine faktiske spørgsmål, f.eks.:
```
Eval 1: Indeholder outputtet alle 15 spørgsmål? (svar true/false)
Eval 2: Er rapporten under 800 ord? (svar true/false)
Eval 3: Er alle konklusioner understøttet af citater? (svar true/false)
```

### Kørselshyppighed
Justér Cron-noden til ønsket interval:
- Hvert 5. minut: `"minutesInterval": 5`
- Hver time: `"hoursInterval": 1`
- Dagligt kl. 07:00: brug cron expression `0 7 * * *`

---

## Tips

**Gem baseline-score persistent**
Tilføj en "Læs Baseline Score" node der henter sidste kendte score fra `results.tsv` — så n8n-workflow'et husker scoren på tværs af kørsler.

**API-rate limiting**
Tilføj en "Wait"-node på 5-10 sekunder mellem Challenger-generering og evaluering for at undgå rate limit-fejl.

**Fejlhåndtering**
Tilføj en "Error Trigger" node der sender Slack-notifikation hvis workflow fejler — så du kan debugge uden at tjekke manuelt.
