document.addEventListener('DOMContentLoaded', function () {
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
    let hls = null;
    let playlist = []; // Начальный плейлист пуст

    // Форматирование времени
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }

    // Загрузка трека
    function loadTrack(index) {
        if (index < 0 || index >= playlist.length) return;

        const track = playlist[index];
        currentTrackIndex = index;

        // Обновляем информацию
        albumCover.src = track.cover;
        currentTrack.textContent = track.title;
        currentArtist.textContent = track.artist;
        totalTimeElement.textContent = formatTime(track.duration);
        progressBar.value = 0;
        currentTimeElement.textContent = '0:00';

        // Останавливаем предыдущее воспроизведение
        if (hls) {
            hls.destroy();
            hls = null;
        }

        // Загрузка HLS
        if (Hls.isSupported()) {
            hls = new Hls({
                maxBufferLength: 2,  // Буфер только на 10 секунд вперед
                backBufferLength: 1,
                maxLoadingDelay: 1000,
                nudgeOffset: 0.1,
                enableWorker: true

            });

            hls.loadSource(track.playlistUrl);
            hls.attachMedia(audio);

            hls.on(Hls.Events.MANIFEST_PARSED, () => {
                console.log("HLS manifest parsed");
            });

            hls.on(Hls.Events.ERROR, (event, data) => {
                console.error("HLS error:", data);
            });
        }
        // Для браузеров с нативной поддержкой HLS (Safari)
        else if (audio.canPlayType('application/vnd.apple.mpegurl')) {
            audio.src = track.playlistUrl;
        }
    }

    // Воспроизведение/пауза
    function togglePlay() {
        if (isPlaying) {
            audio.pause();
            playIcon.classList.replace('fa-pause', 'fa-play');
        } else {
            const playPromise = audio.play();

            if (playPromise !== undefined) {
                playPromise.catch(error => {
                    playIcon.classList.replace('fa-pause', 'fa-play');
                    console.error("Playback error:", error);
                });
            }
            playIcon.classList.replace('fa-play', 'fa-pause');
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
        if (playlist.length === 0) return;
        currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) audio.play();
    }

    // Предыдущий трек
    function prevTrack() {
        if (playlist.length === 0) return;
        currentTrackIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) audio.play();
    }

    // Обработчик события playTrack
    document.addEventListener('playTrack', function (e) {
        const trackData = e.detail;

        // Создаем временный плейлист из одного трека
        playlist = [{
            id: trackData.id,
            title: trackData.title,
            artist: trackData.artist,
            cover: trackData.coverUrl,
            playlistUrl: trackData.playlistUrl,
            duration: parseInt(trackData.duration)
        }];

        // Воспроизводим трек
        currentTrackIndex = 0;
        loadTrack(currentTrackIndex);

        // Попытка воспроизведения
        setTimeout(() => {
            isPlaying = false;
            togglePlay();
        }, 100);
    });
    document.addEventListener('playSingleTrack', function (e) {
        const trackData = e.detail;

        // Создаем временный плейлист из одного трека
        playlist = [{
            id: trackData.id,
            title: trackData.title,
            artist: trackData.artist,
            cover: trackData.coverUrl,
            playlistUrl: trackData.playlistUrl,
            duration: parseInt(trackData.duration)
        }];

        // Воспроизводим трек
        currentTrackIndex = 0;
        loadTrack(currentTrackIndex);

        // Попытка воспроизведения
        setTimeout(() => {
            isPlaying = false;
            togglePlay();
        }, 100);
    });

    // Обработчик события playAlbum
    document.addEventListener('playAlbum', function (e) {
        playlist = e.detail.tracks.map(track => ({
            id: track.id,
            title: track.title,
            artist: track.artist,
            cover: track.coverUrl,
            playlistUrl: track.playlistUrl,
            duration: parseInt(track.duration)
        }));

        currentTrackIndex = 0;
        loadTrack(currentTrackIndex);

        setTimeout(() => {
            isPlaying = false;
            togglePlay();
        }, 100);
    });

    // Инициализация обработчиков
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