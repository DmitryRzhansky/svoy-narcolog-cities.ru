# AGENTS.md — правила frontend-разработки

Твоя задача — писать чистый, модульный, поддерживаемый frontend-код на HTML, CSS и JavaScript.

Основные принципы:

* семантический HTML;
* чистый CSS без SCSS и других препроцессоров;
* vanilla JavaScript без лишних библиотек;
* BEM для именования CSS-классов;
* mobile-first адаптив;
* модульность компонентов и файлов;
* DRY без преждевременного выноса всего подряд;
* KISS без переусложнения;
* доступность;
* производительность;
* читаемость;
* поддерживаемость другим разработчиком;
* шрифты и иконки хранятся локально в проекте.

Главное правило:
не превращай frontend в один огромный `index.html`, `style.css` и `script.js`.

Код должен быть простым, но не примитивным.
Модульным, но не раздробленным на сотню файлов без причины.
Расширяемым, но без лишних абстракций.

============================================================

1. ОБЩАЯ СТРУКТУРА ПРОЕКТА
   ============================================================

Для обычного многостраничного сайта используй понятную структуру:

```text
project/
  index.html

  pages/
    services.html
    contacts.html
    about.html

  assets/
    css/
      base/
        reset.css
        root.css
        typography.css
        base.css

      layout/
        container.css
        section.css
        grid.css

      components/
        header.css
        footer.css
        button.css
        card.css
        form.css
        modal.css

      pages/
        home.css
        services.css
        contacts.css

      utilities/
        visually-hidden.css
        helpers.css

      main.css

    js/
      main.js
      modules/
        menu.js
        modal.js
        slider.js
        form.js

    images/
    icons/
    fonts/
```

Для маленького лендинга структура может быть проще:

```text
project/
  index.html
  assets/
    css/
      base.css
      components.css
      main.css
    js/
      main.js
    images/
    icons/
    fonts/
```

Не дроби проект формально ради красивого дерева директорий.
Если файл содержит 10 строк и используется только в одном месте, отдельный модуль может быть бессмысленным.

Недопустимо без причины:

```text
project/
  index.html
  style.css
  script.js
```

если в этих трёх файлах уже находится весь крупный сайт с десятками компонентов и страниц.

============================================================
2. HTML
=======

Пиши семантическую HTML-разметку.

Используй элементы по назначению:

* `header`;
* `nav`;
* `main`;
* `section`;
* `article`;
* `aside`;
* `footer`;
* `h1`–`h6`;
* `ul`, `ol`, `li`;
* `button`;
* `a`;
* `form`;
* `label`;
* `input`;
* `textarea`;
* `figure`, `figcaption` при необходимости.

Не используй `div` и `span`, если существует подходящий семантический элемент.

На странице должен быть один основной `h1`, описывающий её главный смысл.

Заголовки должны иметь логическую иерархию:

```text
h1
  h2
    h3
    h3
  h2
```

Не перескакивай хаотично с `h2` на `h5` ради размера текста.
Размеры задаются CSS, семантика задаётся HTML.

Ссылки должны быть ссылками:

```html
<a class="button button--primary" href="/services/">
  Подробнее об услугах
</a>
```

Кнопки действий должны быть кнопками:

```html
<button class="menu-toggle" type="button" data-menu-toggle>
  Открыть меню
</button>
```

Не делай кликабельные `div`.

Плохо:

```html
<div class="button">Отправить</div>
```

Хорошо:

```html
<button class="button button--primary" type="submit">
  Отправить
</button>
```

============================================================
3. CSS — ОБЩИЕ ПРАВИЛА
======================

Используй обычный CSS.

Не используй SCSS, Sass, Less, Stylus и другие CSS-препроцессоры, если пользователь явно их не запросил.

CSS должен быть модульным и разделённым по ответственности.

Рекомендуемые группы:

* `base` — reset, root, типографика, глобовые правила;
* `layout` — контейнеры, секции, сетки;
* `components` — самостоятельные UI-компоненты;
* `pages` — стили, уникальные для конкретной страницы;
* `utilities` — маленькие служебные классы.

`main.css` должен быть понятной точкой подключения модулей, а не свалкой всего CSS проекта.

При использовании нескольких CSS-файлов подключай их в контролируемом порядке.

Пример:

```css
@import url("./base/reset.css");
@import url("./base/root.css");
@import url("./base/typography.css");
@import url("./base/base.css");

@import url("./layout/container.css");
@import url("./layout/section.css");
@import url("./layout/grid.css");

@import url("./components/header.css");
@import url("./components/button.css");
@import url("./components/card.css");

@import url("./utilities/visually-hidden.css");
```

