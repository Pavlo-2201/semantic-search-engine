#!/usr/bin/env python3
"""Поиск по корпусу из командной строки.

Примеры:
    python scripts/search.py --retriever bm25 "как получить длину массива"
    python scripts/search.py --retriever tfidf --top-k 5 --json "css анимация элемента"
    python scripts/search.py --retriever dense --model lsa-300 "как получить длину массива"
    python scripts/search.py --retriever faiss --index data/indexes/lsa-300-flat "длина массива"
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import load_corpus  # noqa: E402
from semsearch.pipeline import build_retriever  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="текст запроса")
    parser.add_argument("--corpus", default="data/corpus/mdn-ru.jsonl")
    parser.add_argument("--retriever", default="bm25", choices=["bm25", "tfidf", "dense", "faiss"])
    parser.add_argument("--model", help="имя модели из configs/models.yaml (для dense)")
    parser.add_argument("--models-config", default="configs/models.yaml")
    parser.add_argument("--index", help="каталог сохранённого индекса FAISS (для faiss)")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="вывести результат в JSON")
    args = parser.parse_args()

    query = " ".join(args.query)
    documents = load_corpus(args.corpus)
    started = time.perf_counter()
    retriever = build_retriever(
        args.retriever,
        documents,
        model=args.model,
        models_config=args.models_config,
        index_dir=args.index,
        progress=not args.json,
    )
    build_seconds = time.perf_counter() - started

    started = time.perf_counter()
    hits = retriever.search(query, top_k=args.top_k)
    search_seconds = time.perf_counter() - started

    if args.json:
        print(
            json.dumps(
                {
                    "query": query,
                    "retriever": retriever.name,
                    "index_dir": args.index,
                    "corpus_size": len(documents),
                    "build_seconds": round(build_seconds, 3),
                    "search_seconds": round(search_seconds, 4),
                    "hits": [hit.to_dict() for hit in hits],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f'запрос: "{query}"  поиск: {retriever.name}  документов: {len(documents)}')
    prepared = "индекс загружен" if args.retriever == "faiss" else "индекс построен"
    print(f"{prepared} за {build_seconds:.2f} c, поиск {search_seconds * 1000:.1f} мс\n")
    for hit in hits:
        print(f"{hit.rank:2d}. [{hit.score:.4f}] {hit.title}")
        print(f"    {hit.url}")
        print(f"    {hit.snippet}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
