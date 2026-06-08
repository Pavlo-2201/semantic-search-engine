"""Точный векторный поиск.

Начинается с точного поиска (полный перебор, numpy): он даёт верхнюю границу
качества для выбранной модели, и относительно него потом измеряется потеря от
приближённого индекса FAISS.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .corpus import Document
from .embedding import TextEncoder, build_document_text
from .retriever import BaseRetriever, SearchHit, make_snippet


def encode_corpus(
    encoder: TextEncoder,
    documents: Sequence[Document],
    progress: bool = False,
) -> np.ndarray:
    texts = [
        build_document_text(d.title, d.text, encoder.config.document_max_chars)
        for d in documents
    ]
    if progress:
        print(f"кодирование {len(texts)} документов моделью {encoder.config.name}…")
    vectors = encoder.encode_documents(texts)
    if vectors.shape[0] != len(documents):
        raise RuntimeError("кодировщик вернул не столько векторов, сколько документов")
    return np.ascontiguousarray(vectors, dtype=np.float32)


class ExactDenseRetriever(BaseRetriever):
    """Поиск по косинусной близости полным перебором.

    Векторы нормированы, поэтому скалярное произведение равно косинусу.
    """

    def __init__(
        self,
        documents: Sequence[Document],
        encoder: TextEncoder,
        embeddings: np.ndarray | None = None,
    ):
        self.documents = list(documents)
        self.encoder = encoder
        self.name = f"dense-exact:{encoder.config.name}"
        self.embeddings = (
            encode_corpus(encoder, self.documents) if embeddings is None else embeddings
        )
        if self.embeddings.shape[0] != len(self.documents):
            raise ValueError("число векторов не совпадает с числом документов")

    @property
    def dim(self) -> int:
        return int(self.embeddings.shape[1])

    def _hits_from_scores(self, scores: np.ndarray, top_k: int) -> list[SearchHit]:
        top_k = min(top_k, len(self.documents))
        if top_k <= 0:
            return []
        candidates = np.argpartition(-scores, top_k - 1)[:top_k]
        candidates = candidates[np.argsort(-scores[candidates], kind="stable")]
        hits = []
        for rank, index in enumerate(candidates, start=1):
            document = self.documents[index]
            hits.append(
                SearchHit(
                    doc_id=document.doc_id,
                    score=float(scores[index]),
                    rank=rank,
                    title=document.title,
                    url=document.url,
                    snippet=make_snippet(document.text),
                )
            )
        return hits

    def search(self, query: str, top_k: int = 10) -> list[SearchHit]:
        return self.search_batch([query], top_k=top_k)[0]

    def search_batch(self, queries: Sequence[str], top_k: int = 10) -> list[list[SearchHit]]:
        query_vectors = self.encoder.encode_queries(list(queries))
        scores = query_vectors @ self.embeddings.T
        return [self._hits_from_scores(row, top_k) for row in scores]
