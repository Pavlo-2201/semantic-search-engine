# semantic-search-engine

Поиск по русскоязычной технической документации MDN: лексический baseline (TF-IDF и BM25),
векторный поиск на embeddings и индекс FAISS, с измеренным качеством и задержками.
По запросу на естественном языке («как узнать длину массива», «что означает код ответа 404»)
система находит страницы, которые на него отвечают.

## Итоги

Все способы поиска сравнивались на одном корпусе (2570 документов) и одних запросах. Параметры
настраивались на dev, ниже — test (36 запросов, при настройке не использовались):

| поиск | Recall@1 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |
|---|---|---|---|---|---|
| BM25 | 0.083 | 0.375 | 0.500 | 0.268 | 0.315 |
| TF-IDF | 0.097 | 0.278 | 0.458 | 0.209 | 0.258 |
| `lsa-300`, точный поиск | 0.097 | 0.375 | 0.569 | 0.255 | 0.322 |
| `word2vec-200`, точный поиск | 0.069 | 0.403 | 0.528 | 0.265 | 0.307 |
| `lsa-300`, FAISS hnsw | 0.097 | 0.375 | 0.569 | 0.255 | 0.322 |
| `lsa-300`, FAISS ivf-flat | 0.097 | 0.361 | 0.556 | 0.247 | 0.314 |
| `rubert-tiny2`, точный поиск | 0.083 | 0.222 | 0.292 | 0.195 | 0.191 |
| `e5-small`, точный поиск | **0.167** | **0.528** | **0.681** | **0.399** | **0.454** |

Полные таблицы dev и test — [results/comparison/comparison.md](results/comparison/comparison.md).

- **Лучшая — `e5-small`, модель, обученная под поиск**, с большим отрывом на обоих наборах.
  Главное — первая позиция: нужная страница стоит первой у неё в 12 запросах из 36 на dev
  и в 8 на test, у остальных — в 3–5.
- **Предобученная `rubert-tiny2` оказалась худшей из всех**: она обучена на сходство коротких
  предложений, а не на поиск документов. Нужна модель, обученная под retrieval, а не любая
  предобученная.
- BM25 заметно лучше TF-IDF: нормировка на длину документа работает на корпусе, где страницы
  различаются по длине в сотни раз.
- Время уходит на кодирование запроса (до 14 мс на CPU), а не на поиск по индексу (доли
  миллисекунды). Поэтому приближённый индекс на таком корпусе выигрыша не даёт, а ivf-flat ещё
  и теряет качество. Подробно — [docs/latency.md](docs/latency.md).
- Разметка небольшая и неполная (72 запроса от одного аннотатора), поэтому корректно сравнивать
  способы поиска между собой, а не читать абсолютные значения метрик.

## Данные

Русские переводы MDN Web Docs из [mdn/translated-content](https://github.com/mdn/translated-content),
лицензия [CC-BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/), авторство — MDN Web Docs
contributors. Источник зафиксирован commit'ом `f39fd206` (`configs/corpus.yaml`), у корпуса
считается отпечаток. 72 запроса (dev и test) размечены вручную, наборы не пересекаются. В Git нет
корпуса, индексов и весов.

## Быстрый старт (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/download_corpus.py --config configs/corpus.yaml --output data/corpus/mdn-ru.jsonl
python scripts/build_index.py --model e5-small --index-type flat-ip --output data/indexes/e5-small-flat
python scripts/search.py --retriever faiss --index data/indexes/e5-small-flat "запретить всплытие события"
python -m pytest
```

Веса `rubert-tiny2` и `e5-small` кладутся в `models/<имя>` (ревизии в `configs/models.yaml`);
без них их прогоны пропускаются с пометкой «не измерено». Все числа README воспроизводит
`scripts/run_all.sh` (запускается в Git Bash).

## Структура

```
src/semsearch/  корпус, разбор MDN, BM25/TF-IDF, кодировщики, FAISS, метрики, задержки
scripts/        загрузка, индексы, поиск, оценка, сравнение
configs/        корпус, модели, сравнение
data/queries/   разметка запросов dev и test
results/        метрики и задержки
docs/           API поиска, метрики, задержки, разбор провалов
```

Все способы поиска реализуют один контракт `Retriever` ([docs/retriever-api.md](docs/retriever-api.md)),
он используется в проекте `rag-document-assistant`.

## Стек

Python, sentence-transformers (`multilingual-e5-small`, `rubert-tiny2`), FAISS, scikit-learn
(TF-IDF, LSA), gensim (Word2Vec), BM25 (своя реализация), pytest.
