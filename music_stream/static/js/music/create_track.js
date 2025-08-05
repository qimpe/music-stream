
document.addEventListener('DOMContentLoaded', function () {
    // Элементы для аудио
    const audioInput = document.getElementById('id_audio_file');
    const audioPreview = document.getElementById('audio-preview');
    const uploadInstruction = document.getElementById('upload-instruction');
    const fileInfo = document.getElementById('file-info');
    const audioFileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const changeFileBtn = document.getElementById('change-file');
    const previewPlayer = document.getElementById('preview-player');
    const playButton = document.getElementById('play-preview');

    // Элементы для обложки
    const coverInput = document.getElementById('id_cover');
    const coverUploadInstruction = document.getElementById('cover-upload-instruction');
    const coverPreviewContainer = document.getElementById('cover-preview-container');
    const coverPreview = document.getElementById('cover-preview');
    const coverFileName = document.getElementById('cover-file-name');
    const changeCoverBtn = document.getElementById('change-cover');

    // Функция для форматирования размера файла
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Обработчик для аудиофайла
    audioInput.addEventListener('change', function (e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];

            // Обновляем информацию о файле
            audioFileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);

            // Показываем информацию о файле, скрываем инструкцию
            uploadInstruction.classList.add('hidden');
            fileInfo.classList.remove('hidden');

            // Показываем превью плеера
            audioPreview.classList.remove('hidden');

            // Создаем URL для предпрослушивания
            const objectUrl = URL.createObjectURL(file);
            previewPlayer.src = objectUrl;

            // Генерируем визуализацию
            generateWaveform();
        }
    });

    // Кнопка "Change" для аудио
    changeFileBtn.addEventListener('click', function () {
        audioInput.click();
    });

    // Обработчик для обложки
    coverInput.addEventListener('change', function (e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];

            // Обновляем информацию о файле
            coverFileName.textContent = file.name;

            // Показываем превью, скрываем инструкцию
            coverUploadInstruction.classList.add('hidden');
            coverPreviewContainer.classList.remove('hidden');

            // Создаем URL для превью
            const reader = new FileReader();
            reader.onload = function (e) {
                coverPreview.src = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    });

    // Кнопка "Change" для обложки
    changeCoverBtn.addEventListener('click', function () {
        coverInput.click();
    });

    // Управление аудиоплеером
    playButton.addEventListener('click', function () {
        if (previewPlayer.paused) {
            previewPlayer.play();
            playButton.innerHTML = `
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            `;
        } else {
            previewPlayer.pause();
            playButton.innerHTML = `
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            `;
        }
    });

    // Генерация визуализации аудио
    function generateWaveform() {
        const waveform = document.getElementById('waveform');
        waveform.innerHTML = '';

        // Генерируем случайную визуализацию
        for (let i = 0; i < 50; i++) {
            const bar = document.createElement('div');
            bar.className = 'inline-block mx-0.5 bg-rose-500 rounded-t';
            bar.style.width = '3px';
            bar.style.height = `${Math.floor(Math.random() * 30) + 5}px`;
            bar.style.setProperty('--i', i);
            waveform.appendChild(bar);
        }
    }

    // Drag and drop для аудио
    const audioDropArea = document.querySelector('.audio-upload-area');
    setupDragDrop(audioDropArea, audioInput);

    // Drag and drop для обложки
    const coverDropArea = document.querySelector('.cover-upload-area');
    setupDragDrop(coverDropArea, coverInput);

    // Общая функция для настройки drag & drop
    function setupDragDrop(dropArea, inputElement) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        dropArea.addEventListener('drop', handleDrop, false);

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight() {
            dropArea.classList.add('border-rose-500', 'bg-gray-800/30');
        }

        function unhighlight() {
            dropArea.classList.remove('border-rose-500', 'bg-gray-800/30');
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                // Для аудио проверяем тип файла
                if (inputElement === audioInput) {
                    if (files[0].type.startsWith('audio/')) {
                        inputElement.files = files;
                        const event = new Event('change', { bubbles: true });
                        inputElement.dispatchEvent(event);
                    }
                }
                // Для обложки принимаем любые изображения
                else if (inputElement === coverInput) {
                    if (files[0].type.startsWith('image/')) {
                        inputElement.files = files;
                        const event = new Event('change', { bubbles: true });
                        inputElement.dispatchEvent(event);
                    }
                }
            }
        }
    }
});
