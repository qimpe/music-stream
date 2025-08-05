document.addEventListener('DOMContentLoaded', function() {
    // Функция для обновления отображаемого имени файла
    function updateFileName(input) {
        const container = input.closest('.relative');
        const fileNameSpan = container.querySelector('.file-name');
        
        if (input.files.length > 0) {
            fileNameSpan.textContent = input.files[0].name;
            fileNameSpan.classList.add('text-white');
        } else {
            fileNameSpan.textContent = 'Select audio file';
            fileNameSpan.classList.remove('text-white');
        }
    }

    // Обработчик для всех существующих файловых инпутов
    document.querySelectorAll('.audio-file-input').forEach(input => {
        // При изменении файла
        input.addEventListener('change', function() {
            updateFileName(this);
        });
        
        // Инициализация при загрузке (если файл уже выбран)
        if (input.files.length > 0) {
            updateFileName(input);
        }
    });

    // Обработчик для динамически добавляемых форм
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'add-track') {
            // Ждем, пока форма добавится
            setTimeout(() => {
                // Находим все новые файловые инпуты
                document.querySelectorAll('.audio-file-input').forEach(input => {
                    // Проверяем, не был ли уже добавлен обработчик
                    if (!input.hasAttribute('data-file-handler')) {
                        input.addEventListener('change', function() {
                            updateFileName(this);
                        });
                        input.setAttribute('data-file-handler', 'true');
                        
                        // Инициализация, если файл уже выбран
                        if (input.files.length > 0) {
                            updateFileName(input);
                        }
                    }
                });
            }, 100);
        }
    });
});
