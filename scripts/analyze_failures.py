#!/usr/bin/env python3
"""Разбор провальных запросов: где поиск не нашёл размеченную страницу и что выдал вместо неё.

Прогоняет несколько способов поиска на одних запросах и собирает:

* сколько запросов нашли размеченную страницу на первом месте и в top-K;
* запросы, провалившиеся у всех способов (их стоит смотреть первыми: это либо
  тяжёлые формулировки, либо спорная разметка);
* запросы, где лексический поиск справился, а векторный нет, и наоборот.

Пример:
    python scripts/analyze_failures.py --output results/failures.json \
        --markdown docs/failures.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import load_corpus  # noqa: E402
from semsearch.evaluation import evaluate_queries, load_queries  # noqa: E402
from semsearch.pipeline import build_retriever  # noqa: E402

DEFAULT_RUNS = "bm25,tfidf,dense:lsa-300,dense:word2vec-200"
LEXICAL = ("bm25", "tfidf")


def parse_runs(value: str) -> list[tuple[str, str, str | None]]:
    runs = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            kind, model = item.split(":", 1)
            runs.append((item, kind, model))
        else:
            runs.append((item, item, None))
    return runs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="data/corpus/mdn-ru.jsonl")
    parser.add_argument("--queries", default="data/queries/dev.jsonl,data/queries/test.jsonl")
    parser.add_argument("--runs", default=DEFAULT_RUNS)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output", default="results/failures.json")
    parser.add_argument("--markdown", help="куда записать таблицы в Markdown")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    documents = load_corpus(args.corpus)
    runs = parse_runs(args.runs)
    query_files = [p.strip() for p in args.queries.split(",") if p.strip()]

    retrievers = {}
    for label, kind, model in runs:
        retrievers[label] = build_retriever(
            kind, documents, model=model, progress=not args.quiet
        )

    report = {"corpus_documents": len(documents), "top_k": args.top_k, "sets": {}}

    for path in query_files:
        queries = load_queries(path, documents)
        ranks: dict[str, dict[str, int | None]] = {}
        tops: dict[str, dict[str, str]] = {}
        for label, retriever in retrievers.items():
            _, per_query = evaluate_queries(
                retriever, queries, k_values=[1, args.top_k], keep_top=args.top_k
            )
            ranks[label] = {r.query_id: r.first_relevant_rank for r in per_query}
            tops[label] = {
                r.query_id: (r.retrieved[0]["title"] if r.retrieved else "") for r in per_query
            }

        summary = {}
        for label in retrievers:
            found_first = sum(1 for rank in ranks[label].values() if rank == 1)
            found_any = sum(1 for rank in ranks[label].values() if rank is not None)
            summary[label] = {
                "нашёл на первом месте": found_first,
                f"нашёл в top-{args.top_k}": found_any,
                "не нашёл": len(queries) - found_any,
            }

        failed_everywhere = [
            q
            for q in queries
            if all(ranks[label][q.query_id] is None for label in retrievers)
        ]
        lexical_only = [
            q
            for q in queries
            if any(ranks[label][q.query_id] is not None for label in retrievers if label in LEXICAL)
            and all(
                ranks[label][q.query_id] is None
                for label in retrievers
                if label not in LEXICAL
            )
        ]
        dense_only = [
            q
            for q in queries
            if any(
                ranks[label][q.query_id] is not None
                for label in retrievers
                if label not in LEXICAL
            )
            and all(
                ranks[label][q.query_id] is None for label in retrievers if label in LEXICAL
            )
        ]

        def describe(selected):
            return [
                {
                    "query_id": q.query_id,
                    "query": q.query,
                    "relevant": list(q.slugs),
                    "top1": {label: tops[label][q.query_id] for label in retrievers},
                    "ranks": {label: ranks[label][q.query_id] for label in retrievers},
                }
                for q in selected
            ]

        report["sets"][path] = {
            "queries": len(queries),
            "summary": summary,
            "failed_everywhere": describe(failed_everywhere),
            "lexical_found_dense_missed": describe(lexical_only),
            "dense_found_lexical_missed": describe(dense_only),
        }
        if not args.quiet:
            print(f"\n{path}: {len(queries)} запросов")
            for label, values in summary.items():
                print(f"  {label}: {values}")
            print(f"  провалились у всех: {len(failed_everywhere)}")
            print(f"  нашёл только лексический: {len(lexical_only)}")
            print(f"  нашёл только векторный: {len(dense_only)}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if args.markdown:
        lines = ["# Разбор провальных запросов", ""]
        lines.append(
            f"Корпус: {len(documents)} документов. "
            f"Провал — размеченной страницы нет в первых {args.top_k} результатах."
        )
        lines.append("")
        for path, data in report["sets"].items():
            lines.append(f"## {Path(path).stem} ({data['queries']} запросов)")
            lines.append("")
            lines.append("| поиск | на первом месте | в top-10 | не нашёл |")
            lines.append("|---|---|---|---|")
            for label, values in data["summary"].items():
                lines.append(
                    f"| {label} | {values['нашёл на первом месте']} | "
                    f"{values[f'нашёл в top-{args.top_k}']} | {values['не нашёл']} |"
                )
            lines.append("")
            for key, title in (
                ("failed_everywhere", "Провалились у всех способов"),
                ("lexical_found_dense_missed", "Нашёл только лексический поиск"),
                ("dense_found_lexical_missed", "Нашёл только векторный поиск"),
            ):
                items = data[key]
                lines.append(f"### {title}: {len(items)}")
                lines.append("")
                for item in items:
                    lines.append(f"- «{item['query']}» — ожидалось: {', '.join(item['relevant'])}")
                    for label, top1 in item["top1"].items():
                        rank = item["ranks"][label]
                        rank_text = f"ранг {rank}" if rank else "не найдено"
                        lines.append(f"  - {label}: {rank_text}, на первом месте «{top1}»")
                lines.append("")
        Path(args.markdown).write_text("\n".join(lines) + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"\nтаблицы: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
