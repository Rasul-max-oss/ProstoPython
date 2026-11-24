// =========================================
// ProstoPython — общий скрипт сайта
// =========================================

const BASICS_TOTAL = 11;
const ADVANCED_TOTAL = 6;
const STORAGE = {
    basics: 'prostoPython_progress',
    advanced: 'prostoPython_advanced_progress',
};

document.addEventListener('DOMContentLoaded', () => {
    initBurgerMenu();
    initSidebarToggle();
    markLessonComplete();   // сначала фиксируем текущий урок,
    initProgressBar();      // затем показываем актуальный прогресс
    initSidebarProgress();
    initProgramLists();
    initSolutionToggles();
    highlightActiveTopic();
});

/* Мобильное меню */
function initBurgerMenu() {
    const burger = document.getElementById('burger-menu');
    const overlay = document.getElementById('mobile-menu');
    if (!burger || !overlay) return;

    const closeMenu = () => {
        burger.classList.remove('active');
        overlay.classList.remove('active');
        document.body.classList.remove('menu-open');
        burger.setAttribute('aria-expanded', 'false');
        burger.setAttribute('aria-label', 'Открыть меню');
    };

    burger.addEventListener('click', () => {
        const isOpen = overlay.classList.toggle('active');
        burger.classList.toggle('active', isOpen);
        document.body.classList.toggle('menu-open', isOpen);
        burger.setAttribute('aria-expanded', String(isOpen));
        burger.setAttribute('aria-label', isOpen ? 'Закрыть меню' : 'Открыть меню');
    });

    overlay.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') closeMenu();
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) closeMenu();
    });
}

/* На мобильных уроки в сайдбаре сворачиваются в кнопку */
function initSidebarToggle() {
    const toggle = document.getElementById('sidebar-toggle');
    const list = document.getElementById('course-lessons');
    if (!toggle || !list) return;

    toggle.addEventListener('click', () => {
        const open = list.classList.toggle('open');
        toggle.setAttribute('aria-expanded', String(open));
        toggle.textContent = open ? 'Свернуть список уроков ▴' : 'Все уроки курса ▾';
    });
}

/* Определяем, где находится пользователь */
function currentCourse() {
    const path = window.location.pathname;
    if (path.includes('/advanced/')) return 'advanced';
    if (path.includes('/lessons/')) return 'basics';
    return null;
}

function readProgress(course) {
    try {
        const stored = localStorage.getItem(STORAGE[course]);
        const parsed = stored ? JSON.parse(stored) : [];
        return Array.isArray(parsed) ? parsed.map(Number).filter(Number.isFinite) : [];
    } catch (err) {
        console.warn('Не удалось прочитать прогресс:', err);
        return [];
    }
}

function writeProgress(course, lessons) {
    try {
        localStorage.setItem(STORAGE[course], JSON.stringify([...new Set(lessons)].sort((a, b) => a - b)));
    } catch (err) {
        console.warn('Не удалось сохранить прогресс:', err);
    }
}

/* Отмечаем пройденный урок, когда пользователь долистал до навигации */
function markLessonComplete() {
    const course = currentCourse();
    if (!course) return;

    const match = window.location.pathname.match(/lesson(\d+)\.html/);
    if (!match) return;

    const lessonNum = Number(match[1]);
    const completed = readProgress(course);
    if (!completed.includes(lessonNum)) {
        completed.push(lessonNum);
        writeProgress(course, completed);
    }
}

/* Прогресс-бар на странице урока */
function initProgressBar() {
    const fill = document.getElementById('progress-fill');
    const percentLabel = document.getElementById('progress-percent');
    if (!fill || !percentLabel) return;

    const course = currentCourse();
    if (!course) return;

    const total = course === 'advanced' ? ADVANCED_TOTAL : BASICS_TOTAL;
    const completed = readProgress(course).filter(n => n >= 1 && n <= total);
    const percent = Math.min(100, Math.round((completed.length / total) * 100));

    fill.style.width = percent + '%';
    percentLabel.textContent = percent + '%';
}

/* Отмечаем в сайдбаре пройденные уроки */
function initSidebarProgress() {
    const sidebar = document.querySelector('.sidebar');
    const course = currentCourse();
    if (!sidebar || !course) return;

    const completed = readProgress(course);
    sidebar.querySelectorAll('a.nav-item[href^="lesson"]').forEach(link => {
        const match = link.getAttribute('href').match(/lesson(\d+)\.html/);
        if (!match) return;
        const num = Number(match[1]);
        if (completed.includes(num)) link.classList.add('done');
    });
}

/* Отмечаем пройденные уроки в списке программы курса */
function initProgramLists() {
    const list = document.querySelector('.program-list[data-course]');
    if (!list) return;

    const course = list.dataset.course;
    const completed = readProgress(course);

    list.querySelectorAll('a.program-item').forEach(item => {
        const match = (item.getAttribute('href') || '').match(/lesson(\d+)\.html/);
        if (!match) return;
        if (completed.includes(Number(match[1]))) item.classList.add('done');
    });
}

/* Кнопки «показать решение» в практикуме */
function initSolutionToggles() {
    document.querySelectorAll('.solution-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const code = btn.nextElementSibling;
            if (!code) return;
            const shown = code.style.display === 'block';
            code.style.display = shown ? 'none' : 'block';
            btn.textContent = shown ? 'Показать решение' : 'Скрыть решение';
        });
    });

    document.querySelectorAll('[data-reveal-solution]').forEach(btn => {
        btn.addEventListener('click', () => {
            const target = document.getElementById(btn.dataset.revealSolution);
            if (!target) return;
            const shown = target.style.display === 'block';
            target.style.display = shown ? 'none' : 'block';
            btn.textContent = shown ? 'Показать решение' : 'Скрыть решение';
        });
    });
}

/* В списке тем практикума подсвечиваем текущую */
function highlightActiveTopic() {
    const currentFile = window.location.pathname.split('/').pop();
    document.querySelectorAll('.topic-card').forEach(card => {
        const href = card.getAttribute('href') || '';
        if (href.split('/').pop() === currentFile) {
            card.style.borderColor = 'rgba(0, 255, 65, 0.5)';
        }
    });
}

/* Сброс прогресса (можно вызвать из консоли браузера) */
function resetProgress(course = 'basics') {
    localStorage.removeItem(STORAGE[course] || STORAGE.basics);
    window.location.reload();
}
