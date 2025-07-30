document.addEventListener('DOMContentLoaded', function() {
    // Основные элементы плеера
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
    const nextButton = document.getElementById('next-button');
    const prevButton = document.getElementById('prev-button');
    
    // Состояние плеера
    let currentTrackIndex = 0;
    let isPlaying = false;
    let isLiked = false;
    let playlist = [];
    
    // Генерация плейлиста из данных альбома
    function generatePlaylist() {
        // Используем данные, переданные из Django-шаблона
        playlist = window.currentAlbumPlaylist || [];
        
        // Инициализация плеера первым треком
        if (playlist.length > 0) {
            loadTrack(0);
        }
    }
    
    // Загрузка трека
    function loadTrack(index) {
        if (playlist.length === 0) return;
        
        const track = playlist[index];
        audio.src = track.file;
        albumCover.src = track.cover;
        currentTrack.textContent = track.title;
        currentArtist.textContent = track.artist;
        
        // Сброс прогресса
        progressBar.value = 0;
        currentTimeElement.textContent = '0:00';
        
        // Обновление времени трека после загрузки метаданных
        audio.onloadedmetadata = function() {
            const totalMinutes = Math.floor(audio.duration / 60);
            const totalSeconds = Math.floor(audio.duration % 60);
            totalTimeElement.textContent = `${totalMinutes}:${totalSeconds < 10 ? '0' : ''}${totalSeconds}`;
        };
        
        // Сброс лайка
        resetLikeButton();
    }
    
    // Воспроизведение конкретного трека
    function playTrack(index) {
        if (index < 0 || index >= playlist.length) return;
        
        currentTrackIndex = index;
        loadTrack(currentTrackIndex);
        
        audio.play().then(() => {
            isPlaying = true;
            playIcon.classList.replace('fa-play', 'fa-pause');
            player.classList.add('playing');
            
            // Показываем плеер, если он скрыт
            player.style.display = 'block';
        }).catch(e => console.error("Play error:", e));
    }
    
    // Воспроизведение/пауза
    function togglePlay() {
        if (playlist.length === 0) return;
        
        if (isPlaying) {
            audio.pause();
            playIcon.classList.replace('fa-pause', 'fa-play');
            player.classList.remove('playing');
        } else {
            audio.play().then(() => {
                playIcon.classList.replace('fa-play', 'fa-pause');
                player.classList.add('playing');
                
                // Показываем плеер, если он скрыт
                player.style.display = 'block';
            }).catch(e => console.error("Play error:", e));
        }
        isPlaying = !isPlaying;
    }
    
    // Обновление прогресса
    function updateProgress() {
        if (!audio.duration || audio.duration === Infinity) return;
        
        const percent = (audio.currentTime / audio.duration) * 100;
        progressBar.value = percent;
        
        const currentMinutes = Math.floor(audio.currentTime / 60);
        const currentSeconds = Math.floor(audio.currentTime % 60);
        currentTimeElement.textContent = `${currentMinutes}:${currentSeconds < 10 ? '0' : ''}${currentSeconds}`;
    }
    
    // Перемотка
    function setProgress() {
        if (!audio.duration || audio.duration === Infinity) return;
        
        const seekTime = (progressBar.value / 100) * audio.duration;
        audio.currentTime = seekTime;
    }
    
    // Управление громкостью
    function setVolume() {
        const volume = volumeSlider.value / 100;
        audio.volume = volume;
        
        if (volume === 0) {
            volumeIcon.classList.remove('fa-volume-up', 'fa-volume-down');
            volumeIcon.classList.add('fa-volume-mute');
        } else if (volume < 0.5) {
            volumeIcon.classList.remove('fa-volume-up', 'fa-volume-mute');
            volumeIcon.classList.add('fa-volume-down');
        } else {
            volumeIcon.classList.remove('fa-volume-down', 'fa-volume-mute');
            volumeIcon.classList.add('fa-volume-up');
        }
    }
    
    // Переключение лайка
    function toggleLike() {
        isLiked = !isLiked;
        if (isLiked) {
            likeButton.innerHTML = '<i class="fas fa-heart text-rose-500"></i>';
        } else {
            likeButton.innerHTML = '<i class="far fa-heart"></i>';
        }
    }
    
    // Сброс лайка при смене трека
    function resetLikeButton() {
        isLiked = false;
        likeButton.innerHTML = '<i class="far fa-heart"></i>';
    }
    
    // Следующий трек
    function nextTrack() {
        if (playlist.length === 0) return;
        
        currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) {
            audio.play();
        }
    }
    
    // Предыдущий трек
    function prevTrack() {
        if (playlist.length === 0) return;
        
        currentTrackIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length;
        loadTrack(currentTrackIndex);
        if (isPlaying) {
            audio.play();
        }
    }
    
    // Инициализация плеера
    function initPlayer() {
        generatePlaylist();
        setVolume();
        
        // Обработчики событий
        playButton.addEventListener('click', togglePlay);
        progressBar.addEventListener('input', setProgress);
        volumeSlider.addEventListener('input', setVolume);
        likeButton.addEventListener('click', toggleLike);
        nextButton.addEventListener('click', nextTrack);
        prevButton.addEventListener('click', prevTrack);
        
        audio.addEventListener('timeupdate', updateProgress);
        audio.addEventListener('ended', nextTrack);
        
        // Обработчики для треков
        document.querySelectorAll('.play-track').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                if (!isNaN(index)) {
                    playTrack(index);
                }
            });
        });
        
        // Обработчик для кнопки "Play Album"
        document.querySelector('.play-all').addEventListener('click', function() {
            if (playlist.length > 0) {
                playTrack(0);
            }
        });
    }
    
    // Запуск инициализации
    initPlayer();
});