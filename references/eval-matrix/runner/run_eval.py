#!/usr/bin/env python3
"""
Eval Matrix Runner — Kører eval_matrix.json mod testcase-output.

Usage:
    python run_eval.py --skill-dir <path> --output-dir <path> [--run-id <id>]

Læser eval_matrix.json + testcases.json fra skill-dir/evals/
Scorer output-filer fra output-dir/
Skriver grading til skill-dir/evals/grading/run_<id>.json
Opdaterer results.tsv
"""

import json
import os
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path


def load_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Programmatic Graders
# ---------------------------------------------------------------------------

AI_TELLS_EN = [
    r'\bserves as\b', r'\bstands as\b', r'\bmarks\b',
    r'\bpivotal\b', r'\bcrucial\b', r'\bvital\b',
    r'\bshowcasing\b', r'\bhighlighting\b', r'\bunderscoring\b',
    r'\btapestry\b', r'\blandscape\b', r'\btestament\b', r'\binterplay\b',
    r'\bAdditionally\b', r'\bFurthermore\b',
    r'\bfostering\b', r'\benhancing\b', r'\bensuring alignment\b',
    r'\bexciting times\b', r'\bbright future\b',
    r'\bthrilled\b', r'\bexcited to share\b',
    r'\bgame.changer\b', r'\bcutting.edge\b', r'\bleverage\b',
    r'\bpassionate\b', r'\bjourney\b', r'\brevolutionize\b',
]

AI_TELLS_DA = [
    r'\bi det store hele\b', r'\bdet er værd at bemærke\b',
    r'\bbanebrydende\b', r'\bspændende tider\b',
    r'\bi bund og grund\b', r'\bafgørende\b', r'\bholistisk\b',
    r'\bsømløs\b', r'\bmuliggør\b', r'\bfundamentalt\b',
]

ALL_AI_TELLS = AI_TELLS_EN + AI_TELLS_DA


def count_ai_tells(text: str) -> list[str]:
    """Return list of AI tells found in text."""
    found = []
    for pattern in ALL_AI_TELLS:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(pattern)
    return found


def count_words(text: str) -> int:
    return len(text.split())


def count_chars(text: str) -> int:
    return len(text)


def has_question_mark_at_end(text: str) -> bool:
    """Check if last 200 chars contain a question mark."""
    return '?' in text[-200:]


def count_questions(text: str) -> int:
    """Count question marks in text."""
    return text.count('?')


def has_section(text: str, keywords: list[str]) -> bool:
    """Check if text contains a section with any of the given keywords."""
    for kw in keywords:
        if re.search(rf'(?i)(#{1,3}\s*.*{kw}|{kw}\s*:|\*\*{kw}\*\*)', text):
            return True
    return False


# ---------------------------------------------------------------------------
# Grade a single eval against output
# ---------------------------------------------------------------------------

def grade_programmatic(eval_item: dict, output_text: str, testcase: dict) -> dict:
    """Grade an eval programmatically. Returns grading result."""
    eval_id = eval_item['id']
    hint = eval_item.get('grading_hint', '')

    # Route to appropriate grader based on hint keywords
    if 'ai-tell' in hint.lower() or 'tell-kategori' in hint.lower() or 'scan' in hint.lower():
        found = count_ai_tells(output_text)
        if 'fri for' in eval_item['question'].lower() or 'free' in eval_item['question'].lower():
            passed = len(found) == 0
            evidence = f"Fundet {len(found)} AI-tells: {found[:5]}" if found else "Ingen AI-tells fundet"
        else:
            # "Identificerer mindst 3 AI-tells"
            passed = len(found) >= 3
            evidence = f"Fundet {len(found)} AI-tells i analyse"
        return {"eval_id": eval_id, "passed": passed, "evidence": evidence}

    elif 'ordtælling' in hint.lower() or 'word' in hint.lower():
        wc = count_words(output_text)
        limit = 800  # default
        match = re.search(r'(\d+)', hint)
        if match:
            limit = int(match.group(1))
        passed = wc <= limit
        return {"eval_id": eval_id, "passed": passed, "evidence": f"Ordtælling: {wc} (maks {limit})"}

    elif 'tegn' in hint.lower() or 'char' in hint.lower():
        cc = count_chars(output_text)
        limit = 1300
        match = re.search(r'(\d+)', hint)
        if match:
            limit = int(match.group(1))
        passed = cc <= limit
        return {"eval_id": eval_id, "passed": passed, "evidence": f"Tegnantal: {cc} (maks {limit})"}

    elif 'spørgsmål' in hint.lower() or 'question' in hint.lower():
        if 'slutte' in hint.lower() or 'last' in hint.lower():
            passed = has_question_mark_at_end(output_text)
            return {"eval_id": eval_id, "passed": passed, "evidence": "Spørgsmål i afslutning: " + str(passed)}
        else:
            qc = count_questions(output_text)
            passed = qc >= 2
            return {"eval_id": eval_id, "passed": passed, "evidence": f"Antal spørgsmål: {qc}"}

    elif 'sektion' in hint.lower() or 'section' in hint.lower() or 'header' in hint.lower():
        # Generic section check
        passed = has_section(output_text, ['audit', 'gennemgang', 'draft', 'final'])
        return {"eval_id": eval_id, "passed": passed, "evidence": "Sektioner fundet: " + str(passed)}

    elif 'emoji' in hint.lower() or 'hashtag' in hint.lower():
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', output_text))
        hashtag_count = len(re.findall(r'#\w+', output_text))
        passed = emoji_count <= 3 and hashtag_count <= 3
        return {"eval_id": eval_id, "passed": passed, "evidence": f"Emojis: {emoji_count}, Hashtags: {hashtag_count}"}

    elif 'risiko' in hint.lower() or 'risk' in hint.lower():
        risk_patterns = [r'(?i)risik', r'(?i)risk', r'(?i)mitig', r'(?i)udfordr']
        risk_count = sum(1 for p in risk_patterns if re.search(p, output_text))
        passed = risk_count >= 2
        return {"eval_id": eval_id, "passed": passed, "evidence": f"Risiko-relaterede mønstre: {risk_count}"}

    elif 'sidelængde' in hint.lower() or 'page' in hint.lower():
        wc = count_words(output_text)
        pages = wc / 350
        limit = 1.0
        match = re.search(r'(\d+)', hint)
        if match:
            limit = float(match.group(1))
        passed = pages <= limit
        return {"eval_id": eval_id, "passed": passed, "evidence": f"Estimeret sider: {pages:.1f} (maks {limit})"}

    elif 'referencer' in hint.lower() or 'scan for' in hint.lower():
        # Generic keyword scan
        keywords_str = hint.lower()
        keywords = re.findall(r'[\w-]+', keywords_str)
        found = [kw for kw in keywords if kw in output_text.lower()]
        passed = len(found) >= 2
        return {"eval_id": eval_id, "passed": passed, "evidence": f"Fundne nøgleord: {found[:5]}"}

    # Fallback: mark as needs_llm_judge
    return {"eval_id": eval_id, "passed": None, "evidence": "Kræver LLM-judge — kan ikke grades programmatisk"}


