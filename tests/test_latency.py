import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.latency import (  # noqa: E402
    hardware_info,
    measure,
    measure_dense_latency,
    measure_end_to_end_latency,
    percentile,
)


def test_percentile_uses_nearest_rank():
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    assert percentile(values, 50) == 5.0
    assert percentile(values, 95) == 10.0
    assert percentile(values, 0) == 1.0
    assert percentile([42.0], 95) == 42.0


def test_percentile_requires_measurements():
    with pytest.raises(ValueError, match="нет измерений"):
        percentile([], 50)


def test_measure_counts_only_repeats_and_cycles_through_calls():
    seen = []
    stats = measure(seen.append, n_calls=3, repeats=6, warmup=2, name="x")
    assert len(stats.samples_ms) == 6
    # прогрев не попал в статистику, но операция выполнялась
    assert len(seen) == 8
    # вызовы перебираются по кругу, а не повторяют один и тот же
    assert seen[2:] == [0, 1, 2, 0, 1, 2]


def test_summary_reports_percentiles_and_count():
    summary = measure(lambda i: None, n_calls=1, repeats=20, warmup=1, name="x").summary()
    assert summary["measurements"] == 20
    assert summary["p50_ms"] <= summary["p95_ms"] <= summary["max_ms"]
    assert summary["min_ms"] <= summary["p50_ms"]


class StubEncoder:
    class config:  # noqa: N801 - подражает EncoderConfig
        name = "stub"

    def encode_queries(self, texts):
        return np.ones((len(texts), 4), dtype=np.float32)


def test_measure_dense_latency_separates_encoding_and_search():
    searched = []
    report = measure_dense_latency(
        StubEncoder(),
        lambda vectors: searched.append(vectors),
        ["первый запрос", "второй запрос"],
        repeats=5,
        warmup=1,
    )
    assert report["query_encoding"]["measurements"] == 5
    assert report["index_search"]["measurements"] == 5
    assert report["total_p50_ms"] == pytest.approx(
        report["query_encoding"]["p50_ms"] + report["index_search"]["p50_ms"]
    )
    # поиск вызывался уже на готовых векторах: кодирование в его время не входит
    assert len(searched) == 6


class StubRetriever:
    name = "stub"

    def search(self, query, top_k=10):
        return []


def test_measure_end_to_end_latency_reports_single_phase():
    report = measure_end_to_end_latency(StubRetriever(), ["запрос"], repeats=4, warmup=1)
    assert report["search"]["measurements"] == 4
    assert report["total_p95_ms"] == report["search"]["p95_ms"]


def test_hardware_info_describes_machine():
    info = hardware_info()
    assert info["platform"]
    assert info["cpu_count"] and info["cpu_count"] > 0
    assert "gpu" in info
