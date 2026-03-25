// Конфигурация курса
const COURSE_CONFIG = {
    totalLessons: 11,
    storageKey: 'prostoPython_progress'
};

document.addEventListener('DOMContentLoaded', () => {
    loadLayout();
    updateProgress();
    markLessonComplete();
});

async function loadLayout() {
    try {
        // Загружаем шапку
        const headerRes = await fetch('../includes/header.html');
        if (headerRes.ok) {
            document.getElementById('header-placeholder').innerHTML = await headerRes.text();
        }

        // Загружаем сайдбар
        const sidebarRes = await fetch('../includes/sidebar.html');
        if (sidebarRes.ok) {
            const sidebarHtml = await sidebarRes.text();
            const sidebarPlaceholder = document.getElementById('sidebar-placeholder');

            // Вставляем HTML
            sidebarPlaceholder.innerHTML = sidebarHtml;

            // СРАЗУ ПОСЛЕ вставки запускаем подсветку
            highlightActiveStep();
        }
    } catch (err) {
        console.error("Ошибка загрузки:", err);
    }
}

function highlightActiveStep() {
    // Получаем имя текущего файла, например "lesson2.html"
    const currentFile = window.location.pathname.split('/').pop();

    // Находим все ссылки именно ВНУТРИ сайдбара
    const sidebarLinks = document.querySelectorAll('#sidebar-placeholder a');

    sidebarLinks.forEach(link => {
        // Берем только имя файла из href ссылки
        const linkFile = link.getAttribute('href').split('/').pop();

        if (currentFile === linkFile) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Обновление прогресс-бара
function updateProgress() {
    const progressFill = document.getElementById('progress-fill');
    const progressPercent = document.getElementById('progress-percent');
    
    if (!progressFill || !progressPercent) return;
    
    const completed = getCompletedLessons();
    const percent = Math.round((completed.length / COURSE_CONFIG.totalLessons) * 100);
    
    progressFill.style.width = percent + '%';
    progressPercent.textContent = percent + '%';
}

// Отметить урок как пройденный
function markLessonComplete() {
    const currentFile = window.location.pathname.split('/').pop();
    const lessonMatch = currentFile.match(/lesson(\d+)\.html/);
    
    if (!lessonMatch) return;
    
    const lessonNum = parseInt(lessonMatch[1]);
    const completed = getCompletedLessons();
    
    if (!completed.includes(lessonNum)) {
        completed.push(lessonNum);
        localStorage.setItem(COURSE_CONFIG.storageKey, JSON.stringify(completed));
    }
}

// Получить список пройденных уроков
function getCompletedLessons() {
    const stored = localStorage.getItem(COURSE_CONFIG.storageKey);
    return stored ? JSON.parse(stored) : [];
}

// Сбросить прогресс (для отладки)
function resetProgress() {
    localStorage.removeItem(COURSE_CONFIG.storageKey);
    updateProgress();
}