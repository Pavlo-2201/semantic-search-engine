import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import Document  # noqa: E402
from semsearch.lexical import Bm25Retriever, TfidfRetriever, build_lexical_retriever  # noqa: E402
from semsearch.text import analyze, normalize  # noqa: E402

RAW_DOCUMENTS = [
    ("Web/JavaScript/Array/length", "Array.prototype.length",
     "Свойство length возвращает количество элементов массива. Длина массива меняется при добавлении элементов."),
    ("Web/CSS/animation", "animation",
     "Свойство animation задаёт анимацию элемента: имя, длительность и функцию сглаживания."),
    ("Web/API/fetch", "fetch()",
     "Метод fetch запускает сетевой запрос и возвращает промис с ответом сервера."),
    ("Web/HTTP/Status/404", "404 Not Found",
     "Код состояния HTTP 404 означает, что сервер не нашёл запрошенный ресурс."),
]


@pytest.fixture
def documents() -> list[Document]:
    return [
        Document.create(
            slug=slug,
            title=title,
            text=text,
            url=f"https://example.org/{slug}",
            source_path=f"files/ru/{slug.lower()}/index.md",
            source_repo="mdn/translated-content",
            source_ref="main",
            license="CC-BY-SA-2.5",
        )
        for slug, title, text in RAW_DOCUMENTS
    ]


def test_normalize_merges_yo_and_lowercases():
    assert normalize("Ещё ОДНО") == "еще одно"


def test_analyze_stems_russian_and_keeps_english_identifiers():
    terms = analyze("Длина массива и метод querySelector")
    assert "массив" in terms
    assert "queryselector" in terms
    assert "и" not in terms  # стоп-слово


@pytest.mark.parametrize("kind", ["bm25", "tfidf"])
def test_search_finds_document_by_paraphrase(kind, documents):
    retriever = build_lexical_retriever(kind, documents)
    hits = retriever.search("сколько элементов в массиве", top_k=4)
    assert hits[0].doc_id == documents[0].doc_id
    assert hits[0].title == "Array.prototype.length"


@pytest.mark.parametrize("kind", ["bm25", "tfidf"])
def test_results_are_ranked_and_scores_do_not_increase(kind, documents):
    retriever = build_lexical_retriever(kind, documents)
    hits = retriever.search("анимация элемента css", top_k=4)
    assert [h.rank for h in hits] == [1, 2, 3, 4]
    assert all(a.score >= b.score for a, b in zip(hits, hits[1:]))


@pytest.mark.parametrize("kind", ["bm25", "tfidf"])
def test_top_k_is_respected_and_clipped_to_corpus(kind, documents):
    retriever = build_lexical_retriever(kind, documents)
    assert len(retriever.search("запрос", top_k=2)) == 2
    assert len(retriever.search("запрос", top_k=99)) == len(documents)


@pytest.mark.parametrize("kind", ["bm25", "tfidf"])
def test_unknown_terms_do_not_break_search(kind, documents):
    hits = build_lexical_retriever(kind, documents).search("ламбумиз крокодилит", top_k=3)
    assert len(hits) == 3
    assert all(hit.score == pytest.approx(0.0) for hit in hits)


def test_search_batch_matches_single_search(documents):
    retriever = Bm25Retriever(documents)
    queries = ["длина массива", "сетевой запрос"]
    batch = retriever.search_batch(queries, top_k=2)
    assert [[h.doc_id for h in hits] for hits in batch] == [
        [h.doc_id for h in retriever.search(query, top_k=2)] for query in queries
    ]


def test_bm25_normalizes_document_length(documents):
    """Дописанный в конец длинный текст не должен сам по себе поднимать документ."""
    padded = list(documents)
    padded[3] = Document.create(
        slug=padded[3].slug,
        title=padded[3].title,
        text=padded[3].text + " сервер ресурс " * 200,
        url=padded[3].url,
        source_path=padded[3].source_path,
        source_repo=padded[3].source_repo,
        source_ref=padded[3].source_ref,
        license=padded[3].license,
    )
    retriever = Bm25Retriever(padded)
    hits = retriever.search("сетевой запрос промис", top_k=4)
    assert hits[0].doc_id == documents[2].doc_id


def test_tfidf_uses_cosine_scores_in_unit_range(documents):
    hits = TfidfRetriever(documents, min_df=1, max_df=1.0).search("длина массива", top_k=4)
    assert 0.0 <= hits[0].score <= 1.0
