document.addEventListener('DOMContentLoaded', function() {
    // ... (остальной код без изменений) ...
    
    // Обработчик добавления трека
    addButton.addEventListener('click', function() {
        const formIndex = parseInt(totalFormsInput.value);
        const currentTrackCount = container.querySelectorAll('.track-form:not([style*="display: none"])').length;
        const newPosition = currentTrackCount + 1;
        
        // Создаем новую форму с подставленными значениями
        let newFormHtml = emptyFormTemplate
            .replace(/__prefix__/g, formIndex)
            .replace(/__position__/g, newPosition);
        
        const newFormDiv = document.createElement('div');
        newFormDiv.innerHTML = newFormHtml;
        container.appendChild(newFormDiv);
        
        // Обновляем счетчик форм
        totalFormsInput.value = parseInt(totalFormsInput.value) + 1;
        
        // Обновляем позиции всех треков
        updateTrackPositions();
    });
    
    // Функция удаления формы
    function removeTrackForm(event) {
        // ... (код без изменений до перенумерации) ...
        
        // Перенумеровываем оставшиеся треки
        updateTrackPositions();
    }
    
    // Функция для обновления позиций треков
    // В create_album.js
    function updateTrackPositions() {
        const visibleForms = container.querySelectorAll('.track-form:not([style*="display: none"])');
        visibleForms.forEach((form, index) => {
            const position = index + 1;
            const positionSpan = form.querySelector('.track-position');
            const positionInput = form.querySelector('.position-field');
            
            if (positionSpan) positionSpan.textContent = position;
            if (positionInput) positionInput.value = position;
        });

}
    document.getElementById('album-form').addEventListener('submit', function(e) {
    const visibleTracks = document.querySelectorAll('#track-forms-container .track-form:not([style*="display: none"])');
    if (visibleTracks.length < 1) {
        e.preventDefault();
        alert('Альбом должен содержать хотя бы один трек!');
    }
    });
    const title = document.getElementById('id_title').value;
    const cover = document.getElementById('id_cover').files.length;
    
    if (!title || !cover) {
        e.preventDefault();
        alert('Заполните обязательные поля альбома!');
    }
    // Инициализируем позиции при загрузке страницы
    updateTrackPositions();
});