window.currentAlbumPlaylist = [
    {% for track in album_tracks %}
    {
        title: "{{ track.title|escapejs }}",
        artist: "{{ album.artist.name|escapejs }}",
        file: "{{ track.audio.url|escapejs }}",
        cover: "{{ album.cover.url|escapejs }}"
    }{% if not forloop.last %},{% endif %}
    {% endfor %}
];