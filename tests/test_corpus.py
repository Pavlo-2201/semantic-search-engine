import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semsearch.corpus import (  # noqa: E402
    Document,
    corpus_fingerprint,
    load_corpus,
    make_doc_id,
    write_corpus,
)
from semsearch.mdn import extract_title, markdown_to_text, slug_to_folder  # noqa: E402


def make_document(slug: str, text: str = "текст документа") -> Document:
    return Document.create(
        slug=slug,
        title=slug,
        text=text,
        url=f"https://example.org/{slug}",
        source_path=f"files/ru/{slug.lower()}/index.md",
        source_repo="mdn/translated-content",
        source_ref="main",
        license="CC-BY-SA-2.5",
    )


def test_doc_id_is_stable_and_depends_only_on_slug():
    assert make_doc_id("Web/CSS/flex") == make_doc_id("Web/CSS/flex")
    assert make_doc_id("Web/CSS/flex") != make_doc_id("Web/CSS/grid")
    # идентификатор не зависит от текста: правка статьи не ломает разметку запросов
    assert make_document("Web/CSS/flex", "старый текст").doc_id == (
        make_document("Web/CSS/flex", "новый текст").doc_id
    )


def test_write_and_load_corpus_roundtrip(tmp_path):
    documents = [make_document("Web/CSS/grid"), make_document("Web/CSS/flex")]
    path = tmp_path / "corpus.jsonl"
    assert write_corpus(path, documents) == 2

    loaded = load_corpus(path)
    assert [d.doc_id for d in loaded] == sorted(d.doc_id for d in documents)
    assert {d.slug for d in loaded} == {"Web/CSS/grid", "Web/CSS/flex"}
    assert loaded[0].char_len == len(loaded[0].text)


def test_load_corpus_rejects_duplicate_ids(tmp_path):
    path = tmp_path / "corpus.jsonl"
    doc = make_document("Web/CSS/grid")
    path.write_text(doc.to_json() + "\n" + doc.to_json() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="повторяющийся doc_id"):
        load_corpus(path)


def test_fingerprint_ignores_order_but_reacts_to_content():
    a, b = make_document("Web/CSS/grid"), make_document("Web/CSS/flex")
    assert corpus_fingerprint([a, b]) == corpus_fingerprint([b, a])
    changed = make_document("Web/CSS/flex", "другой текст")
    assert corpus_fingerprint([a, b]) != corpus_fingerprint([a, changed])


def test_slug_to_folder_handles_special_characters():
    assert slug_to_folder("Web/CSS/Flex") == "web/css/flex"
    assert slug_to_folder("Web/CSS/*") == "web/css/_star_"
    assert slug_to_folder("Web/CSS/:hover") == "web/css/_colon_hover"


MARKDOWN = """---
title: Array.prototype.map()
slug: Web/JavaScript/Reference/Global_Objects/Array/map
---

{{JSRef}}

## Сводка

Метод `map()` создаёт **новый** массив.

```js
const doubled = [1, 2].map((x) => x * 2);
```

Смотрите также [цикл for](/ru/docs/Web/JavaScript/Reference/Statements/for).
"""


def test_markdown_to_text_removes_code_macros_and_links():
    text = markdown_to_text(MARKDOWN)
    assert "title:" not in text
    assert "JSRef" not in text
    assert "const doubled" not in text
    assert "Метод map() создаёт новый массив." in text  # ** убраны
    assert "цикл for" in text
    assert "/ru/docs/" not in text


def test_extract_title_prefers_frontmatter():
    assert extract_title(MARKDOWN, "Web/JavaScript/x") == "Array.prototype.map()"
    assert extract_title("нет frontmatter", "Web/CSS/box_model") == "box model"