Если проекту не нужна такая детализация, допустимо подключать несколько CSS-файлов напрямую через `<link>`.

Не создавай отдельный CSS-файл для каждого микроскопического элемента без причины.

============================================================
4. CSS CUSTOM PROPERTIES И DESIGN TOKENS
========================================

Повторяющиеся системные значения выноси в CSS custom properties.

Пример:

```css
:root {
  --color-primary: #18a96d;
  --color-primary-hover: #138a5a;
  --color-text: #111111;
  --color-muted: #666666;
  --color-background: #ffffff;
  --color-surface: #f6f7f8;

  --font-main: "Montserrat", Arial, sans-serif;

  --container-width: 75rem;

  --radius-sm: 0.5rem;
  --radius-md: 0.75rem;
  --radius-lg: 1.25rem;

  --transition-base: 0.2s ease;
}
```

Выноси в глобальные токены только значения, которые действительно образуют систему:

* основные цвета;
* типографику;
* контейнер;
* повторяющиеся радиусы;
* системные интервалы;
* стандартные переходы;
* системные z-index уровни, если они реально нужны.

Не превращай `:root` в склад каждой случайной цифры проекта.
Локальное значение одного компонента может оставаться внутри его CSS-файла.

============================================================
5. BEM
======

Используй BEM для CSS-классов, если нет объективной причины применять другую методологию.

Формат:

```text
.block
.block__element
.block--modifier
.block__element--modifier
```

Примеры:

```text
.header
.header__logo
.header__nav
.header__nav-link
.header__nav-link--active

.button
.button--primary
.button--secondary

.service-card
.service-card__icon
.service-card__title
.service-card__text
.service-card--featured
```

Block — самостоятельный компонент.

Хорошо:

```text
.header
.footer
.button
.hero
.faq
.modal
.service-card
.contact-form
```

Element — часть блока, не имеющая самостоятельного смысла вне него.

Хорошо:

```text
.header__logo
.header__nav
.hero__title
.service-card__title
.contact-form__field
.modal__close
```

Modifier — состояние или вариант блока/элемента.

Хорошо:

```text
.button--primary
.button--large
.service-card--featured
.header__nav-link--active
.modal--open
```

Не создавай длинные цепочки BEM.

Плохо:

```text
.header__nav__list__item__link
```

Хорошо:

```text
.header__nav-list
.header__nav-item
.header__nav-link
```

Не используй случайные классы:

```text
.block1
.text2
.green
.big
.left
.item123
.new-style
.final-fix
```

Имена должны отражать смысл компонента, а не его текущий внешний вид.

============================================================
6. CSS-СЕЛЕКТОРЫ И СПЕЦИФИЧНОСТЬ
================================

Старайся стилизовать компоненты через классы.

Не используй ID для стилизации без необходимости.

Плохо:

```css
#main-button {}
```

Хорошо:

```css
.button {}
```

Не повторяй DOM-структуру в селекторах.

Плохо:

```css
.page .section .container .services .service-card .service-card__title {}
```

Хорошо:

```css
.service-card__title {}
```

Не создавай глубокую вложенную зависимость компонентов друг от друга.

Избегай `!important`.
Использовать его можно только в исключительных случаях, когда причина понятна и другого нормального решения нет.

Не используй inline-стили без прямой необходимости.

Плохо:

```html
<div style="padding: 20px; color: red;"></div>
```

Хорошо:

```html
<div class="alert alert--error"></div>
```

============================================================
7. МОДУЛЬНОСТЬ КОМПОНЕНТОВ
==========================

Компонент должен быть максимально самостоятельным.

Пример:

```text
HTML:
.service-card
.service-card__icon
.service-card__title
.service-card__text
.service-card__link

CSS:
assets/css/components/service-card.css

JS, если требуется:
assets/js/modules/service-card.js
```

Не копируй один и тот же компонент на разных страницах с разными случайными классами.

Если карточка концептуально одна и та же, используй общий BEM-блок и модификаторы.

Плохо:

```text
.home-card
.services-card
.about-card
```

если это один и тот же компонент с незначительными визуальными отличиями.

Лучше:

```text
.card
.card--service
.card--compact
```

Но не объединяй разные по смыслу компоненты только потому, что они визуально похожи.

============================================================
8. DRY
======

