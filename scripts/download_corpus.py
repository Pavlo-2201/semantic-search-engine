#!/usr/bin/env python3
"""Воспроизводимая загрузка корпуса: configs/corpus.yaml -> data/corpus/mdn-ru.jsonl.

Пример:
    python scripts/download_corpus.py --config configs/corpus.yaml \
        --output data/corpus/mdn-ru.jsonl
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import corpus_fingerprint, write_corpus  # noqa: E402
from semsearch.mdn import MdnSource  # noqa: E402


def select_slugs(slugs: list[str], selection: dict) -> list[str]:
    include = tuple(selection.get("include_prefixes") or ())
    exclude = tuple(selection.get("exclude_prefixes") or ())

    def keep(slug: str) -> bool:
        if exclude and slug.startswith(exclude):
            return False
        if include and not slug.startswith(include):
            return False
        return True

    return [slug for slug in slugs if keep(slug)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/corpus.yaml")
    parser.add_argument("--output", default="data/corpus/mdn-ru.jsonl")
    parser.add_argument("--ref", help="переопределить ref (ветка или commit sha)")
    parser.add_argument("--limit", type=int, help="взять только первые N страниц (для отладки)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    source_config = config["source"]
    if args.ref:
        source_config["ref"] = args.ref
    download_config = config.get("download", {})

    source = MdnSource(
        repo=source_config["repo"],
        ref=source_config["ref"],
        docs_prefix=source_config["docs_prefix"],
        listing_path=source_config["listing_path"],
        base_url=source_config["base_url"],
        page_url_template=source_config["page_url_template"],
        license=source_config["license"],
        timeout=int(download_config.get("timeout_seconds", 30)),
        retries=int(download_config.get("retries", 3)),
    )

    session = requests.Session()
    all_slugs = source.list_slugs(session)
    slugs = select_slugs(all_slugs, config.get("selection", {}))
    if args.limit:
        slugs = slugs[: args.limit]
    if not args.quiet:
        print(f"страниц в источнике: {len(all_slugs)}, после отбора: {len(slugs)}")

    documents, missing = source.fetch_documents(
        slugs,
        workers=int(download_config.get("workers", 8)),
        progress=not args.quiet,
    )

    min_chars = int(config.get("selection", {}).get("min_chars", 0))
    too_short = [d.slug for d in documents if d.char_len < min_chars]
    documents = [d for d in documents if d.char_len >= min_chars]

    written = write_corpus(args.output, documents)
    fingerprint = corpus_fingerprint(documents)

    meta = {
        "corpus_name": config.get("name"),
        "output": args.output,
        "downloaded_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "repo": source.repo,
            "ref": source.ref,
            "listing_path": source.listing_path,
            "license": source.license,
            "license_url": source_config.get("license_url"),
            "attribution": source_config.get("attribution"),
        },
        "slugs_in_source": len(all_slugs),
        "slugs_selected": len(slugs),
        "documents": written,
        "missing_pages": len(missing),
        "dropped_too_short": len(too_short),
        "total_chars": sum(d.char_len for d in documents),
        "fingerprint_sha256": fingerprint,
    }
    meta_path = Path(args.output).with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.quiet:
        print(f"документов: {written}, пропущено страниц без файла: {len(missing)}")
        print(f"отпечаток корпуса: {fingerprint}")
        print(f"метаданные: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
