#!/usr/bin/env python3
"""Собирает общую навигацию сайта ProstoPython в статические HTML-страницы.

Что делает скрипт:
  * вставляет шапку с меню и мобильным бургер-меню;
  * вставляет подвал;
  * вставляет боковое меню уроков (Основы / Продвинутый курс);
  * делает хлебные крошки и кнопки «назад / вперёд» между уроками;
  * добавляет крошки и навигацию между темами практикума;
  * подключает к страницам практикума общий style.css, Prism и app.js.

Скрипт идемпотентен: его можно запускать повторно после правки навигации.

Запуск:  python3 tools/build_nav.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BASICS = [
    (1, "Установка VS Code"),
    (2, "Переменные и типы данных"),
    (3, "Условные операторы"),
    (4, "Циклы for и while"),
    (5, "Списки"),
    (6, "Кортежи и множества"),
    (7, "Словари"),
    (8, "Функции"),
    (9, "Работа с файлами"),
    (10, "Обработка исключений"),
    (11, "Модули и импорт"),
]

ADVANCED = [
    (1, "ООП — Классы и объекты"),
    (2, "Работа с API и JSON"),
    (3, "Обработка CSV таблиц"),
    (4, "Визуализация в Matplotlib"),
    (5, "Pandas и Numpy"),
    (6, "SQLite базы данных"),
]

# (файл, полное название, короткое название, число задач)
PRACTICES = [
    ("practice-variables.html", "Переменные и типы данных", "Переменные", 15),
    ("practice-conditions.html", "Условные операторы", "Условия", 12),
    ("practice-loops.html", "Циклы", "Циклы", 15),
    ("practice-lists.html", "Списки", "Списки", 14),
    ("practice-dicts.html", "Словари и множества", "Словари", 12),
    ("practice-functions.html", "Функции", "Функции", 15),
    ("practice-files.html", "Работа с файлами", "Файлы", 10),
    ("practice-modules.html", "Модули", "Модули", 24),
    ("practice-oop.html", "ООП: Классы и объекты", "ООП", 12),
    ("practice-api-json.html", "API и JSON", "API и JSON", 10),
    ("practice-csv.html", "Обработка CSV", "CSV", 8),
    ("practice-matplotlib.html", "Визуализация в Matplotlib", "Matplotlib", 10),
    ("practice-pandas.html", "Pandas и Numpy", "Pandas", 14),
    ("practice-sqlite.html", "SQLite: Базы данных", "SQLite", 12),
]

NAV_LINKS = [
    ("home", "Главная", "{p}index.html"),
    ("basics", "Основы", "{p}lessons/index.html"),
    ("advanced", "Продвинутый", "{p}advanced/index.html"),
    ("practices", "Практикум", "{p}practices/index.html"),
]


def header_html(prefix: str, active: str, start_href: str) -> str:
    def links(indent: int = 12, mobile: bool = False) -> str:
        rows = []
        for key, label, href in NAV_LINKS:
            href = href.format(p=prefix)
            current = ' aria-current="page"' if key == active else ""
            cls = ' class="active"' if key == active else ""
            rows.append(
                f'{" " * indent}<a href="{href}"{cls}{current}>{label}</a>'
            )
        cta_class = "btn-contact-mobile" if mobile else "btn-contact"
        rows.append(
            f'{" " * indent}<a href="{prefix}{start_href}" class="{cta_class}">Начать обучение</a>'
        )
        return "\n".join(rows)

    return f"""<!-- NAV-HEADER:START -->
<header class="main-header">
    <div class="container flex-header">
        <a href="{prefix}index.html" class="logo"{' aria-current="page"' if active == 'home' else ''}>Prosto<span>Python</span></a>
        <nav class="nav-menu" aria-label="Основная навигация">
{links()}
        </nav>
        <button class="burger-menu" id="burger-menu" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="mobile-menu">
            <span class="burger-line"></span>
            <span class="burger-line"></span>
            <span class="burger-line"></span>
        </button>
    </div>
</header>
<div class="mobile-menu-overlay" id="mobile-menu">
    <nav class="mobile-nav" aria-label="Мобильная навигация">
{links(8, mobile=True)}
    </nav>
