#!/usr/bin/env python3
"""Сравнение способов поиска на одном корпусе и одних запросах.

Все прогоны из configs/compare.yaml выполняются на одном и том же корпусе и на
одних и тех же файлах запросов; результат — таблица Markdown и машиночитаемый
JSON. Прогоны, помеченные `enabled: false` (например, требующие загрузки весов
с Hugging Face), в таблицу попадают строкой «не измерено».

Пример:
    python scripts/compare_models.py --config configs/compare.yaml \
        --output results/comparison
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import corpus_fingerprint, load_corpus  # noqa: E402
from semsearch.dense import ExactDenseRetriever, FaissDenseRetriever  # noqa: E402
from semsearch.evaluation import evaluate_queries, load_queries  # noqa: E402
from semsearch.faiss_index import IndexSpec, VectorIndex  # noqa: E402
from semsearch.lexical import build_lexical_retriever  # noqa: E402
from semsearch.pipeline import (  # noqa: E402
    build_encoder_for_corpus,
    resolve_model_config,
)
from semsearch.dense import encode_corpus  # noqa: E402

NOT_MEASURED = "не измерено"


def make_retriever(run: dict, documents, models_config: str, cache: dict):
    """Собрать поиск для одного прогона, переиспользуя кодировщики и векторы.

    Кодирование корпуса — самая дорогая часть, и для точного поиска и для
    индексов FAISS на одной модели оно одно и то же, поэтому результат
    кэшируется. Это не влияет на метрики: векторы те же.
    """
    kind = run["retriever"]
    if kind in ("bm25", "tfidf"):
        return build_lexical_retriever(kind, documents)

    model_name = run["model"]
    if model_name not in cache:
        config = resolve_model_config(model_name, models_config)
        encoder = build_encoder_for_corpus(config, documents)
        cache[model_name] = (config, encoder, encode_corpus(encoder, documents))
    config, encoder, embeddings = cache[model_name]

    if kind == "dense":
        return ExactDenseRetriever(documents, encoder, embeddings=embeddings)
    if kind == "faiss":
        spec = IndexSpec(
            index_type=run.get("index_type", "flat-ip"),
            nlist=int(run.get("nlist", 128)),
            nprobe=int(run.get("nprobe", 8)),
            hnsw_m=int(run.get("hnsw_m", 32)),
            ef_construction=int(run.get("ef_construction", 200)),
            ef_search=int(run.get("ef_search", 64)),
        )
        index = VectorIndex.build(
            embeddings,
            [d.doc_id for d in documents],
            spec=spec,
            model=config.to_dict(),
            corpus_fingerprint=corpus_fingerprint(documents),
        )
        return FaissDenseRetriever(documents, encoder, index)
    raise ValueError(f"неизвестный способ поиска: {kind}")


def format_table(rows: list[dict], queries_file: str, k_values: list[int]) -> str:
    columns = [f"Recall@{k}" for k in k_values] + [f"MRR@{max(k_values)}", f"nDCG@{max(k_values)}"]
    lines = [
        f"### {Path(queries_file).stem} ({rows[0]['queries']} запросов)"
        if rows and rows[0].get("queries")
        else f"### {Path(queries_file).stem}",
        "",
        "| поиск | " + " | ".join(columns) + " |",
        "|" + "---|" * (len(columns) + 1),
    ]
    for row in rows:
        if row.get("status") == NOT_MEASURED:
            values = [NOT_MEASURED] * len(columns)
        else:
            metrics = row["metrics"]
            values = [f"{metrics[f'recall@{k}']:.3f}" for k in k_values]
            values.append(f"{metrics[f'mrr@{max(k_values)}']:.3f}")
            values.append(f"{metrics[f'ndcg@{max(k_values)}']:.3f}")
        lines.append(f"| {row['name']} | " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/compare.yaml")
    parser.add_argument("--models-config", default="configs/models.yaml")
    parser.add_argument("--output", default="results/comparison")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    documents = load_corpus(config["corpus"])
    fingerprint = corpus_fingerprint(documents)
    k_values = [int(k) for k in config.get("k_values", [1, 5, 10])]
    query_files = list(config["queries"])

    cache: dict = {}
    results: dict[str, list[dict]] = {path: [] for path in query_files}

    for run in config["runs"]:
        name = run["name"]
        if not run.get("enabled", True):
            reason = "требуется доступ к huggingface.co для загрузки весов модели"
            for path in query_files:
                results[path].append({"name": name, "status": NOT_MEASURED, "reason": reason})
            if not args.quiet:
                print(f"{name}: {NOT_MEASURED} ({reason})")
            continue

        started = time.perf_counter()
        retriever = make_retriever(run, documents, args.models_config, cache)
        prepare_seconds = time.perf_counter() - started

        for path in query_files:
            queries = load_queries(path, documents)
            metrics, _ = evaluate_queries(retriever, queries, k_values=k_values)
            results[path].append(
                {
                    "name": name,
                    "retriever": retriever.name,
                    "config": {k: v for k, v in run.items() if k != "name"},
                    "queries": len(queries),
                    "metrics": metrics,
                    "prepare_seconds": round(prepare_seconds, 2),
                    "compare_with": run.get("compare_with"),
                }
            )
            if not args.quiet:
                print(f"{name} / {Path(path).stem}: {metrics}")

    # потеря качества приближённого индекса относительно точного поиска
    for path, rows in results.items():
        by_name = {row["name"]: row for row in rows if row.get("metrics")}
        for row in rows:
            baseline_name = row.get("compare_with")
            if not baseline_name or baseline_name not in by_name:
                continue
            baseline = by_name[baseline_name]["metrics"]
            row["loss_vs_exact"] = {
                name: round(row["metrics"][name] - baseline[name], 4) for name in baseline
            }

    report = {
        "corpus": config["corpus"],
        "corpus_documents": len(documents),
        "corpus_fingerprint": fingerprint,
        "k_values": k_values,
        "compared_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": {path: rows for path, rows in results.items()},
    }

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    tables = [
        "# Сравнение способов поиска",
        "",
        f"Корпус: `{config['corpus']}`, {len(documents)} документов, "
        f"отпечаток `{fingerprint[:16]}…`.",
        "",
        "Все строки таблицы получены на одном корпусе и одних запросах.",
        "",
    ]
    for path in query_files:
        tables.append(format_table(results[path], path, k_values))
        tables.append("")
    (out_dir / "comparison.md").write_text("\n".join(tables) + "\n", encoding="utf-8")

    if not args.quiet:
        print(f"\nтаблица: {out_dir / 'comparison.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
