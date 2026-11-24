#!/usr/bin/env python3
"""Проверка целостности сайта ProstoPython.

Запуск:  python3 tools/check_site.py

Проверяет:
  * все внутренние ссылки (href/src) ведут на существующие файлы;
  * на каждой странице есть шапка, меню, мобильное меню, подвал и один <h1>;
  * на страницах уроков есть боковое меню, крошки, прогресс-бар и переход к следующему уроку;
  * на страницах практикума есть задачи, кнопки решений, крошки и переход к следующей теме;
  * все страницы достижимы по ссылкам с главной;
  * в каждой папке есть index.html.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "tools"}

errors: list[str] = []


def html_pages() -> list[Path]:
    pages = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        pages.append(path)
    return sorted(pages)


def check_links(page: Path, html: str) -> None:
    for attr in ("href", "src"):
        for value in re.findall(rf'{attr}="([^"]+)"', html):
            if not value or value.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:")):
                continue
            target = (page.parent / value.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: битая ссылка {attr}=\"{value}\"")


def check_page(page: Path, html: str) -> None:
    rel = page.relative_to(ROOT)
    rel_posix = rel.as_posix()

    required = {
        'шапка (class="main-header")': "main-header",
        "кнопка мобильного меню": 'id="burger-menu"',
        "мобильное меню": 'id="mobile-menu"',
        "подвал": "site-footer",
    }
    for label, needle in required.items():
        if needle not in html:
            errors.append(f"{rel_posix}: нет элемента «{label}»")

    if len(re.findall(r"<h1[ >]", html)) != 1:
        errors.append(f"{rel_posix}: ожидается ровно один <h1>")
    if html.count('class="nav-menu"') != 1:
        errors.append(f"{rel_posix}: основное меню должно быть одно")
    for needle, label in (
        ('class="mobile-menu-overlay"', "мобильное меню"),
        ('id="burger-menu"', "кнопка мобильного меню"),
        ('class="main-header"', "шапка"),
    ):
        if html.count(needle) != 1:
            errors.append(f"{rel_posix}: «{label}» должно быть ровно одно (найдено {html.count(needle)})")

    if "viewport" not in html:
        errors.append(f"{rel_posix}: нет meta viewport")
    if not re.search(r"<title>[^<]{5,}</title>", html):
        errors.append(f"{rel_posix}: пустой <title>")

    is_lesson = re.fullmatch(r"(lessons|advanced)/lesson\d+\.html", rel_posix)
    if is_lesson:
        if "sidebar-links" not in html:
            errors.append(f"{rel_posix}: пустое боковое меню")
        if "breadcrumb" not in html:
            errors.append(f"{rel_posix}: нет хлебных крошек")
        if "progress-fill" not in html:
            errors.append(f"{rel_posix}: нет прогресс-бара")
        if 'class="btn-next"' not in html:
            errors.append(f"{rel_posix}: нет кнопки следующего урока")
        if 'id="sidebar-toggle"' not in html:
            errors.append(f"{rel_posix}: нет кнопки списка уроков для мобильных")

    if re.fullmatch(r"practices/practice-.+\.html", rel_posix):
        tasks = len(re.findall(r'<div class="task-card">', html))
        toggles = html.count('class="solution-toggle"')
        solutions = html.count('class="solution-code"')
        if tasks == 0:
            errors.append(f"{rel_posix}: нет задач")
        if toggles != tasks or solutions != tasks:
            errors.append(f"{rel_posix}: задач {tasks}, кнопок решений {toggles}, решений {solutions}")
        if "breadcrumb" not in html:
            errors.append(f"{rel_posix}: нет хлебных крошек")
        if "practice-topic-nav" not in html:
            errors.append(f"{rel_posix}: нет перехода между темами практикума")
        if "../css/style.css" not in html:
            errors.append(f"{rel_posix}: не подключён общий style.css")
        if "../js/app.js" not in html:
            errors.append(f"{rel_posix}: не подключён app.js")


def check_reachability(pages: list[Path]) -> None:
    by_path = {p.resolve() for p in pages}
    start = (ROOT / "index.html").resolve()
    seen = {start}
    queue = [start]
    while queue:
        page = queue.pop()
        html = page.read_text(encoding="utf-8")
        for value in re.findall(r'href="([^"]+)"', html):
            if value.startswith(("#", "http://", "https://", "mailto:", "tel:")):
                continue
            target = (page.parent / value.split("#")[0].split("?")[0]).resolve()
            if target in by_path and target not in seen:
                seen.add(target)
                queue.append(target)
    for page in pages:
        if page.resolve() not in seen:
            errors.append(f"{page.relative_to(ROOT)}: страница недостижима по ссылкам с главной")


def main() -> int:
    pages = html_pages()
    for page in pages:
        html = page.read_text(encoding="utf-8")
        check_links(page, html)
        check_page(page, html)
    check_reachability(pages)

    for folder in ("lessons", "advanced", "practices"):
        if not (ROOT / folder / "index.html").exists():
            errors.append(f"нет страницы {folder}/index.html")

    print(f"Проверено страниц: {len(pages)}")
    if errors:
        print(f"Найдено проблем: {len(errors)}")
        for error in sorted(set(errors)):
            print(" -", error)
        return 1
    print("Проблем не найдено ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
