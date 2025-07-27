document.addEventListener('DOMContentLoaded', function() {
    const audio = new Audio();
    const playPauseBtn = document.getElementById('play-pause');
    const prevBtn = document.getElementById('prev');
    const nextBtn = document.getElementById('next');
    const progress = document.getElementById('progress');
    const trackTitle = document.getElementById('track-title');
    const trackArtist = document.getElementById('track-artist');
    const volumeBtn = document.getElementById('volume');
    let currentPlaylist = [];
    let currentTrackIndex = 0;

    // Функция для воспроизведения трека
    function playTrack(src, title, artist) {
        audio.src = src;
        audio.play();
        trackTitle.textContent = title;
        trackArtist.textContent = artist;
        playPauseBtn.innerHTML = '<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M6 4h4v16H6zm8 0h4v16h-4z"></path></svg>';
    }

    // Обработчик клика на кнопке Play/Pause
    playPauseBtn.addEventListener('click', function() {
        if (audio.paused) {
            audio.play();
            playPauseBtn.innerHTML = '<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M6 4h4v16H6zm8 0h4v16h-4z"></path></svg>';
        } else {
            audio.pause();
            playPauseBtn.innerHTML = '<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M14 10l-2 2m0 0l-2-2m2 2v6m2-6v6m-6-6h6m-6 6H6"></path></svg>';
        }
    });

    // Обработчик клика на треке
    document.querySelectorAll('.play-track').forEach(button => {
        button.addEventListener('click', function() {
            const src = this.dataset.src;
            const title = this.dataset.title;
            const artist = this.dataset.artist;
            playTrack(src, title, artist);
        });
    });

    // Обновление прогресс-бара
    audio.addEventListener('timeupdate', function() {
        const progressPercent = (audio.currentTime / audio.duration) * 100;
        progress.value = progressPercent || 0;
    });

    // Перемотка трека
    progress.addEventListener('input', function() {
        const time = (progress.value / 100) * audio.duration;
        audio.currentTime = time;
    });

    // Управление громкостью
    volumeBtn.addEventListener('click', function() {
        audio.volume = audio.volume === 1 ? 0 : 1;
        volumeBtn.innerHTML = audio.volume === 1
            ? '<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.943.984L5.586 15z"></path></svg>'
            : '<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.943.984L5.586 15zM15 6l6 6m0 0l-6 6"></path></svg>';
    });
});