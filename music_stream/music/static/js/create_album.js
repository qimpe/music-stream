
document.addEventListener('DOMContentLoaded', function() {
        const addButton = document.getElementById('add-track');
        const container = document.getElementById('track-forms-container');
        
        // 1. Находим поле TOTAL_FORMS альтернативным способом
        const totalFormsInput = document.querySelector('[name$="-TOTAL_FORMS"]');
        if (!totalFormsInput) {
            console.error('Total forms input not found!');
            return;
        }
        
        // 2. Получаем префикс из имени поля
        const prefix = totalFormsInput.name.replace('-TOTAL_FORMS', '');
        const emptyFormTemplate = document.getElementById('empty-form').innerHTML;
        
        // 3. Добавляем обработчики через делегирование
        container.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-track')) {
                removeTrackForm(e);
            }
        });
        
        // 4. Обработчик добавления трека
        addButton.addEventListener('click', function() {
            const formIndex = parseInt(totalFormsInput.value);
            const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formIndex);
            
            const newFormDiv = document.createElement('div');
            newFormDiv.innerHTML = newFormHtml;
            container.appendChild(newFormDiv);
            
            // Обновляем счетчик форм
            totalFormsInput.value = formIndex + 1;
        });
        
        // 5. Функция удаления формы
        function removeTrackForm(event) {
            const formDiv = event.target.closest('.track-form');
            const trackForms = container.querySelectorAll('.track-form:not([style*="display: none"])');
            
            // Проверка минимального количества форм
            if (trackForms.length <= 1) {
                alert('Альбом должен содержать хотя бы один трек!');
                return;
            }
            
            // Помечаем форму на удаление
            const deleteInput = formDiv.querySelector('input[name$="-DELETE"]');
            if (deleteInput) {
                deleteInput.value = 'on';
            }
            
            // Скрываем форму
            formDiv.style.display = 'none';
           
        }
    });
