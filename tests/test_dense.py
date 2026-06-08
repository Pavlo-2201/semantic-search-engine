import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.dense import ExactDenseRetriever, encode_corpus  # noqa: E402
from semsearch.embedding import (  # noqa: E402
    EncoderConfig,
    LsaEncoder,
    SentenceTransformerEncoder,
    build_document_text,
    build_encoder,
    l2_normalize,
    load_model_configs,
)

LSA_CONFIG = EncoderConfig(name="lsa-test", backend="lsa", dim=8)


def document_texts(documents):
    return [build_document_text(d.title, d.text) for d in documents]


def test_build_document_text_cuts_by_chars_and_keeps_title():
    text = build_document_text("Заголовок", "слово " * 100, max_chars=30)
    assert text.startswith("Заголовок. ")
    assert len(text) <= 45
    assert "  " not in text


def test_l2_normalize_handles_zero_rows():
    matrix = np.array([[3.0, 4.0], [0.0, 0.0]], dtype=np.float32)
    normalized = l2_normalize(matrix)
    assert normalized[0] == pytest.approx([0.6, 0.8])
    assert normalized[1] == pytest.approx([0.0, 0.0])


def test_lsa_encoder_is_normalized_and_deterministic(documents):
    encoder = build_encoder(LSA_CONFIG, document_texts(documents))
    vectors = encoder.encode_documents(document_texts(documents))
    assert vectors.shape[0] == len(documents)
    assert np.linalg.norm(vectors, axis=1) == pytest.approx(1.0, abs=1e-5)
    again = build_encoder(LSA_CONFIG, document_texts(documents)).encode_documents(
        document_texts(documents)
    )
    assert np.allclose(vectors, again)


def test_lsa_encoder_save_and_load_give_same_vectors(documents, tmp_path):
    encoder = build_encoder(LSA_CONFIG, document_texts(documents))
    before = encoder.encode_queries(["длина массива"])
    path = tmp_path / "lsa.pkl"
    encoder.save(path)
    after = LsaEncoder.load(path).encode_queries(["длина массива"])
    assert np.allclose(before, after)


def test_exact_dense_retriever_ranks_and_keeps_doc_ids(documents):
    encoder = build_encoder(LSA_CONFIG, document_texts(documents))
    retriever = ExactDenseRetriever(documents, encoder)
    hits = retriever.search("сколько элементов в массиве", top_k=3)
    assert [h.rank for h in hits] == [1, 2, 3]
    assert all(a.score >= b.score for a, b in zip(hits, hits[1:]))
    assert {h.doc_id for h in hits} <= {d.doc_id for d in documents}
    assert hits[0].doc_id == documents[0].doc_id


def test_exact_dense_search_batch_matches_single(documents):
    encoder = build_encoder(LSA_CONFIG, document_texts(documents))
    retriever = ExactDenseRetriever(documents, encoder)
    queries = ["анимация элемента", "сетевой запрос"]
    batch = retriever.search_batch(queries, top_k=3)
    assert [[h.doc_id for h in hits] for hits in batch] == [
        [h.doc_id for h in retriever.search(query, top_k=3)] for query in queries
    ]


def test_dense_retriever_rejects_mismatched_embeddings(documents):
    encoder = build_encoder(LSA_CONFIG, document_texts(documents))
    embeddings = encode_corpus(encoder, documents)[:-1]
    with pytest.raises(ValueError, match="не совпадает"):
        ExactDenseRetriever(documents, encoder, embeddings=embeddings)


def test_model_configs_from_repo_declare_model_requirements():
    configs = load_model_configs(Path(__file__).resolve().parents[1] / "configs/models.yaml")
    assert configs["e5-small"].query_prefix == "query: "
    assert configs["e5-small"].document_prefix == "passage: "
    assert configs["e5-small"].pooling == "mean"
    assert configs["labse"].pooling == "cls"
    assert all(config.normalize for config in configs.values())


# Дальше — проверки механики sentence-transformers на крошечной локальной модели
# со случайными весами: качество не проверяется, проверяется только обращение с
# моделью (префиксы, пулинг, нормализация).


def test_sentence_transformer_encoder_normalizes_and_uses_prefixes(tiny_st_model_mean):
    config = EncoderConfig(
        name="tiny",
        backend="sentence-transformers",
        model_name=tiny_st_model_mean,
        query_prefix="query: ",
        document_prefix="passage: ",
        pooling="mean",
        normalize=True,
    )
    encoder = SentenceTransformerEncoder(config)
    queries = encoder.encode_queries(["длина массива"])
    documents = encoder.encode_documents(["длина массива"])
    assert queries.shape == (1, encoder.dim)
    assert np.linalg.norm(queries, axis=1) == pytest.approx(1.0, abs=1e-5)
    # один и тот же текст с разными префиксами кодируется по-разному,
    # значит префиксы действительно доходят до модели
    assert not np.allclose(queries, documents)


def test_sentence_transformer_encoder_can_disable_normalization(tiny_st_model_mean):
    config = EncoderConfig(
        name="tiny-raw",
        backend="sentence-transformers",
        model_name=tiny_st_model_mean,
        pooling="mean",
        normalize=False,
    )
    vectors = SentenceTransformerEncoder(config).encode_documents(["длина массива"])
    assert not np.allclose(np.linalg.norm(vectors, axis=1), 1.0)


def test_sentence_transformer_encoder_detects_wrong_pooling(tiny_st_model_cls):
    config = EncoderConfig(
        name="tiny-wrong-pooling",
        backend="sentence-transformers",
        model_name=tiny_st_model_cls,
        pooling="mean",
    )
    with pytest.raises(ValueError, match="pooling"):
        SentenceTransformerEncoder(config)


def test_exact_dense_retriever_works_with_sentence_transformer(documents, tiny_st_model_mean):
    config = EncoderConfig(
        name="tiny",
        backend="sentence-transformers",
        model_name=tiny_st_model_mean,
        query_prefix="query: ",
        document_prefix="passage: ",
        pooling="mean",
    )
    retriever = ExactDenseRetriever(documents, SentenceTransformerEncoder(config))
    hits = retriever.search("длина массива", top_k=4)
    assert len(hits) == 4
    assert [h.rank for h in hits] == [1, 2, 3, 4]
    assert len({h.doc_id for h in hits}) == 4
