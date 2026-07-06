# GitHub Actions — Auto Research Cloud Kørsel

Kør autoresearch-loopet i skyen på tidsplan — ingen lokal server nødvendig.

---

## Hvornår bruge GitHub Actions vs n8n?

| Situation | Anbefaling |
|---|---|
| Du har allerede n8n sat op | Brug n8n (se n8n-integration.md) |
| Du vil køre på GitHub-repo | Brug GitHub Actions |
| Simpel tekst-optimering uden API-integration | GitHub Actions er nemmere |
| Du vil have versionsstyring af alle eksperimenter | GitHub Actions (alt i git) |

---

## Workflow YAML

Gem som `.github/workflows/autoresearch.yml` i dit repository:

```yaml
name: Auto Research Loop

on:
  schedule:
    # Kør hver time (justér efter behov)
    - cron: '0 * * * *'
  workflow_dispatch:
    # Tillad manuel kørsel fra GitHub UI

jobs:
  experiment:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install anthropic python-dotenv

      - name: Run experiment
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
        run: python run_experiment.py

      - name: Commit results
        run: |
          git config --local user.email "autoresearch@bot"
          git config --local user.name "Auto Research Bot"
          git add resource.md results.tsv
          git diff --staged --quiet || git commit -m "autoresearch: experiment $(date +%Y%m%d-%H%M)"
          git push
```

---

## Python Script (`run_experiment.py`)

Gem i roden af dit repository:

