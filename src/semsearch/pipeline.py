"""Сборка поиска по имени: одно место, где лексический и векторный поиск
создаются одинаково — для CLI, оценки и сравнения моделей.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .corpus import Document
from .dense import ExactDenseRetriever, encode_corpus
from .embedding import EncoderConfig, build_document_text, build_encoder, load_model_configs
from .lexical import build_lexical_retriever

LEXICAL_KINDS = ("bm25", "tfidf")
DEFAULT_MODELS_CONFIG = "configs/models.yaml"


def resolve_model_config(name: str, models_config: str | Path = DEFAULT_MODELS_CONFIG) -> EncoderConfig:
    configs = load_model_configs(models_config)
    if name not in configs:
        raise ValueError(f"модель '{name}' не найдена в {models_config}; есть {sorted(configs)}")
    return configs[name]


def build_retriever(
    kind: str,
    documents: Sequence[Document],
    model: str | None = None,
    models_config: str | Path = DEFAULT_MODELS_CONFIG,
    progress: bool = False,
):
    """`kind` — bm25, tfidf или dense.

    Для dense нужна модель из configs/models.yaml: `model`.
    """
    if kind in LEXICAL_KINDS:
        return build_lexical_retriever(kind, documents)
    if kind == "dense":
        if not model:
            raise ValueError("для dense нужно указать модель из configs/models.yaml")
        config = resolve_model_config(model, models_config)
        corpus_texts = [
            build_document_text(d.title, d.text, config.document_max_chars) for d in documents
        ]
        encoder = build_encoder(config, corpus_texts)
        embeddings = encode_corpus(encoder, documents, progress=progress)
        return ExactDenseRetriever(documents, encoder, embeddings=embeddings)
    raise ValueError(f"неизвестный способ поиска: {kind}")


def retriever_label(kind: str, model: str | None) -> str:
    """Короткое имя прогона для отчётов и имён файлов."""
    return f"{kind}:{model}" if kind == "dense" and model else kind
