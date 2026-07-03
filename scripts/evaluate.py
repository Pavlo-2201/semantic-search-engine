#!/usr/bin/env python3
"""Оценка качества поиска на наборе запросов с разметкой.

Примеры:
    python scripts/evaluate.py --retriever bm25 --queries data/queries/dev.jsonl
    python scripts/evaluate.py --retriever dense --model lsa-300 \
        --queries data/queries/dev.jsonl --output artifacts/eval
    python scripts/evaluate.py --retriever faiss --index data/indexes/lsa-300-hnsw \
        --queries data/queries/test.jsonl
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import corpus_fingerprint, load_corpus  # noqa: E402
from semsearch.evaluation import evaluate_queries, load_queries  # noqa: E402
from semsearch.pipeline import build_retriever, retriever_label  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="data/corpus/mdn-ru.jsonl")
    parser.add_argument("--queries", default="data/queries/dev.jsonl")
    parser.add_argument("--retriever", default="bm25", choices=["bm25", "tfidf", "dense", "faiss"])
    parser.add_argument("--model", help="имя модели из configs/models.yaml (для dense)")
    parser.add_argument("--models-config", default="configs/models.yaml")
    parser.add_argument("--index", help="каталог сохранённого индекса FAISS (для faiss)")
    parser.add_argument("--k", default="1,5,10", help="глубины метрик через запятую")
    parser.add_argument("--output", help="каталог для записи результатов")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    k_values = [int(k) for k in args.k.split(",") if k.strip()]
    documents = load_corpus(args.corpus)
    queries = load_queries(args.queries, documents)

    started = time.perf_counter()
    retriever = build_retriever(
        args.retriever,
        documents,
        model=args.model,
        models_config=args.models_config,
        index_dir=args.index,
        progress=not args.quiet,
    )
    prepare_seconds = time.perf_counter() - started

    started = time.perf_counter()
    metrics, per_query = evaluate_queries(retriever, queries, k_values=k_values)
    evaluate_seconds = time.perf_counter() - started

    run = {
        "retriever": retriever.name,
        "label": retriever_label(args.retriever, args.model),
        "corpus": args.corpus,
        "corpus_documents": len(documents),
        "corpus_fingerprint": corpus_fingerprint(documents),
        "queries_file": args.queries,
        "queries": len(queries),
        "index_dir": args.index,
        "k_values": k_values,
        "metrics": metrics,
        "prepare_seconds": round(prepare_seconds, 2),
        "evaluate_seconds": round(evaluate_seconds, 2),
        "evaluated_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if args.output:
        directory = Path(args.output)
        directory.mkdir(parents=True, exist_ok=True)
        name = f"{run['label'].replace(':', '_')}__{Path(args.queries).stem}"
        (directory / f"{name}.json").write_text(
            json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        with (directory / f"{name}.per_query.jsonl").open("w", encoding="utf-8") as handle:
            for result in per_query:
                handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        run["output_dir"] = str(directory)

    if not args.quiet:
        print(json.dumps(run, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
