/* ═════════════════════════════════════════════════════════════════════════
   🖤 COUPLE TRACKER WEB APP — JAVASCRIPT
   ═════════════════════════════════════════════════════════════════════════ */

// Утилиты
const API = {
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async get(url) {
        const response = await fetch(url);
        return response.json();
    }
};

// Уведомления
function showNotification(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    const container = document.querySelector('.main-content');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        setTimeout(() => alert.remove(), 3000);
    }
}

// Форматирование дат
function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return new Intl.DateTimeFormat('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// Проверка сессии
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, если пользователь не авторизован на защищённых страницах
    const userIdFromSession = document.body.getAttribute('data-user-id');
    if (!userIdFromSession && window.location.pathname !== '/login') {
        // Может быть перенаправлен на login через Flask
    }

    // Инициализация всех интерактивных элементов
    initializeTooltips();
    initializeLoadingStates();
});

// Tooltips
function initializeTooltips() {
    document.querySelectorAll('[title]').forEach(el => {
        el.style.cursor = 'help';
    });
}

// Состояния загрузки для кнопок
function initializeLoadingStates() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Загрузка...';
                
                // Восстанавливаем после отправки
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }, 3000);
            }
        });
    });
}

// Валидация форм
function validateForm(form) {
    return form.checkValidity();
}

// Анимация при загрузке элементов
function addFadeInAnimation() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideDown 0.5s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    });

    document.querySelectorAll('.card, .challenge-card, .entry').forEach(el => {
        observer.observe(el);
    });
}

// Обработчики для страниц
const PageHandlers = {
    dashboard: function() {
        // Загружаем статистику
        console.log('📱 Dashboard loaded');
    },

    tree: function() {
        console.log('🌱 Tree page loaded');
        // Анимация дерева уже в HTML
    },

    diary: function() {
        const textarea = document.getElementById('diary-text');
        if (textarea) {
            textarea.addEventListener('input', function() {
                const count = document.getElementById('char-count');
                if (count) {
                    count.textContent = this.value.length;
                }
            });
        }
        console.log('📝 Diary page loaded');
    },

    goals: function() {
        console.log('🎯 Goals page loaded');
    },

    challenges: function() {
        document.querySelectorAll('.challenge-card .btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                showNotification('✅ Челлендж принят!', 'success');
            });
        });
        console.log('🎪 Challenges page loaded');
    },

    partner: function() {
        console.log('👥 Partner page loaded');
    },

    settings: function() {
        console.log('⚙️ Settings page loaded');
    }
};

// Детектирование текущей страницы
function detectCurrentPage() {
    const path = window.location.pathname;
    
    if (path.includes('dashboard')) {
        PageHandlers.dashboard?.();
    } else if (path.includes('tree')) {
        PageHandlers.tree?.();
    } else if (path.includes('diary')) {
        PageHandlers.diary?.();
    } else if (path.includes('goals')) {
        PageHandlers.goals?.();
    } else if (path.includes('challenges')) {
        PageHandlers.challenges?.();
    } else if (path.includes('partner')) {
        PageHandlers.partner?.();
    } else if (path.includes('settings')) {
        PageHandlers.settings?.();
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    detectCurrentPage();
    addFadeInAnimation();
});

// Горячие клавиши
document.addEventListener('keydown', function(e) {
    // Ctrl+S - сохранить форму
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const form = document.querySelector('form');
        if (form) form.submit();
    }
});

// Service Worker для офлайна (опционально)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => {
        // Service Worker не доступен
    });
}

// Логирование ошибок
window.addEventListener('error', function(e) {
    console.error('Error:', e.error);
});

// Предупреждение при выходе с несохранённых данных
let hasUnsavedChanges = false;

document.addEventListener('change', function(e) {
    if (e.target.matches('input, textarea, select')) {
        hasUnsavedChanges = true;
    }
});

document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        hasUnsavedChanges = false;
    });
});

window.addEventListener('beforeunload', function(e) {
    if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Дебаунс функция для поиска
function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

// Локальное хранилище для черновиков
const DraftManager = {
    save(key, value) {
        try {
            localStorage.setItem(`draft_${key}`, JSON.stringify(value));
        } catch (e) {
            console.error('Не удалось сохранить черновик:', e);
        }
    },

    load(key) {
        try {
            const value = localStorage.getItem(`draft_${key}`);
            return value ? JSON.parse(value) : null;
        } catch (e) {
            console.error('Не удалось загрузить черновик:', e);
            return null;
        }
    },

    remove(key) {
        try {
            localStorage.removeItem(`draft_${key}`);
        } catch (e) {
            console.error('Не удалось удалить черновик:', e);
        }
    }
};

// Сохранение черновиков при вводе
document.querySelectorAll('textarea[id], input[type="text"][id]').forEach(el => {
    const debouncedSave = debounce(() => {
        DraftManager.save(el.id, el.value);
    }, 1000);

    el.addEventListener('input', debouncedSave);

    // Загружаем черновик при загрузке страницы
    const draft = DraftManager.load(el.id);
    if (draft) {
        el.value = draft;
        hasUnsavedChanges = true;
    }
});

// Формматирование номеров (добавляем пробелы)
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// Экспорт основных функций
window.Couple = {
    API,
    showNotification,
    formatDate,
    formatNumber,
    DraftManager
};
