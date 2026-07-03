#!/usr/bin/env bash
# Полное воспроизведение результатов из README: корпус, индексы, метрики,
# сравнение, задержки, разбор провалов. Все числа в репозитории получены
# этим путём.
#
#   bash scripts/run_all.sh
#
# Переменные окружения:
#   CORPUS   путь к корпусу (по умолчанию data/corpus/mdn-ru.jsonl)
#   REPEATS  число замеров задержки (по умолчанию 200)
set -euo pipefail

CORPUS="${CORPUS:-data/corpus/mdn-ru.jsonl}"
REPEATS="${REPEATS:-200}"

echo "== 1/6 корпус"
if [ -f "$CORPUS" ]; then
  echo "корпус уже загружен: $CORPUS (удалите файл, чтобы загрузить заново)"
else
  python scripts/download_corpus.py --config configs/corpus.yaml --output "$CORPUS"
fi

echo "== 2/6 тесты"
python -m pytest

echo "== 3/6 индексы FAISS"
python scripts/build_index.py --quiet --corpus "$CORPUS" --model lsa-300 \
  --index-type flat-ip --output data/indexes/lsa-300-flat
python scripts/build_index.py --quiet --corpus "$CORPUS" --model lsa-300 \
  --index-type hnsw --output data/indexes/lsa-300-hnsw
python scripts/build_index.py --quiet --corpus "$CORPUS" --model word2vec-200 \
  --index-type flat-ip --output data/indexes/word2vec-200-flat

echo "== 4/6 метрики по отдельным способам поиска"
for queries in data/queries/dev.jsonl data/queries/test.jsonl; do
  for retriever in bm25 tfidf; do
    python scripts/evaluate.py --quiet --corpus "$CORPUS" --retriever "$retriever" \
      --queries "$queries" --output results
  done
  models="lsa-300 word2vec-200"
  # предобученная модель — только если её веса уже скачаны (см. configs/models.yaml)
  if [ -d models/rubert-tiny2 ]; then models="$models rubert-tiny2"; fi
  for model in $models; do
    python scripts/evaluate.py --quiet --corpus "$CORPUS" --retriever dense --model "$model" \
      --queries "$queries" --output results
  done
done

echo "== 5/6 сравнение способов поиска на одном корпусе и одних запросах"
python scripts/compare_models.py --quiet --config configs/compare.yaml --output results/comparison

echo "== 6/6 задержки и разбор провальных запросов"
python scripts/benchmark_latency.py --quiet --corpus "$CORPUS" --repeats "$REPEATS" \
  --output results/latency.json
python scripts/benchmark_latency.py --quiet --corpus "$CORPUS" --repeats "$REPEATS" \
  --output results/latency-run2.json
python scripts/analyze_failures.py --quiet --corpus "$CORPUS" \
  --output results/failures.json --markdown results/failures.md

echo
echo "готово; результаты в results/"
