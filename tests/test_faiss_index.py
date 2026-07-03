import numpy as np
import pytest

from semsearch.corpus import corpus_fingerprint
from semsearch.dense import ExactDenseRetriever, FaissDenseRetriever
from semsearch.embedding import EncoderConfig
from semsearch.faiss_index import IndexSpec, VectorIndex
from semsearch.pipeline import (
    build_encoder_for_corpus,
    build_index,
    load_index_retriever,
    save_encoder,
)

LSA_CONFIG = EncoderConfig(name="lsa-test", backend="lsa", dim=8)


def build_test_index(documents, index_type="flat-ip"):
    return build_index(documents, LSA_CONFIG, spec=IndexSpec(index_type=index_type))


def test_index_keeps_position_to_doc_id_mapping(documents):
    index, _ = build_test_index(documents)
    assert index.size == len(documents)
    assert index.doc_ids == [d.doc_id for d in documents]
    for position, document in enumerate(documents):
        assert index.position_of(document.doc_id) == position


def test_index_search_returns_doc_ids_not_positions(documents):
    index, encoder = build_test_index(documents)
    vectors = encoder.encode_queries(["сколько элементов в массиве"])
    scores, doc_id_rows = index.search(vectors, top_k=3)
    assert scores.shape == (1, 3)
    assert doc_id_rows[0][0] == documents[0].doc_id
    assert all(doc_id in {d.doc_id for d in documents} for doc_id in doc_id_rows[0])


def test_index_save_and_load_give_identical_results(documents, tmp_path):
    index, encoder = build_test_index(documents)
    vectors = encoder.encode_queries(["анимация элемента", "сетевой запрос"])
    before_scores, before_ids = index.search(vectors, top_k=3)

    index.save(tmp_path / "index")
    save_encoder(encoder, tmp_path / "index")
    loaded = VectorIndex.load(tmp_path / "index")

    after_scores, after_ids = loaded.search(vectors, top_k=3)
    assert before_ids == after_ids
    assert np.allclose(before_scores, after_scores)
    assert loaded.doc_ids == index.doc_ids
    assert loaded.dim == index.dim
    assert loaded.model["name"] == "lsa-test"


def test_loaded_retriever_reproduces_search_after_reload(documents, tmp_path):
    index, encoder = build_test_index(documents)
    index.save(tmp_path / "index")
    save_encoder(encoder, tmp_path / "index")

    before = FaissDenseRetriever(documents, encoder, index).search("длина массива", top_k=3)
    # имя модели lsa-test есть только в метаданных индекса, не в configs/models.yaml
    after = load_index_retriever(documents, tmp_path / "index").search("длина массива", top_k=3)
    assert [h.doc_id for h in before] == [h.doc_id for h in after]
    assert [round(h.score, 5) for h in before] == [round(h.score, 5) for h in after]


def test_exact_faiss_index_matches_bruteforce_search(documents):
    index, encoder = build_test_index(documents)
    faiss_hits = FaissDenseRetriever(documents, encoder, index).search_batch(
        ["длина массива", "код ответа сервера"], top_k=4
    )
    exact_hits = ExactDenseRetriever(documents, encoder).search_batch(
        ["длина массива", "код ответа сервера"], top_k=4
    )
    for from_index, from_bruteforce in zip(faiss_hits, exact_hits):
        assert [h.doc_id for h in from_index] == [h.doc_id for h in from_bruteforce]
        assert [round(h.score, 4) for h in from_index] == [
            round(h.score, 4) for h in from_bruteforce
        ]


def test_load_detects_corpus_change(documents, tmp_path):
    index, encoder = build_test_index(documents)
    index.save(tmp_path / "index")
    save_encoder(encoder, tmp_path / "index")
    with pytest.raises(ValueError, match="другом наборе документов"):
        load_index_retriever(documents[:-1], tmp_path / "index")


def test_check_matches_corpus_detects_changed_text(documents):
    index, _ = build_test_index(documents)
    with pytest.raises(ValueError, match="отпечаток корпуса"):
        index.check_matches_corpus([d.doc_id for d in documents], fingerprint="другой")
    # тот же корпус проверку проходит
    index.check_matches_corpus([d.doc_id for d in documents], corpus_fingerprint(documents))


def test_index_rejects_mismatched_query_dim(documents):
    index, _ = build_test_index(documents)
    with pytest.raises(ValueError, match="размерность"):
        index.search(np.zeros((1, index.dim + 1), dtype=np.float32), top_k=2)


def test_index_rejects_mismatched_doc_ids(documents):
    encoder = build_encoder_for_corpus(LSA_CONFIG, documents)
    embeddings = encoder.encode_documents([d.text for d in documents])
    with pytest.raises(ValueError, match="не совпадает"):
        VectorIndex.build(embeddings, [d.doc_id for d in documents][:-1])


def test_duplicate_doc_ids_are_rejected(documents):
    encoder = build_encoder_for_corpus(LSA_CONFIG, documents)
    embeddings = encoder.encode_documents([d.text for d in documents])
    doc_ids = [documents[0].doc_id] * len(documents)
    with pytest.raises(ValueError, match="повторяются doc_id"):
        VectorIndex.build(embeddings, doc_ids)


@pytest.mark.parametrize("index_type", ["ivf-flat", "hnsw"])
def test_approximate_index_returns_valid_doc_ids(documents, index_type, tmp_path):
    index, encoder = build_test_index(documents, index_type=index_type)
    index.save(tmp_path / index_type)
    save_encoder(encoder, tmp_path / index_type)
    loaded = VectorIndex.load(tmp_path / index_type)
    assert loaded.spec.index_type == index_type
    hits = FaissDenseRetriever(documents, encoder, loaded).search("длина массива", top_k=3)
    assert 0 < len(hits) <= 3
    assert all(hit.doc_id in {d.doc_id for d in documents} for hit in hits)
    assert [hit.rank for hit in hits] == list(range(1, len(hits) + 1))