Не дублируй большие одинаковые блоки HTML, CSS и JS.

Если один паттерн повторяется несколько раз и действительно имеет одну семантику, вынеси его в общий компонент или общую функцию.

Не применяй DRY фанатично.

Два визуально похожих блока могут быть разными компонентами, если у них разная ответственность или поведение.

Не создавай общий класс уровня `.thing` только ради того, чтобы убрать три одинаковые CSS-декларации.

============================================================
9. KISS
=======

Выбирай самое простое решение, которое полностью закрывает задачу.

Не добавляй без необходимости:

* React;
* Vue;
* Angular;
* jQuery;
* Tailwind;
* Bootstrap;
* сборщики;
* TypeScript;
* CSS-in-JS;
* сложные state-менеджеры;
* сторонние UI-фреймворки.

Если сайт можно нормально сделать на HTML + CSS + vanilla JS, используй HTML + CSS + vanilla JS.

============================================================
10. RESPONSIVE / MOBILE-FIRST
=============================

Верстка должна быть mobile-first.

Сначала базовые стили для мобильных устройств, затем расширяй интерфейс через `min-width` media queries.

Проверяй как минимум ширины:

* 320px;
* 375px;
* 430px;
* 768px;
* 1024px;
* 1280px;
* 1440px.

Не допускай горизонтальный скролл, если он не предусмотрен дизайном.

Не фиксируй большие ширины элементов через `px`, если это ломает адаптивность.

Плохо:

```css
.card {
  width: 600px;
}
```

Хорошо:

```css
.card {
  width: min(100%, 37.5rem);
}
```

Используй современные CSS-возможности:

* Grid;
* Flexbox;
* `gap`;
* `min()`;
* `max()`;
* `clamp()`;
* `minmax()`;
* `aspect-ratio`;
* `object-fit`;
* container queries, когда они реально дают пользу.

Пример:

```css
.services-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 48rem) {
  .services-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 64rem) {
  .services-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
```

Не создавай десятки случайных breakpoints под отдельные элементы.

============================================================
11. JAVASCRIPT
==============

JavaScript должен быть модульным.

Рекомендуемая структура:

```text
assets/js/
  main.js
  modules/
    menu.js
    modal.js
    slider.js
    form.js
```

Используй ES modules.

Пример:

```js
import { initMenu } from "./modules/menu.js";
import { initModal } from "./modules/modal.js";

function initApp() {
  initMenu();
  initModal();
}

document.addEventListener("DOMContentLoaded", initApp);
```

Каждый модуль должен отвечать за одну понятную задачу.

Не загрязняй глобальную область видимости.

Не используй inline JS.

Плохо:

```html
<button onclick="openMenu()">Меню</button>
```

Хорошо:

```html
<button type="button" data-menu-toggle>
  Меню
</button>
```

```js
const menuToggle = document.querySelector("[data-menu-toggle]");

if (menuToggle) {
  menuToggle.addEventListener("click", openMenu);
}
```

Используй defensive coding.

Плохо:

```js
const modal = document.querySelector("[data-modal]");
modal.classList.add("modal--open");
```

Хорошо:

```js
const modal = document.querySelector("[data-modal]");

if (!modal) {
  return;
}

modal.classList.add("modal--open");
```

Отсутствие компонента на конкретной странице не должно вызывать ошибку в консоли.

Не используй jQuery, если задача нормально решается на vanilla JS.

============================================================
12. JS-ХУКИ
===========

Не завязывай JavaScript на CSS-классы, используемые только для стилизации.

Предпочтительно использовать `data-*` атрибуты.

Хорошо:

```html
<button
  class="header__menu-toggle"
  type="button"
  data-menu-toggle
  aria-label="Открыть меню"
>
</button>
```

```js
const button = document.querySelector("[data-menu-toggle]");
```

Не рекомендуется:

```js
const button = document.querySelector(".header__menu-toggle");
```

если этот класс существует исключительно для CSS.

Состояние компонента можно отражать BEM-модификатором или состоянием через `aria-*`.

Например:

```js
menu.classList.toggle("mobile-menu--open");
button.setAttribute("aria-expanded", String(isOpen));
```

============================================================
13. ACCESSIBILITY
=================

Верстка должна быть доступной.

Обязательно:

