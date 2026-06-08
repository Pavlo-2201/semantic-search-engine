"""Общие фикстуры тестов.

Главная из них — крошечная локальная модель sentence-transformers со случайными
весами. Она нужна, чтобы проверять механику векторного поиска (префиксы, пулинг,
нормализацию, соответствие ID) без загрузки реальных весов из сети. Качество
такой модели никакого смысла не имеет и в тестах не проверяется.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import Document  # noqa: E402

SAMPLE_DOCUMENTS = [
    ("Web/JavaScript/Array/length", "Array.prototype.length",
     "Свойство length возвращает количество элементов массива."),
    ("Web/CSS/animation", "animation",
     "Свойство animation задаёт анимацию элемента: имя, длительность, функцию сглаживания."),
    ("Web/API/fetch", "fetch()",
     "Метод fetch запускает сетевой запрос и возвращает промис с ответом сервера."),
    ("Web/HTTP/Status/404", "404 Not Found",
     "Код состояния HTTP 404 означает, что сервер не нашёл запрошенный ресурс."),
    ("Web/JavaScript/Statements/async_function", "async function",
     "Объявление async function создаёт асинхронную функцию, возвращающую промис."),
    ("Web/CSS/flexbox", "Основные концепции flexbox",
     "Flexbox помогает выравнивать и распределять элементы по оси контейнера."),
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
        for slug, title, text in SAMPLE_DOCUMENTS
    ]


def _build_tiny_tokenizer(words: list[str]):
    """Словарный токенизатор по пробелам: для проверки механики этого достаточно."""
    from tokenizers import Tokenizer, models, pre_tokenizers, processors
    from transformers import PreTrainedTokenizerFast

    special = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
    vocab = {token: index for index, token in enumerate(special + words)}
    tokenizer = Tokenizer(models.WordLevel(vocab=vocab, unk_token="[UNK]"))
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    tokenizer.post_processor = processors.TemplateProcessing(
        single="[CLS] $A [SEP]",
        special_tokens=[("[CLS]", vocab["[CLS]"]), ("[SEP]", vocab["[SEP]"])],
    )
    wrapped = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        unk_token="[UNK]",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]",
    )
    return wrapped, len(vocab)


def _build_tiny_sentence_transformer(path: Path, pooling_mode: str = "mean") -> None:
    from sentence_transformers import SentenceTransformer, models
    from transformers import BertConfig, BertModel

    words = [
        "query", "passage", ":", "массив", "массива", "длина", "элемент", "элементов",
        "css", "анимация", "запрос", "сетевой", "сервер", "ошибка", "функция", "промис",
        "сколько", "в", "и", "код", "состояния", "flexbox", "свойство", "метод",
    ]
    path.mkdir(parents=True, exist_ok=True)
    tokenizer, vocab_size = _build_tiny_tokenizer(words)
    config = BertConfig(
        vocab_size=vocab_size,
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        max_position_embeddings=64,
    )
    backbone = BertModel(config)
    backbone_dir = path / "backbone"
    backbone.save_pretrained(backbone_dir)
    tokenizer.save_pretrained(backbone_dir)

    word_embedding = models.Transformer(str(backbone_dir), max_seq_length=32)
    pooling = models.Pooling(word_embedding.get_word_embedding_dimension(), pooling_mode)
    SentenceTransformer(modules=[word_embedding, pooling]).save(str(path / "model"))


@pytest.fixture(scope="session")
def tiny_st_model_mean(tmp_path_factory) -> str:
    path = tmp_path_factory.mktemp("tiny-st-mean")
    _build_tiny_sentence_transformer(path, "mean")
    return str(path / "model")


@pytest.fixture(scope="session")
def tiny_st_model_cls(tmp_path_factory) -> str:
    path = tmp_path_factory.mktemp("tiny-st-cls")
    _build_tiny_sentence_transformer(path, "cls")
    return str(path / "model")