```python
import os
import json
import anthropic
import requests
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def log_result(experiment_id, score, max_score, status, description, learning):
    with open("results.tsv", "a", encoding="utf-8") as f:
        f.write(f"{experiment_id}\t{score}\t{max_score}\t{status}\t{description}\t{learning}\n")

def send_slack(message):
    webhook = os.environ.get("SLACK_WEBHOOK")
    if webhook:
        requests.post(webhook, json={"text": message})

def generate_challenger(baseline, resource):
    """Bed Claude om at generere én forbedret variant."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Du er en autonom optimerings-agent.

Nuværende baseline:
{baseline}

Tidligere læringer (hvad der har virket/ikke virket):
{resource}

Generér ÉN forbedret Challenger-version. Foreslå kun én ændring ad gangen.
Basér din ændring på lærings-loggen ovenfor.

Returner KUN dette JSON (ingen anden tekst):
{{
  "challenger": "[NY VERSION HER]",
  "hypothesis": "[Hvad tester du, og hvorfor forventer du forbedring]",
  "change_description": "[Kort beskrivelse af ændringen, maks 10 ord]"
}}"""
        }]
    )
    return json.loads(response.content[0].text)

def evaluate(content, evals):
    """Evaluer indhold mod eval-suite. Returnér score."""
    eval_text = "\n".join([f"{i+1}. {e}" for i, e in enumerate(evals)])
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Evaluer dette indhold mod nedenstående kriterier.
Svar kun true eller false per kriterium.

Indhold at evaluere:
{content}

Kriterier:
{eval_text}

Returner KUN dette JSON:
{{
  "scores": [true/false for hvert kriterie i rækkefølge],
  "total": [sum af true-værdier],
  "max": {len(evals)}
}}"""
        }]
    )
    return json.loads(response.content[0].text)

def update_resource(resource, experiment_id, score, max_score, status, hypothesis, learning):
    """Tilføj ny entry til resource.md."""
    entry = f"\n| {experiment_id} | {score}/{max_score} | {status} | {hypothesis} | {learning} |"
    
    # Find tabellen og tilføj rad
    if "| # |" in resource:
        resource += entry
    else:
        resource += f"\n\n## Eksperiment Log\n| # | Score | Status | Hypotese | Læring |\n|---|-------|--------|----------|--------|\n{entry}"
    
    return resource

def main():
    # ── Konfiguration ──────────────────────────────────────────────────
    # TILPAS DISSE til dit projekt:
    
    EVALS = [
        "Er outputtet struktureret korrekt med alle nødvendige sektioner? (Ja/Nej)",
        "Er sprogtonen konsistent og professionel? (Ja/Nej)",
        "Dækker outputtet alle nødvendige elementer? (Ja/Nej)",
        "Er outputtet fri for generiske AI-fraser? (Ja/Nej)",
    ]
    # ──────────────────────────────────────────────────────────────────
    
    baseline = read_file("baseline.md")
    resource = read_file("resource.md") if os.path.exists("resource.md") else ""
    
    # Hent seneste baseline-score fra results.tsv
    baseline_score = 0
    if os.path.exists("results.tsv"):
        with open("results.tsv") as f:
            lines = [l for l in f.readlines() if "\tKEEP\t" in l]
            if lines:
                last_keep = lines[-1].split("\t")
                baseline_score = int(last_keep[1].split("/")[0]) if "/" in last_keep[1] else int(last_keep[1])
    
    # Generér experiment ID
    experiment_id = datetime.now().strftime("%Y%m%d-%H%M")
    
    print(f"[{experiment_id}] Genererer Challenger...")
    challenger_data = generate_challenger(baseline, resource)
    challenger = challenger_data["challenger"]
    hypothesis = challenger_data["hypothesis"]
    change_desc = challenger_data["change_description"]
    
    print(f"[{experiment_id}] Evaluerer Challenger...")
    eval_result = evaluate(challenger, EVALS)
    score = eval_result["total"]
    max_score = eval_result["max"]
    
    print(f"[{experiment_id}] Score: {score}/{max_score} (baseline: {baseline_score})")
    
    if score > baseline_score:
        status = "KEEP"
        write_file("baseline.md", challenger)
        learning = f"Forbedring: {change_desc} øgede score fra {baseline_score} til {score}"
        send_slack(f"✅ *KEEP* [{experiment_id}]\nScore: {score}/{max_score}\n_{change_desc}_")
        print(f"[{experiment_id}] KEEP — ny baseline!")
    else:
        status = "DISCARD"
        learning = f"Ingen forbedring: {change_desc} gav score {score} (baseline {baseline_score})"
        print(f"[{experiment_id}] DISCARD")
    
    # Opdater resource.md
    resource = update_resource(resource, experiment_id, score, max_score, status, hypothesis, learning)
    write_file("resource.md", resource)
    
    # Log til results.tsv
    log_result(experiment_id, f"{score}/{max_score}", max_score, status, change_desc, learning)
    
    print(f"[{experiment_id}] Done.")

if __name__ == "__main__":
    main()
```

---

## Opsætning (trin for trin)

### 1. Opret GitHub repository
```bash
mkdir mit-autoresearch-projekt
cd mit-autoresearch-projekt
git init
```

### 2. Opret filstruktur
```bash
mkdir -p .github/workflows
touch baseline.md resource.md results.tsv
echo "experiment_id	score	max_score	status	description	learning" > results.tsv
```

### 3. Tilpas `run_experiment.py`
Erstat `EVALS`-listen med dine binære eval-spørgsmål.

### 4. Skriv din baseline
Skriv startversionen af det der skal optimeres i `baseline.md`.

### 5. Tilføj GitHub Secrets
I GitHub repo → Settings → Secrets → Actions:
- `ANTHROPIC_API_KEY` = din API-nøgle
- `SLACK_WEBHOOK` = din Slack webhook URL (optional)

### 6. Push og aktiver
```bash
git add .
git commit -m "init autoresearch"
git push origin main
```

Workflow kører automatisk efter cron-schedule, eller manuelt via GitHub Actions UI.

---

## Overvågning

GitHub Actions giver dig automatisk:
- Log over alle kørsler (succesfulde og fejlede)
- Email-notifikation ved fejl
- Historik over alle commits (resource.md + results.tsv versionsstyret)

Tjek `resource.md` i GitHub for at se den akkumulerede læring.
