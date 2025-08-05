document.addEventListener('DOMContentLoaded', function () {
    const player = document.getElementById('player');
    const audio = document.getElementById('audio-player');
    const playButton = document.getElementById('play-button');
    const playIcon = document.getElementById('play-icon');
    const progressBar = document.getElementById('progress-bar');
    const currentTimeElement = document.getElementById('current-time');
    const totalTimeElement = document.getElementById('total-time');
    const volumeSlider = document.getElementById('volume-slider');
    const volumeIcon = document.getElementById('volume-icon');
    const likeButton = document.getElementById('like-button');
    const albumCover = document.getElementById('current-album-cover');
    const currentTrack = document.getElementById('current-track');
    const currentArtist = document.getElementById('current-artist');

    let currentTrackIndex = 0;
    let isPlaying = false;
    let isLiked = false;
    let hls = null; // Добавляем HLS.js объект

    // Форматирование времени
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }

    // Загрузка трека с HLS
    function loadTrack(index) {
        const track = playlist[index];

        // Уничтожаем предыдущий HLS-поток
        if (hls) {
            hls.destroy();
            hls = null;
        }

        // Создаем новый HLS-поток
        if (Hls.isSupported()) {
            hls = new Hls({
                // Ключевые настройки для загрузки по требованию
                maxBufferLength: 30,      // Макс. длина буфера (сек)
                maxMaxBufferLength: 60,   // Абсолютный макс. буфер
                backBufferLength: 10,     // Буфер позади текущей позиции
                maxBufferSize: 0,         // Автоматический размер буфера
                enableWorker: true,       // Используем Web Worker
                lowLatencyMode: true,      // Режим низкой задержки
            });

            hls.loadSource(track.hlsUrl); // URL плейлиста M3U8
            hls.attachMedia(audio);

            // Обработчики событий HLS
            hls.on(Hls.Events.MANIFEST_PARSED, function () {
                console.log("HLS manifest parsed");
            });
        }
        // Для браузеров с нативной поддержкой HLS (Safari)
        else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
            audio.src = track.hlsUrl;
        }

        // Обновляем UI
        albumCover.src = track.cover;
        currentTrack.textContent = track.title;
        currentArtist.textContent = track.artist;
        progressBar.value = 0;
        currentTimeElement.textContent = '0:00';
        totalTimeElement.textContent = formatTime(track.duration);
    }

    // Воспроизведение/пауза
    function togglePlay() {
        if (isPlaying) {
            audio.pause();
            playIcon.classList.replace('fa-pause', 'fa-play');
            player.classList.remove('playing');
        } else {
            audio.play().catch(e => console.error("Play error:", e));
            playIcon.classList.replace('fa-play', 'fa-pause');
            player.classList.add('playing');
        }
        isPlaying = !isPlaying;
    }

    // Обновление прогресса
    function updateProgress() {
        if (isFinite(audio.duration)) {
            const percent = (audio.currentTime / audio.duration) * 100;
            progressBar.value = percent;
            currentTimeElement.textContent = formatTime(audio.currentTime);
        }
    }

    // Перемотка
    function setProgress() {
        if (isFinite(audio.duration)) {
            const seekTime = (progressBar.value / 100) * audio.duration;
            audio.currentTime = seekTime;
        }
    }

    // Управление громкостью
    function setVolume() {
        audio.volume = volumeSlider.value / 100;
        volumeIcon.className = audio.volume === 0 ?
            'fas fa-volume-mute' :
            audio.volume < 0.5 ?
                'fas fa-volume-down' :
                'fas fa-volume-up';
    }

    // Переключение лайка
    function toggleLike() {
        isLiked = !isLiked;
        likeButton.innerHTML = isLiked ?
            '<i class="fas fa-heart text-rose-500"></i>' :
            '<i class="far fa-heart"></i>';
    }

    // Следующий трек
    function nextTrack() {
        currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) audio.play();
    }

    // Предыдущий трек
    function prevTrack() {
        currentTrackIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) audio.play();
    }

    // Инициализация плеера
    loadTrack(currentTrackIndex);

    // Обработчики событий
    playButton.addEventListener('click', togglePlay);
    progressBar.addEventListener('input', setProgress);
    volumeSlider.addEventListener('input', setVolume);
    likeButton.addEventListener('click', toggleLike);
    document.getElementById('next-button').addEventListener('click', nextTrack);
    document.getElementById('prev-button').addEventListener('click', prevTrack);

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', nextTrack);
    setVolume();
});
