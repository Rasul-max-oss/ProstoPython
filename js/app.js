document.addEventListener('DOMContentLoaded', () => {
    loadLayout();
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
            console.log("Успешно подсвечено:", linkFile);
        } else {
            link.classList.remove('active');
        }
    });
}