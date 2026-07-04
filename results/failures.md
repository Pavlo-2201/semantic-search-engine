# Разбор провальных запросов

Корпус: 2570 документов. Провал — размеченной страницы нет в первых 10 результатах.

## dev (36 запросов)

| поиск | на первом месте | в top-10 | не нашёл |
|---|---|---|---|
| bm25 | 5 | 16 | 20 |
| tfidf | 5 | 12 | 24 |
| dense:lsa-300 | 4 | 22 | 14 |
| dense:word2vec-200 | 4 | 17 | 19 |
| dense:rubert-tiny2 | 3 | 11 | 25 |

### Провалились у всех способов: 8

- «дождаться выполнения нескольких асинхронных операций сразу» — ожидалось: Web/JavaScript/Reference/Global_Objects/Promise/all, Web/JavaScript/Reference/Global_Objects/Promise/allSettled
  - bm25: не найдено, на первом месте «Введение в асинхронный JavaScript»
  - tfidf: не найдено, на первом месте «Асинхронный»
  - dense:lsa-300: не найдено, на первом месте «Использование промисов»
  - dense:word2vec-200: не найдено, на первом месте «Использование промисов»
  - dense:rubert-tiny2: не найдено, на первом месте «Использование промисов»
- «как перехватить ошибку и не уронить программу» — ожидалось: Web/JavaScript/Reference/Statements/try...catch
  - bm25: не найдено, на первом месте «500 Internal Server Error»
  - tfidf: не найдено, на первом месте «WebGLProgram»
  - dense:lsa-300: не найдено, на первом месте «WebGLProgram»
  - dense:word2vec-200: не найдено, на первом месте «Error»
  - dense:rubert-tiny2: не найдено, на первом месте «Что пошло не так? Устранение ошибок JavaScript»
- «подписаться на нажатие кнопки» — ожидалось: Web/API/EventTarget/addEventListener
  - bm25: не найдено, на первом месте «MouseEvent.button»
  - tfidf: не найдено, на первом месте «MouseEvent.button»
  - dense:lsa-300: не найдено, на первом месте «MouseEvent.button»
  - dense:word2vec-200: не найдено, на первом месте «MouseEvent.button»
  - dense:rubert-tiny2: не найдено, на первом месте «<input type="button">»
- «как сделать запрос к серверу из javascript» — ожидалось: Web/API/Fetch_API/Using_Fetch, Web/API/XMLHttpRequest_API/Using_XMLHttpRequest
  - bm25: не найдено, на первом месте «Как настроить локальный сервер для тестирования?»
  - tfidf: не найдено, на первом месте «Прокси сервер»
  - dense:lsa-300: не найдено, на первом месте «OPTIONS»
  - dense:word2vec-200: не найдено, на первом месте «Коды состояния ответа HTTP»
  - dense:rubert-tiny2: не найдено, на первом месте «CORS»
- «запретить всплытие события к родителю» — ожидалось: Web/API/Event/stopPropagation, Web/API/Event/stopImmediatePropagation
  - bm25: не найдено, на первом месте «Event: свойство target»
  - tfidf: не найдено, на первом месте «Event: свойство target»
  - dense:lsa-300: не найдено, на первом месте «Event: свойство target»
  - dense:word2vec-200: не найдено, на первом месте «Event»
  - dense:rubert-tiny2: не найдено, на первом месте «Event.bubbles»
- «плавная покадровая анимация в браузере» — ожидалось: Web/API/Window/requestAnimationFrame
  - bm25: не найдено, на первом месте «Производительность анимации и частота кадров»
  - tfidf: не найдено, на первом месте «Частота кадров (FPS)»
  - dense:lsa-300: не найдено, на первом месте «animation-delay»
  - dense:word2vec-200: не найдено, на первом месте «Использование CSS-анимации»
  - dense:rubert-tiny2: не найдено, на первом месте «description»
- «адрес страницы изменился навсегда» — ожидалось: Web/HTTP/Reference/Status/301
  - bm25: не найдено, на первом месте «404 Not Found»
  - tfidf: не найдено, на первом месте «404 Not Found»
  - dense:lsa-300: не найдено, на первом месте «IP-адрес»
  - dense:word2vec-200: не найдено, на первом месте «URL»
  - dense:rubert-tiny2: не найдено, на первом месте «Пересчёт (Reflow)»
- «ошибка при обращении к другому домену из браузера» — ожидалось: Web/HTTP/Guides/CORS
  - bm25: не найдено, на первом месте «HTTP»
  - tfidf: не найдено, на первом месте «Доменное имя»
  - dense:lsa-300: не найдено, на первом месте «Error: Permission denied to access property "x"»
  - dense:word2vec-200: не найдено, на первом месте «Referer»
  - dense:rubert-tiny2: не найдено, на первом месте «FileReader.error»

