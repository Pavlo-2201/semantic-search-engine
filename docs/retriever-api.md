# Интерфейс поиска для повторного использования

Корпус и поиск сделаны так, чтобы их можно было взять в следующий проект (RAG)
без правок: внешнему коду нужен один контракт, а не знание о том, лексический
поиск внутри или векторный.

## Контракт

```python
@dataclass(frozen=True)
class SearchHit:
    doc_id: str      # устойчивый идентификатор документа, mdnru-<sha1(slug)[:12]>
    score: float     # оценка способа поиска; сравнима только внутри одного способа
    rank: int        # позиция в выдаче, с единицы
    title: str
    url: str
    snippet: str


class Retriever(Protocol):
    name: str
    def search(self, query: str, top_k: int = 10) -> list[SearchHit]: ...
    def search_batch(self, queries: Sequence[str], top_k: int = 10) -> list[list[SearchHit]]: ...
```

Гарантии: результаты упорядочены по убыванию оценки, `rank` начинается с единицы
и идёт без пропусков, `doc_id` всегда есть в корпусе, длина выдачи не больше
`top_k` (меньше — только если в корпусе или в приближённом индексе меньше
кандидатов).

Все реализации подчиняются этому контракту: `Bm25Retriever`, `TfidfRetriever`,
`ExactDenseRetriever`, `FaissDenseRetriever`.

## Как подключить

```python
from semsearch import open_retriever, load_corpus

# готовый индекс: корпус не кодируется заново
retriever = open_retriever("data/corpus/mdn-ru.jsonl", "data/indexes/lsa-300-flat")

for hit in retriever.search("как узнать длину массива", top_k=5):
    print(hit.rank, hit.score, hit.title, hit.url)

# лексический поиск без индекса
bm25 = open_retriever("data/corpus/mdn-ru.jsonl", kind="bm25")

# векторный поиск, модель кодирует корпус на месте
dense = open_retriever("data/corpus/mdn-ru.jsonl", kind="dense", model="lsa-300")
```

Полные тексты документов для генерации ответа берутся из корпуса по `doc_id`:

```python
documents = {d.doc_id: d for d in load_corpus("data/corpus/mdn-ru.jsonl")}
context = [documents[hit.doc_id].text for hit in retriever.search(question, top_k=3)]
```

## Выбор модели для RAG

На этом корпусе измерены: `lsa-300` (Recall@10 0.569 на финальном наборе),
`word2vec-200` (0.528), BM25 (0.500), TF-IDF (0.458), `rubert-tiny2` (0.292).
Предобученная `rubert-tiny2` — худшая: она обучена на сходстве коротких
предложений, а не на поиске документа по запросу. Для RAG имеет смысл брать
модель, обученную под retrieval (multilingual-e5 с префиксами `query:`/`passage:`,
LaBSE), а до тех пор — `lsa-300` или BM25, которые здесь измерены и работают.

## Что учесть в RAG-проекте

- **Единица поиска здесь — страница целиком.** Для генерации ответа это слишком
  крупно: медианная страница около 1300 символов, но встречаются и по 70 000.
  Нарезку на фрагменты лучше делать в RAG-проекте, переиспользуя `semsearch.corpus`
  (`Document`, `make_doc_id`) и добавляя к `doc_id` номер фрагмента.
- **Отпечаток корпуса** (`data/corpus/mdn-ru.meta.json`, `fingerprint_sha256`)
  стоит сохранять вместе с ответами: источник (ветка `main` MDN) меняется.
- **Лицензия корпуса — CC-BY-SA 2.5**, авторство MDN Web Docs contributors. Если
  ответы RAG показываются пользователю, ссылку на страницу-источник нужно
  показывать тоже: `SearchHit.url` для этого и есть.
- **Индекс самодостаточен**: в `meta.json` рядом с ним лежат конфигурация модели,
  соответствие позиция → `doc_id` и отпечаток корпуса, а обученная на корпусе
  модель — в `encoder.pkl`. Перенос каталога индекса на другую машину достаточен
  для поиска.
