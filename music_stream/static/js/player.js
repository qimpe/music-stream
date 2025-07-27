document.addEventListener('DOMContentLoaded', function() {
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
            
            // Загрузка трека
            function loadTrack(index) {
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
            }
            
            // Воспроизведение/пауза
            function togglePlay() {
                if (isPlaying) {
                    audio.pause();
                    playIcon.classList.remove('fa-pause');
                    playIcon.classList.add('fa-play');
                    player.classList.remove('playing');
                } else {
                    audio.play();
                    playIcon.classList.remove('fa-play');
                    playIcon.classList.add('fa-pause');
                    player.classList.add('playing');
                }
                isPlaying = !isPlaying;
            }
            
            // Обновление прогресса
            function updateProgress() {
                const percent = (audio.currentTime / audio.duration) * 100;
                progressBar.value = percent;
                
                const currentMinutes = Math.floor(audio.currentTime / 60);
                const currentSeconds = Math.floor(audio.currentTime % 60);
                currentTimeElement.textContent = `${currentMinutes}:${currentSeconds < 10 ? '0' : ''}${currentSeconds}`;
            }
            
            // Перемотка
            function setProgress() {
                const seekTime = (progressBar.value / 100) * audio.duration;
                audio.currentTime = seekTime;
            }
            
            // Управление громкостью
            function setVolume() {
                audio.volume = volumeSlider.value / 100;
                
                if (audio.volume === 0) {
                    volumeIcon.classList.remove('fa-volume-up', 'fa-volume-down');
                    volumeIcon.classList.add('fa-volume-mute');
                } else if (audio.volume < 0.5) {
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
            
            // Следующий трек
            function nextTrack() {
                currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
                loadTrack(currentTrackIndex);
                if (isPlaying) {
                    audio.play();
                }
            }
            
            // Предыдущий трек
            function prevTrack() {
                currentTrackIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length;
                loadTrack(currentTrackIndex);
                if (isPlaying) {
                    audio.play();
                }
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
            
            // Инициализация громкости
            setVolume();
            
            // Показать/скрыть плеер
            
        });