### Нашёл только лексический поиск: 1

- «как оставить в массиве только подходящие элементы» — ожидалось: Web/JavaScript/Reference/Global_Objects/Array/filter
  - bm25: ранг 10, на первом месте «Array.prototype.concat()»
  - tfidf: не найдено, на первом месте «Array.prototype.concat()»
  - dense:lsa-300: не найдено, на первом месте «Array.prototype.reverse()»
  - dense:word2vec-200: не найдено, на первом месте «Array»
  - dense:rubert-tiny2: не найдено, на первом месте «Смежные селекторы»

### Нашёл только векторный поиск: 11

- «проверить есть ли значение в массиве» — ожидалось: Web/JavaScript/Reference/Global_Objects/Array/includes, Web/JavaScript/Reference/Global_Objects/Array/indexOf
  - bm25: не найдено, на первом месте «in»
  - tfidf: не найдено, на первом месте «Массив»
  - dense:lsa-300: не найдено, на первом месте «TypedArray.prototype.set()»
  - dense:word2vec-200: не найдено, на первом месте «TypedArray.prototype.set()»
  - dense:rubert-tiny2: ранг 2, на первом месте «Error: Permission denied to access property "x"»
- «заменить часть строки на другую» — ожидалось: Web/JavaScript/Reference/Global_Objects/String/replace, Web/JavaScript/Reference/Global_Objects/String/replaceAll
  - bm25: не найдено, на первом месте «String.prototype.substring()»
  - tfidf: не найдено, на первом месте «String.prototype.substring()»
  - dense:lsa-300: не найдено, на первом месте «VRStageParameters: свойство sittingToStandingTransform»
  - dense:word2vec-200: ранг 3, на первом месте «Node.replaceChild»
  - dense:rubert-tiny2: ранг 3, на первом месте «SyntaxError: string literal contains an unescaped line break»
- «как написать асинхронную функцию» — ожидалось: Web/JavaScript/Reference/Statements/async_function, Web/JavaScript/Reference/Operators/await
  - bm25: не найдено, на первом месте «JavaScript APIs»
  - tfidf: не найдено, на первом месте «Асинхронный»
  - dense:lsa-300: ранг 5, на первом месте «Делаем асинхронное программирование более простым с async и await»
  - dense:word2vec-200: ранг 4, на первом месте «Асинхронные скрипты для asm.js»
  - dense:rubert-tiny2: не найдено, на первом месте «async function expression»
- «округлить число до двух знаков после запятой» — ожидалось: Web/JavaScript/Reference/Global_Objects/Number/toFixed
  - bm25: не найдено, на первом месте «Number.prototype.toExponential()»
  - tfidf: не найдено, на первом месте «Math.round()»
  - dense:lsa-300: ранг 9, на первом месте «Number.prototype.toExponential()»
  - dense:word2vec-200: ранг 3, на первом месте «Number.prototype.toExponential()»
  - dense:rubert-tiny2: не найдено, на первом месте «Числа и даты»
- «найти элемент на странице по селектору» — ожидалось: Web/API/Document/querySelector, Web/API/Element/querySelector
  - bm25: не найдено, на первом месте «Селекторы CSS»
  - tfidf: не найдено, на первом месте «Селекторы по ID»
  - dense:lsa-300: не найдено, на первом месте «Селектор дочерних элементов»
  - dense:word2vec-200: не найдено, на первом месте «Селекторы CSS»
  - dense:rubert-tiny2: ранг 5, на первом месте «Псевдоэлемент»
- «добавить класс элементу из кода» — ожидалось: Web/API/Element/classList
  - bm25: не найдено, на первом месте «Начало работы с CSS»
  - tfidf: не найдено, на первом месте «Селекторы по классу»
  - dense:lsa-300: не найдено, на первом месте «Селекторы по классу»
  - dense:word2vec-200: не найдено, на первом месте «constructor»
  - dense:rubert-tiny2: ранг 9, на первом месте «Блок (скриптинг)»
- «страница не найдена какой код ответа» — ожидалось: Web/HTTP/Reference/Status/404
  - bm25: не найдено, на первом месте «Cache.match()»
  - tfidf: не найдено, на первом месте «DELETE»
  - dense:lsa-300: ранг 9, на первом месте «303 See Other»
  - dense:word2vec-200: не найдено, на первом месте «Коды состояния ответа HTTP»
  - dense:rubert-tiny2: не найдено, на первом месте «Cache.match()»