* интерактивные элементы имеют видимое `:focus-visible` состояние;
* icon-only кнопки имеют `aria-label`;
* поля форм имеют `label`;
* placeholder не заменяет label;
* декоративные изображения имеют `alt=""`;
* содержательные изображения имеют осмысленный `alt`;
* меню, модалки, табы и другие интерактивные компоненты доступны с клавиатуры;
* нельзя удалять `outline` без качественной замены;
* ARIA используется только там, где нативной HTML-семантики недостаточно;
* анимации учитывают `prefers-reduced-motion`.

Пример:

```css
.button:focus-visible {
  outline: 0.1875rem solid var(--color-primary);
  outline-offset: 0.1875rem;
}
```

Пример visually hidden:

```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}
```

Плохо:

```html
<div role="button">Открыть</div>
```

Хорошо:

```html
<button type="button">Открыть</button>
```

============================================================
14. ИЗОБРАЖЕНИЯ
===============

Для изображений указывай:

* `alt`;
* `width`;
* `height`;
* `loading="lazy"` для изображений ниже первого экрана;
* `decoding="async"`, когда это уместно.

Пример:

```html
<img
  src="/assets/images/example.webp"
  alt="Краткое содержательное описание изображения"
  width="800"
  height="600"
  loading="lazy"
  decoding="async"
>
```

Для главного LCP-изображения не используй `loading="lazy"`.

Для важного hero-изображения при необходимости используй:

```html
<img
  src="/assets/images/hero.webp"
  alt="..."
  width="1600"
  height="900"
  fetchpriority="high"
  decoding="async"
>
```

Декоративное изображение:

```html
<img
  src="/assets/images/decor.svg"
  alt=""
  width="120"
  height="120"
  loading="lazy"
  decoding="async"
>
```

Предпочитай современные форматы:

* WebP;
* AVIF, если поддержка и пайплайн проекта это позволяют;
* SVG для векторной графики и иконок.

Не вставляй важный текст внутрь изображения.

============================================================
15. ЛОКАЛЬНЫЕ ШРИФТЫ
====================

Шрифты должны храниться локально в проекте.

Не подключай Google Fonts, Adobe Fonts и другие внешние CDN, если пользователь явно этого не попросил.

Рекомендуемая структура:

```text
assets/fonts/
  montserrat/
    montserrat-regular.woff2
    montserrat-medium.woff2
    montserrat-semibold.woff2
    montserrat-bold.woff2
```

Используй `.woff2` как основной web-формат.

Подключай только реально используемые начертания.
Не скачивай 9 весов шрифта, если сайт использует только 400, 500 и 700.

Пример:

```css
@font-face {
  font-family: "Montserrat";
  src: url("../../fonts/montserrat/montserrat-regular.woff2") format("woff2");
  font-style: normal;
  font-weight: 400;
  font-display: swap;
}

@font-face {
  font-family: "Montserrat";
  src: url("../../fonts/montserrat/montserrat-semibold.woff2") format("woff2");
  font-style: normal;
  font-weight: 600;
  font-display: swap;
}
```

При добавлении шрифта:

1. скачай файлы локально из официального или надёжного источника;
2. сохрани их в `assets/fonts/`;
3. используй понятные имена файлов;
4. подключи через `@font-face`;
5. обязательно укажи `font-display: swap`;
6. не оставляй внешнюю загрузку этого же шрифта;
7. не добавляй неиспользуемые начертания и форматы.

Никогда не встраивай шрифты в CSS через огромные base64-строки без объективной причины.

============================================================
16. ЛОКАЛЬНЫЕ ИКОНКИ
====================

Иконки должны храниться локально.

Не подключай Font Awesome, Phosphor, Material Icons, Bootstrap Icons и другие библиотеки через CDN.

Если проект использует конкретный набор иконок:

1. скачай только нужные SVG-файлы;
2. сохрани их в `assets/icons/`;
3. используй понятные имена;
4. не тяни целую библиотеку ради нескольких иконок.

Пример:

```text
assets/icons/
  arrow-right.svg
  phone.svg
  mail.svg
  menu.svg
  close.svg
  check.svg
```

Имена файлов:

Хорошо:

```text
arrow-right.svg
chevron-down.svg
phone.svg
map-pin.svg
```

Плохо:

```text
icon1.svg
new.svg
img123.svg
final-icon.svg
```

Для простых декоративных иконок допустим inline SVG, если это улучшает управление цветом и состояниями.

Если SVG вставлен через `<img>`, декоративная иконка должна иметь `alt=""`.

Если icon-only кнопка содержит SVG, кнопка должна иметь `aria-label`, а SVG обычно `aria-hidden="true"`.

Пример:

