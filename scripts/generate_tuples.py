import random
import sys
from pathlib import Path

# Add project root to sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import litellm
from dotenv import load_dotenv
import os

load_dotenv(override=False)

MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")

CUISINE_TYPES = [
    "Italian", "Chinese", "Indian", "Japanese",
    #"Thai", "French", "Mediterranean", "American", "Korean"
]

MEAL_TYPES = [
    "breakfast", "lunch", "dinner"#, "snack", "dessert", "brunch"
]

DIETARY_REQUIREMENTS = [
    "vegetarian", "vegan", "gluten-free", 
    #"dairy-free", "keto", "paleo", "nut-free", "low-sodium", None
]


def generate_random_tuple() -> tuple[str, str, str]:
    """Generate a random (cuisine_type, meal_type, dietary_requirement) tuple."""
    cuisine = random.choice(CUISINE_TYPES)
    meal = random.choice(MEAL_TYPES)
    dietary = random.choice(DIETARY_REQUIREMENTS)
    return (cuisine, meal, dietary)


def generate_tuples(n: int):
    """Generate n random tuples."""
    return [generate_random_tuple() for _ in range(n)]


def generate_query_from_tuple(cuisine: str, meal: str, dietary: str | None) -> str:
    """Use LLM to generate a synthetic user query from the tuple parameters."""
    dietary_text = f"with a {dietary} dietary requirement" if dietary else "with no specific dietary restrictions"

    prompt = f"""Generate a natural user query that someone might ask a recipe chatbot.
The query should be about {cuisine} cuisine, for {meal}, {dietary_text}.

Return ONLY the query text, nothing else. Make it sound natural and varied.
Examples of good queries:
- "What's a quick Italian dinner I can make tonight?"
- "I need a vegan breakfast idea"
- "Can you suggest a gluten-free Mexican lunch?"

Generate one query:"""

    response = litellm.completion(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["choices"][0]["message"]["content"].strip()


def generate_synthetic_queries(n: int):
    """Generate n synthetic queries from random tuples."""
    tuples = generate_tuples(n)
    results = []
    for cuisine, meal, dietary in tuples:
        query = generate_query_from_tuple(cuisine, meal, dietary)
        results.append({
            "cuisine": cuisine,
            "meal": meal,
            "dietary": dietary,
            "query": query
        })
    return results


if __name__ == "__main__":
    import argparse
    import csv

    parser = argparse.ArgumentParser(
        description="Generate random tuples for synthetic query generation"
    )
    parser.add_argument(
        "-n", "--count", type=int, default=10,
        help="Number of tuples to generate (default: 10)"
    )
    parser.add_argument(
        "--generate", action="store_true",
        help="Generate synthetic queries using LLM (otherwise just print tuples)"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Output CSV path (e.g. data/hw2_queries.csv)"
    )
    args = parser.parse_args()

    if args.generate:
        results = generate_synthetic_queries(args.count)
        for r in results:
            print(f"[{r['cuisine']}, {r['meal']}, {r['dietary']}]")
            print(f"  -> {r['query']}")
            print()

        if args.output:
            output_path = PROJECT_ROOT / args.output
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "query"])
                for i, r in enumerate(results, start=1):
                    writer.writerow([i, r["query"]])
            print(f"Saved {len(results)} queries to {output_path}")
    else:
        tuples = generate_tuples(args.count)
        for t in tuples:
            print(t)
