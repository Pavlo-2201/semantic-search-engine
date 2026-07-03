#!/usr/bin/env python3
"""Измерение задержек поиска: кодирование запроса и поиск по индексу отдельно.

Примеры:
    python scripts/benchmark_latency.py --repeats 200 --output results/latency.json
    python scripts/benchmark_latency.py --runs bm25,lsa-300,lsa-300-hnsw
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import corpus_fingerprint, load_corpus  # noqa: E402
from semsearch.dense import ExactDenseRetriever, FaissDenseRetriever, encode_corpus  # noqa: E402
from semsearch.evaluation import load_queries  # noqa: E402
from semsearch.faiss_index import IndexSpec, VectorIndex  # noqa: E402
from semsearch.latency import (  # noqa: E402
    hardware_info,
    measure_dense_latency,
    measure_end_to_end_latency,
)
from semsearch.lexical import build_lexical_retriever  # noqa: E402
from semsearch.embedding import local_weights_path  # noqa: E402
from semsearch.pipeline import build_encoder_for_corpus, resolve_model_config  # noqa: E402

# Что измеряем по умолчанию: лексический baseline, точный векторный поиск и
# оба приближённых индекса на одной модели.
DEFAULT_RUNS = (
    "bm25",
    "tfidf",
    "lsa-300",
    "word2vec-200",
    "rubert-tiny2",
    "lsa-300-hnsw",
    "lsa-300-ivf",
)

DENSE_RUNS = {
    "lsa-300": {"model": "lsa-300", "index": None},
    "word2vec-200": {"model": "word2vec-200", "index": None},
    "rubert-tiny2": {"model": "rubert-tiny2", "index": None},
    "lsa-300-flat": {"model": "lsa-300", "index": IndexSpec(index_type="flat-ip")},
    "lsa-300-hnsw": {"model": "lsa-300", "index": IndexSpec(index_type="hnsw")},
    "lsa-300-ivf": {"model": "lsa-300", "index": IndexSpec(index_type="ivf-flat", nlist=64)},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="data/corpus/mdn-ru.jsonl")
    parser.add_argument("--queries", default="data/queries/dev.jsonl")
    parser.add_argument("--models-config", default="configs/models.yaml")
    parser.add_argument("--runs", default=",".join(DEFAULT_RUNS))
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=200)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--output", default="results/latency.json")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    documents = load_corpus(args.corpus)
    queries = [q.query for q in load_queries(args.queries, documents)]
    run_names = [name.strip() for name in args.runs.split(",") if name.strip()]

    report = {
        "corpus": args.corpus,
        "corpus_documents": len(documents),
        "corpus_fingerprint": corpus_fingerprint(documents),
        "queries_file": args.queries,
        "queries": len(queries),
        "top_k": args.top_k,
        "repeats": args.repeats,
        "warmup": args.warmup,
        "percentile_definition": "ближайший ранг по отсортированным измерениям",
        "hardware": hardware_info(),
        "measured_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runs": {},
    }

    encoder_cache: dict = {}
    for name in run_names:
        if name in ("bm25", "tfidf"):
            retriever = build_lexical_retriever(name, documents)
            measured = measure_end_to_end_latency(
                retriever,
                queries,
                top_k=args.top_k,
                repeats=args.repeats,
                warmup=args.warmup,
            )
            measured["note"] = (
                "лексический поиск измерен целиком: разбор запроса на термины "
                "неотделим от обхода словаря"
            )
        elif name in DENSE_RUNS:
            spec = DENSE_RUNS[name]["index"]
            model_name = DENSE_RUNS[name]["model"]
            config = resolve_model_config(model_name, args.models_config)
            if config.backend == "sentence-transformers" and config.local_path:
                if local_weights_path(config) is None:
                    report["runs"][name] = {
                        "status": "не измерено",
                        "reason": f"нет скачанных весов в {config.local_path}",
                    }
                    if not args.quiet:
                        print(f"{name}: не измерено (нет скачанных весов)")
                    continue
            if model_name not in encoder_cache:
                encoder = build_encoder_for_corpus(config, documents)
                encoder_cache[model_name] = (
                    config,
                    encoder,
                    encode_corpus(encoder, documents),
                )
            config, encoder, embeddings = encoder_cache[model_name]
            if spec is None:
                retriever = ExactDenseRetriever(documents, encoder, embeddings=embeddings)

                def search(vectors, retriever=retriever):
                    scores = vectors @ retriever.embeddings.T
                    return retriever._hits_from_scores(scores[0], args.top_k)

            else:
                index = VectorIndex.build(
                    embeddings,
                    [d.doc_id for d in documents],
                    spec=spec,
                    model=config.to_dict(),
                    corpus_fingerprint=report["corpus_fingerprint"],
                )
                retriever = FaissDenseRetriever(documents, encoder, index)

                def search(vectors, index=index):
                    return index.search(vectors, args.top_k)

            measured = measure_dense_latency(
                encoder,
                search,
                queries,
                repeats=args.repeats,
                warmup=args.warmup,
            )
            measured["retriever"] = retriever.name
        else:
            raise SystemExit(f"неизвестный прогон: {name}; есть {sorted(DENSE_RUNS) + ['bm25', 'tfidf']}")

        report["runs"][name] = measured
        if not args.quiet:
            print(f"{name}: p50 {measured['total_p50_ms']} мс, p95 {measured['total_p95_ms']} мс")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not args.quiet:
        print(f"отчёт: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
