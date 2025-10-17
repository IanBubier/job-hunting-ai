"""
Pre-download the sentence-transformers model to avoid runtime download delays.
Run this script once after installing dependencies:
    python backend/download_model.py

The model will be cached in ~/.cache/torch/sentence_transformers/
(or $SENTENCE_TRANSFORMERS_HOME if set).
"""

from sentence_transformers import SentenceTransformer
import sys

MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    print(f"Downloading model: {MODEL_NAME}")
    print("This may take a minute (downloading ~82MB)...")

    try:
        model = SentenceTransformer(MODEL_NAME)
        print("✓ Model downloaded successfully!")
        print(f"  Cached at: ~/.cache/torch/sentence_transformers/{MODEL_NAME}")
        print(f"  Embedding dimension: {model.get_sentence_embedding_dimension()}")
        return 0
    except Exception as e:
        print(f"✗ Failed to download model: {e}", file=sys.stderr)
        print("\nTroubleshooting:")
        print("  - Check your internet connection")
        print("  - Verify proxy settings if behind a corporate firewall")
        print("  - Try setting SENTENCE_TRANSFORMERS_HOME to a writable directory")
        print(
            "  - Manually download from: "
            "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