- «сервер отказал в доступе к ресурсу» — ожидалось: Web/HTTP/Reference/Status/403, Web/HTTP/Reference/Status/401
  - bm25: не найдено, на первом месте «CDN»
  - tfidf: не найдено, на первом месте «CDN»
  - dense:lsa-300: ранг 5, на первом месте «CDN»
  - dense:word2vec-200: не найдено, на первом месте «Прокси сервер»
  - dense:rubert-tiny2: ранг 1, на первом месте «403 Forbidden»
- «как указать тип содержимого в ответе» — ожидалось: Web/HTTP/Reference/Headers/Content-Type
  - bm25: не найдено, на первом месте «XMLHttpRequest.response»
  - tfidf: не найдено, на первом месте «HEAD»
  - dense:lsa-300: не найдено, на первом месте «422 Unprocessable Entity»
  - dense:word2vec-200: ранг 8, на первом месте «Content-Disposition»
  - dense:rubert-tiny2: не найдено, на первом месте «a»
- «отправить данные формы на сервер» — ожидалось: Web/HTTP/Reference/Methods/POST, Web/API/FormData
  - bm25: не найдено, на первом месте «Отправка данных формы»
  - tfidf: не найдено, на первом месте «PUT»
  - dense:lsa-300: ранг 10, на первом месте «Отправка данных формы»
  - dense:word2vec-200: не найдено, на первом месте «Отправка данных формы»
  - dense:rubert-tiny2: не найдено, на первом месте «Server-sent events»
- «как разложить блоки по сетке» — ожидалось: Web/CSS/Guides/Grid_layout/Basic_concepts, Web/CSS/Reference/Properties/grid-template-columns
  - bm25: не найдено, на первом месте «Выравнивание блоков в CSS разметке Grid»
  - tfidf: не найдено, на первом месте «Grid Column»
  - dense:lsa-300: ранг 6, на первом месте «CSS Grid Layout»
  - dense:word2vec-200: ранг 6, на первом месте «Grid Column»
  - dense:rubert-tiny2: не найдено, на первом месте «align-items»

## test (36 запросов)

| поиск | на первом месте | в top-10 | не нашёл |
|---|---|---|---|
| bm25 | 4 | 21 | 15 |
| tfidf | 4 | 19 | 17 |
| dense:lsa-300 | 4 | 23 | 13 |
| dense:word2vec-200 | 4 | 24 | 12 |
| dense:rubert-tiny2 | 4 | 14 | 22 |

### Провалились у всех способов: 4

- «убрать элемент со страницы средствами стилей» — ожидалось: Web/CSS/Reference/Properties/display, Web/CSS/Reference/Properties/visibility
  - bm25: не найдено, на первом месте «<li>»
  - tfidf: не найдено, на первом месте «<acronym>»
  - dense:lsa-300: не найдено, на первом месте «style»
  - dense:word2vec-200: не найдено, на первом месте «style»
  - dense:rubert-tiny2: не найдено, на первом месте «Псевдоэлемент»
- «плавное изменение цвета при наведении мыши» — ожидалось: Web/CSS/Reference/Properties/transition
  - bm25: не найдено, на первом месте «Псевдоклассы»
  - tfidf: не найдено, на первом месте «Псевдоклассы»
  - dense:lsa-300: не найдено, на первом месте «Псевдоклассы»
  - dense:word2vec-200: не найдено, на первом месте «backface-visibility»
  - dense:rubert-tiny2: не найдено, на первом месте «<filter-function>»
- «узнать где находится пользователь» — ожидалось: Web/API/Geolocation/getCurrentPosition, Web/API/Geolocation
  - bm25: не найдено, на первом месте «Прокси сервер»
  - tfidf: не найдено, на первом месте «Браузер»
  - dense:lsa-300: не найдено, на первом месте «:read-only»
  - dense:word2vec-200: не найдено, на первом месте «Стилизация ссылок»
  - dense:rubert-tiny2: не найдено, на первом месте «Использование геолокации»
- «загрузить файл на сервер из формы» — ожидалось: Web/API/FormData
  - bm25: не найдено, на первом месте «Отправка данных формы»
  - tfidf: не найдено, на первом месте «Использование Объектов FormData»
  - dense:lsa-300: не найдено, на первом месте «Отправка данных формы»
  - dense:word2vec-200: не найдено, на первом месте «Как настроить локальный сервер для тестирования?»
  - dense:rubert-tiny2: не найдено, на первом месте «File.name»

### Нашёл только лексический поиск: 2

