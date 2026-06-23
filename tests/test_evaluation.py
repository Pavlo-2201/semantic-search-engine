import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import make_doc_id  # noqa: E402
from semsearch.evaluation import (  # noqa: E402
    LabeledQuery,
    evaluate_queries,
    load_queries,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank_at_k,
)
from semsearch.retriever import SearchHit  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def hits(*doc_ids: str) -> list[SearchHit]:
    return [
        SearchHit(doc_id=doc_id, score=1.0 - index / 100, rank=index + 1)
        for index, doc_id in enumerate(doc_ids)
    ]


def query(relevance: dict[str, int]) -> LabeledQuery:
    return LabeledQuery(query_id="q1", query="запрос", relevance=relevance)


def test_recall_counts_share_of_relevant_documents():
    q = query({"a": 2, "b": 1})
    assert recall_at_k(hits("a", "x", "y"), q, 3) == pytest.approx(0.5)
    assert recall_at_k(hits("a", "b", "y"), q, 3) == pytest.approx(1.0)
    assert recall_at_k(hits("x", "y", "a"), q, 2) == pytest.approx(0.0)


def test_reciprocal_rank_uses_first_relevant_position():
    q = query({"a": 2})
    assert reciprocal_rank_at_k(hits("a", "x"), q, 5) == pytest.approx(1.0)
    assert reciprocal_rank_at_k(hits("x", "a"), q, 5) == pytest.approx(0.5)
    assert reciprocal_rank_at_k(hits("x", "y", "a"), q, 5) == pytest.approx(1 / 3)
    # за пределами K вклад нулевой
    assert reciprocal_rank_at_k(hits("x", "y", "a"), q, 2) == pytest.approx(0.0)


def test_ndcg_is_one_for_ideal_order_and_lower_otherwise():
    q = query({"a": 2, "b": 1})
    assert ndcg_at_k(hits("a", "b", "x"), q, 3) == pytest.approx(1.0)
    swapped = ndcg_at_k(hits("b", "a", "x"), q, 3)
    assert 0.0 < swapped < 1.0
    assert ndcg_at_k(hits("x", "y", "z"), q, 3) == pytest.approx(0.0)


def test_ndcg_respects_relevance_grades():
    """Документ с оценкой 2 на первом месте должен давать больше, чем с оценкой 1."""
    q = query({"a": 2, "b": 1})
    assert ndcg_at_k(hits("a", "x"), q, 1) > ndcg_at_k(hits("b", "x"), q, 1)


def test_ndcg_at_k_normalizes_by_achievable_ideal():
    """Если релевантных больше, чем K, идеал тоже считается по K документам."""
    q = query({"a": 2, "b": 2, "c": 2})
    assert ndcg_at_k(hits("a", "b"), q, 2) == pytest.approx(1.0)


class StubRetriever:
    name = "stub"

    def __init__(self, ranking: dict[str, list[str]]):
        self.ranking = ranking

    def search_batch(self, queries, top_k=10):
        return [hits(*self.ranking[q][:top_k]) for q in queries]


def test_evaluate_queries_averages_over_queries_and_keeps_details():
    queries = [
        LabeledQuery(query_id="q1", query="первый", relevance={"a": 2}),
        LabeledQuery(query_id="q2", query="второй", relevance={"b": 2}),
    ]
    retriever = StubRetriever({"первый": ["a", "z"], "второй": ["z", "b"]})
    metrics, per_query = evaluate_queries(retriever, queries, k_values=[1, 2])

    assert metrics["recall@1"] == pytest.approx(0.5)
    assert metrics["recall@2"] == pytest.approx(1.0)
    assert metrics["mrr@2"] == pytest.approx((1.0 + 0.5) / 2)
    assert [r.query_id for r in per_query] == ["q1", "q2"]
    assert per_query[0].first_relevant_rank == 1
    assert per_query[1].first_relevant_rank == 2
    assert per_query[0].retrieved[0]["grade"] == 2


# --- разметка в репозитории ---


def test_query_files_load_and_reference_existing_pages():
    for name in ("dev", "test"):
        queries = load_queries(REPO / f"data/queries/{name}.jsonl")
        assert len(queries) >= 30
        for q in queries:
            assert q.query.strip()
            assert q.relevance
            assert all(doc_id == make_doc_id(slug) for slug, doc_id in zip(q.slugs, q.relevance))


def test_dev_and_test_queries_do_not_overlap():
    dev = load_queries(REPO / "data/queries/dev.jsonl")
    test = load_queries(REPO / "data/queries/test.jsonl")
    assert not {q.query_id for q in dev} & {q.query_id for q in test}
    # одинаковых текстов запросов тоже быть не должно: иначе настройка видит тест
    assert not {q.query.lower() for q in dev} & {q.query.lower() for q in test}


def test_load_queries_rejects_duplicate_ids(tmp_path):
    record = {"query_id": "q1", "query": "текст", "relevant": [{"slug": "Web/CSS", "grade": 2}]}
    path = tmp_path / "queries.jsonl"
    path.write_text(json.dumps(record) + "\n" + json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="повторяющийся query_id"):
        load_queries(path)


def test_load_queries_checks_pages_against_corpus(tmp_path, documents):
    record = {
        "query_id": "q1",
        "query": "текст",
        "relevant": [{"slug": "Web/Does/Not/Exist", "grade": 2}],
    }
    path = tmp_path / "queries.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="нет в корпусе"):
        load_queries(path, documents)


def test_load_queries_rejects_unknown_grade(tmp_path):
    record = {"query_id": "q1", "query": "текст", "relevant": [{"slug": "Web/CSS", "grade": 3}]}
    path = tmp_path / "queries.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="градация"):
        load_queries(path)
