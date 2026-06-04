# Примеры работы лексического поиска

Корпус: 2570 документов MDN на русском (`data/corpus/mdn-ru.jsonl`).

Файл сгенерирован на этапе лексического baseline; команда запуска — в README.

## Запрос: «как узнать длину массива в javascript»

**bm25**

1. 14.6495 — Массивы  
   https://developer.mozilla.org/ru/docs/Learn_web_development/Core/Scripting/Arrays
2. 12.4906 — TypeError: can't delete non-configurable array element(Тип ошибки:не удаётся удалить настраиваемый элемент массива)  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Errors/Non_configurable_array_element
3. 12.3169 — Упорядоченные наборы данных  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Guide/Indexed_collections

**tfidf**

1. 0.2468 — Массив  
   https://developer.mozilla.org/ru/docs/Glossary/Array
2. 0.2342 — TypedArray.prototype.set()  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/TypedArray/set
3. 0.2218 — Array.length  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/Array/length

## Запрос: «центрировать блок по горизонтали css»

**bm25**

1. 14.1419 — box-shadow  
   https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/box-shadow
2. 13.7449 — margin  
   https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/margin
3. 13.0104 — text-indent  
   https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/text-indent

**tfidf**

1. 0.1806 — margin  
   https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/margin
2. 0.1491 — text-indent  
   https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/text-indent
3. 0.1446 — Блок (CSS)  
   https://developer.mozilla.org/ru/docs/Glossary/Block/CSS

## Запрос: «отправить http запрос из браузера»

**bm25**

1. 14.9175 — Expect  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Headers/Expect
2. 14.5555 — PUT  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Methods/PUT
3. 14.4745 — Коды состояния ответа HTTP  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status

**tfidf**

1. 0.2712 — 100 Continue  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status/100
2. 0.2703 — PUT  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Methods/PUT
3. 0.2602 — GET  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Methods/GET

## Запрос: «что означает код ответа 404»

**bm25**

1. 17.1134 — 404 Not Found  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status/404
2. 12.4841 — Использование Fetch  
   https://developer.mozilla.org/ru/docs/Web/API/Fetch_API/Using_Fetch
3. 11.4314 — Что такое веб-сервер  
   https://developer.mozilla.org/ru/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_web_server

**tfidf**

1. 0.3810 — 404 Not Found  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status/404
2. 0.1585 — DELETE  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Methods/DELETE
3. 0.1488 — 202 Accepted  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Status/202

## Запрос: «как отменить всплытие события»

**bm25**

1. 20.4410 — focusout  
   https://developer.mozilla.org/ru/docs/Web/API/Element/focusout_event
2. 17.6993 — Document: DOMContentLoaded event  
   https://developer.mozilla.org/ru/docs/Web/API/Document/DOMContentLoaded_event
3. 16.7410 — EventTarget: метод addEventListener()  
   https://developer.mozilla.org/ru/docs/Web/API/EventTarget/addEventListener

**tfidf**

1. 0.3878 — Event: свойство target  
   https://developer.mozilla.org/ru/docs/Web/API/Event/target
2. 0.3585 — focusout  
   https://developer.mozilla.org/ru/docs/Web/API/Element/focusout_event
3. 0.3499 — Event.bubbles  
   https://developer.mozilla.org/ru/docs/Web/API/Event/bubbles

## Запрос: «асинхронная функция и ожидание результата»

**bm25**

1. 17.4618 — Promise  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/Promise
2. 14.7798 — Синхронные и асинхронные запросы  
   https://developer.mozilla.org/ru/docs/Web/API/XMLHttpRequest_API/Synchronous_and_Asynchronous_Requests
3. 13.1469 — Делаем асинхронное программирование более простым с async и await  
   https://developer.mozilla.org/ru/docs/Learn_web_development/Extensions/Async_JS/Promises

**tfidf**

1. 0.3104 — Асинхронный  
   https://developer.mozilla.org/ru/docs/Glossary/Asynchronous
2. 0.1944 — Promise  
   https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/Promise
3. 0.1836 — Expect  
   https://developer.mozilla.org/ru/docs/Web/HTTP/Reference/Headers/Expect