- «закрепить блок на месте при прокрутке страницы» — ожидалось: Web/CSS/Reference/Properties/position
  - bm25: ранг 2, на первом месте «Переполнение содержимого»
  - tfidf: не найдено, на первом месте «overflow-block»
  - dense:lsa-300: не найдено, на первом месте «overflow»
  - dense:word2vec-200: не найдено, на первом месте «overscroll-behavior»
  - dense:rubert-tiny2: не найдено, на первом месте «Выравнивание блоков в разметке Flexbox»
- «каким методом запрашивают данные с сервера» — ожидалось: Web/HTTP/Reference/Methods/GET
  - bm25: не найдено, на первом месте «Методы HTTP запроса»
  - tfidf: ранг 6, на первом месте «Range»
  - dense:lsa-300: не найдено, на первом месте «CONNECT»
  - dense:word2vec-200: не найдено, на первом месте «CONNECT»
  - dense:rubert-tiny2: не найдено, на первом месте «CORS»

### Нашёл только векторный поиск: 7

- «как узнать длину строки» — ожидалось: Web/JavaScript/Reference/Global_Objects/String/length
  - bm25: не найдено, на первом месте «Полезные методы для строк»
  - tfidf: не найдено, на первом месте «String.prototype.padStart()»
  - dense:lsa-300: ранг 9, на первом месте «String.prototype.padStart()»
  - dense:word2vec-200: не найдено, на первом месте «String.prototype.padStart()»
  - dense:rubert-tiny2: не найдено, на первом месте «CanvasRenderingContext2D.lineCap»
- «перебрать все элементы массива по очереди» — ожидалось: Web/JavaScript/Reference/Statements/for...of, Web/JavaScript/Reference/Global_Objects/Array/forEach
  - bm25: не найдено, на первом месте «NodeList»
  - tfidf: не найдено, на первом месте «NodeList»
  - dense:lsa-300: не найдено, на первом месте «Array.prototype.reverse()»
  - dense:word2vec-200: ранг 2, на первом месте «Array.prototype.concat()»
  - dense:rubert-tiny2: не найдено, на первом месте «Array.prototype.join()»
- «преобразовать текст в число» — ожидалось: Web/JavaScript/Reference/Global_Objects/parseInt, Web/JavaScript/Reference/Global_Objects/parseFloat
  - bm25: не найдено, на первом месте «Math.clz32()»
  - tfidf: не найдено, на первом месте «String.prototype.toUpperCase()»
  - dense:lsa-300: не найдено, на первом месте «Math.clz32()»
  - dense:word2vec-200: ранг 1, на первом месте «parseInt()»
  - dense:rubert-tiny2: не найдено, на первом месте «Шаблонные строки»
- «что делать если содержимое не влезает в блок» — ожидалось: Web/CSS/Reference/Properties/overflow
  - bm25: не найдено, на первом месте «Переполнение содержимого»
  - tfidf: не найдено, на первом месте «Блок (скриптинг)»
  - dense:lsa-300: ранг 8, на первом месте «Блок (скриптинг)»
  - dense:word2vec-200: не найдено, на первом месте «Блок (скриптинг)»
  - dense:rubert-tiny2: не найдено, на первом месте «Array.prototype.splice()»
- «подключить собственный шрифт на сайт» — ожидалось: Web/CSS/Reference/At-rules/@font-face
  - bm25: не найдено, на первом месте «Что такое веб-сервер»
  - tfidf: не найдено, на первом месте «Gamepad.connected»
  - dense:lsa-300: ранг 9, на первом месте «font-style»
  - dense:word2vec-200: ранг 2, на первом месте «Веб-шрифты»
  - dense:rubert-tiny2: ранг 6, на первом месте «Встраиваемый скрипт»
- «выровнять текст по центру» — ожидалось: Web/CSS/Reference/Properties/text-align
  - bm25: не найдено, на первом месте «<col>: элемент столбца таблицы»
  - tfidf: не найдено, на первом месте «<col>: элемент столбца таблицы»
  - dense:lsa-300: не найдено, на первом месте «Гипертекст»
  - dense:word2vec-200: не найдено, на первом месте «CanvasRenderingContext2D.textAlign»
  - dense:rubert-tiny2: ранг 2, на первом месте «text-anchor»
- «чтобы сайт работал без интернета» — ожидалось: Web/API/Service_Worker_API/Using_Service_Workers, Web/API/Service_Worker_API
  - bm25: не найдено, на первом месте «Распространённые вопросы»
  - tfidf: не найдено, на первом месте «Интернет-провайдер»
  - dense:lsa-300: не найдено, на первом месте «Распространённые вопросы»
  - dense:word2vec-200: не найдено, на первом месте «Интернет-провайдер»
  - dense:rubert-tiny2: ранг 1, на первом месте «Service Worker API»

