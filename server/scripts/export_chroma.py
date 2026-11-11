"""Export the local Chroma collection for a controlled migration."""

import json
import sys
from pathlib import Path

from server.adapters.chromadb_adapter import ChromaDBAdapter
from server.app.configurations import Settings


def main() -> None:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "chroma-export.json")
    settings = Settings()
    collection = ChromaDBAdapter(
        number_of_vectorial_results=settings.NUMBER_OF_VECTORIAL_RESULTS,
        path=settings.CHROMA_PATH,
        chunk_size_tokens=settings.CHUNK_SIZE_TOKENS,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(collection.get_vectors(), default=str), encoding="utf-8")
    print(f"Exported Chroma collection to {output}")


if __name__ == "__main__":
    main()