# ---------------------------------------------------------------------------
# Main evaluation pipeline
# ---------------------------------------------------------------------------

def evaluate_run(skill_dir: str, output_dir: str, run_id: str = None):
    """Run full evaluation of outputs against eval matrix."""
    evals_dir = os.path.join(skill_dir, 'evals')
    matrix_path = os.path.join(evals_dir, 'eval_matrix.json')
    testcases_path = os.path.join(evals_dir, 'testcases.json')

    if not os.path.exists(matrix_path):
        print(f"ERROR: eval_matrix.json not found at {matrix_path}")
        sys.exit(1)

    matrix = load_json(matrix_path)
    testcases = load_json(testcases_path) if os.path.exists(testcases_path) else {"testcases": []}

    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "run_id": run_id,
        "skill_name": matrix["skill_name"],
        "timestamp": datetime.now().isoformat(),
        "testcase_results": [],
        "category_scores": {},
        "total_score": 0.0,
        "max_score": 0.0,
    }

    # Collect all gradings across testcases
    all_gradings_by_category = {}

    for tc in testcases.get("testcases", []):
        tc_id = tc["id"]
        output_file = os.path.join(output_dir, f"{tc_id}.txt")

        if not os.path.exists(output_file):
            print(f"WARNING: No output for {tc_id} at {output_file}")
            continue

        with open(output_file, 'r', encoding='utf-8') as f:
            output_text = f.read()

        tc_result = {
            "testcase_id": tc_id,
            "testcase_name": tc["name"],
            "gradings": []
        }

        for category in matrix["categories"]:
            cat_name = category["name"]
            if cat_name not in all_gradings_by_category:
                all_gradings_by_category[cat_name] = {"weight": category["weight"], "passed": 0, "total": 0}

            for eval_item in category["evals"]:
                if eval_item["grading"] == "programmatic":
                    grading = grade_programmatic(eval_item, output_text, tc)
                else:
                    # LLM judge — mark as needing manual/llm grading
                    grading = {
                        "eval_id": eval_item["id"],
                        "passed": None,
                        "evidence": "NEEDS_LLM_JUDGE: " + eval_item["question"]
                    }

                tc_result["gradings"].append(grading)

                if grading["passed"] is not None:
                    all_gradings_by_category[cat_name]["total"] += 1
                    if grading["passed"]:
                        all_gradings_by_category[cat_name]["passed"] += 1

        results["testcase_results"].append(tc_result)

    # Calculate scores
    total = 0.0
    max_total = 0.0
    for cat_name, data in all_gradings_by_category.items():
        if data["total"] > 0:
            ratio = data["passed"] / data["total"]
            cat_score = data["weight"] * ratio
            total += cat_score
        max_total += data["weight"]
        results["category_scores"][cat_name] = {
            "passed": data["passed"],
            "total": data["total"],
            "weight": data["weight"],
            "score": data["weight"] * (data["passed"] / data["total"]) if data["total"] > 0 else 0
        }

    results["total_score"] = round(total, 3)
    results["max_score"] = round(max_total, 3)

    # Save grading result
    grading_dir = os.path.join(evals_dir, 'grading')
    grading_path = os.path.join(grading_dir, f'run_{run_id}.json')
    save_json(grading_path, results)
    print(f"Grading saved to {grading_path}")
    print(f"Score: {results['total_score']}/{results['max_score']}")

    for cat_name, data in results["category_scores"].items():
        print(f"  {cat_name}: {data['passed']}/{data['total']} (score: {data['score']:.2f}/{data['weight']:.1f})")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eval matrix against skill outputs")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory (containing evals/)")
    parser.add_argument("--output-dir", required=True, help="Path to directory with output files (TC1.txt, TC2.txt, etc.)")
    parser.add_argument("--run-id", default=None, help="Run identifier (defaults to timestamp)")
    args = parser.parse_args()

    evaluate_run(args.skill_dir, args.output_dir, args.run_id)