</div>
<!-- NAV-HEADER:END -->"""


def footer_html(prefix: str) -> str:
    return f"""<!-- NAV-FOOTER:START -->
<footer class="site-footer">
    <div class="container footer-inner">
        <div class="footer-about">
            <a href="{prefix}index.html" class="logo">Prosto<span>Python</span></a>
            <p>Понятные уроки Python: основы, продвинутый курс и практикум с задачами.</p>
        </div>
        <nav class="footer-nav" aria-label="Навигация в подвале">
            <a href="{prefix}index.html">Главная</a>
            <a href="{prefix}lessons/index.html">Основы Python</a>
            <a href="{prefix}advanced/index.html">Продвинутый курс</a>
            <a href="{prefix}practices/index.html">Практикум</a>
        </nav>
    </div>
    <div class="container footer-bottom">
        <span>© 2026 ProstoPython</span>
        <span>Учись программировать просто.</span>
    </div>
</footer>
<!-- NAV-FOOTER:END -->"""


def sidebar_html(course: str, current: int, prefix: str) -> str:
    """Боковое меню урока. course: 'basics' | 'advanced'."""
    is_basics = course == "basics"
    lessons = BASICS if is_basics else ADVANCED
    category = "Курс: Основы Python" if is_basics else "Курс: Продвинутый Python"

    rows = []
    for num, title in lessons:
        active = ' active' if num == current else ""
        current_attr = ' aria-current="page"' if num == current else ""
        rows.append(
            f'    <a href="lesson{num}.html" class="nav-item{active}"{current_attr}>'
            f'<span class="num">{num:02d}</span> {title}</a>'
        )
    lessons_html = "\n".join(rows)

    if is_basics:
        cross = (
            '<a href="../advanced/index.html" class="nav-item nav-item-accent">'
            '<span class="num">➜</span> Продвинутый курс</a>'
        )
    else:
        cross = (
            '<a href="../lessons/index.html" class="nav-item nav-item-accent">'
            '<span class="num">⬅</span> Основы Python</a>'
        )

    return f"""<div class="sidebar-header">
    <span class="course-category">{category}</span>
    <h4>Содержание</h4>
    <button class="sidebar-toggle" type="button" id="sidebar-toggle" aria-expanded="false" aria-controls="course-lessons">
        Все уроки курса ▾
    </button>
</div>
<nav class="sidebar-links sidebar-course-links" id="course-lessons" aria-label="Уроки курса">
{lessons_html}
</nav>
<div class="sidebar-header sidebar-header-top">
    <h4>Другие разделы</h4>
</div>
<nav class="sidebar-links" aria-label="Другие разделы">
    {cross}
    <a href="../practices/index.html" class="nav-item nav-item-accent"><span class="num">📝</span> Практикум</a>
    <a href="completion.html" class="nav-item nav-item-accent"><span class="num">🏆</span> Курс завершён</a>
</nav>"""


def breadcrumb_html(course: str, num: int, prefix: str) -> str:
    if course == "basics":
        section_label, section_href = "Основы", "index.html"
    else:
        section_label, section_href = "Продвинутый курс", "index.html"
    return (
        '<nav class="breadcrumb" aria-label="Хлебные крошки">'
        f'<a href="{prefix}index.html">Главная</a>'
        '<span class="sep">/</span>'
        f'<a href="{section_href}">{section_label}</a>'
        '<span class="sep">/</span>'
        f'<span class="current">Урок {num}</span>'
        "</nav>"
    )


def lesson_nav_html(course: str, num: int) -> str:
    lessons = BASICS if course == "basics" else ADVANCED
    total = len(lessons)
    if num == 1:
        prev = '<a href="index.html" class="btn-prev">← Программа курса</a>'
    else:
        prev = f'<a href="lesson{num - 1}.html" class="btn-prev">← Предыдущий урок</a>'
    if num == total:
        nxt = '<a href="completion.html" class="btn-next">Завершить курс 🏆</a>'
    else:
        nxt = f'<a href="lesson{num + 1}.html" class="btn-next">Следующий урок →</a>'
    return f'<div class="lesson-nav">\n                {prev}\n                {nxt}\n            </div>'


def topic_nav_html(file_name: str) -> str:
    ids = [p[0] for p in PRACTICES]
    titles = {p[0]: p[2] for p in PRACTICES}
    index = ids.index(file_name)
    if index == 0:
        prev = '<a href="index.html" class="btn-prev">← Все темы</a>'
    else:
        prev_file = ids[index - 1]
        prev = f'<a href="{prev_file}" class="btn-prev">← {titles[prev_file]}</a>'
    if index == len(ids) - 1:
        nxt = '<a href="index.html" class="btn-next">Все темы →</a>'
    else:
        next_file = ids[index + 1]
        nxt = f'<a href="{next_file}" class="btn-next">{titles[next_file]} →</a>'
    return f"""<!-- NAV-TOPIC:START -->
