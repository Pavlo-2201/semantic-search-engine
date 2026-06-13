# Лексический и векторный поиск на одних запросах

Корпус: 2570 документов MDN. Векторная модель — lsa-300 (обучается на корпусе).

Разметки релевантности на этом этапе ещё нет, поэтому это примеры, а не измерение качества.

## Запрос: «как узнать длину массива в javascript»

**BM25**

1. 14.6495 — Массивы  
   https://developer.mozilla.org/ru/docs/Learn_web_development/Core/Scripting/Arrays
2. 12.4906 — TypeError: can't delete non-configurable array element(Тип ошибки:не удаётся удалить настраиваемый элемент массива)  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Errors/Non_configurable_array_element
3. 12.3169 — Упорядоченные наборы данных  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Guide/Indexed_collections

**dense-exact: lsa-300**

1. 0.5252 — TypedArray.prototype.set()  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/TypedArray/set
2. 0.4920 — Массив  
   https://developer.mozilla.org/ru/docs/Glossary/Array
3. 0.4702 — Упорядоченные наборы данных  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Guide/Indexed_collections

## Запрос: «отправить http запрос из браузера»

**BM25**

1. 14.9175 — Expect  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Headers/Expect
2. 14.5555 — PUT  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Methods/PUT
3. 14.4745 — Коды состояния ответа HTTP  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status

**dense-exact: lsa-300**

1. 0.6349 — 429 Too Many Requests  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status/429
2. 0.5810 — 100 Continue  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status/100
3. 0.5766 — GET  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Methods/GET

## Запрос: «как отменить всплытие события»

**BM25**

1. 20.4410 — focusout  
   https://developer.mozilla.org/ru/docs/Web/API/Element/focusout_event
2. 17.6993 — Document: DOMContentLoaded event  
   https://developer.mozilla.org/ru/docs/Web/API/Document/DOMContentLoaded_event
3. 16.7410 — EventTarget: метод addEventListener()  
   https://developer.mozilla.org/ru/docs/Web/API/EventTarget/addEventListener

**dense-exact: lsa-300**

1. 0.7003 — Event.cancelable  
   https://developer.mozilla.org/ru/docs/Web/API/Event/cancelable
2. 0.6686 — Event.bubbles  
   https://developer.mozilla.org/ru/docs/Web/API/Event/bubbles
3. 0.6631 — Event: свойство target  
   https://developer.mozilla.org/ru/docs/Web/API/Event/target

## Запрос: «выровнять элементы по центру контейнера»

**BM25**

1. 14.3448 — Выравнивание блоков в CSS разметке Grid  
   https://developer.mozilla.org/ru/docs/Web/CSS/Guides/Grid_layout/Box_alignment
2. 14.1483 — <col>: элемент столбца таблицы  
   https://developer.mozilla.org/ru/docs/Web/HTML/Reference/Elements/col
3. 14.1338 — Выравнивание полей CSS  
   https://developer.mozilla.org/ru/docs/Web/CSS/Guides/Box_alignment

**dense-exact: lsa-300**

1. 0.5252 — justify-content  
   https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/justify-content
2. 0.5072 — Выравнивание элементов во Flex контейнере  
   https://developer.mozilla.org/ru/docs/Web/CSS/Guides/Flexible_box_layout/Aligning_items
3. 0.5039 — align-content  
   https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/align-content

