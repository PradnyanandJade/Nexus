import requests
from pathlib import Path


URL = (
    "https://storage.googleapis.com/"
    "pinecone-datasets-dev/bm25_params/"
    "msmarco_bm25_params_v4_0_0.json"
)

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "rag" / "bm25_params"
OUTPUT_FILE = OUTPUT_DIR / "msmarco_bm25_params.json"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading BM25 parameters...")

    response = requests.get(URL, timeout=120)
    response.raise_for_status()

    OUTPUT_FILE.write_bytes(response.content)

    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()