<div class="practice-container practice-topic-nav">
    <div class="lesson-nav">
        {prev}
        {nxt}
    </div>
</div>
<!-- NAV-TOPIC:END -->"""


def replace_region(html: str, name: str, block: str) -> str | None:
    start = f"<!-- {name}:START -->"
    end = f"<!-- {name}:END -->"
    if start in html and end in html:
        pattern = re.escape(start) + r".*?" + re.escape(end)
        return re.sub(pattern, lambda _m: block, html, count=1, flags=re.S)
    return None


def insert_after_body(html: str, block: str) -> str:
    match = re.search(r"<body[^>]*>", html)
    if not match:
        return html
    return html[: match.end()] + "\n" + block + html[match.end():]


def insert_before_body_end(html: str, block: str) -> str:
    """Вставляет блок перед </body>, но выше подключаемых скриптов."""
    match = re.search(r'\n((?:[ \t]*<script\b[^>]*>\s*</script>[ \t]*\n)+)[ \t]*</body>', html, re.S)
    if match:
        return html[: match.start()] + "\n" + block + html[match.start():]
    index = html.rfind("</body>")
    if index == -1:
        return html
    return html[:index] + block + "\n" + html[index:]


def apply_header(html: str, prefix: str, active: str, start_href: str) -> str:
    block = header_html(prefix, active, start_href)
    # Удаляем устаревшие шапки, оставшиеся от старой версии сайта
    html = re.sub(
        r'\n?    <header class="main-header">\s*<div class="container flex-header">\s*<div class="logo">.*?</header>\n',
        '\n',
        html,
        count=1,
        flags=re.S,
    )
    replaced = replace_region(html, "NAV-HEADER", block)
    if replaced is not None:
        return replaced

    # Старая шапка практикума
    old_practice_header = re.search(r'<header class="practice-header-fixed">.*?</header>', html, re.S)
    if old_practice_header:
        return html[: old_practice_header.start()] + block + html[old_practice_header.end():]

    # Страница урока
    placeholder = '<div id="header-placeholder"></div>'
    if placeholder in html:
        return html.replace(placeholder, block, 1)

    return insert_after_body(html, block)


def apply_footer(html: str, prefix: str) -> str:
    """Подвал всегда стоит после контента, но до подключаемых скриптов."""
    block = footer_html(prefix)
    footer_pattern = r"(?:\n\s*)?<!-- NAV-FOOTER:START -->.*?<!-- NAV-FOOTER:END -->\s*"
    if re.search(footer_pattern, html, re.S):
        html = re.sub(footer_pattern, "\n", html, count=1, flags=re.S)
    return insert_before_body_end(html, block + "\n")


def ensure_assets(html: str) -> str:
    """Общие css/js для страниц, у которых их не было."""
    if 'href="../css/style.css"' not in html:
        html = html.replace(
            "</head>",
            '    <link rel="stylesheet" href="../css/style.css">\n</head>',
            1,
        )
    if "prism-tomorrow" not in html:
        html = html.replace(
            "</head>",
            '    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />\n</head>',
            1,
        )
    if "prism.min.js" not in html:
        index = html.rfind("</body>")
        snippet = (
            '    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>\n'
            '    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>\n'
        )
        html = html[:index] + snippet + html[index:]
    if 'src="../js/app.js"' not in html:
        index = html.rfind("</body>")
        html = html[:index] + '    <script src="../js/app.js"></script>\n' + html[index:]
    return html


def strip_old_practice_header_css(html: str) -> str:
    """Удаляет стили несуществующей шапки практикума (остаются стили задач)."""
    def clean_style(match: re.Match[str]) -> str:
        css = match.group(1)
        css = re.sub(
            r"\s*\.practice-header-fixed(?::hover)?\s*\{[^}]*\}",
            "",
            css,
        )
        css = re.sub(
            r"\s*\.header-(?:btn|nav|left|logo)(?:\.primary)?(?::hover)?\s*\{[^}]*\}",
            "",
            css,
        )
        return f"<style>{css}</style>"

    return re.sub(r"<style>(.*?)</style>", clean_style, html, count=1, flags=re.S)


def add_practice_breadcrumb(html: str, file_name: str, prefix: str) -> str:
    short = next(p[2] for p in PRACTICES if p[0] == file_name)
    crumb = (
        '<nav class="breadcrumb" aria-label="Хлебные крошки">'
        f'<a href="{prefix}index.html">Главная</a>'
        '<span class="sep">/</span>'
        '<a href="index.html">Практикум</a>'
        '<span class="sep">/</span>'
        f'<span class="current">{short}</span>'
        "</nav>\n"
    )
    if '<nav class="breadcrumb"' in html:
        return re.sub(
            r'<nav class="breadcrumb".*?</nav>\n?',
            lambda _m: crumb,
            html,
            count=1,
            flags=re.S,
        )
    match = re.search(r'(<div class="practice-container">\s*)', html)
    if match:
        return html[: match.end()] + crumb + html[match.end():]
    return html


def process(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    original = html
    rel = path.relative_to(ROOT)
    prefix = "../" if len(rel.parts) > 1 else ""

    is_basics_lesson = bool(re.fullmatch(r"lessons/lesson\d+\.html", rel.as_posix()))
    is_advanced_lesson = bool(re.fullmatch(r"advanced/lesson\d+\.html", rel.as_posix()))
    is_practice = bool(re.fullmatch(r"practices/practice-[\w-]+\.html", rel.as_posix()))

    if is_practice:
        html = strip_old_practice_header_css(html)
        html = ensure_assets(html)

    # Активный пункт меню
    if rel.as_posix() == "index.html":
        active = "home"
    elif rel.as_posix().startswith("lessons/"):
        active = "basics"
    elif rel.as_posix().startswith("advanced/"):
        active = "advanced"
    elif rel.as_posix().startswith("practices/"):
        active = "practices"
    else:
        active = "home"

    html = apply_header(html, prefix, active, "lessons/lesson1.html")

    if is_basics_lesson or is_advanced_lesson:
        course = "basics" if is_basics_lesson else "advanced"
        num = int(re.search(r"lesson(\d+)\.html", rel.as_posix()).group(1))
        html = re.sub(
            r'(<aside class="sidebar" id="sidebar-placeholder"[^>]*>).*?(</aside>)',
            lambda m: m.group(1) + "\n" + sidebar_html(course, num, prefix) + "\n" + m.group(2),
            html,
            count=1,
            flags=re.S,
        )
        html = re.sub(
            r'<nav class="breadcrumb".*?</nav>',
            lambda _m: breadcrumb_html(course, num, prefix),
            html,
            count=1,
            flags=re.S,
        )
        html = re.sub(
            r'<div class="lesson-nav">.*?</div>',
            lambda _m: lesson_nav_html(course, num),
            html,
            count=1,
            flags=re.S,
        )

    if is_practice:
        html = add_practice_breadcrumb(html, rel.name, prefix)
        topic_block = topic_nav_html(rel.name)
        replaced = replace_region(html, "NAV-TOPIC", topic_block)
        if replaced is not None:
            html = replaced
        else:
            html = insert_before_body_end(html, topic_block)

    html = apply_footer(html, prefix)

    if html != original:
        path.write_text(html, encoding="utf-8")
        print(f"обновлён {rel}")


def main() -> None:
    files = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/*.html"))
    for path in files:
        if path.parent.name == "tools":
            continue
        process(path)


if __name__ == "__main__":
    main()