```html
<button
  class="modal__close"
  type="button"
  aria-label="Закрыть окно"
  data-modal-close
>
  <img
    src="/assets/icons/close.svg"
    alt=""
    width="24"
    height="24"
    aria-hidden="true"
  >
</button>
```

============================================================
17. ФОРМЫ В HTML
================

Каждое поле должно иметь `label`.

Плейсхолдер не заменяет label.

Используй корректные типы полей:

* `text`;
* `email`;
* `tel`;
* `number`;
* `checkbox`;
* `radio`;
* `password`;
* `file`.

Добавляй подходящие `autocomplete` значения.

Пример:

```html
<form class="contact-form" action="#" method="post">
  <div class="contact-form__field">
    <label class="contact-form__label" for="phone">
      Телефон
    </label>

    <input
      class="contact-form__input"
      id="phone"
      name="phone"
      type="tel"
      autocomplete="tel"
      required
    >
  </div>

  <button class="contact-form__submit button button--primary" type="submit">
    Отправить
  </button>
</form>
```

Если форма пока не подключена к реальной отправке данных, не имитируй успешную отправку.
Оставь корректную разметку и явно отделяй демонстрационное поведение от реальной отправки.

============================================================
18. SEO И ТЕХНИЧЕСКАЯ РАЗМЕТКА
==============================

Каждая полноценная HTML-страница должна иметь минимум:

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Заголовок страницы</title>
<meta name="description" content="Описание страницы">
```

При необходимости добавляй:

* canonical;
* Open Graph;
* favicon;
* structured data.

Не создавай пустые заголовки ради дизайна.

Не прячь важный SEO-текст в изображениях.

Анкор ссылки должен объяснять назначение ссылки.

Плохо:

```html
<a href="/services/">Подробнее</a>
```

Лучше:

```html
<a href="/services/">Подробнее об услугах</a>
```

============================================================
19. PERFORMANCE
===============

Frontend должен быть быстрым без ритуальной микрооптимизации всего подряд.

Требования:

* не подключай тяжёлые библиотеки ради простых задач;
* используй локальные шрифты;
* подключай только реально используемые начертания;
* используй локальные SVG-иконки;
* не подключай целую иконочную библиотеку ради нескольких SVG;
* оптимизируй изображения;
* используй `loading="lazy"` ниже первого экрана;
* не используй lazy loading для LCP-изображения;
* задавай `width` и `height` изображениям для уменьшения CLS;
* JavaScript подключай как ES module или с `defer`;
* не блокируй первый рендер тяжёлыми скриптами;
* не делай тяжёлую JS-логику для того, что решается CSS;
* не злоупотребляй preload;
* не добавляй лишние preconnect;
* удаляй реально неиспользуемый CSS и JS после проверки.

Пример подключения CSS:

```html
<link rel="stylesheet" href="/assets/css/main.css">
```

Пример подключения JS:

```html
<script type="module" src="/assets/js/main.js"></script>
```

============================================================
20. АНИМАЦИИ
============

Анимации должны помогать интерфейсу, а не мешать ему.

Не добавляй анимацию каждому элементу просто потому, что CSS это позволяет.

Учитывай `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Не используй тяжёлый JavaScript для простых hover/fade/transform эффектов, которые нормально реализуются CSS.

============================================================
21. ИМЕНОВАНИЕ ФАЙЛОВ
=====================

Файлы должны называться понятно, на английском и единообразно.

Для CSS, JS, изображений, иконок и шрифтов предпочитай `kebab-case`.

Хорошо:

```text
service-card.css
mobile-menu.css
contact-form.css
mobile-menu.js
contact-form.js
hero-cleaning.webp
arrow-right.svg
montserrat-semibold.woff2
```

Плохо:

```text
style1.css
new.css
final-final.css
script-final.js
img123.png
правка.css
icon-new2.svg
```

Имена функций и переменных JavaScript должны отражать назначение.

Плохо:

```js
function doIt() {}
const data = {};
```

Хорошо:

```js
function openMobileMenu() {}
const menuToggleButton = document.querySelector("[data-menu-toggle]");
```

============================================================
22. КАЧЕСТВО КОДА
=================

Перед выдачей или завершением работы проверь:

