import os
import re
import csv
import nltk
from typing import List, Tuple, Optional
from nltk.tokenize import sent_tokenize
from PyPDF2 import PdfReader

# Download NLTK punkt tokenizer if not already available
nltk.download("punkt")

# === Config ===
INPUT_PDF = "data/Comfort Systems.pdf"  # Change path to your target PDF
OUTPUT_CSV = "output/risk_sentences.csv"

# === Patterns and keywords ===
RISK_KEYWORDS = [
    "concentration", "depend", "rely", "reliance", "material", "significant",
    "top customer", "largest customer", "major customer", "important supplier",
    "exposure", "accounted for", "substantial", "limited", "few customers", "critical"
]
CUSTOMER_SUPPLIER_WORDS = ["customer", "customers", "client", "clients", "supplier", "suppliers", "vendor", "vendors"]
PERCENT_REGEX = re.compile(r"\b\d{1,3}(\.\d+)?\s?%")

# === Functions ===
def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    all_text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            all_text += content + " "
    return re.sub(r"\s+", " ", all_text.strip())

def extract_risk_sentences(text: str) -> List[Tuple[str, str, str, bool]]:
    results = []
    sentences = sent_tokenize(text)

    for sent in sentences:
        s = sent.lower()

        if any(kw in s for kw in CUSTOMER_SUPPLIER_WORDS) and any(rk in s for rk in RISK_KEYWORDS):
            sent_type = "customer" if "customer" in s or "client" in s else "supplier"
            percent_match = PERCENT_REGEX.search(sent)
            percent_value = percent_match.group() if percent_match else ""

            is_high = (
                "top" in s
                or "largest" in s
                or "significant" in s
                or "material" in s
                or "substantial" in s
                or (percent_value and float(percent_value.replace("%", "")) >= 10)
            )

            results.append((sent.strip(), sent_type, percent_value, is_high))

    return results

def save_to_csv(rows: List[Tuple[str, str, str, bool]], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sentence", "type", "percent", "is_high_risk"])
        writer.writerows(rows)

# === Main ===
def main():
    print("🔍 Reading PDF and extracting text...")
    text = extract_text_from_pdf(INPUT_PDF)

    print("📊 Processing sentences for risk...")
    extracted = extract_risk_sentences(text)

    print(f"✅ Found {len(extracted)} potential risk disclosures.")
    save_to_csv(extracted, OUTPUT_CSV)
    print(f"📁 Output saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

