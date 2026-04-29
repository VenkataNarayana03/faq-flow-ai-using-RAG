import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT_DIR / "data" / "raw" / "faqs.jsonl"
PROCESSED_PATH = ROOT_DIR / "data" / "processed" / "faqs.jsonl"

def clean(value):
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)
    elif isinstance(value, dict):
        value = " ".join(str(item) for item in value.values())
    return " ".join((value or "").split())


def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Run scripts/load_data.py first. Missing: {RAW_PATH}")

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with RAW_PATH.open("r", encoding="utf-8") as source, PROCESSED_PATH.open("w", encoding="utf-8") as target:
        for line in source:
            item = json.loads(line)
            question = clean(item.get("question"))
            answer = clean(item.get("answer"))
            context = clean(item.get("context"))
            if not question or not answer:
                continue

            text = clean(f"Question: {question}\nAnswer: {answer}\nContext: {context}")

            row = {
                "id": f"faq-{count}",
                "source": item.get("source", "unknown"),
                "question": question,
                "answer": answer,
                "text": text,
            }
            target.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1

    print(f"Processed {count} records to {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
