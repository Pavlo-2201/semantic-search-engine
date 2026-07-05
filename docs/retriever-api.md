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

На этом корпусе измерены (Recall@10 на финальном наборе): `e5-small` 0.681,
`lsa-300` 0.569, `word2vec-200` 0.528, BM25 0.500, TF-IDF 0.458, `rubert-tiny2`
0.292. Для RAG стоит брать `e5-small` (`intfloat/multilingual-e5-small`, ревизия
`614241f`): она лучшая и по полноте, и по первой позиции (MRR@10 0.399 против
0.268 у BM25), а для генерации ответа важно именно то, что стоит в первых
нескольких результатах. Префиксы `query: ` и `passage: ` модель требует; они
подставляются автоматически — из `configs/models.yaml` при сборке и из
`meta.json` индекса при загрузке. Цена — кодирование
запроса около 13 мс на CPU и несколько минут на кодирование всего корпуса;
поэтому индекс стоит собрать один раз (`scripts/build_index.py --model
e5-small`) и открывать готовым.

Если весов `e5-small` нет, рабочая замена без загрузки весов — `lsa-300` или
BM25. Предобученная `rubert-tiny2` для поиска не подходит: она обучена на
сходстве коротких предложений, а не на поиске документа по запросу.

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
