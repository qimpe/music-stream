document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('track-forms-container');
    const addButton = document.getElementById('add-track');
    const totalFormsInput = document.querySelector('[name="tracks-TOTAL_FORMS"]');
    const emptyFormTemplate = document.getElementById('empty-form').innerHTML;

    // Назначаем обработчики удаления для существующих форм
    container.addEventListener('click', function(e) {
        if (e.target.closest('.remove-track')) {
            removeTrackForm(e.target.closest('.remove-track'));
        }
    });

    // Обработчик добавления трека
    addButton.addEventListener('click', function() {
        const formIndex = parseInt(totalFormsInput.value);
        const newFormHtml = emptyFormTemplate
            .replace(/__prefix__/g, formIndex)
            .replace(/__position__/g, container.children.length + 1);
        
        const newFormDiv = document.createElement('div');
        newFormDiv.innerHTML = newFormHtml;
        container.appendChild(newFormDiv);
        
        // Обновляем счетчик форм
        totalFormsInput.value = parseInt(totalFormsInput.value) + 1;
        
        // Обновляем позиции всех треков
        updateTrackPositions();
    });
    
    // Функция удаления формы
    function removeTrackForm(button) {
        const trackForm = button.closest('.track-form');
        if (container.querySelectorAll('.track-form').length > 1) {
            trackForm.remove();
            
            // Обновляем счетчик форм
            totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
            
            // Обновляем позиции всех треков
            updateTrackPositions();
        } else {
            alert('Альбом должен содержать хотя бы один трек!');
        }
    }
    
    // Функция для обновления позиций треков
    function updateTrackPositions() {
        const visibleForms = container.querySelectorAll('.track-form');
        visibleForms.forEach((form, index) => {
            const position = index + 1;
            const positionSpan = form.querySelector('.track-position');
            const positionInput = form.querySelector('.position-field');
            
            if (positionSpan) positionSpan.textContent = position;
            if (positionInput) positionInput.value = position;
        });
    }

    // Валидация при отправке формы
    document.getElementById('album-form').addEventListener('submit', function(e) {
        const visibleTracks = container.querySelectorAll('.track-form');
        if (visibleTracks.length < 1) {
            e.preventDefault();
            alert('Альбом должен содержать хотя бы один трек!');
        }
        
        const title = document.getElementById('id_title').value;
        const cover = document.getElementById('id_cover').files.length;
        
        if (!title || !cover) {
            e.preventDefault();
            alert('Заполните обязательные поля альбома!');
        }
    });
    
    // Инициализируем позиции при загрузке страницы
    updateTrackPositions();
});