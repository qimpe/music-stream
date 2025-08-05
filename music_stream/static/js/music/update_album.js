
    // Cover image preview
    document.getElementById('id_cover').addEventListener('change', function(e) {
        const preview = document.getElementById('cover-preview');
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Cover preview" class="w-full h-full object-cover">`;
            }
            reader.readAsDataURL(this.files[0]);
        }
    });

    // Audio file preview (update display when file selected)
    document.querySelectorAll('.audio-file-input').forEach(input => {
        input.addEventListener('change', function() {
            const display = this.closest('.relative').querySelector('.file-name');
            if (this.files && this.files[0]) {
                display.textContent = this.files[0].name;
            } else {
                display.textContent = "Select audio file";
            }
        });
    });
