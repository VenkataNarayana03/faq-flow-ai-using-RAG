from datasets import DownloadConfig, load_dataset
import json
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT_DIR / "data" / "raw" / "faqs.jsonl"
LOCAL_ONLY = DownloadConfig(local_files_only=True)
SQUAD_LIMIT = int(os.getenv("SQUAD_LIMIT", "1000"))


FALLBACK_FAQS = [
    {
        "question": "How can I track my order?",
        "answer": "You can track your order from the order history page using the tracking link.",
    },
    {
        "question": "How do I request a refund?",
        "answer": "Contact support with your order ID and reason for the refund request.",
    },
    {
        "question": "Can I change my shipping address?",
        "answer": "You can change the shipping address before the order is dispatched.",
    },
]


def load_faq_dataset():
    if os.getenv("USE_HF_DATASETS", "").lower() not in {"1", "true", "yes"}:
        print("Using built-in starter FAQ records. Set USE_HF_DATASETS=true to download Hugging Face data.")
        return {"train": FALLBACK_FAQS}

    try:
        return load_dataset(
            "MakTek/Customer_support_faqs_dataset",
            download_config=LOCAL_ONLY,
        )
    except Exception:
        try:
            return load_dataset("MakTek/Customer_support_faqs_dataset")
        except Exception as error:
            print(f"Using fallback FAQ records: {error}")
            return {"train": FALLBACK_FAQS}


def load_squad_dataset():
    try:
        return load_dataset("squad", download_config=LOCAL_ONLY)
    except Exception:
        try:
            return load_dataset("squad")
        except Exception as error:
            print(f"Skipping SQuAD dataset: {error}")
            return None


def first_answer_text(item):
    answers = item.get("answers") or {}
    answer_texts = answers.get("text") or []
    return answer_texts[0] if answer_texts else ""


def main():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with RAW_PATH.open("w", encoding="utf-8") as file:
        faq = load_faq_dataset()
        for item in faq["train"]:
            row = {
                "source": "MakTek/Customer_support_faqs_dataset",
                "question": item.get("question", ""),
                "answer": item.get("answer", ""),
                "context": "",
            }
            file.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1

        if os.getenv("INCLUDE_SQUAD", "false").lower() in {"1", "true", "yes"}:
            squad = load_squad_dataset()
            if squad:
                squad_count = 0
                for item in squad["train"]:
                    answer = first_answer_text(item)
                    if not answer:
                        continue

                    row = {
                        "source": "squad",
                        "question": item.get("question", ""),
                        "answer": answer,
                        "context": item.get("context", ""),
                    }
                    file.write(json.dumps(row, ensure_ascii=False) + "\n")
                    count += 1
                    squad_count += 1

                    if SQUAD_LIMIT and squad_count >= SQUAD_LIMIT:
                        break

                print(f"Added {squad_count} SQuAD records.")

    print(f"Saved {count} records to {RAW_PATH}")


if __name__ == "__main__":
    main()