* единый стиль форматирования;
* понятные имена;
* отсутствие мёртвого кода;
* отсутствие закомментированных старых кусков без причины;
* отсутствие лишнего дублирования;
* отсутствие неиспользуемых CSS-классов;
* отсутствие неиспользуемых JS-функций и импортов;
* отсутствие ошибок в консоли;
* отсутствие битых путей к изображениям, шрифтам и иконкам;
* отсутствие внешних CDN для шрифтов и иконок;
* отсутствие горизонтального скролла на мобильных;
* корректную работу интерактивных элементов с клавиатуры;
* предсказуемую структуру проекта.

============================================================
23. ЗАПРЕТЫ
===========

Запрещено без прямой необходимости:

* использовать SCSS/Sass/Less вместо обычного CSS;
* складывать весь крупный CSS в один неструктурированный файл;
* складывать весь крупный JS в один файл;
* строить всю страницу на `div` без семантики;
* делать кнопки через `div`;
* делать переходы между страницами через `button`, когда нужен `a`;
* использовать inline CSS;
* использовать inline JS;
* использовать `!important` как основной способ борьбы со специфичностью;
* использовать ID для обычной стилизации;
* создавать селекторы, полностью повторяющие DOM-дерево;
* использовать случайные названия классов;
* завязывать JS на стилистические классы, если можно использовать `data-*`;
* подключать jQuery для простых задач;
* подключать тяжёлые frontend-фреймворки без причины;
* подключать внешние CDN для шрифтов;
* подключать внешние CDN для иконок;
* подключать целую библиотеку иконок ради нескольких SVG;
* использовать изображения без корректного `alt`;
* удалять focus outline без замены;
* создавать горизонтальный скролл на мобильной версии;
* оставлять ошибки в консоли;
* оставлять неиспользуемый CSS и JS;
* копировать стили одного компонента в несколько файлов вместо нормального переиспользования;
* встраивать большие шрифты, SVG или изображения через base64 без необходимости.

============================================================
24. ФОРМАТ ОТВЕТА ПРИ ГЕНЕРАЦИИ КОДА
====================================

Если пользователь просит код, сначала кратко покажи структуру изменяемых или создаваемых файлов.

Затем выдавай код по файлам.

Пример:

```text
/index.html

код

/assets/css/base/root.css

код

/assets/css/components/header.css

код

/assets/css/components/button.css

код

/assets/css/main.css

код

/assets/js/modules/menu.js

код

/assets/js/main.js

код
```

Если пользователь просит полный код, не ограничивайся несколькими фрагментами.

Если изменяешь существующий проект:

* сохраняй текущую рабочую функциональность;
* не меняй структуру без реальной необходимости;
* не переименовывай классы и файлы просто ради вкусовщины;
* явно учитывай существующие компоненты;
* переиспользуй уже существующие BEM-блоки;
* проверяй пути к CSS, JS, изображениям, иконкам и шрифтам;
* не добавляй зависимости без необходимости.

============================================================
25. ЧЕКЛИСТ ПЕРЕД ВЫДАЧЕЙ КОДА
==============================

HTML:

* используется семантическая разметка;
* на странице один основной `h1`;
* иерархия заголовков логична;
* кнопки и ссылки используются по назначению;
* нет кликабельных `div`;
* формы имеют `label`;
* изображения имеют корректный `alt`, `width`, `height`;
* декоративные изображения имеют `alt=""`;
* icon-only кнопки имеют `aria-label`;
* SEO meta-теги заполнены там, где они требуются.

CSS:

* используется обычный CSS, не SCSS;
* CSS разложен по понятным модулям;
* классы названы по BEM;
* нет глубокой специфичности;
* нет бессмысленного `!important`;
* системные значения вынесены в custom properties;
* используется mobile-first;
* нет горизонтального скролла;
* есть `:focus-visible`;
* адаптив проверен на основных ширинах;
* нет неиспользуемых правил.

JavaScript:

* используется vanilla JS;
* код разделён на модули, когда это оправдано;
* нет inline JS;
* нет загрязнения глобальной области;
* JS-хуки используют `data-*`;
* компоненты корректно работают, даже если некоторых из них нет на странице;
* нет ошибок в консоли;
* нет неиспользуемых импортов и функций.

Шрифты и иконки:

* шрифты скачаны локально;
* используются `.woff2`;
* подключены только нужные веса;
* есть `font-display: swap`;
* иконки скачаны локально;
* нет внешних CDN;
* нет целой библиотеки ради нескольких иконок;
* пути к локальным файлам корректны.

Общее:

* решение соответствует DRY, KISS и модульности;
* код не переусложнён;
* структура проекта понятна;
* компоненты можно переиспользовать;
* другой разработчик сможет быстро понять и продолжить проект.