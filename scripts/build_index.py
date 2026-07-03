#!/usr/bin/env python3
"""Сборка и сохранение векторного индекса FAISS.

Примеры:
    python scripts/build_index.py --model lsa-300 --output data/indexes/lsa-300-flat
    python scripts/build_index.py --model e5-small --index-type hnsw \
        --output data/indexes/e5-small-hnsw
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import load_corpus  # noqa: E402
from semsearch.faiss_index import INDEX_TYPES, IndexSpec  # noqa: E402
from semsearch.pipeline import build_index, resolve_model_config, save_encoder  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="data/corpus/mdn-ru.jsonl")
    parser.add_argument("--models-config", default="configs/models.yaml")
    parser.add_argument("--model", required=True, help="имя модели из configs/models.yaml")
    parser.add_argument("--index-type", default="flat-ip", choices=list(INDEX_TYPES))
    parser.add_argument("--nlist", type=int, default=128)
    parser.add_argument("--nprobe", type=int, default=8)
    parser.add_argument("--hnsw-m", type=int, default=32)
    parser.add_argument("--ef-construction", type=int, default=200)
    parser.add_argument("--ef-search", type=int, default=64)
    parser.add_argument("--output", required=True, help="каталог индекса")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    documents = load_corpus(args.corpus)
    config = resolve_model_config(args.model, args.models_config)
    spec = IndexSpec(
        index_type=args.index_type,
        nlist=args.nlist,
        nprobe=args.nprobe,
        hnsw_m=args.hnsw_m,
        ef_construction=args.ef_construction,
        ef_search=args.ef_search,
    )

    started = time.perf_counter()
    index, encoder = build_index(
        documents, config, spec=spec, corpus_path=args.corpus, progress=not args.quiet
    )
    build_seconds = time.perf_counter() - started

    index.save(args.output)
    save_encoder(encoder, args.output)

    report = {
        "index_dir": args.output,
        "corpus": args.corpus,
        "documents": index.size,
        "dim": index.dim,
        "index_type": spec.index_type,
        "model": config.to_dict(),
        "corpus_fingerprint": index.corpus_fingerprint,
        "build_seconds": round(build_seconds, 2),
    }
    Path(args.output, "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not args.quiet:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
