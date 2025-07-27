document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-track');
    const container = document.getElementById('track-forms-container');
    
    // Находим поле TOTAL_FORMS
    const totalFormsInput = document.querySelector('[name$="-TOTAL_FORMS"]');
    if (!totalFormsInput) {
        console.error('Total forms input not found!');
        return;
    }
    
    const prefix = totalFormsInput.name.replace('-TOTAL_FORMS', '');
    const emptyFormTemplate = document.getElementById('empty-form').innerHTML;
    
    // Добавляем обработчики
    container.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-track')) {
            removeTrackForm(e);
        }
    });
    
    // Обработчик добавления трека
    addButton.addEventListener('click', function() {
        const formIndex = parseInt(totalFormsInput.value);
        const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formIndex);
        
        const newFormDiv = document.createElement('div');
        newFormDiv.innerHTML = newFormHtml;
        container.appendChild(newFormDiv);
        
        // Устанавливаем позицию для нового трека
        setPositionForNewTrack(newFormDiv);
        
        // Обновляем счетчик форм
        totalFormsInput.value = formIndex + 1;
    });
    
    // Функция для установки позиции нового трека
    function setPositionForNewTrack(newFormDiv) {
        // Считаем только существующие видимые формы (без новой)
        const existingForms = container.querySelectorAll('.track-form:not([style*="display: none"]):not(.newly-added)');
        const newPosition = existingForms.length; // Позиция нового трека = кол-во существующих
        
        newFormDiv.classList.add('newly-added'); // Помечаем как новый
        
        const positionInput = newFormDiv.querySelector(`input[name$="-position"]`);
        if (positionInput) {
            positionInput.value = newPosition; // Устанавливаем позицию
        }
    }
    
    // Функция удаления формы
    function removeTrackForm(event) {
        const formDiv = event.target.closest('.track-form');
        const trackForms = container.querySelectorAll('.track-form:not([style*="display: none"])');
        
        if (trackForms.length <= 1) {
            alert('Альбом должен содержать хотя бы один трек!');
            return;
        }
        
        const deleteInput = formDiv.querySelector('input[name$="-DELETE"]');
        if (deleteInput) {
            deleteInput.value = 'on';
        }
        
        formDiv.style.display = 'none';
        
        // Перенумеровываем оставшиеся треки
        renumberTracks();
    }
    
    // Функция для перенумерации треков
    function renumberTracks() {
        const trackForms = container.querySelectorAll('.track-form:not([style*="display: none"])');
        trackForms.forEach((form, index) => {
            form.classList.remove('newly-added'); // Убираем метку "новый"
            const positionInput = form.querySelector(`input[name$="-position"]`);
            if (positionInput) {
                positionInput.value = index+1; // Устанавливаем позиции с 0
            }
        });
    }
    
    // Инициализируем позиции при загрузке страницы
    renumberTracks();
});